from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
import uuid

from dotenv import load_dotenv
import pandas as pd
from pymongo import MongoClient
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
import torch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from model_loader import load_tokenizer_and_model
from privacy_utils import env_flag, pseudonymize_identifier
from reporting import ensure_run_dir, mirror_latest_files, relative_report_path, write_json


load_dotenv()


@dataclass
class SimulatedCase:
    scenario_id: str
    scenario: str
    text: str
    expected_label: int


def preprocesar_texto(msg: str) -> str:
    msg = re.sub(r"\s+", " ", str(msg))
    return msg.lower().strip()


def simulated_cases() -> list[SimulatedCase]:
    return [
        SimulatedCase("S1", "Benigno corporativo", "Gracias, cierro el ticket y te confirmo.", 0),
        SimulatedCase(
            "S2",
            "URL sospechosa con urgencia",
            "URGENTE: verifica tu cuenta ahora mismo en http://secure-login-check.example.net",
            1,
        ),
        SimulatedCase("S3", "Solicitud credenciales", "Necesito tu codigo 2FA para finalizar la validacion del acceso.", 1),
        SimulatedCase("S4", "Multilingue", "Please send the final report by 17:00 CET.", 0),
        SimulatedCase("S5", "Mensaje vacio/simbolos", "   ...   ", 0),
        SimulatedCase("S6", "Phishing con factura", "Your invoice is pending. Open now: http://invoice-security-check.example.org", 1),
        SimulatedCase("S7", "Comunicacion interna", "Reunion de seguimiento de riesgos a las 09:00.", 0),
        SimulatedCase("S8", "Amenaza extorsion", "Tenemos tu contrasena filtrada, paga en BTC o publicamos los datos.", 1),
    ]


def predict_rule_based(text: str) -> tuple[int, float, str]:
    lowered = preprocesar_texto(text)
    suspicious_patterns = [
        r"http[s]?://",
        r"\bverifica\b",
        r"\bverify\b",
        r"\b2fa\b",
        r"\bpassword\b",
        r"\bcontrasena\b",
        r"\bbtc\b",
        r"\burgente\b",
        r"\bsuspended\b",
    ]
    hits = sum(1 for pattern in suspicious_patterns if re.search(pattern, lowered))
    score = min(0.95, 0.1 + hits * 0.15)
    pred = 1 if score >= 0.5 else 0
    return pred, score, "rule_based_fallback"


def predict_model(text: str, tokenizer, model, threshold: float, device: torch.device) -> tuple[int, float, float]:
    clean = preprocesar_texto(text)
    inputs = tokenizer(clean, return_tensors="pt", truncation=True, padding=True)
    inputs = {key: value.to(device) for key, value in inputs.items()}

    started = time.perf_counter()
    with torch.no_grad():
        logits = model(**inputs).logits
        probs = torch.softmax(logits, dim=1)[0].tolist()
    latency_ms = round((time.perf_counter() - started) * 1000, 3)

    score_1 = float(probs[1])
    pred = 1 if score_1 >= threshold else 0
    return pred, score_1, latency_ms


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulador de casos E2E para Fase 5.")
    parser.add_argument("--threshold", type=float, default=float(os.getenv("THRESHOLD", "0.05")))
    parser.add_argument("--outdir", default="reports")
    parser.add_argument("--write-mongo", action="store_true")
    parser.add_argument("--mongo-uri", default=os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    parser.add_argument("--mongo-db", default=os.getenv("MONGO_DB", "tfg"))
    parser.add_argument("--mongo-collection", default=os.getenv("MONGO_COLLECTION", "messages"))
    args = parser.parse_args()

    reports_dir = Path(args.outdir)
    run_id = f"sim-{uuid.uuid4()}"
    run_dir = ensure_run_dir(reports_dir, run_id)
    hf_model = os.getenv("HF_MODEL", "alvaroosuna/distilbert_fast_fixed_labels")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    pii_salt = os.getenv("PII_SALT", "change-me-local-salt")
    store_msg_original = env_flag(os.getenv("STORE_MSG_ORIGINAL"), default=False)
    store_msg_normalized = env_flag(os.getenv("STORE_MSG_NORMALIZED"), default=False)

    rows: list[dict[str, object]] = []
    tokenizer = model = None
    model_source = "rule_based_fallback"
    mode = "fallback"
    try:
        tokenizer, model, model_source = load_tokenizer_and_model(hf_model, device)
        mode = "model"
    except Exception:
        tokenizer = model = None

    for case in simulated_cases():
        if mode == "model":
            pred, score_1, latency_ms = predict_model(case.text, tokenizer, model, args.threshold, device)
            source = model_source
        else:
            pred, score_1, source = predict_rule_based(case.text)
            latency_ms = 0.0

        rows.append(
            {
                "run_id": run_id,
                "scenario_id": case.scenario_id,
                "scenario": case.scenario,
                "text": case.text,
                "text_sha256": hashlib.sha256(case.text.encode("utf-8")).hexdigest(),
                "expected_label": case.expected_label,
                "pred": pred,
                "score_1": round(score_1, 6),
                "is_match": int(pred == case.expected_label),
                "latency_ms": latency_ms,
                "mode": mode,
                "model_source": source,
                "threshold_used": args.threshold,
                "created_at_utc": datetime.now(timezone.utc).isoformat(),
            }
        )

    frame = pd.DataFrame(rows)
    out_csv = run_dir / "simulated_cases_results.csv"
    frame.to_csv(out_csv, index=False)

    y_true = frame["expected_label"].tolist()
    y_pred = frame["pred"].tolist()
    out_json = run_dir / "e2e_evidence.json"
    summary: dict[str, object] = {
        "run_id": run_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "num_cases": int(len(frame)),
        "mode": mode,
        "hf_model": hf_model,
        "model_source": model_source if mode == "model" else "rule_based_fallback",
        "threshold": args.threshold,
        "artifacts_dir": relative_report_path(run_dir, reports_dir),
        "metrics": {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision_pos": float(precision_score(y_true, y_pred, pos_label=1, zero_division=0)),
            "recall_pos": float(recall_score(y_true, y_pred, pos_label=1, zero_division=0)),
            "f1_pos": float(f1_score(y_true, y_pred, pos_label=1, zero_division=0)),
        },
        "outputs": {
            "csv": relative_report_path(out_csv, reports_dir),
            "json": relative_report_path(out_json, reports_dir),
        },
    }

    mongo_result: dict[str, object] = {"enabled": bool(args.write_mongo)}
    if args.write_mongo:
        try:
            client = MongoClient(args.mongo_uri, serverSelectionTimeoutMS=1500)
            collection = client[args.mongo_db][args.mongo_collection]
            docs = []
            for row in rows:
                item = {
                    "run_id": row["run_id"],
                    "created_at_utc": datetime.now(timezone.utc),
                    "chat_hash": pseudonymize_identifier("sim-chat", namespace="chat_id", salt=pii_salt),
                    "user_hash": pseudonymize_identifier("sim-user", namespace="user_id", salt=pii_salt),
                    "message_id": int(str(row["scenario_id"])[1:]),
                    "msg_sha256": row["text_sha256"],
                    "pred": row["pred"],
                    "score_1": row["score_1"],
                    "latency_ms": row["latency_ms"],
                    "ok": True,
                    "error": None,
                    "threshold": row["threshold_used"],
                    "hf_model": hf_model,
                    "model_source": row["model_source"],
                    "device": str(device),
                    "scenario": row["scenario"],
                    "expected_label": row["expected_label"],
                }
                if store_msg_original:
                    item["msg_original"] = row["text"]
                if store_msg_normalized:
                    item["msg_limpio"] = preprocesar_texto(str(row["text"]))
                docs.append(item)
            if docs:
                collection.insert_many(docs)
            client.close()
            mongo_result = {"enabled": True, "inserted_docs": len(docs), "ok": True}
        except Exception as exc:
            mongo_result = {"enabled": True, "ok": False, "error": str(exc)}

    summary["mongo"] = mongo_result
    write_json(out_json, summary)
    mirror_latest_files(run_dir, reports_dir, ["simulated_cases_results.csv", "e2e_evidence.json"])

    print(
        "OK -> "
        f"{relative_report_path(out_csv, reports_dir)} | "
        f"{relative_report_path(out_json, reports_dir)}"
    )


if __name__ == "__main__":
    main()

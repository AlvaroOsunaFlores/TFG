from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import shutil
from typing import Any

from preprocessing import preprocess_record


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parents[2]

DEFAULT_INPUT_RAW = PROJECT_ROOT / "data" / "raw" / "sample_messages.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "labeled" / "fake_news_seed.csv"
DEFAULT_ROOT_MIRROR = WORKSPACE_ROOT / "datos_entrenamiento" / "tfg_informatica_fake_news" / "fake_news_seed.csv"

FIELDNAMES = [
    "source_id",
    "channel",
    "date_utc",
    "text",
    "normalized_text",
    "language",
    "label",
    "label_name",
    "source",
]

LABEL_NAMES = {
    0: "verificado_o_neutro",
    1: "fake_news",
}

RAW_SAMPLE_LABELS = {
    1001: 1,
    1002: 0,
    1003: 1,
}

CURATED_SEED_MESSAGES = [
    {
        "source_id": "synthetic-2001",
        "channel": "alerta_bulos_salud",
        "date_utc": "2026-03-20T09:00:00+00:00",
        "text": "Difunden que beber lejia elimina cualquier virus en menos de una hora. Comparte antes de que lo borren.",
        "label": 1,
        "source": "synthetic_seed",
    },
    {
        "source_id": "synthetic-2002",
        "channel": "verificacion_publica",
        "date_utc": "2026-03-20T09:05:00+00:00",
        "text": "El ministerio desmiente el rumor sobre el cierre inmediato de todos los colegios y publica el calendario oficial.",
        "label": 0,
        "source": "synthetic_seed",
    },
    {
        "source_id": "synthetic-2003",
        "channel": "politica_viral",
        "date_utc": "2026-03-20T09:10:00+00:00",
        "text": "Urgente: circula una captura falsa sobre un supuesto fraude electoral masivo sin fuente verificable.",
        "label": 1,
        "source": "synthetic_seed",
    },
    {
        "source_id": "synthetic-2004",
        "channel": "agencia_verifica",
        "date_utc": "2026-03-20T09:20:00+00:00",
        "text": "La imagen viral del hospital inundado pertenece a 2021 y no al temporal de esta semana.",
        "label": 0,
        "source": "synthetic_seed",
    },
    {
        "source_id": "synthetic-2005",
        "channel": "global_watch",
        "date_utc": "2026-03-20T09:30:00+00:00",
        "text": "Breaking: a fabricated article claims that a city banned all vaccines overnight with no official decree attached.",
        "label": 1,
        "source": "synthetic_seed",
    },
    {
        "source_id": "synthetic-2006",
        "channel": "fact_check_world",
        "date_utc": "2026-03-20T09:40:00+00:00",
        "text": "Fact check: the viral post about bank withdrawals being frozen is false according to the central bank notice.",
        "label": 0,
        "source": "synthetic_seed",
    },
    {
        "source_id": "synthetic-2007",
        "channel": "tecnologia_viral",
        "date_utc": "2026-03-20T09:50:00+00:00",
        "text": "Se comparte que una aplicacion oficial espia automaticamente todos los telefonos, pero el mensaje no aporta ninguna prueba.",
        "label": 1,
        "source": "synthetic_seed",
    },
    {
        "source_id": "synthetic-2008",
        "channel": "consumo_verificado",
        "date_utc": "2026-03-20T10:00:00+00:00",
        "text": "La organizacion de consumidores aclara que la supuesta retirada masiva de leche no existe y enlaza el aviso real.",
        "label": 0,
        "source": "synthetic_seed",
    },
    {
        "source_id": "synthetic-2009",
        "channel": "rumores_locales",
        "date_utc": "2026-03-20T10:10:00+00:00",
        "text": "Aseguran que el ayuntamiento va a cortar el agua durante un mes entero, pero solo circula un audio anonimo.",
        "label": 1,
        "source": "synthetic_seed",
    },
    {
        "source_id": "synthetic-2010",
        "channel": "servicio_publico",
        "date_utc": "2026-03-20T10:15:00+00:00",
        "text": "La compania electrica confirma que el mensaje sobre un apagado total del pais es un bulo y mantiene el servicio normal.",
        "label": 0,
        "source": "synthetic_seed",
    },
]


def _load_raw_records(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _record_from_sample(raw_record: dict[str, Any]) -> dict[str, Any]:
    processed = preprocess_record(raw_record)
    message_id = int(raw_record["message_id"])
    label = RAW_SAMPLE_LABELS[message_id]
    return {
        "source_id": f"sample-{message_id}",
        "channel": str(raw_record.get("channel", "")),
        "date_utc": str(raw_record.get("date_utc", "")),
        "text": str(raw_record.get("text", "")),
        "normalized_text": processed.normalized_text,
        "language": processed.language,
        "label": label,
        "label_name": LABEL_NAMES[label],
        "source": "sample_messages_json",
    }


def _record_from_curated(raw_record: dict[str, Any]) -> dict[str, Any]:
    processed = preprocess_record(
        {
            "message_id": 0,
            "channel": raw_record["channel"],
            "text": raw_record["text"],
        }
    )
    label = int(raw_record["label"])
    return {
        "source_id": raw_record["source_id"],
        "channel": raw_record["channel"],
        "date_utc": raw_record["date_utc"],
        "text": raw_record["text"],
        "normalized_text": processed.normalized_text,
        "language": processed.language,
        "label": label,
        "label_name": LABEL_NAMES[label],
        "source": raw_record["source"],
    }


def build_seed_rows(raw_records: list[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    if raw_records is None:
        raw_records = _load_raw_records(DEFAULT_INPUT_RAW)

    rows = [_record_from_sample(record) for record in raw_records if int(record["message_id"]) in RAW_SAMPLE_LABELS]
    rows.extend(_record_from_curated(record) for record in CURATED_SEED_MESSAGES)
    rows.sort(key=lambda row: row["source_id"])
    return rows


def write_dataset(rows: list[dict[str, Any]], output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    return output_path


def mirror_dataset(source_path: Path, mirror_path: Path) -> Path:
    mirror_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, mirror_path)
    return mirror_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Construye un dataset ficticio y etiquetado para la siguiente fase del TFG.")
    parser.add_argument("--input-raw", default=str(DEFAULT_INPUT_RAW))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--mirror-root", default=str(DEFAULT_ROOT_MIRROR))
    parser.add_argument("--skip-root-mirror", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_raw = Path(args.input_raw)
    output = Path(args.output)
    mirror_root = Path(args.mirror_root)

    if not input_raw.is_absolute():
        input_raw = PROJECT_ROOT / input_raw
    if not output.is_absolute():
        output = PROJECT_ROOT / output
    if not mirror_root.is_absolute():
        mirror_root = PROJECT_ROOT / mirror_root

    rows = build_seed_rows(_load_raw_records(input_raw))
    write_dataset(rows, output)

    fake_count = sum(row["label"] for row in rows)
    neutral_count = sum(1 for row in rows if row["label"] == 0)
    print(f"OK dataset -> {output.relative_to(PROJECT_ROOT).as_posix()}")
    print(f"Registros: {len(rows)} | fake_news={fake_count} | verificado_o_neutro={neutral_count}")

    if not args.skip_root_mirror:
        mirror_dataset(output, mirror_root)
        print(f"OK mirror -> {mirror_root}")


if __name__ == "__main__":
    main()

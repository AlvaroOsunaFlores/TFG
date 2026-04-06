from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "data" / "labeled" / "fake_news_unified.csv.gz"

REQUIRED_COLUMNS = [
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


def load_dataset(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, compression="infer", keep_default_na=False)


def validate_dataframe(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []

    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        errors.append(f"Faltan columnas obligatorias: {', '.join(missing)}")
        return errors, warnings

    duplicated_ids = int(df["source_id"].duplicated().sum())
    if duplicated_ids:
        errors.append(f"Hay {duplicated_ids} source_id duplicados.")

    if df.empty:
        errors.append("El dataset esta vacio.")
        return errors, warnings

    invalid_labels = sorted(set(df["label"].dropna().tolist()) - {0, 1})
    if invalid_labels:
        errors.append(f"Se han encontrado etiquetas no validas: {invalid_labels}")

    for label, label_name in LABEL_NAMES.items():
        mismatched = df[(df["label"] == label) & (df["label_name"] != label_name)]
        if not mismatched.empty:
            errors.append(f"Hay filas con label={label} y label_name incoherente.")

    for column in REQUIRED_COLUMNS:
        if df[column].isnull().any():
            errors.append(f"La columna {column} contiene valores nulos.")

    empty_text = int(df["text"].astype(str).str.strip().eq("").sum())
    if empty_text:
        errors.append(f"La columna text contiene {empty_text} filas vacias.")

    empty_normalized = int(df["normalized_text"].astype(str).str.strip().eq("").sum())
    if empty_normalized:
        errors.append(f"La columna normalized_text contiene {empty_normalized} filas vacias.")

    label_counts = df["label"].value_counts().to_dict()
    if len(label_counts) < 2:
        warnings.append("Solo hay una clase presente; el entrenamiento posterior no sera valido.")

    languages = sorted(df["language"].dropna().astype(str).unique().tolist())
    if len(languages) == 1:
        warnings.append(f"Solo se ha detectado un idioma en el dataset: {languages[0]}")

    return errors, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Valida schema y consistencia del dataset etiquetado.")
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = PROJECT_ROOT / input_path

    df = load_dataset(input_path)
    errors, warnings = validate_dataframe(df)

    print(f"Dataset: {input_path}")
    print(f"Filas: {len(df)}")
    print(f"Distribucion etiquetas: {df['label'].value_counts().sort_index().to_dict()}")
    print(f"Idiomas: {sorted(df['language'].astype(str).unique().tolist())}")

    for warning in warnings:
        print(f"WARNING: {warning}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)

    print("OK dataset validado")


if __name__ == "__main__":
    main()

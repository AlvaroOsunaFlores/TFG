import pandas as pd
import os

# Carpeta donde están tus CSVs
DATA_PATH = "./"  # Cambia si están en otra carpeta

files = {
    "malicious": "malicious_phish.csv",
    "phishing": "phishing.csv",
    "spam": "spam.csv"
}

datasets = []


def safe_read_csv(filepath):
    """Lee CSV intentando distintos encodings si UTF-8 falla."""
    try:
        return pd.read_csv(filepath)
    except UnicodeDecodeError:
        return pd.read_csv(filepath, encoding="latin1")


# 1️⃣ MALICIOUS_PHISH
malicious_path = os.path.join(DATA_PATH, files["malicious"])
if os.path.exists(malicious_path):
    df = safe_read_csv(malicious_path)
    print("Malicious columns:", df.columns.tolist())

    if "url" in df.columns and "type" in df.columns:
        df = df.rename(columns={"url": "text"})
        df["label"] = df["type"].map({
            "benign": -1,
            "defacement": 1,
            "phishing": 1,
            "malware": 1
        }).fillna(-1).astype(int)
        datasets.append(df[["text", "label"]])

# 2️⃣ PHISHING (dataset técnico)
phishing_path = os.path.join(DATA_PATH, files["phishing"])
if os.path.exists(phishing_path):
    df = safe_read_csv(phishing_path)
    print("Phishing columns:", df.columns.tolist())

    if "URL" in df.columns and "class" in df.columns:
        df = df.rename(columns={"URL": "text", "class": "label"})
        df["label"] = df["label"].apply(lambda x: 1 if x == -1 else -1)
        datasets.append(df[["text", "label"]])
    elif "class" in df.columns:
        df["text"] = "Phishing site with technical features"
        df["label"] = df["class"].apply(lambda x: 1 if x == -1 else -1)
        datasets.append(df[["text", "label"]])

# 3️⃣ SPAM (mensajes SMS o emails)
spam_path = os.path.join(DATA_PATH, files["spam"])
if os.path.exists(spam_path):
    df = safe_read_csv(spam_path)
    print("Spam columns:", df.columns.tolist())

    # Normalizamos nombres de columnas a minúsculas
    df.columns = [c.lower() for c in df.columns]

    if "v1" in df.columns and "v2" in df.columns:  # Formato clásico SMS
        df = df.rename(columns={"v1": "label", "v2": "text"})
        df["label"] = df["label"].map({"spam": 1, "ham": -1})
    elif "label" in df.columns and "text" in df.columns:
        df["label"] = df["label"].map({"spam": 1, "ham": -1})
    else:
        print("⚠️ El dataset de spam no tiene columnas esperadas 'v1/v2' ni 'label/text'. Se omite.")

    if "text" in df.columns and "label" in df.columns:
        datasets.append(df[["text", "label"]])

# 🔄 UNIFICAR TODOS LOS DATASETS
if datasets:
    combined = pd.concat(datasets, ignore_index=True)
    combined.dropna(subset=["text", "label"], inplace=True)
    combined = combined.sample(frac=1, random_state=42).reset_index(drop=True)

    print(f"✅ Dataset combinado con {len(combined)} ejemplos.")
    print(combined.head())

    # 💾 Guardar el dataset combinado
    combined.to_csv("combined_cyber_dataset.csv", index=False)
    print("\nArchivo guardado como 'combined_cyber_dataset.csv'")
else:
    print("⚠️ No se encontraron datasets válidos para combinar.")

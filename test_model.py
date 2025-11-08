# test_model.py
import torch
import spacy
import numpy as np

# -----------------------------
# 1️⃣ CARGAR MODELO GUARDADO
# -----------------------------
checkpoint = torch.load("cyber_spacy_model.pt", map_location="cpu")

itos = checkpoint["vocab"]
stoi = {w: i for i, w in enumerate(itos)}
params = checkpoint["params"]

# -----------------------------
# 2️⃣ DEFINIR CLASE DEL MODELO
# -----------------------------
class MeanEmbeddingClassifier(torch.nn.Module):
    def __init__(self, vocab_size, emb_dim, hidden_dim):
        super().__init__()
        self.embedding = torch.nn.Embedding(vocab_size, emb_dim, padding_idx=0)
        self.fc = torch.nn.Sequential(
            torch.nn.Linear(emb_dim, hidden_dim),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.3),
            torch.nn.Linear(hidden_dim, 2)
        )

    def forward(self, x):
        emb = self.embedding(x)
        mask = (x != 0).unsqueeze(-1).float()
        summed = (emb * mask).sum(1)
        counts = mask.sum(1).clamp(min=1e-9)
        mean = summed / counts
        return self.fc(mean)

# -----------------------------
# 3️⃣ RECONSTRUIR MODELO
# -----------------------------
model = MeanEmbeddingClassifier(
    vocab_size=len(itos),
    emb_dim=params["embedding_dim"],
    hidden_dim=params["hidden_dim"]
)
model.load_state_dict(checkpoint["model_state_dict"])
model.eval()

# -----------------------------
# 4️⃣ CARGAR TOKENIZADOR SPACY
# -----------------------------
SPACY_MODEL = "es_core_news_sm"
try:
    nlp = spacy.load(SPACY_MODEL, disable=["parser", "ner", "tagger"])
except OSError:
    raise RuntimeError(f"Debes descargar el modelo spaCy con:\n  python -m spacy download {SPACY_MODEL}")

def tokenize(text):
    doc = nlp(str(text))
    return [tok.text.lower() for tok in doc if not tok.is_space]

# -----------------------------
# 5️⃣ FUNCIONES AUXILIARES
# -----------------------------
def text_to_ids(text, max_len=params["max_len"]):
    toks = tokenize(text)
    ids = [stoi.get(t, stoi["<UNK>"]) for t in toks[:max_len]]
    if len(ids) < max_len:
        ids += [stoi["<PAD>"]] * (max_len - len(ids))
    return ids

def predict_text(text):
    ids = torch.tensor([text_to_ids(text)], dtype=torch.long)
    with torch.no_grad():
        logits = model(ids)
        pred = logits.argmax(dim=1).item()
        score = torch.softmax(logits, dim=1)[0, pred].item()
        label = "⚠️ Phishing / Spam / Malicioso" if pred == 0 else "✅ Seguro / Benigno"

    print(f"\n📝 Texto: {text}")
    print(f"📊 Predicción: {label} (confianza: {score:.2f})")
    return pred, score

# -----------------------------
# 6️⃣ PROBAR EJEMPLOS
# -----------------------------
if __name__ == "__main__":
    print("🔍 Probando modelo anti-phishing...\n")

    ejemplos = [
        # 🟢 Ejemplos seguros
        "Hola Marta, te envío el resumen de la reunión de ayer en el archivo adjunto.",
        "Gracias por tu compra en Amazon. Tu pedido será entregado mañana.",
        "Tu paquete se encuentra en reparto. Puedes hacer seguimiento en: https://www.correos.es",
        "Hola Luis, te dejo el enlace del documento en Google Drive: https://drive.google.com/document/d/12345",

        # 🔴 Ejemplos sospechosos
        "Su cuenta será suspendida si no confirma sus datos en el siguiente enlace: http://secure-login-verification.com",
        "¡Felicidades! Has ganado un iPhone 15. Reclama tu premio ahora: http://free-apple-gift.win",
        "Último aviso: su paquete no pudo ser entregado. Complete el formulario: http://correos-españa.info/entrega",
        "Confirme su cuenta de Netflix para evitar la cancelación del servicio: http://netflix-renewal-confirm.com"
    ]

    for t in ejemplos:
        predict_text(t)

    print("\n✅ Prueba completada.")

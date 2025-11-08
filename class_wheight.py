import pandas as pd
import numpy as np
import torch

# 📂 1️⃣ Carga el dataset balanceado que creaste en el paso 2
df_bal = pd.read_csv("combined_cyber_balanced.csv")

# 🧾 2️⃣ Convierte las etiquetas de [-1,1] → [0,1]
df_bal["label_int"] = ((df_bal["label"] + 1) // 2).astype(int)

# 📊 3️⃣ Cuenta cuántos ejemplos hay de cada clase
counts = np.bincount(df_bal["label_int"])
print("Conteo de clases:", counts)

# ⚖️ 4️⃣ Calcula los pesos inversos
weights = 1.0 / (counts + 1e-9)
weights = weights / weights.sum()  # normaliza
class_weights = torch.tensor(weights, dtype=torch.float)

# 🧠 5️⃣ Crea tu criterio de pérdida con pesos de clase
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
criterion = torch.nn.CrossEntropyLoss(weight=class_weights.to(device))

print("Pesos de clase:", class_weights)

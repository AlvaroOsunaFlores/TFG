from sklearn.utils import resample
import pandas as pd

df = pd.read_csv("combined_cyber_dataset.csv")

# Separar clases
benignos = df[df.label == -1]
maliciosos = df[df.label == 1]

# Aumentar la minoría hasta igualar la mayoría
maliciosos_up = resample(maliciosos,
                         replace=True,
                         n_samples=len(benignos),
                         random_state=42)

df_bal = pd.concat([benignos, maliciosos_up]).sample(frac=1, random_state=42)

df_bal.to_csv("combined_cyber_balanced.csv", index=False)
print(df_bal.label.value_counts())

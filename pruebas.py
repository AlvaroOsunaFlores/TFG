import pandas as pd

df = pd.read_csv("combined_cyber_dataset.csv")
print(df.label.value_counts())
print(df.label.unique())
print(df.head(10))

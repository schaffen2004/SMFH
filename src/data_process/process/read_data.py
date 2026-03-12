import pandas as pd

df = pd.read_parquet("/home/schaffen/Workspace/Project/SMFH/data/processed/samples.parquet")

print(df.columns)
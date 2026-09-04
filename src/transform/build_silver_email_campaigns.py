from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_PATH = PROJECT_ROOT / "data" / "raw" / "csv_weekly" / "email_campaigns.csv"
SILVER_PATH = PROJECT_ROOT / "data" / "silver"

df = pd.read_csv(RAW_PATH)

df["week_start"] = pd.to_datetime(df["week_start"], format="%Y-%m-%d")
df["week_end"] = pd.to_datetime(df["week_end"], format="%Y-%m-%d")

df.to_parquet(SILVER_PATH / "email_campaigns.parquet")

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(df.dtypes)
print(df.head())

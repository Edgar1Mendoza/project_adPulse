from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_PATH = PROJECT_ROOT / "data" / "raw" / "csv_crm" / "crm_sales.csv"
SILVER_PATH = PROJECT_ROOT / "data" / "silver"

df_crm = pd.read_csv(RAW_PATH)

df_crm["sale_date"] = pd.to_datetime(df_crm["sale_date"], format="%Y-%m-%d")

df_crm.to_parquet(SILVER_PATH / "crm_sales.parquet")

print(f"Rows: {len(df_crm)}")
print(f"Columns: {len(df_crm.columns)}")
print(df_crm.dtypes)
print(df_crm.head())

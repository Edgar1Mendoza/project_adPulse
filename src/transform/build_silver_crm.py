import pandas as pd

from src.utils.paths import get_data_dir, get_project_root

PROJECT_ROOT = get_project_root()

RAW_PATH = get_data_dir("raw") / "csv_crm" / "crm_sales.csv"
SILVER_PATH = get_data_dir("silver")

df_crm = pd.read_csv(RAW_PATH)

df_crm["sale_date"] = pd.to_datetime(df_crm["sale_date"], format="%Y-%m-%d")

df_crm.to_parquet(SILVER_PATH / "crm_sales.parquet")

print(f"Rows: {len(df_crm)}")
print(f"Columns: {len(df_crm.columns)}")
print(df_crm.dtypes)
print(df_crm.head())

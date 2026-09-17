import pandas as pd

from src.utils.paths import get_data_dir, get_project_root

PROJECT_ROOT = get_project_root()

RAW_PATH = get_data_dir("raw") / "csv_weekly" / "email_campaigns.csv"
SILVER_PATH = get_data_dir("silver")

df = pd.read_csv(RAW_PATH)

df["week_start"] = pd.to_datetime(df["week_start"], format="%Y-%m-%d")
df["week_end"] = pd.to_datetime(df["week_end"], format="%Y-%m-%d")

SILVER_PATH.mkdir(parents=True, exist_ok=True)
df.to_parquet(SILVER_PATH / "email_campaigns.parquet")

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(df.dtypes)
print(df.head())

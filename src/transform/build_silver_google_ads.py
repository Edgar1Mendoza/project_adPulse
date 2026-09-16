import pandas as pd

from src.utils.paths import get_data_dir, get_project_root

PROJECT_ROOT = get_project_root()

RAW_PATH = get_data_dir("raw") / "csv_daily" / "google_ads_weekly.csv"
SILVER_PATH = get_data_dir("silver")

df = pd.read_csv(RAW_PATH)

df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

df.to_parquet(SILVER_PATH / "google_ads_weekly.parquet")

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(df.dtypes)
print(df.head())

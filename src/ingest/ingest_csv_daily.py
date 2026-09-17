import shutil

import pandas as pd

from src.utils.paths import get_data_dir, get_project_root, get_source_dir

PROJECT_ROOT = get_project_root()

SOURCE_DIR = get_source_dir()
SOURCE_PATH = SOURCE_DIR / "google_ads_weekly.csv"
RAW_PATH = get_data_dir("raw") / "csv_daily" / "google_ads_weekly.csv"

RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
shutil.copy(SOURCE_PATH, RAW_PATH)

df = pd.read_csv(RAW_PATH)

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(df.dtypes)

import shutil

import pandas as pd

from src.utils.paths import get_data_dir, get_project_root, get_source_dir

PROJECT_ROOT = get_project_root()

FILE_NAME = "email_campaigns.csv"
SOURCE_DIR = get_source_dir()
SOURCE_PATH = SOURCE_DIR / "email_campaigns.csv"

RAW_DIR = get_data_dir("raw") / "csv_weekly"
RAW_PATH = RAW_DIR / FILE_NAME
RAW_DIR.mkdir(parents=True, exist_ok=True)

shutil.copy(SOURCE_PATH, RAW_PATH)

df = pd.read_csv(RAW_PATH)

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(df.dtypes)

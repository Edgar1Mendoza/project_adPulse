import shutil

import pandas as pd

from src.utils.paths import get_data_dir, get_project_root, get_source_dir

PROJECT_ROOT = get_project_root()
FILENAME = "campaign_mapping.csv"
SOURCE_DIR = get_source_dir()
SOURCE_PATH = SOURCE_DIR / "campaign_mapping.csv"
RAW_DIR = get_data_dir("raw") / "csv_mapping"
RAW_PATH = RAW_DIR / FILENAME

RAW_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy(SOURCE_PATH, RAW_PATH)

df_mapping = pd.read_csv(RAW_PATH)

print(f"Rows: {len(df_mapping)}")
print(f"Columns: {len(df_mapping.columns)}")
print(df_mapping.dtypes)

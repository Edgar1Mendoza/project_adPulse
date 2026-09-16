import shutil

import pandas as pd

from src.utils.paths import get_data_dir, get_project_root, get_source_dir

PROJECT_ROOT = get_project_root()

SOURCE_DIR = get_source_dir()
SOURCE_PATH = SOURCE_DIR / "campaign_mapping.csv"
RAW_PATH = get_data_dir("raw") / "csv_mapping" / "campaign_mapping.csv"

shutil.copy(SOURCE_PATH, RAW_PATH)

df_mapping = pd.read_csv(RAW_PATH)

print(f"Rows: {len(df_mapping)}")
print(f"Columns: {len(df_mapping.columns)}")
print(df_mapping.dtypes)

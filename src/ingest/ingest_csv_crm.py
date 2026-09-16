import shutil

import pandas as pd

from src.utils.paths import get_data_dir, get_project_root, get_source_dir

PROJECT_ROOT = get_project_root()

SOURCE_DIR = get_source_dir()
SOURCE_PATH = SOURCE_DIR / "crm_ventas.csv"
RAW_PATH = get_data_dir("raw") / "csv_crm" / "crm_sales.csv"

shutil.copy(SOURCE_PATH, RAW_PATH)

df = pd.read_csv(RAW_PATH)

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(df.dtypes)

import os
import shutil
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from src.utils.paths import get_project_root

load_dotenv()

PROJECT_ROOT = get_project_root()

SOURCE_DIR = Path(os.environ["DOWNLOADS_SOURCE_DIR"])
SOURCE_PATH = SOURCE_DIR / "campaign_mapping.csv"
RAW_PATH = PROJECT_ROOT / "data" / "raw" / "csv_mapping" / "campaign_mapping.csv"

shutil.copy(SOURCE_PATH, RAW_PATH)

df_mapping = pd.read_csv(RAW_PATH)

print(f"Rows: {len(df_mapping)}")
print(f"Columns: {len(df_mapping.columns)}")
print(df_mapping.dtypes)

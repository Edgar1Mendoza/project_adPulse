import os
import shutil
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from src.utils.paths import get_data_dir, get_project_root

load_dotenv()

PROJECT_ROOT = get_project_root()

SOURCE_DIR = Path(os.environ["DOWNLOADS_SOURCE_DIR"])
SOURCE_PATH = SOURCE_DIR / "google_ads_weekly.csv"
RAW_PATH = get_data_dir("raw") / "csv_daily" / "google_ads_weekly.csv"

shutil.copy(SOURCE_PATH, RAW_PATH)

df = pd.read_csv(RAW_PATH)

print(f"Rows: {len(df)}")
print(f"Columns: {len(df.columns)}")
print(df.dtypes)

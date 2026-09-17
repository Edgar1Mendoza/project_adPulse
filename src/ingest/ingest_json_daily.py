import json
import shutil

import pandas as pd

from src.utils.paths import get_data_dir, get_project_root, get_source_dir

PROJECT_ROOT = get_project_root()

SOURCE_DIR = get_source_dir()
SOURCE_PATH = SOURCE_DIR / "meta_ads.json"
RAW_PATH = get_data_dir("raw") / "json_daily" / "meta_ads.json"

RAW_PATH.parent.mkdir(parents=True, exist_ok=True)
shutil.copy(SOURCE_PATH, RAW_PATH)

with open(RAW_PATH) as f:
    data = json.load(f)

records = data["data"]

print(f"Rows: {len(records)}")


df_meta = pd.DataFrame(records)

print(f"Columns: {len(df_meta.columns)}")
print(df_meta.dtypes)

import json
import shutil
from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir, get_project_root, get_source_dir

logger = get_logger(Path(__file__).stem)

PROJECT_ROOT = get_project_root()
FILENAME = "meta_ads.json"
SOURCE_DIR = get_source_dir()
SOURCE_PATH = SOURCE_DIR / "meta_ads.json"
RAW_DIR = get_data_dir("raw") / "json_daily"
RAW_PATH = RAW_DIR / FILENAME

RAW_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy(SOURCE_PATH, RAW_PATH)

with open(RAW_PATH) as f:
    data = json.load(f)

records = data["data"]

df_meta = pd.DataFrame(records)

logger.info(f"Rows: {len(records)}")
logger.info(f"Columns: {len(df_meta.columns)}")
logger.info(df_meta.dtypes)

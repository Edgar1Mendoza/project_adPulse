import shutil
from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir, get_source_dir

logger = get_logger(Path(__file__).stem)

FILENAME = "campaign_mapping.csv"
SOURCE_DIR = get_source_dir()
SOURCE_PATH = SOURCE_DIR / "campaign_mapping.csv"
RAW_DIR = get_data_dir("raw") / "csv_mapping"
RAW_PATH = RAW_DIR / FILENAME

RAW_DIR.mkdir(parents=True, exist_ok=True)
shutil.copy(SOURCE_PATH, RAW_PATH)

df_mapping = pd.read_csv(RAW_PATH)

logger.info(f"Rows: {len(df_mapping)}")
logger.info(f"Columns: {len(df_mapping.columns)}")
logger.info(df_mapping.dtypes)

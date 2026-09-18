from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir, get_project_root

logger = get_logger(Path(__file__).stem)

PROJECT_ROOT = get_project_root()

RAW_PATH = get_data_dir("raw") / "csv_daily" / "google_ads_weekly.csv"
SILVER_PATH = get_data_dir("silver")

df = pd.read_csv(RAW_PATH)

df["date"] = pd.to_datetime(df["date"], format="%Y-%m-%d")

SILVER_PATH.mkdir(parents=True, exist_ok=True)
df.to_parquet(SILVER_PATH / "google_ads_weekly.parquet")

logger.info(f"Rows: {len(df)}")
logger.info(f"Columns: {len(df.columns)}")
logger.info(df.dtypes)
logger.info(df.head())

from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir

logger = get_logger(Path(__file__).stem)

RAW_PATH = get_data_dir("raw") / "csv_weekly" / "email_campaigns.csv"
SILVER_PATH = get_data_dir("silver")

df = pd.read_csv(RAW_PATH)

df["week_start"] = pd.to_datetime(df["week_start"], format="%Y-%m-%d")
df["week_end"] = pd.to_datetime(df["week_end"], format="%Y-%m-%d")

SILVER_PATH.mkdir(parents=True, exist_ok=True)
df.to_parquet(SILVER_PATH / "email_campaigns.parquet")

logger.info(f"Rows: {len(df)}")
logger.info(f"Columns: {len(df.columns)}")
logger.info(df.dtypes)
logger.info(df.head())

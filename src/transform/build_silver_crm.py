from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir, get_project_root

logger = get_logger(Path(__file__).stem)

PROJECT_ROOT = get_project_root()

RAW_PATH = get_data_dir("raw") / "csv_crm" / "crm_sales.csv"
SILVER_PATH = get_data_dir("silver")

df_crm = pd.read_csv(RAW_PATH)

df_crm["sale_date"] = pd.to_datetime(df_crm["sale_date"], format="%Y-%m-%d")

SILVER_PATH.mkdir(parents=True, exist_ok=True)
df_crm.to_parquet(SILVER_PATH / "crm_sales.parquet")

logger.info(f"Rows: {len(df_crm)}")
logger.info(f"Columns: {len(df_crm.columns)}")
logger.info(df_crm.dtypes)
logger.info(df_crm.head())

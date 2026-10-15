from pathlib import Path

import pandas as pd

from src.utils.cleaning import (
    coerce_datetime,
    coerce_numeric,
    drop_exact_duplicates,
    filter_future_dates,
    strip_whitespace,
)
from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir


def run():
    logger = get_logger(Path(__file__).stem)

    RAW_PATH = get_data_dir("raw") / "csv_crm" / "crm_sales.csv"
    SILVER_PATH = get_data_dir("silver")

    dtype = {"sale_id": "string", "customer_id": "string", "touchpoints": "string"}
    df_crm = pd.read_csv(RAW_PATH, dtype=dtype)

    df_crm, invalid = coerce_datetime(df_crm, "sale_date", format="%Y-%m-%d")
    if invalid > 0:
        logger.warning(f"{invalid} invalid values in sale_date converted to null")

    df_crm, invalid = coerce_numeric(df_crm, "amount_eur", dtype="float64")
    if invalid > 0:
        logger.warning(f"{invalid} invalid values in amount_eur converted to null")

    df_crm = strip_whitespace(df_crm, columns=["sale_id", "customer_id", "touchpoints"])
    df_crm, removed = drop_exact_duplicates(df_crm)
    if removed > 0:
        logger.info(f"Removed {removed} exact duplicates rows")

    df_crm, removed = filter_future_dates(df_crm, "sale_date")
    if removed > 0:
        logger.info(f"Removed {removed} future sale_date rows")

    SILVER_PATH.mkdir(parents=True, exist_ok=True)
    df_crm.to_parquet(SILVER_PATH / "crm_sales.parquet", index=False)

    logger.info(f"Rows: {len(df_crm)}")
    logger.info(f"Columns: {len(df_crm.columns)}")
    logger.info(df_crm.head())


if __name__ == "__main__":
    run()

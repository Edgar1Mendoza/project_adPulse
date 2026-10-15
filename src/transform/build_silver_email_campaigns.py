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

    RAW_PATH = get_data_dir("raw") / "csv_weekly" / "email_campaigns.csv"
    SILVER_PATH = get_data_dir("silver")

    dtype = {"campaign_name": "string"}
    df = pd.read_csv(RAW_PATH, dtype=dtype)

    date_cols = ["week_start", "week_end"]
    for col in date_cols:
        df, invalid = coerce_datetime(df, col, format="%Y-%m-%d")
        if invalid > 0:
            logger.warning(f"{invalid} invalid values in {col} converted to null")

    numeric_cols = ["sent", "opened", "clicked", "converted"]
    for col in numeric_cols:
        df, invalid = coerce_numeric(df, col, dtype="Int64")
        if invalid > 0:
            logger.warning(f"{invalid} invalid values in {col} converted to null")

    decimal_cols = ["revenue_eur", "total_cost"]
    for col in decimal_cols:
        df, invalid = coerce_numeric(df, col, dtype="float64")
        if invalid > 0:
            logger.warning(f"{invalid} invalid values in {col} converted to null")

    df = strip_whitespace(df, columns=["campaign_name"])
    df, removed = drop_exact_duplicates(df)
    if removed > 0:
        logger.info(f"Removed {removed} exact duplicates rows")

    df, removed_start = filter_future_dates(df, "week_start")
    df, removed_end = filter_future_dates(df, "week_end")
    if removed_start + removed_end > 0:
        logger.info(f"Removed {removed_start + removed_end} future sale_date rows")

    SILVER_PATH.mkdir(parents=True, exist_ok=True)
    df.to_parquet(SILVER_PATH / "email_campaigns.parquet", index=False)

    logger.info(f"Rows: {len(df)}")
    logger.info(f"Columns: {len(df.columns)}")
    logger.info(df.head())


if __name__ == "__main__":
    run()

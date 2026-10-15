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

    RAW_PATH = get_data_dir("raw") / "csv_daily" / "google_ads_weekly.csv"
    SILVER_PATH = get_data_dir("silver")

    dtype = {"campaign_name": "string"}
    df = pd.read_csv(RAW_PATH, dtype=dtype)

    df, invalid = coerce_datetime(df, "date", format="%Y-%m-%d")
    if invalid > 0:
        logger.warning(f"{invalid} invalid values in date converted to null")

    numeric_cols = ["impressions", "clicks", "conversions"]
    for col in numeric_cols:
        df, invalid = coerce_numeric(df, col, dtype="Int64")
        if invalid > 0:
            logger.warning(f"{invalid} invalid values in {col} converted to null")

    df, invalid = coerce_numeric(df, "cost_eur", dtype="float64")
    if invalid > 0:
        logger.warning(f"{invalid} invalid values in cost_eur converted to null")

    df = strip_whitespace(df, columns=["campaign_name"])
    df, removed = drop_exact_duplicates(df)
    if removed > 0:
        logger.info(f"Removed {removed} exact duplicates rows")

    df, removed = filter_future_dates(df, "date")
    if removed > 0:
        logger.info(f"Removed {removed} future sale_date rows")

    SILVER_PATH.mkdir(parents=True, exist_ok=True)
    df.to_parquet(SILVER_PATH / "google_ads_weekly.parquet", index=False)

    logger.info(f"Rows: {len(df)}")
    logger.info(f"Columns: {len(df.columns)}")
    logger.info(df.head())


if __name__ == "__main__":
    run()

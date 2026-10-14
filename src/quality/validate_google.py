from pathlib import Path

import pandas as pd

from src.quality.checks import (
    assert_columns_present,
    assert_min_rows,
    assert_no_duplicates,
    assert_no_nulls,
    assert_positive,
)
from src.quality.schema import detect_new_columns
from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir

logger = get_logger(Path(__file__).stem)

EXPECTED_COLUMNS = ["date", "campaign_name", "impressions", "clicks", "conversions", "cost_eur"]


def run():
    SILVER_PATH = get_data_dir("silver")
    google_ads = pd.read_parquet(SILVER_PATH / "google_ads_weekly.parquet")

    assert_min_rows(google_ads, min_rows=1)
    assert_columns_present(google_ads, columns=EXPECTED_COLUMNS)
    assert_no_nulls(google_ads, columns=["date", "campaign_name"])
    assert_no_duplicates(google_ads, subset=["date", "campaign_name"])
    assert_positive(google_ads, columns=["cost_eur"])

    new_columns = detect_new_columns(google_ads, expected_columns=EXPECTED_COLUMNS)
    if new_columns:
        logger.warning(f"Unexpected new columns in google_ads: {new_columns}")

    logger.info(f"google_ads passed all quality checks: {len(google_ads)} rows")


if __name__ == "__main__":
    run()

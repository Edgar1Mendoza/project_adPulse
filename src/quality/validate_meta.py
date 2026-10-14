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

EXPECTED_COLUMNS = [
    "campaign_id",
    "campaign_name",
    "date_start",
    "date_stop",
    "impressions",
    "reach",
    "clicks",
    "spend",
    "purchase",
    "add_to_cart",
    "view_content",
    "initiate_checkout",
    "cost_per_purchase",
]


def run():
    SILVER_PATH = get_data_dir("silver")
    meta_ads = pd.read_parquet(SILVER_PATH / "meta_ads.parquet")

    assert_min_rows(meta_ads, min_rows=1)
    assert_columns_present(meta_ads, columns=EXPECTED_COLUMNS)
    assert_no_nulls(
        meta_ads, columns=["campaign_id", "campaign_name", "date_start", "date_stop"]
    )
    assert_no_duplicates(meta_ads, subset=["campaign_id", "date_start"])
    assert_positive(meta_ads, columns=["spend"])

    new_columns = detect_new_columns(meta_ads, expected_columns=EXPECTED_COLUMNS)
    if new_columns:
        logger.warning(f"Unexpected new columns in meta_ads: {new_columns}")

    logger.info(f"meta_ads passed all quality checks: {len(meta_ads)} rows")


if __name__ == "__main__":
    run()

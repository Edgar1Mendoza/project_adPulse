from pathlib import Path

import pandas as pd

from src.quality.checks import (
    assert_columns_present,
    assert_min_rows,
    assert_no_duplicates,
    assert_no_nulls,
)
from src.quality.schema import detect_new_columns
from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir

logger = get_logger(Path(__file__).stem)

EXPECTED_COLUMNS = ["campaign_group", "product_category", "source", "original_campaign_name"]


def run():
    SILVER_PATH = get_data_dir("silver")
    campaign_mapping = pd.read_parquet(SILVER_PATH / "campaign_mapping_long.parquet")

    assert_min_rows(campaign_mapping, min_rows=1)
    assert_columns_present(campaign_mapping, columns=EXPECTED_COLUMNS)
    assert_no_nulls(campaign_mapping, columns=EXPECTED_COLUMNS)
    assert_no_duplicates(campaign_mapping, subset=["source", "original_campaign_name"])

    new_columns = detect_new_columns(campaign_mapping, expected_columns=EXPECTED_COLUMNS)
    if new_columns:
        logger.warning(f"Unexpected new columns in campaign_mapping: {new_columns}")

    logger.info(f"campaign_mapping passed all quality checks: {len(campaign_mapping)} rows")


if __name__ == "__main__":
    run()

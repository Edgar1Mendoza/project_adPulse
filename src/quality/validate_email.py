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
    "week_start",
    "week_end",
    "campaign_name",
    "sent",
    "opened",
    "clicked",
    "converted",
    "revenue_eur",
    "total_cost",
]


def run():
    SILVER_PATH = get_data_dir("silver")
    email_campaigns = pd.read_parquet(SILVER_PATH / "email_campaigns.parquet")

    assert_min_rows(email_campaigns, min_rows=1)
    assert_columns_present(email_campaigns, columns=EXPECTED_COLUMNS)
    assert_no_nulls(email_campaigns, columns=["campaign_name", "week_start", "week_end"])
    assert_no_duplicates(email_campaigns, subset=["campaign_name", "week_start"])
    assert_positive(email_campaigns, columns=["total_cost", "revenue_eur"])

    new_columns = detect_new_columns(email_campaigns, expected_columns=EXPECTED_COLUMNS)
    if new_columns:
        logger.warning(f"Unexpected new columns in email_campaigns: {new_columns}")

    logger.info(f"email_campaigns passed all quality checks: {len(email_campaigns)} rows")


if __name__ == "__main__":
    run()

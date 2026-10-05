from pathlib import Path

import pandas as pd

from src.quality.checks import (
    assert_columns_present,
    assert_min_rows,
    assert_no_duplicates,
    assert_no_nulls,
    assert_positive,
)
from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir

logger = get_logger(Path(__file__).stem)


def run():
    SILVER_PATH = get_data_dir("silver")
    crm_sales = pd.read_parquet(SILVER_PATH / "crm_sales.parquet")

    assert_min_rows(crm_sales, min_rows=1)
    assert_columns_present(
        crm_sales, ["sale_id", "customer_id", "amount_eur", "sale_date", "touchpoints"]
    )
    assert_no_nulls(crm_sales, columns=["customer_id", "sale_id"])
    assert_no_duplicates(crm_sales, subset=["sale_id"])
    assert_positive(crm_sales, columns=["amount_eur"])

    logger.info(f"crm_sales passed all quality checks: {len(crm_sales)} rows")


if __name__ == "__main__":
    run()

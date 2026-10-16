from pathlib import Path

import pandas as pd

from src.quality.idempotency import diff_rows, hash_rows, load_manifest, save_manifest
from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir

logger = get_logger(Path(__file__).stem)

RAW_PATH = get_data_dir("raw") / "csv_crm" / "crm_sales.csv"
MANIFEST_PATH = get_data_dir("manifest") / "crm_sales_row_hashes.parquet"

KEY_COLUMN = "sale_id"
VALUE_COLUMNS = ["customer_id", "sale_date", "amount_eur", "touchpoints"]


def run():
    df_crm = pd.read_csv(RAW_PATH)

    current_hashes = hash_rows(df_crm, KEY_COLUMN, VALUE_COLUMNS)
    previous_hashes = load_manifest(MANIFEST_PATH, KEY_COLUMN)

    changes = diff_rows(current_hashes, previous_hashes)
    logger.info(
        f"crm_sales: {len(changes['inserted'])} inserted, "
        f"{len(changes['updated'])} updated, {len(changes['deleted'])} deleted"
    )

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    save_manifest(current_hashes, MANIFEST_PATH, KEY_COLUMN)


if __name__ == "__main__":
    run()

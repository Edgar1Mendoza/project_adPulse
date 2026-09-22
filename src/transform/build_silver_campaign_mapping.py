from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir

logger = get_logger(Path(__file__).stem)

RAW_PATH = get_data_dir("raw") / "csv_mapping" / "campaign_mapping.csv"
SILVER_PATH = get_data_dir("silver")

mapping = pd.read_csv(RAW_PATH)
logger.info(
    f"Read {len(mapping)} rows and {len(mapping.columns)} columns from raw campaign mapping"
)

mapping = mapping.rename(
    columns={"google_name": "google", "meta_name": "meta", "email_name": "email"}
)

mapping_long = mapping.melt(
    id_vars=["campaign_group", "product_category"],
    value_vars=["google", "meta", "email"],
    value_name="original_campaign_name",
    var_name="source",
)
logger.info(
    f"After melt, rows: {len(mapping_long)} and columns: {len(mapping_long.columns)}"
)

mapping_long = mapping_long.dropna(subset=["original_campaign_name"])
logger.info(
    f"After dropna, rows: {len(mapping_long)} and columns: {len(mapping_long.columns)}"
)

mapping_dupes = mapping_long.duplicated(subset=["source", "original_campaign_name"])
assert mapping_dupes.sum() == 0, "Duplicate (source, campaign) pairs in campaign mapping"


SILVER_PATH.mkdir(parents=True, exist_ok=True)
mapping_long.to_parquet(SILVER_PATH / "campaign_mapping_long.parquet")

logger.info(
    f"Saved {len(mapping_long)} rows and {len(mapping_long.columns)} columns to SILVER campaign parquet"
)

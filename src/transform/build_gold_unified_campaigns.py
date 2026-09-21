from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir, get_project_root

logger = get_logger(Path(__file__).stem)

PROJECT_ROOT = get_project_root()

SILVER_PATH = get_data_dir("silver")
GOLD_PATH = get_data_dir("gold")

TARGET_COLUMNS = [
    "date",
    "source",
    "original_campaign_name",
    "impressions",
    "clicks",
    "conversions",
    "spend_eur",
    "revenue_eur",
]


def standardize_source(df, source, rename_map, defaults=None):
    df = df.rename(columns=rename_map)
    df["source"] = source
    if defaults:
        for col, value in defaults.items():
            df[col] = value
    return df[TARGET_COLUMNS]


mapping_long = pd.read_parquet(SILVER_PATH / "campaign_mapping_long.parquet")

google = pd.read_parquet(SILVER_PATH / "google_ads_weekly.parquet")
google = standardize_source(
    google,
    source="google",
    rename_map={"campaign_name": "original_campaign_name", "cost_eur": "spend_eur"},
    defaults={"revenue_eur": 0.0},
)
logger.info(f"Google standardization complete. Rows: {len(google)}")


meta = pd.read_parquet(SILVER_PATH / "meta_ads.parquet")

meta = standardize_source(
    meta,
    source="meta",
    rename_map={
        "campaign_name": "original_campaign_name",
        "date_start": "date",
        "spend": "spend_eur",
        "purchase": "conversions",
    },
    defaults={"revenue_eur": 0.0},
)
logger.info(f"Meta standardization complete. Rows: {len(meta)}")


email = pd.read_parquet(SILVER_PATH / "email_campaigns.parquet")

email = standardize_source(
    email,
    source="email",
    rename_map={
        "campaign_name": "original_campaign_name",
        "week_start": "date",
        "total_cost": "spend_eur",
        "converted": "conversions",
        "clicked": "clicks",
    },
    defaults={"impressions": 0},
)
logger.info(f"Email standardization complete. Rows: {len(email)}")


facts = pd.concat([google, meta, email], ignore_index=True)
logger.info(f"General standardization and union complete. Rows: {len(facts)}")

unified = facts.merge(
    mapping_long,
    on=["source", "original_campaign_name"],
    how="left",
)

unified["is_mapped"] = unified["campaign_group"].notna()
logger.info(unified["is_mapped"].value_counts())

unified["loaded_at"] = pd.Timestamp.now()

unified = unified[
    [
        "date",
        "source",
        "campaign_group",
        "original_campaign_name",
        "product_category",
        "impressions",
        "clicks",
        "conversions",
        "spend_eur",
        "revenue_eur",
        "is_mapped",
        "loaded_at",
    ]
]

count_cols = [
    "impressions",
    "clicks",
    "conversions",
]
unified[count_cols] = unified[count_cols].astype("Int64")
logger.info(f"Unified data types: {unified.dtypes}")


duplicated = unified.duplicated(subset=["date", "source", "original_campaign_name"])
assert duplicated.sum() == 0
if duplicated.sum() > 0:
    logger.warning(f"Found {duplicated.sum()} duplicated rows")
else:
    logger.info("No duplicated rows found")

GOLD_PATH.mkdir(parents=True, exist_ok=True)
unified.to_parquet(GOLD_PATH / "unified_campaigns.parquet")
logger.info(f"Saved {len(unified)} rows to {GOLD_PATH / 'unified_campaigns.parquet'}")

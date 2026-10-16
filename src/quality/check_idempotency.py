from pathlib import Path

from src.quality.idempotency import check_idempotency
from src.transform import (
    build_silver_campaign_mapping,
    build_silver_crm,
    build_silver_email_campaigns,
    build_silver_google_ads,
    build_silver_meta_ads,
)
from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir

logger = get_logger(Path(__file__).stem)

SILVER_PATH = get_data_dir("silver")

SOURCES = [
    (
        "campaign_mapping",
        build_silver_campaign_mapping.run,
        SILVER_PATH / "campaign_mapping_long.parquet",
    ),
    ("crm_sales", build_silver_crm.run, SILVER_PATH / "crm_sales.parquet"),
    (
        "email_campaigns",
        build_silver_email_campaigns.run,
        SILVER_PATH / "email_campaigns.parquet",
    ),
    ("google_ads", build_silver_google_ads.run, SILVER_PATH / "google_ads_weekly.parquet"),
    ("meta_ads", build_silver_meta_ads.run, SILVER_PATH / "meta_ads.parquet"),
]


def run():
    failures = []
    for name, run_fn, output_path in SOURCES:
        try:
            check_idempotency(run_fn, output_path)
            logger.info(f"{name}: idempotency check passed")
        except ValueError as e:
            logger.error(f"{name}: idempotency check failed - {e}")
            failures.append(name)

    if failures:
        raise ValueError(f"Idempotency check failed for: {failures}")


if __name__ == "__main__":
    run()

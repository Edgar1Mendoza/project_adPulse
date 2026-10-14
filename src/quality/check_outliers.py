from pathlib import Path

import pandas as pd

from src.quality.outliers import detect_outliers_iqr, detect_outliers_percentile
from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir

logger = get_logger(Path(__file__).stem)


def run():
    SILVER_PATH = get_data_dir("silver")

    google = pd.read_parquet(SILVER_PATH / "google_ads_weekly.parquet")
    google_outliers = detect_outliers_iqr(google, "cost_eur")
    logger.info(f"google.cost_eur: {len(google_outliers)} outliers de {len(google)} filas")

    meta = pd.read_parquet(SILVER_PATH / "meta_ads.parquet")
    meta_outliers = detect_outliers_iqr(meta, "spend")
    logger.info(f"meta.spend: {len(meta_outliers)} outliers de {len(meta)} filas")

    crm = pd.read_parquet(SILVER_PATH / "crm_sales.parquet")
    crm_outliers = detect_outliers_percentile(crm, "amount_eur", threshold=0.99)
    logger.info(f"crm.amount_eur: {len(crm_outliers)} outliers de {len(crm)} filas")

    email = pd.read_parquet(SILVER_PATH / "email_campaigns.parquet")
    email_cost_outliers = detect_outliers_iqr(email, "total_cost")
    logger.info(
        f"email.total_cost: {len(email_cost_outliers)} outliers out of {len(email)} rows"
    )

    email_revenue_outliers = detect_outliers_iqr(email, "revenue_eur")
    logger.info(
        f"email.revenue_eur: {len(email_revenue_outliers)} outliers out of {len(email)} rows"
    )


if __name__ == "__main__":
    run()

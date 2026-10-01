from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir
from src.utils.roas import build_source_roas


def run():

    logger = get_logger(Path(__file__).stem)

    SILVER_PATH = get_data_dir("silver")
    GOLD_PATH = get_data_dir("gold")

    unified = pd.read_parquet(GOLD_PATH / "unified_campaigns.parquet")
    crm_sales = pd.read_parquet(SILVER_PATH / "crm_sales.parquet")

    def get_reconciliation_factor(
        crm_total_conversions: int, total_reported_conversions: int
    ) -> float:
        return crm_total_conversions / total_reported_conversions

    def get_reconciled_conversions(
        conversions_by_source: pd.Series, reconciliation_factor: float
    ) -> pd.Series:
        return conversions_by_source * reconciliation_factor

    crm_total_conversions = len(crm_sales)
    total_reported_conversions = unified["conversions"].sum()
    reconciliation_factor = get_reconciliation_factor(
        crm_total_conversions, total_reported_conversions
    )

    conversions_by_source = unified.groupby("source")["conversions"].sum()
    reconciled_conversions = get_reconciled_conversions(
        conversions_by_source, reconciliation_factor
    )

    source_roas = build_source_roas(reconciled_conversions, crm_sales, unified)
    print(source_roas)

    for _, row in source_roas.iterrows():
        logger.info(
            f"{row['source']}: {row['credit']:.2f} credit, "
            f"€{row['attributed_revenue']:,.2f} revenue, "
            f"ROAS {row['roas']:.2f}x, ROAS LTV {row['roas_ltv']:.2f}x"
        )

    logger.info(
        f"Total credit: {source_roas['credit'].sum():.2f} (CRM sales: {len(crm_sales)})"
    )

    GOLD_PATH.mkdir(parents=True, exist_ok=True)
    source_roas.to_parquet(GOLD_PATH / "proportional_reconciliation_roas.parquet")
    logger.info(
        f"Saved {len(source_roas)} rows to {GOLD_PATH / 'proportional_reconciliation_roas.parquet'}"
    )


if __name__ == "__main__":
    run()

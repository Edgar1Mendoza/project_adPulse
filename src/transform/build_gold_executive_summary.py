from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir
from src.utils.roas import LTV_MULTIPLIER


def run():

    logger = get_logger(Path(__file__).stem)

    SILVER_PATH = get_data_dir("silver")
    GOLD_PATH = get_data_dir("gold")

    crm_sales = pd.read_parquet(SILVER_PATH / "crm_sales.parquet")
    unified = pd.read_parquet(GOLD_PATH / "unified_campaigns.parquet")

    proportional_roas = pd.read_parquet(
        GOLD_PATH / "proportional_reconciliation_roas.parquet"
    )
    linear_roas = pd.read_parquet(GOLD_PATH / "linear_attribution_roas.parquet")
    time_decay_roas = pd.read_parquet(GOLD_PATH / "time_decay_attribution_roas.parquet")

    proportional_roas["method"] = "proportional_reconciliation"
    linear_roas["method"] = "linear_reconciliation"
    time_decay_roas["method"] = "time_decay_reconciliation"

    executive_summary = pd.concat(
        [proportional_roas, linear_roas, time_decay_roas], ignore_index=True
    )

    total_revenue = crm_sales["amount_eur"].sum()
    total_revenue_ltv = total_revenue * LTV_MULTIPLIER
    total_spend = unified["spend_eur"].sum()

    total_roas = total_revenue / total_spend
    total_roas_ltv = total_revenue_ltv / total_spend

    total_row = pd.DataFrame(
        [
            {
                "source": "TOTAL",
                "credit": len(crm_sales),
                "attributed_revenue": total_revenue,
                "attributed_revenue_ltv": total_revenue_ltv,
                "spend_eur": total_spend,
                "roas": total_roas,
                "roas_ltv": total_roas_ltv,
                "method": "GLOBAL",
            }
        ]
    )

    executive_summary = executive_summary.sort_values(["source", "method"]).reset_index(
        drop=True
    )
    executive_summary = pd.concat([executive_summary, total_row], ignore_index=True)
    logger.info(
        f"rows: {len(executive_summary)} columns: {len(executive_summary.columns)}"
    )

    for _, row in executive_summary.iterrows():
        logger.info(
            f"{row['source']} ({row['method']}): {row['credit']:.2f} credit, "
            f"€{row['attributed_revenue']:,.2f} revenue, "
            f"ROAS {row['roas']:.2f}x, ROAS LTV {row['roas_ltv']:.2f}x"
        )

    GOLD_PATH.mkdir(parents=True, exist_ok=True)
    executive_summary.to_parquet(GOLD_PATH / "executive_summary.parquet")
    logger.info(
        f"saved {len(executive_summary)} rows to {GOLD_PATH / 'executive_summary.parquet'}"
    )


if __name__ == "__main__":
    run()

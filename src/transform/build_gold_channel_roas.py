# ASSUMPTION: 2.3x repeat-purchase multiplier comes from PharmaLife's 3-year
# CRM history (external to this pipeline). January alone shows 1.01
# purchases/customer, not enough time span to observe real recurrence.

from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir

logger = get_logger(Path(__file__).stem)

SILVER_PATH = get_data_dir("silver")
GOLD_PATH = get_data_dir("gold")

unified = pd.read_parquet(GOLD_PATH / "unified_campaigns.parquet")
crm = pd.read_parquet(SILVER_PATH / "crm_sales.parquet")

LTV_MULTIPLIER = 2.3


def calculate_metrics(
    unified: pd.DataFrame, crm: pd.DataFrame, LTV_MULTIPLIER: float
) -> dict:
    total_crm = len(crm)
    total_reported_conversions = unified["conversions"].sum()
    reconciliation_factor = total_crm / total_reported_conversions

    conversions_by_source = unified.groupby(["source"])["conversions"].sum()
    reconciled_conversions = conversions_by_source * reconciliation_factor
    average_order_value = crm["amount_eur"].mean()

    reconciled_revenue = reconciled_conversions * average_order_value
    spend_by_source = unified.groupby(["source"])["spend_eur"].sum()
    roas_by_source = reconciled_revenue / spend_by_source

    crm_total_sales = reconciled_revenue.sum()
    crm_total_spend = spend_by_source.sum()
    global_roas = crm_total_sales / crm_total_spend

    ltv_order_value = average_order_value * LTV_MULTIPLIER

    reconciled_revenue_ltv = reconciled_conversions * ltv_order_value
    roas_ltv_by_source = reconciled_revenue_ltv / spend_by_source

    global_revenue_ltv = crm_total_sales * ltv_order_value
    global_roas_ltv = global_revenue_ltv / crm_total_spend

    return {
        "total_crm": total_crm,
        "total_reported_conversions": total_reported_conversions,
        "reconciliation_factor": reconciliation_factor,
        "conversions_by_source": conversions_by_source,
        "reconciled_conversions": reconciled_conversions,
        "average_order_value": average_order_value,
        "reconciled_revenue": reconciled_revenue,
        "spend_by_source": spend_by_source,
        "roas_by_source": roas_by_source,
        "crm_total_sales": crm_total_sales,
        "crm_total_spend": crm_total_spend,
        "global_roas": global_roas,
        "reconciled_revenue_ltv": reconciled_revenue_ltv,
        "roas_ltv_by_source": roas_ltv_by_source,
        "global_revenue_ltv": global_revenue_ltv,
        "global_roas_ltv": global_roas_ltv,
    }


def log_metrics_info(metrics: dict) -> None:
    logger.info(
        f"Reconciliation factor: {metrics['reconciliation_factor']:.4f} => "
        f"({metrics['total_crm']} CRM sales / {metrics['total_reported_conversions']} reported conversions)"
    )

    for source in metrics["reconciled_revenue"].index:
        logger.info(
            f"{source}: {metrics['reconciled_conversions'][source]:.0f} reconciled conversions, "
            f"€{metrics['reconciled_revenue'][source]:,.2f} revenue, "
            f"ROAS {metrics['roas_by_source'][source]:.2f}x"
        )

    logger.info(
        f"Global ROAS: {metrics['global_roas']:.2f}x  =>"
        f" (€{metrics['reconciled_revenue'].sum():,.2f} reconciled revenue / €{metrics['spend_by_source'].sum():,.2f} spend)"
    )

    for source in metrics["reconciled_revenue_ltv"].index:
        logger.info(
            f"{source}: LTV revenue €{metrics['reconciled_revenue_ltv'][source]:,.2f}, "
            f"ROAS (LTV) {metrics['roas_ltv_by_source'][source]:.2f}x"
        )

    logger.warning(
        f"Global ROAS (LTV, 12mo): {metrics['global_roas_ltv']:.2f}x vs first-purchase ROAS: {metrics['global_roas']:.2f}x — "
        "these mix 1 month of spend against a 12-month revenue projection, not directly comparable"
    )


def channel_roas_df(metrics: dict) -> pd.DataFrame:
    channel_roas = pd.DataFrame(
        {
            "reported_conversions": metrics["conversions_by_source"],
            "reconciled_conversions": metrics["reconciled_conversions"],
            "reconciled_revenue": metrics["reconciled_revenue"],
            "reconciled_revenue_ltv": metrics["reconciled_revenue_ltv"],
            "spend_eur": metrics["spend_by_source"],
            "roas": metrics["roas_by_source"],
            "roas_ltv": metrics["roas_ltv_by_source"],
        }
    ).reset_index()

    return channel_roas


def create_executive_summary_df(metrics: dict) -> pd.DataFrame:
    executive_summary = pd.DataFrame(
        {
            "spend_eur": metrics["spend_by_source"],
            "conv_plat": metrics["conversions_by_source"],
            "conv_recon": metrics["reconciled_conversions"],
            "roas": metrics["roas_by_source"],
            "roas_ltv": metrics["roas_ltv_by_source"],
        }
    ).reset_index()

    total_row = pd.DataFrame(
        [
            {
                "source": "TOTAL",
                "spend_eur": metrics["spend_by_source"].sum(),
                "conv_plat": metrics["conversions_by_source"].sum(),
                "conv_recon": metrics["reconciled_conversions"].sum(),
                "roas": metrics["global_roas"],
                "roas_ltv": metrics["global_roas_ltv"],
            }
        ]
    )

    executive_summary = pd.concat([executive_summary, total_row], ignore_index=True)
    return executive_summary


def save_dataframe(channel_roas: pd.DataFrame, executive_summary: pd.DataFrame) -> None:
    GOLD_PATH.mkdir(parents=True, exist_ok=True)
    channel_roas.to_parquet(GOLD_PATH / "channel_roas.parquet")
    logger.info(f"saved {len(channel_roas)} rows to {GOLD_PATH / 'channel_roas.parquet'}")

    GOLD_PATH.mkdir(parents=True, exist_ok=True)
    executive_summary.to_parquet(GOLD_PATH / "executive_summary.parquet")
    logger.info(
        f"saved {len(channel_roas)} rows to {GOLD_PATH / 'executive_summary.parquet'}"
    )


if __name__ == "__main__":
    metrics = calculate_metrics(unified, crm, LTV_MULTIPLIER)
    log_metrics_info(metrics)
    channel_roas = channel_roas_df(metrics)
    executive_summary = create_executive_summary_df(metrics)
    save_dataframe(channel_roas, executive_summary)

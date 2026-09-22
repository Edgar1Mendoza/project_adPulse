from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir

logger = get_logger(Path(__file__).stem)

SILVER_PATH = get_data_dir("silver")
GOLD_PATH = get_data_dir("gold")

unified = pd.read_parquet(GOLD_PATH / "unified_campaigns.parquet")
crm = pd.read_parquet(SILVER_PATH / "crm_sales.parquet")


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

# ASSUMPTION: 2.3x repeat-purchase multiplier comes from PharmaLife's 3-year
# CRM history (external to this pipeline). January alone shows 1.01
# purchases/customer, not enough time span to observe real recurrence.

LTV_MULTIPLIER = 2.3
ltv_order_value = average_order_value * LTV_MULTIPLIER

reconciled_revenue_ltv = reconciled_conversions * ltv_order_value
roas_ltv_by_source = reconciled_revenue_ltv / spend_by_source

global_revenue_ltv = crm_total_sales * ltv_order_value
global_roas_ltv = global_revenue_ltv / crm_total_spend


logger.info(
    f"Reconciliation factor: {reconciliation_factor:.4f} => "
    f"({total_crm} CRM sales / {total_reported_conversions} reported conversions)"
)

for source in reconciled_revenue.index:
    logger.info(
        f"{source}: {reconciled_conversions[source]:.0f} reconciled conversions, "
        f"€{reconciled_revenue[source]:,.2f} revenue, "
        f"ROAS {roas_by_source[source]:.2f}x"
    )

logger.info(
    f"Global ROAS: {global_roas:.2f}x  =>"
    f" (€{reconciled_revenue.sum():,.2f} reconciled revenue / €{spend_by_source.sum():,.2f} spend)"
)

for source in reconciled_revenue_ltv.index:
    logger.info(
        f"{source}: LTV revenue €{reconciled_revenue_ltv[source]:,.2f}, "
        f"ROAS (LTV) {roas_ltv_by_source[source]:.2f}x"
    )

logger.warning(
    f"Global ROAS (LTV, 12mo): {global_roas_ltv:.2f}x vs first-purchase ROAS: {global_roas:.2f}x — "
    "these mix 1 month of spend against a 12-month revenue projection, not directly comparable"
)

channel_roas = pd.DataFrame(
    {
        "reported_conversions": conversions_by_source,
        "reconciled_conversions": reconciled_conversions,
        "reconciled_revenue": reconciled_revenue,
        "reconciled_revenue_ltv": reconciled_revenue_ltv,
        "spend_eur": spend_by_source,
        "roas": roas_by_source,
        "roas_ltv": roas_ltv_by_source,
    }
).reset_index()


GOLD_PATH.mkdir(parents=True, exist_ok=True)
channel_roas.to_parquet(GOLD_PATH / "channel_roas.parquet")

logger.info(f"saved {len(channel_roas)} rows to {GOLD_PATH / 'channel_roas.parquet'}")

from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir

logger = get_logger(Path(__file__).stem)

SILVER_PATH = get_data_dir("silver")
GOLD_PATH = get_data_dir("gold")

crm_sales = pd.read_parquet(SILVER_PATH / "crm_sales.parquet")
unified = pd.read_parquet(GOLD_PATH / "unified_campaigns.parquet")
LTV_MULTIPLIER = 2.3


def parse_touchpoints(touchpoints_str):
    channels = [touchpoint.split(":")[0] for touchpoint in touchpoints_str.split(",")]
    credit = 1 / len(channels)
    return [{"source": channel, "credit": credit} for channel in channels]


attribution_rows = []
for touchpoint in crm_sales["touchpoints"]:
    attribution_rows.extend(parse_touchpoints(touchpoint))

attribution = pd.DataFrame(attribution_rows)

credit_by_source = attribution.groupby(["source"])["credit"].sum()
assert credit_by_source.sum() == len(crm_sales), (
    "Attribution credit does not sum to total CRM sales"
)
logger.info(credit_by_source)
logger.info(credit_by_source.sum())

average_order_value = crm_sales["amount_eur"].mean()

attributed_revenue = credit_by_source * average_order_value
logger.info(attributed_revenue)

spend_by_source = unified.groupby("source")["spend_eur"].sum()
roas = attributed_revenue / spend_by_source
logger.info(f"ROAS: {roas}")

ltv_order_value = average_order_value * LTV_MULTIPLIER
attributed_revenue_ltv = credit_by_source * ltv_order_value
roas_ltv = attributed_revenue_ltv / spend_by_source
logger.info(f"ROAS (LTV): {roas_ltv}")

linear_attribution_roas = pd.DataFrame(
    {
        "credit": credit_by_source,
        "attributed_revenue": attributed_revenue,
        "attributed_revenue_ltv": attributed_revenue_ltv,
        "spend_eur": spend_by_source,
        "roas": roas,
        "roas_ltv": roas_ltv,
    }
).reset_index()

GOLD_PATH.mkdir(parents=True, exist_ok=True)
linear_attribution_roas.to_parquet(GOLD_PATH / "linear_attribution_roas.parquet")
logger.info(
    f"saved {len(linear_attribution_roas)} rows to {GOLD_PATH / 'linear_attribution_roas.parquet'}"
)

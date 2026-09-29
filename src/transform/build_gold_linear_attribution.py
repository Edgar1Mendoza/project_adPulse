from pathlib import Path

import pandas as pd

from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir
from src.utils.roas import build_source_roas

logger = get_logger(Path(__file__).stem)

SILVER_PATH = get_data_dir("silver")
GOLD_PATH = get_data_dir("gold")

crm_sales = pd.read_parquet(SILVER_PATH / "crm_sales.parquet")
unified = pd.read_parquet(GOLD_PATH / "unified_campaigns.parquet")


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

linear_attribution_roas = build_source_roas(credit_by_source, crm_sales)

for _, row in linear_attribution_roas.iterrows():
    logger.info(
        f"{row['source']}: {row['credit']:.2f} credit, "
        f"€{row['attributed_revenue']:,.2f} revenue, "
        f"ROAS {row['roas']:.2f}x, ROAS LTV {row['roas_ltv']:.2f}x"
    )

logger.info(
    f"Total credit: {linear_attribution_roas['credit'].sum():.2f} (CRM sales: {len(crm_sales)})"
)

GOLD_PATH.mkdir(parents=True, exist_ok=True)
linear_attribution_roas.to_parquet(GOLD_PATH / "linear_attribution_roas.parquet")
logger.info(
    f"saved {len(linear_attribution_roas)} rows to {GOLD_PATH / 'linear_attribution_roas.parquet'}"
)

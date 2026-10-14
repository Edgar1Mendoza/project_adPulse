import json
from pathlib import Path

import pandas as pd

from src.utils.cleaning import drop_exact_duplicates, filter_future_dates, strip_whitespace
from src.utils.logging_config import get_logger
from src.utils.paths import get_data_dir


def run():
    logger = get_logger(Path(__file__).stem)

    RAW_PATH = get_data_dir("raw") / "json_daily" / "meta_ads.json"
    SILVER_PATH = get_data_dir("silver")

    with open(RAW_PATH) as f:
        data = json.load(f)

    records = data["data"]
    base_df = pd.json_normalize(records).drop(columns=["actions", "cost_per_action_type"])

    base_df["date_start"] = pd.to_datetime(base_df["date_start"], format="%Y-%m-%d")
    base_df["date_stop"] = pd.to_datetime(base_df["date_stop"], format="%Y-%m-%d")

    actions_list = [
        {a["action_type"]: a["value"] for a in record.get("actions", [])} for record in records
    ]
    actions_df = pd.DataFrame(actions_list)

    cost_per_action_type_list = [
        {
            f"cost_per_{c['action_type']}": c["value"]
            for c in record.get("cost_per_action_type", [])
        }
        for record in records
    ]
    cost_per_action_df = pd.DataFrame(cost_per_action_type_list)

    df_meta = pd.concat([base_df, actions_df, cost_per_action_df], axis=1)

    numeric_cols = (
        ["impressions", "reach", "clicks", "spend"]
        + list(actions_df.columns)
        + list(cost_per_action_df.columns)
    )
    df_meta[numeric_cols] = df_meta[numeric_cols].astype("float64")

    df_meta["cost_per_purchase"] = df_meta["cost_per_purchase"].fillna(
        df_meta["spend"] / df_meta["purchase"]
    )

    logger.info(df_meta.head())

    df_meta = strip_whitespace(df_meta, columns=["campaign_id", "campaign_name"])
    df_meta, removed = drop_exact_duplicates(df_meta)
    if removed > 0:
        logger.info(f"Removed {removed} exact duplicates rows")

    df_meta, removed_start = filter_future_dates(df_meta, "date_start")
    df_meta, removed_stop = filter_future_dates(df_meta, "date_stop")
    if removed_start + removed_stop > 0:
        logger.info(f"Removed {removed_start + removed_stop} future date_start rows")

    SILVER_PATH.mkdir(parents=True, exist_ok=True)
    df_meta.to_parquet(SILVER_PATH / "meta_ads.parquet", index=False)


if __name__ == "__main__":
    run()

import json
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_PATH = PROJECT_ROOT / "data" / "raw" / "json_daily" / "meta_ads.json"
SILVER_PATH = PROJECT_ROOT / "data" / "silver"

with open(RAW_PATH) as f:
    data = json.load(f)

records = data["data"]
base_df = pd.json_normalize(records).drop(columns=["actions", "cost_per_action_type"])

base_df["date_start"] = pd.to_datetime(base_df["date_start"], format="%Y-%m-%d")
base_df["date_stop"] = pd.to_datetime(base_df["date_stop"], format="%Y-%m-%d")

actions_list = [
    {a["action_type"]: a["value"] for a in record.get("actions", [])}
    for record in records
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
df_meta[numeric_cols] = df_meta[numeric_cols].astype(float)

print(df_meta.head())
print(df_meta.dtypes)

df_meta.to_parquet(SILVER_PATH / "meta_ads.parquet")

import pandas as pd

from src.utils.paths import get_data_dir, get_project_root

PROJECT_ROOT = get_project_root()

MAPPING_PATH = get_data_dir("raw") / "csv_mapping" / "campaign_mapping.csv"
GOLD_PATH = get_data_dir("gold")

TARGET_COLUMNS = [
    "date",
    "source",
    "original_campaign_name",
    "impressions",
    "clicks",
    "conversions",
    "spend_eur",
    "revenue_eur",
]


def standardize_source(df, source, rename_map, defaults=None):
    df = df.rename(columns=rename_map)
    df["source"] = source
    if defaults:
        for col, value in defaults.items():
            df[col] = value
    return df[TARGET_COLUMNS]


mapping = pd.read_csv(MAPPING_PATH)

mapping = mapping.rename(
    columns={"google_name": "google", "meta_name": "meta", "email_name": "email"}
)

mapping_long = mapping.melt(
    id_vars=["campaign_group", "product_category"],
    value_vars=["google", "meta", "email"],
    value_name="original_campaign_name",
    var_name="source",
)


mapping_long = mapping_long.dropna(subset=["original_campaign_name"])

# print(f"Rows: {len(mapping_long)}")
# print(mapping_long)


SILVER_PATH = get_data_dir("silver")
google = pd.read_parquet(SILVER_PATH / "google_ads_weekly.parquet")

google = standardize_source(
    google,
    source="google",
    rename_map={"campaign_name": "original_campaign_name", "cost_eur": "spend_eur"},
    defaults={"revenue_eur": 0.0},
)


meta = pd.read_parquet(SILVER_PATH / "meta_ads.parquet")

meta = standardize_source(
    meta,
    source="meta",
    rename_map={
        "campaign_name": "original_campaign_name",
        "date_start": "date",
        "spend": "spend_eur",
        "purchase": "conversions",  # Only action representing an actual conversion
    },
    defaults={"revenue_eur": 0.0},
)


email = pd.read_parquet(SILVER_PATH / "email_campaigns.parquet")

email = standardize_source(
    email,
    source="email",
    rename_map={
        "campaign_name": "original_campaign_name",
        "week_start": "date",
        "total_cost": "spend_eur",
        "converted": "conversions",
        "clicked": "clicks",
    },
    defaults={"impressions": 0},
)


facts = pd.concat([google, meta, email], ignore_index=True)

print(f"Rows: {len(facts)}")
print(facts)

unified = facts.merge(
    mapping_long,
    on=["source", "original_campaign_name"],
    how="left",
)

unified["is_mapped"] = unified["campaign_group"].notna()
print(unified["is_mapped"].value_counts())

unified["loaded_at"] = pd.Timestamp.now()

unified = unified[
    [
        "date",
        "source",
        "campaign_group",
        "original_campaign_name",
        "product_category",
        "impressions",
        "clicks",
        "conversions",
        "spend_eur",
        "revenue_eur",
        "is_mapped",
        "loaded_at",
    ]
]

count_cols = [
    "impressions",
    "clicks",
    "conversions",
]
unified[count_cols] = unified[count_cols].astype("Int64")

print(unified.head())
print(unified.dtypes)

duplicated = unified.duplicated(subset=["date", "source", "original_campaign_name"])

assert duplicated.sum() == 0

unified.to_parquet(GOLD_PATH / "unified_campaigns.parquet")
print(f"saved {len(unified)} rows to {GOLD_PATH / 'unified_campaigns.parquet'}")

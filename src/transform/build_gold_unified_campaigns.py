import pandas as pd

from src.utils.paths import get_project_root

PROJECT_ROOT = get_project_root()

MAPPING_PATH = PROJECT_ROOT / "data" / "raw" / "csv_mapping" / "campaign_mapping.csv"
GOLD_PATH = PROJECT_ROOT / "data" / "gold"

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


SILVER_PATH = PROJECT_ROOT / "data" / "silver"
google = pd.read_parquet(SILVER_PATH / "google_ads_weekly.parquet")

google = google.rename(
    columns={
        "campaign_name": "original_campaign_name",
        "cost_eur": "spend_eur",
    }
)
google["source"] = "google"
google["revenue_eur"] = 0.0

google = google[
    [
        "date",
        "source",
        "original_campaign_name",
        "impressions",
        "clicks",
        "conversions",
        "spend_eur",
        "revenue_eur",
    ]
]
# print(google)


meta = pd.read_parquet(SILVER_PATH / "meta_ads.parquet")

meta = meta.rename(
    columns={
        "campaign_name": "original_campaign_name",
        "date_start": "date",
        "spend": "spend_eur",
        "purchase": "conversions",  # Only action representing an actual conversion
    }
)
meta["source"] = "meta"
meta["revenue_eur"] = 0.0

meta = meta[
    [
        "date",
        "source",
        "original_campaign_name",
        "impressions",
        "clicks",
        "conversions",
        "spend_eur",
        "revenue_eur",
    ]
]
# print(meta)


email = pd.read_parquet(SILVER_PATH / "email_campaigns.parquet")

email = email.rename(
    columns={
        "campaign_name": "original_campaign_name",
        "week_start": "date",
        "total_cost": "spend_eur",
        "converted": "conversions",
        "clicked": "clicks",
    }
)
email["source"] = "email"
email["impressions"] = 0

email = email[
    [
        "date",
        "source",
        "original_campaign_name",
        "impressions",
        "clicks",
        "conversions",
        "spend_eur",
        "revenue_eur",
    ]
]
# print(email)


facts = pd.concat([google, meta, email], ignore_index=True)

print(f"Rows: {len(facts)}")
print(facts)

unified = facts.merge(
    mapping_long,
    on=["source", "original_campaign_name"],
    how="left",
)
# print(f"Rows: {len(unified)}")
# print(unified)

unified["is_mapped"] = unified["campaign_group"].notna()
print(unified["is_mapped"].value_counts())

unified["loaded_at"] = pd.Timestamp.now()
# print(unified[["date", "source", "loaded_at"]].head())

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

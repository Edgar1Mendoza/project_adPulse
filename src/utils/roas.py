import pandas as pd

# ASSUMPTION: 2.3x repeat-purchase multiplier comes from PharmaLife's 3-year
# CRM history (external to this pipeline). One month of CRM data isn't
# enough to observe real recurrence.
LTV_MULTIPLIER = 2.3


def build_source_roas(
    credit_by_source: pd.Series, crm_sales: pd.DataFrame, unified: pd.DataFrame
) -> pd.DataFrame:
    average_order_value = crm_sales["amount_eur"].mean()
    attributed_revenue = credit_by_source * average_order_value

    spend_by_source = unified.groupby("source")["spend_eur"].sum()
    roas = attributed_revenue / spend_by_source

    ltv_order_value = average_order_value * LTV_MULTIPLIER
    attributed_revenue_ltv = credit_by_source * ltv_order_value
    roas_ltv = attributed_revenue_ltv / spend_by_source

    return pd.DataFrame(
        {
            "credit": credit_by_source,
            "attributed_revenue": attributed_revenue,
            "attributed_revenue_ltv": attributed_revenue_ltv,
            "spend_eur": spend_by_source,
            "roas": roas,
            "roas_ltv": roas_ltv,
        }
    ).reset_index()

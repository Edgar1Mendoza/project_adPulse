import duckdb
import pandas as pd


def create_table() -> pd.DataFrame:
    query = """
        WITH sources AS (
            SELECT
                'googleAds' AS platform,
                2340 AS reported_conversion,
                110000 AS spend_eur
            UNION ALL
            SELECT
                'META',
                1890,
                70000
            UNION ALL
            SELECT
                'email',
                480,
                20000
        ),

        total AS (
            SELECT
                SUM(reported_conversion) AS conversion_total,
                3150::numeric AS crm_sales
            FROM sources
        )

        SELECT
            s.platform,
            s.reported_conversion,
            ROUND((s.reported_conversion / t.conversion_total) * 100, 2) AS total_percentage,
            t.crm_sales,
            ROUND(t.crm_sales / t.conversion_total, 2) AS global_corretion_factor,
            ROUND(s.reported_conversion * (t.crm_sales / t.conversion_total), 2) AS corrected_conversion,
            s.spend_eur,
            ROUND(s.reported_conversion * (t.crm_sales / t.conversion_total) * 90.48 / s.spend_eur, 2) AS corrected_roas
        FROM sources AS s
        CROSS JOIN total AS t

        UNION ALL
        SELECT
            'TOTAL',
            t.conversion_total,
            100,
            t.crm_sales,
            ROUND(t.crm_sales::numeric / t.conversion_total, 4),
            t.crm_sales,
            (SELECT SUM(spend_eur) FROM sources),
            ROUND(t.crm_sales * 90.48 / (SELECT SUM(spend_eur) FROM sources), 2)
        FROM total AS t
    """
    return duckdb.sql(query).df


if __name__ == "__main__":
    df = create_table()
    print(df)

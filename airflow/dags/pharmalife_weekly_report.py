from datetime import datetime, timedelta

from airflow.providers.smtp.notifications.smtp import send_smtp_notification
from airflow.providers.standard.operators.python import PythonOperator

from airflow import DAG
from src.ingest.ingest_csv_crm import run as ingest_crm_fn
from src.ingest.ingest_csv_daily import run as ingest_google_fn
from src.ingest.ingest_csv_mapping import run as ingest_mapping_fn
from src.ingest.ingest_csv_weekly import run as ingest_email_fn
from src.ingest.ingest_json_daily import run as ingest_meta_fn
from src.quality.validate_crm import run as validate_crm_fn
from src.transform.build_gold_executive_summary import (
    run as build_gold_executive_summary_fn,
)
from src.transform.build_gold_linear_attribution import (
    run as build_gold_linear_attribution_fn,
)
from src.transform.build_gold_proportional_reconciliation import (
    run as build_gold_proportional_reconciliation_fn,
)
from src.transform.build_gold_time_decay_attribution import (
    run as build_gold_time_decay_attribution_fn,
)
from src.transform.build_gold_unified_campaigns import (
    run as build_gold_unified_campaigns_fn,
)
from src.transform.build_silver_campaign_mapping import (
    run as build_silver_campaign_mapping_fn,
)
from src.transform.build_silver_crm import run as build_silver_crm_fn
from src.transform.build_silver_email_campaigns import (
    run as build_silver_email_campaigns_fn,
)
from src.transform.build_silver_google_ads import run as build_silver_google_ads_fn
from src.transform.build_silver_meta_ads import run as build_silver_meta_ads_fn

default_args = {
    "owner": "data-team",
    "depends_on_past": False,
    "on_failure_callback": send_smtp_notification(
        to=["edgar1programacion@gmail.com"],
        subject="Airflow: task {{ ti.task_id }} failed",
        html_content="Task {{ ti.task_id }} in DAG {{ dag.dag_id }} failed.",
        smtp_conn_id="adpulse_smtp",
    ),
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    "pharmalife_weekly_report",
    default_args=default_args,
    description="Pipeline semanal PharmaLife: ingesta -> unificacion -> reconciliación -> reporte",
    schedule="0 7 * * 1",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["pharmalife", "weekly", "production"],
) as dag:
    ingest_google = PythonOperator(task_id="ingest_google", python_callable=ingest_google_fn)
    ingest_meta = PythonOperator(task_id="ingest_meta", python_callable=ingest_meta_fn)
    ingest_email = PythonOperator(task_id="ingest_email", python_callable=ingest_email_fn)
    ingest_crm = PythonOperator(task_id="ingest_crm", python_callable=ingest_crm_fn)
    ingest_mapping = PythonOperator(task_id="ingest_mapping", python_callable=ingest_mapping_fn)

    build_silver_campaign_mapping = PythonOperator(
        task_id="build_silver_campaign_mapping",
        python_callable=build_silver_campaign_mapping_fn,
    )
    build_silver_crm = PythonOperator(
        task_id="build_silver_crm", python_callable=build_silver_crm_fn
    )
    build_silver_email_campaigns = PythonOperator(
        task_id="build_silver_email_campaigns",
        python_callable=build_silver_email_campaigns_fn,
    )
    build_silver_google_ads = PythonOperator(
        task_id="build_silver_google_ads", python_callable=build_silver_google_ads_fn
    )
    build_silver_meta_ads = PythonOperator(
        task_id="build_silver_meta_ads", python_callable=build_silver_meta_ads_fn
    )
    validate_crm = PythonOperator(task_id="validate_crm", python_callable=validate_crm_fn)

    build_gold_unified_campaigns = PythonOperator(
        task_id="build_gold_unified_campaigns",
        python_callable=build_gold_unified_campaigns_fn,
    )
    build_gold_linear_attribution = PythonOperator(
        task_id="build_gold_linear_attribution",
        python_callable=build_gold_linear_attribution_fn,
    )
    build_gold_time_decay_attribution = PythonOperator(
        task_id="build_gold_time_decay_attribution",
        python_callable=build_gold_time_decay_attribution_fn,
    )
    build_gold_proportional_reconciliation = PythonOperator(
        task_id="build_gold_proportional_reconciliation",
        python_callable=build_gold_proportional_reconciliation_fn,
    )
    build_gold_executive_summary = PythonOperator(
        task_id="build_gold_executive_summary",
        python_callable=build_gold_executive_summary_fn,
    )

    ingest_google >> build_silver_google_ads
    ingest_meta >> build_silver_meta_ads
    ingest_email >> build_silver_email_campaigns
    ingest_mapping >> build_silver_campaign_mapping
    ingest_crm >> build_silver_crm >> validate_crm

    [
        build_silver_google_ads,
        build_silver_meta_ads,
        build_silver_email_campaigns,
        build_silver_campaign_mapping,
    ] >> build_gold_unified_campaigns

    [
        validate_crm,
        build_gold_unified_campaigns,
    ] >> build_gold_proportional_reconciliation
    [validate_crm, build_gold_unified_campaigns] >> build_gold_linear_attribution
    [validate_crm, build_gold_unified_campaigns] >> build_gold_time_decay_attribution
    [
        build_gold_linear_attribution,
        build_gold_time_decay_attribution,
        build_gold_proportional_reconciliation,
    ] >> build_gold_executive_summary

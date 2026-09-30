from datetime import datetime, timedelta

from airflow.providers.smtp.notifications.smtp import send_smtp_notification
from airflow.providers.standard.operators.python import PythonOperator

from airflow import DAG
from src.ingest.ingest_csv_crm import run as ingest_crm_fn
from src.ingest.ingest_csv_daily import run as ingest_google_fn
from src.ingest.ingest_csv_weekly import run as ingest_email_fn
from src.ingest.ingest_json_daily import run as ingest_meta_fn

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
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["pharmalife", "weekly", "production"],
) as dag:
    ingest_google = PythonOperator(
        task_id="ingest_google", python_callable=ingest_google_fn
    )
    ingest_meta = PythonOperator(task_id="ingest_meta", python_callable=ingest_meta_fn)
    ingest_email = PythonOperator(task_id="ingest_email", python_callable=ingest_email_fn)
    ingest_crm = PythonOperator(task_id="ingest_crm", python_callable=ingest_crm_fn)

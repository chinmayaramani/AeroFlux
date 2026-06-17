from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import sys

# Ensure Airflow can locate our ingestion script
sys.path.append('/opt/airflow')
from ingest_flights import fetch_live_flights, load_to_postgres

# 1. Define the execution wrapper for our Python Ingestion step
def run_ingestion():
    df = fetch_live_flights()
    load_to_postgres(df)

# 2. Set up the baseline settings for our automated pipeline
default_args = {
    'owner': 'aeroflux_team',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1), # A placeholder starting date
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# 3. Instantiate our Automation Blueprint
with DAG(
    'aeroflux_main_pipeline',
    default_args=default_args,
    description='Automated real-time flight ingestion and dbt transformation platform',
    schedule_interval='@hourly', # Tells Airflow to run this automatically every hour!
    catchup=False,
) as dag:

    # TASK 1: Run the Python Ingestion Script
    extract_and_load_task = PythonOperator(
        task_id='ingest_live_aviation_data',
        python_callable=run_ingestion,
    )

    # TASK 2: Execute the dbt transformations to clean the data
    # (Since dbt lives in its own folder, we pass a bash command to run it)
    transform_data_task = BashOperator(
        task_id='transform_with_dbt',
        bash_command='cd /opt/airflow/aeroflux_transform && dbt run --profiles-dir .',
    )

    # Establish the sequence: Ingestion MUST succeed before Transformation runs
    extract_and_load_task >> transform_data_task
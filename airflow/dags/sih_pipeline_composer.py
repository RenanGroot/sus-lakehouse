from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from datetime import datetime
import sys
import os
from datetime import timedelta


sys.path.insert(0, "/home/airflow/gcs/data")

@dag(
    schedule="@monthly",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["sih", "sus"],
    default_args={"retries": 2, "retry_delay": timedelta(minutes=5)}
)
def sih_pipeline():
    
    @task.virtualenv(
        requirements=["dbt-core==1.11.11", "dbt-bigquery==1.11.2"],
        system_site_packages=False,
        )
    def dbt_run():
        import subprocess
        import sys
        from pathlib import Path
        dbt_bin = Path(sys.executable).parent / "dbt"
        subprocess.run(
            [str(dbt_bin), "run", "--target", "cloud", "--profiles-dir", "/home/airflow/gcs/data/dbt", "--project-dir", "/home/airflow/gcs/data/dbt"],
            check=True
        )

    @task.virtualenv(
        requirements=["dbt-core==1.11.11", "dbt-bigquery==1.11.2"],
        system_site_packages=False,
        )
    def dbt_test():
        import subprocess
        import sys
        from pathlib import Path
        dbt_bin = Path(sys.executable).parent / "dbt"
        subprocess.run(
            [str(dbt_bin), "test", "--target", "cloud", "--profiles-dir", "/home/airflow/gcs/data/dbt", "--project-dir", "/home/airflow/gcs/data/dbt"],
            check=True
        )
    @task.virtualenv(requirements=["pysus", "pyarrow"], system_site_packages=False)
    def download():
        import sys
        sys.path.insert(0, "/home/airflow/gcs/data")
        from ingestion.download import download_parquet_files
        download_parquet_files()
    
    @task
    def upload_gcs():
        from ingestion.upload_gcs import upload_all_files
        upload_all_files()
    
    @task
    def bq_create():
        from ingestion.bigquery import create_table
        import google.auth
        _, PROJECT_ID = google.auth.default()
        table_id = f"{PROJECT_ID}.sih_raw.SP24"
        create_table(table_id)
        
    download() >> upload_gcs() >> bq_create() >> dbt_run() >> dbt_test()

sih_pipeline()
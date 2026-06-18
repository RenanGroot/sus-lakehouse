FROM apache/airflow:3.0.4-python3.12

USER airflow

RUN pip install --no-cache-dir \
    google-cloud-storage \
    google-cloud-bigquery \
    db-dtypes \
    python-dotenv
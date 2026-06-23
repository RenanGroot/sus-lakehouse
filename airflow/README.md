# Airflow Orchestration — Development Journey

> **Note:** This folder documents the orchestration approach explored during the development of this project. **The production pipeline does not use Airflow** — it uses Cloud Run Jobs triggered by Cloud Scheduler for ingestion and manual `dbt run` invocations (see `../terraform/main.tf`).

## What's here

- `dags/sih_pipeline.py` — Airflow DAG designed for local Docker setup
- `dags/sih_pipeline_composer.py` — DAG adapted for Google Cloud Composer
- `docker-compose.yaml` — local Airflow infrastructure (5 services)
- `Dockerfile` — custom Airflow image with our Python dependencies

## Why Airflow was evaluated

Airflow is the industry standard for workflow orchestration. The DAGs here demonstrate how the full pipeline (`download → upload_gcs → bq_create → dbt_run → dbt_test`) would be expressed as Airflow tasks with proper dependencies, retries, and scheduling.

## Why production moved to Cloud Run Jobs

Two reasons drove the architecture decision:

1. **Cost** — Cloud Composer (managed Airflow on GCP) costs ~$300-400/month minimum, even when idle. For a monthly ingestion job, this is overkill.

2. **Network restrictions** — Composer workers run in a managed GKE cluster with restricted outbound connectivity. FTP connections to `ftp.datasus.gov.br` consistently timed out, while Cloud Run Jobs have full network access by default.

## The final architecture
```
Cloud Scheduler (monthly)
    ↓
Cloud Run Job (download FTP → upload GCS)
    ↓
BigQuery external table
    ↓
dbt (manual or future GitHub Actions)
    ↓
Cloud Run Service (Streamlit dashboard)
```

Cloud Run Jobs cost effectively $0 when not running, scale automatically, and have unrestricted network access — making them the better fit for this use case.

## When Airflow would be the right choice

This project's pipeline is simple and monthly. Airflow would be more appropriate if:
- The pipeline grew to 50+ tasks with complex dependencies
- Tasks ran daily or hourly
- Multiple data sources needed coordinated orchestration
- The team needed a visual UI for monitoring

For a single-source, monthly pipeline, serverless is simpler and cheaper.
.PHONY: setup run dashboard ingestion-trigger dbt-run dbt-test infra-plan

setup:
	uv sync

run:
	uv run streamlit run dashboard/app.py

dashboard-deploy:
	docker build -t southamerica-east1-docker.pkg.dev/$(PROJECT_ID)/sus-lakehouse/streamlit:latest dashboard/
	docker push southamerica-east1-docker.pkg.dev/$(PROJECT_ID)/sus-lakehouse/streamlit:latest
	gcloud run deploy sus-lakehouse-dashboard --image=southamerica-east1-docker.pkg.dev/$(PROJECT_ID)/sus-lakehouse/streamlit:latest --region=southamerica-east1

ingestion-trigger:
	gcloud run jobs execute sus-lakehouse-ingestion --region=southamerica-east1

dbt-run:
	cd dbt && dbt run --target local

dbt-test:
	cd dbt && dbt test --target local

infra-plan:
	cd terraform && terraform plan
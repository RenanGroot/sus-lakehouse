.PHONY: setup download upload bq-create run
setup:
	uv sync

download:
	uv run ingestion/download.py

run:
	uv run streamlit run dashboard/app.py

upload:
	uv run ingestion/upload_gcs.py

bq-create:
	uv run ingestion/bigquery.py
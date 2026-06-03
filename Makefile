.PHONY: setup download run
setup:
	uv sync

download:
	uv run ingestion/download.py

run:
	uv run streamlit run dashboard/app.py
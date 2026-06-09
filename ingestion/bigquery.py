from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import os
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

project_id = os.getenv("GCP_PROJECT_ID")
table_id = f"{project_id}.sih_raw.SP24"
bucket_name = os.getenv("BUCKET_NAME")

client = bigquery.Client()
external_source_format = bigquery.ExternalSourceFormat.PARQUET
source_uris = [f"gs://{bucket_name}/*.parquet"]

def create_table(target_table: str) -> None:
    """
    Connects to BigQuery Client, create a new external source 
    table configured for Parquet files, skips if it already exists.
    
    Args:
        target_table: Table ID to be created

    Returns:
        None
    """
    try:
        client.get_table(target_table)
        logging.warning("Table already exists, skipping")

    except NotFound:
        external_config = bigquery.ExternalConfig(external_source_format)
        external_config.source_uris = source_uris
        table = bigquery.Table(target_table)
        table.external_data_configuration = external_config
        client.create_table(table)
        logging.info("Table created sucessfully!")

if __name__ == "__main__":
    create_table(table_id)
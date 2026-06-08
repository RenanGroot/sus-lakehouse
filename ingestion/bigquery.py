from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
import logging

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

client = bigquery.Client()

table_id = "project-8c33836c-e0e4-4c1d-9d8.sih_raw.SP24"
external_source_format = bigquery.ExternalSourceFormat.PARQUET
source_uris = ["gs://project-8c33836c-e0e4-4c1d-9d8-sus-lakehouse-raw/*.parquet"]

def create_table():
    try:
        client.get_table(table_id)
        logging.warning("Table already exists, skipping")
    except NotFound:
        external_config = bigquery.ExternalConfig(external_source_format)
        external_config.source_uris = source_uris
        table = bigquery.Table(table_id)
        table.external_data_configuration = external_config
        client.create_table(table)
        logging.info("Table created sucessfully!")

if __name__ == "__main__":
    create_table()
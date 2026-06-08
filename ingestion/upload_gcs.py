import os
import logging
from google.cloud import storage
from google.oauth2 import service_account
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

RAW_PATH = Path("data/raw")
BUCKET_NAME = os.getenv("BUCKET_NAME")

#credentials = service_account.Credentials.from_service_account_file(filename=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),scopes=['https://www.googleapis.com/auth/cloud-platform'])

def upload_blob(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    if not blob.exists():
        blob.upload_from_filename(source_file_name)
        logging.info(f"The {destination_blob_name} was uploaded sucessfully")
    else:
        logging.warning(f"The {destination_blob_name} already exists in the bucket")


def upload_all_files():
    logging.info("Starting the full upload")
    for file in RAW_PATH.glob("*.parquet"):
        upload_blob(BUCKET_NAME, file, file.name)
    logging.info("Uploads finished")

upload_all_files()
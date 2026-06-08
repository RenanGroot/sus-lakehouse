import os
import logging
from google.cloud import storage
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

RAW_PATH = Path("data/raw")
BUCKET_NAME = os.getenv("BUCKET_NAME")


def upload_blob(bucket_name: str, source_file_name: str, destination_blob_name: str) -> None:
    """Uploads a file to the bucket.
    
    Args:
        bucket_name: The ID of your GCS bucket.
        source_file_name: The path to your file to upload.
        destination_blob_name: The ID of your GCS object.

    Returns:
        None
    """

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    if not blob.exists():
        blob.upload_from_filename(source_file_name)
        logging.info(f"The {destination_blob_name} was uploaded sucessfully")
    else:
        logging.warning(f"The {destination_blob_name} already exists in the bucket")


def upload_all_files() -> None:
    """
    Loops the folder where is the raw data, and calls upload_blob for each file

    Returns:
        None
    """
    files = list(RAW_PATH.glob("*.parquet"))
    logging.info(f"Found {len(files)} files to upload")
    for file in files:
        upload_blob(BUCKET_NAME, file, file.name)
    logging.info("Uploads finished")

if __name__ == "__main__":
    upload_all_files()
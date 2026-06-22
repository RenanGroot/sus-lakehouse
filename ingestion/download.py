# Importing libraries
from pysus.api.extensions import DBC
from pathlib import Path
from ftplib import FTP
import asyncio
import os
import logging
from google.cloud import storage
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

RAW_PATH = Path("/tmp/raw")
BUCKET_NAME = os.getenv("BUCKET_NAME")
FTP_HOST = "ftp.datasus.gov.br"
FTP_PATH = "dissemin/publicos/SIHSUS/200801_/Dados/"
FILE_FILTER = "RDSP24" # RD table, SP state, year 2024


def download_to_gcs(bucket_name: str) -> None:
    """
    Connect to DATASUS FTP, download SIH/RD files, convert to parquet,
    and upload directly to GCS. Files are stored only temporarily on disk
    during conversion. Skips files already present in the bucket.
    
    Args:
        bucket_name: Target GCS bucket name
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    
    RAW_PATH.mkdir(parents=True, exist_ok=True)
    
    logging.info("Connecting to FTP server")
    ftp = FTP(FTP_HOST)
    ftp.login()
    ftp.cwd(FTP_PATH)
    
    files = []
    ftp.retrlines("LIST", files.append)
    rd_files = [f.split()[-1] for f in files if FILE_FILTER in f]
    logging.info(f"Found {len(rd_files)} files to process")
    
    for file in rd_files:
        file_stem = file.replace(".dbc", "")
        blob_name = f"{file_stem}.parquet"
        blob = bucket.blob(blob_name)
        
        if blob.exists():
            logging.warning(f"{blob_name} already exists in bucket, skipping")
            continue
        
        local_dbc = RAW_PATH / file
        local_parquet = RAW_PATH / blob_name
        
        try:
            logging.info(f"Downloading {file} from FTP")
            with open(local_dbc, "wb") as f:
                ftp.retrbinary(f"RETR {file}", f.write)
            
            logging.info(f"Converting {file} to parquet")
            dbc = DBC(path=local_dbc)
            asyncio.run(dbc.to_parquet(str(local_parquet)))
            
            logging.info(f"Uploading {blob_name} to GCS")
            blob.upload_from_filename(str(local_parquet))
            logging.info(f"{blob_name} uploaded successfully")
        finally:
            local_dbc.unlink(missing_ok=True)
            local_parquet.unlink(missing_ok=True)
    
    ftp.quit()
    logging.info("All files processed")


if __name__ == "__main__":
    download_to_gcs(BUCKET_NAME)
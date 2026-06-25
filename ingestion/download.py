# Importing libraries
from pysus.api.extensions import DBC
from pathlib import Path
from ftplib import FTP
import asyncio
import os
import logging
from google.cloud import storage
from dotenv import load_dotenv
from datetime import datetime
import re

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Global Variables
RAW_PATH = Path("/tmp/raw")
BUCKET_NAME = os.getenv("BUCKET_NAME")
FTP_HOST = "ftp.datasus.gov.br"
FTP_PATH = "dissemin/publicos/SIHSUS/200801_/Dados/"
RD_PATTERN = re.compile(r"^RD[A-Z]{2}\d{4}\.dbc$", re.IGNORECASE)
MIN_YEAR = int(os.getenv("MIN_YEAR", "2025"))


# Functions
def extract_year_state(filename: str) -> tuple[str, str]:
    """
    Extracts the state and converts the 2-digit year to a 4-digit format from a filename.

    The filename must follow the strict pattern 'RD{STATE}{YY}{MM}.dbc', where
    STATE is a 2-letter code, YY is a 2-digit year, and MM is a 2-digit month.

    Args:
        filename: The name of the file to parse (e.g., 'RDNY2612.dbc').

    Returns:
        A tuple containing:
            - state (str): The 2-letter state abbreviation (e.g., 'NY').
            - yyyy (int): The 4-digit converted year (e.g., 2026).
    """
    pattern = r"^RD([A-Za-z]{2})(\d{2})(\d{2})\.dbc$"
    match = re.match(pattern, filename, re.IGNORECASE)
    state = match.group(1)
    yy = match.group(2)
    month = match.group(3)

    # Convert 2-digit year (YY) to 4-digit year (YYYY)
    yyyy = str(datetime.strptime(yy, "%y").year)
    return state, yyyy


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
    rd_files = []
    for line in files:
        filename = line.split()[-1]
        if not RD_PATTERN.match(filename):
            continue
        _, year = extract_year_state(filename)
        if int(year) < MIN_YEAR:
            continue
        rd_files.append(filename)

    logging.info(f"Found {len(rd_files)} files to process")
    
    for file in rd_files:
        file_stem = file.replace(".dbc", "")
        state, year = extract_year_state(file)
        blob_name = f"year={year}/state={state}/{file_stem}.parquet"
        blob = bucket.blob(blob_name)
        
        if blob.exists():
            logging.warning(f"{blob_name} already exists in bucket, skipping")
            continue
        
        local_dbc = RAW_PATH / file
        local_parquet = RAW_PATH / f"{file_stem}.parquet"
        
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

# Main
if __name__ == "__main__":
    download_to_gcs(BUCKET_NAME)
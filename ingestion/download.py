# Importing libraries
from pysus.api.extensions import DBC
from pathlib import Path
from ftplib import FTP
import asyncio
import os
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

RAW_PATH = Path("data/raw")

FTP_HOST = "ftp.datasus.gov.br"
FTP_PATH = "dissemin/publicos/SIHSUS/200801_/Dados/"
FILE_FILTER = "RDSP24"  # RD table, SP state, year 2024

def download_parquet_files() -> None:
    """
    Connect to DATASUS FTP server, download SIH/RD files for SP 2024,
    convert from .dbc to parquet format, and save to RAW_PATH.
    Skips files that have already been downloaded and converted.
    
    Returns:
        None
    """

    RAW_PATH.mkdir(parents=True, exist_ok=True)

    logging.info("Setting the connection to FTP server")
    ftp = FTP(FTP_HOST)
    ftp.login()
    ftp.cwd(FTP_PATH)
    files = []
    ftp.retrlines("LIST", files.append)
    rd_files = [f.split()[-1] for f in files if FILE_FILTER in f]

    logging.info(f"Found {len(rd_files)} files to process")
    for file in rd_files:
        file_output = file.replace(".dbc","")
        if Path(f"{RAW_PATH}/{file_output}.parquet").exists():
            logging.warning(f"File already exists, skipping {file_output}")
            continue
        logging.info(f"Starting download file: {file}")
        ftp.retrbinary(f"RETR {file}", open(f"{RAW_PATH}/{file}", "wb").write)
        dbc = DBC(path=Path(f"{RAW_PATH}/{file}"))
        asyncio.run(dbc.to_parquet(f"{RAW_PATH}/{file_output}.parquet"))
        os.remove(Path(f"{RAW_PATH}/{file}"))
        logging.info("Download finished")
    ftp.quit()

if __name__ == "__main__":
    download_parquet_files()
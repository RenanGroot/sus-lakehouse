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

ftp = FTP("ftp.datasus.gov.br")
ftp.login()
ftp.cwd("dissemin/publicos/SIHSUS/200801_/Dados/")
files = []
ftp.retrlines("LIST", files.append)
rd_files = [f.split()[-1] for f in files if "RDSP24" in f]


logging.info("Starting the loop")
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

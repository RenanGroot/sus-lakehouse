# Importing libraries
import os
import logging
from google.cloud import storage
from dotenv import load_dotenv
import requests
import pandas as pd
from io import BytesIO

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Global Variables
BUCKET_NAME = os.getenv("BUCKET_NAME")


# Functions
def upload_df_to_gcs(df: pd.DataFrame, bucket_name: str, blob_name: str) -> None:
    """
    Upload a pandas DataFrame as parquet to GCS, without touching the filesystem.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    
    buffer = BytesIO()
    df.to_parquet(buffer, index=False)
    buffer.seek(0)
    
    blob.upload_from_file(buffer, content_type="application/octet-stream")
    logging.info(f"Uploaded {blob_name} to GCS")


def fetch_population() -> pd.DataFrame:
    """
    Connect to API SINDRA from IBGE, get the population from specific table (table 6579), map columns names and 
    state acronyms. Return in pandas Data Frame format.

    Returns:
        df(pd.DataFrame): DataFrame with population by state across the years
    """
    IBGE_TO_ACRONYM = {
    "11": "RO", "12": "AC", "13": "AM", "14": "RR", "15": "PA",
    "16": "AP", "17": "TO", "21": "MA", "22": "PI", "23": "CE",
    "24": "RN", "25": "PB", "26": "PE", "27": "AL", "28": "SE",
    "29": "BA", "31": "MG", "32": "ES", "33": "RJ", "35": "SP",
    "41": "PR", "42": "SC", "43": "RS", "50": "MS", "51": "MT",
    "52": "GO", "53": "DF"
    }

    logging.info("Connect to apisindra.ibge.gov.br for population download")
    try:
        response = requests.get("https://apisidra.ibge.gov.br/values/t/6579/n3/all/v/all/p/all")
        logging.info("Sucessfully got response")
    except requests.ConnectionError as e:
        logging.error(f"Unable to get response. Connection error:{e}")
    data = response.json()
    df = pd.DataFrame(data[1:])
    df = df[["D1C","D3N","V"]]
    df.columns = ["ibge_code", "year", "population"]
    df["state"] = df["ibge_code"].map(IBGE_TO_ACRONYM)
    df["year"] = df["year"].astype(int)
    df["population"] = df["population"].astype(int)
    df = df[["state", "year", "population"]]
    logging.info(f"Sucessfully downloaded and converted to df. DataFrame shape:{df.shape}")
    return df

def fetch_ipca() -> pd.DataFrame:
    """
    Connect to API SINDRA from IBGE, get the population from specific table (table 1737), select columns
    , convert columns types. Return in pandas Data Frame format.

    Returns:
        df(pd.DataFrame): DataFrame with population by state across the years 
    """
    logging.info("Connect to apisindra.ibge.gov.br for IPCA index download")
    try:
        response = requests.get("https://apisidra.ibge.gov.br/values/t/1737/n1/all/v/2266/p/last%20221/d/v2266%2013")
        logging.info("Sucessfully got response")
    except requests.ConnectionError as e:
        logging.error(f"Unable to get response. Connection error:{e}")
    data = response.json()
    df = pd.DataFrame(data[1:])
    df = df[["V"]].assign(
        year = df["D3C"].str[0:4],
        month = df["D3C"].str[4:]
    )
    df = df[["V", "year", "month"]]
    df.rename(columns={"V":"ipca_index"}, inplace=True)
    df["year"] = df["year"].astype(int)
    df["month"] = df["month"].astype(int)
    df["ipca_index"] = df["ipca_index"].astype(float)
    logging.info(f"Sucessfully downloaded and converted to df. DataFrame shape:{df.shape}")
    return df

# Main
if __name__ == "__main__":
    population_df = fetch_population()
    upload_df_to_gcs(population_df, BUCKET_NAME, "reference/population/state_population.parquet")
    
    ipca_df = fetch_ipca()
    upload_df_to_gcs(ipca_df, BUCKET_NAME, "reference/ipca/ipca_monthly.parquet")
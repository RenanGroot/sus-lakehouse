import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px
from google.cloud import bigquery


# Steamlit setup
st.set_page_config(page_title="SUS Lakehouse", layout="wide")
st.title("SIH/SUS — São Paulo 2024")

@st.cache_data
def load_data() -> dict:
    """
    Connects to BigQuery, query the data (SQL), and loads into cache as a pandas DataFrame.

    Returns:
        dict
    """
    client = bigquery.Client()
    project_id = client.project
    marts ={}
    marts_list = ["mart_avg_length_of_stay","mart_mortality_rate","mart_total_cost"]
    for mart in marts_list:
        query = f"SELECT * FROM `{project_id}.sih_raw.{mart}`"
        marts[mart] = client.query(query).to_dataframe()
    return marts


# Chart Functions
def chart_avg_length_of_stay(df: pd.DataFrame) -> None:
    """
    Creates a Bar Chart with the average length of stay by the CID-10 diseases
      through querying the data frame.
    
    Args:
        df: Datasource as a DataFrame
    
    Returns:
        None
    """
    result = df.nlargest(10,"avg_days")
    fig = px.bar(
        result,
        x="diag_princ",
        y="avg_days",
        hover_data=["description"],
        title="Average Days by Diagnosis",
        labels={
            "diag_princ": "Diagnosis (CID-10)",
            "avg_days": "Average Length of Stay (days)"
        }
    )
    st.plotly_chart(fig)

def chart_total_cost(df: pd.DataFrame) -> None:
    """
    Creates a Bar Chart with the total costs by the CID-10 diseases
      through querying the data frame.
    
    Args:
        df: Datasource as a DataFrame
    
    Returns:
        None
    """
    result = df.nlargest(10,"sum_totalval")
    fig = px.bar(
        result,
        x="diag_princ",
        y="sum_totalval",
        hover_data=["description"],
        title="Total Cost Value by Diagnosis",
        labels={
            "diag_princ": "Diagnosis (CID-10)",
            "sum_totalval": "Total Cost Value (reais)"
        }
    )
    st.plotly_chart(fig)

def chart_mortality_rate(df: pd.DataFrame, min_cases: int) -> None:
    """
    Creates a Bar Chart with the mortality rate by the CID-10 diseases 
    given a minimum threshold for the cases.
    
    Args:
        df: Datasource as a DataFrame
        min_cases: Minimum cases threshold
    
    Returns:
        None
    """
    result = df[df['count_cases']>= min_cases].nlargest(10,"avg_morte")
    fig = px.bar(
        result,
        x="diag_princ",
        y="avg_morte",
        hover_data=["description"],
        title="Mortality Rate by Diagnosis (%)",
        labels={
            "diag_princ": "Diagnosis (CID-10)",
            "avg_morte": "Mortality Rate"
        }
    )
    st.plotly_chart(fig)

#Main

df = load_data()

st.subheader("Filters")
min_cases = st.slider("Minimum number of cases", min_value=10, max_value=1000, value=100)
col1, col2, col3 = st.columns(3)
with col1:
    chart_avg_length_of_stay(df["mart_avg_length_of_stay"])
with col2:
    chart_total_cost(df["mart_total_cost"])
with col3:
    chart_mortality_rate(df["mart_mortality_rate"], min_cases)
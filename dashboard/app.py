import streamlit as st
import pandas as pd
from pathlib import Path
import duckdb
import plotly.express as px

# Steamlit setup
st.set_page_config(page_title="SUS Lakehouse", layout="wide")
st.title("SIH/SUS — São Paulo 2024")

@st.cache_data
def load_data() -> pd.DataFrame:
    folder_data = Path("data/raw")
    df = pd.concat([pd.read_parquet(file) for file in folder_data.glob("*.parquet")])
    df = df.astype({"DIAS_PERM":"int32", "VAL_TOT":"float32", "MORTE":"int8"})
    return df


# Chart Functions

def chart_avg_length_of_stay(df):
    query = """
        SELECT DIAG_PRINC, AVG(DIAS_PERM) as avg_days 
        FROM df 
        GROUP BY DIAG_PRINC 
        ORDER BY avg_days DESC 
        LIMIT 10
    """
    result = duckdb.sql(query).df()
    fig = px.bar(
        result,
        x="DIAG_PRINC",
        y="avg_days",
        title="Average Days by Diagnosis",
        labels={
            "DIAG_PRINC": "Diagnosis (CID-10)",
            "avg_days": "Average Length of Stay (days)"
        }
    )
    st.plotly_chart(fig)

def chart_total_cost(df):
    query = """
        SELECT DIAG_PRINC, SUM(VAL_TOT) as sum_totalval 
        FROM df 
        GROUP BY DIAG_PRINC 
        ORDER BY sum_totalval DESC 
        LIMIT 10
    """
    result = duckdb.sql(query).df()
    fig = px.bar(
        result,
        x="DIAG_PRINC",
        y="sum_totalval",
        title="Total Cost Value by Diagnosis",
        labels={
            "DIAG_PRINC": "Diagnosis (CID-10)",
            "sum_totalval": "Total Cost Value (reais)"
        }
    )
    st.plotly_chart(fig)

def chart_mortality_rate(df):
    query = """
        SELECT DIAG_PRINC, AVG(MORTE) as avg_morte 
        FROM df 
        GROUP BY DIAG_PRINC 
        ORDER BY avg_morte DESC 
        LIMIT 10
    """
    result = duckdb.sql(query).df()
    fig = px.bar(
        result,
        x="DIAG_PRINC",
        y="avg_morte",
        title="Mortality Rate by Diagnosis",
        labels={
            "DIAG_PRINC": "Diagnosis (CID-10)",
            "avg_morte": "Mortality Rate"
        }
    )
    st.plotly_chart(fig)

#Main

# Loading the data and adjusting data types
df = load_data()
col1, col2, col3 = st.columns(3)
with col1:
    chart_avg_length_of_stay(df)
with col2:
    chart_total_cost(df)
with col3:
    chart_mortality_rate(df)
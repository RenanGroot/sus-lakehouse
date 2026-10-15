import streamlit as st
import pandas as pd
import plotly.express as px
from google.cloud import bigquery
import json
from pathlib import Path

# Steamlit
st.set_page_config(page_title="SUS Lakehouse", layout="wide")
st.title("SIH/SUS - Across Brazil")

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
    marts_list = ["mart_avg_length_of_stay","mart_mortality_rate","mart_total_cost",
                  "mart_hospitalizations_by_state","mart_monthly_trend"]
    for mart in marts_list:
        query = f"SELECT * FROM `{project_id}.sih_raw.{mart}`"
        marts[mart] = client.query(query).to_dataframe()
    return marts

@st.cache_data
def load_geojson() -> dict:
    """Load Brazilian state boundaries GeoJSON from disk."""
    path = Path(__file__).parent / "data" / "brasil_estados.geojson"
    with open(path) as f:
        return json.load(f)

# Chart Functions
def chart_avg_length_of_stay(df: pd.DataFrame, min_year_filter: int, max_year_filter: int) -> None:
    """
    Creates a Bar Chart with the average length of stay by the ICD-10 diseases
      through querying the data frame.
    
    Args:
        df: Datasource as a DataFrame
        min_year_filter: Minimum year used in filtering the DataFrame
        max_year_filter: Maximum year used in filtering the DataFrame
    
    Returns:
        None
    """
    df_filtered = df[df["admission_year"].between(min_year_filter, max_year_filter)]
    df_agg = df_filtered.groupby(
    ["diag_princ", "description", "chapter_description"], as_index=False
    ).apply(
        lambda g: pd.Series({
            "avg_days": (g["avg_days"] * g["count_cases"]).sum() / g["count_cases"].sum(),
            "count_cases": g["count_cases"].sum(),
        })
    ).reset_index(drop=True)
    result = df_agg.nlargest(10,"avg_days")
    fig = px.bar(
        result,
        x="diag_princ",
        y="avg_days",
        hover_data=["description","chapter_description"],
        title="Average Days by Diagnosis",
        labels={
            "diag_princ": "Diagnosis (ICD-10)",
            "avg_days": "Average Length of Stay (days)",
            "description": "Diagnosis name",
            "chapter_description": "Chapter"
        }
    )
    st.plotly_chart(fig)

def chart_total_cost(df: pd.DataFrame, min_year_filter: int, max_year_filter: int) -> None:
    """
    Creates a Bar Chart with the total costs by the ICD-10 diseases
      through querying the data frame.
    
    Args:
        df: Datasource as a DataFrame
        min_year_filter: Minimum year used in filtering the DataFrame
        max_year_filter: Maximum year used in filtering the DataFrame
    
    Returns:
        None
    """
    df_filtered = df[df["admission_year"].between(min_year_filter, max_year_filter)]
    df_agg = df_filtered.groupby(
    ["diag_princ", "description", "chapter_description"], as_index=False
    ).agg(
        sum_total_cost_corrected=("sum_total_cost_corrected", "sum"),
    )
    result = df_agg.nlargest(10,"sum_total_cost_corrected")
    fig = px.bar(
        result,
        x="diag_princ",
        y="sum_total_cost_corrected",
        hover_data=["description","chapter_description"],
        title="Total Cost Value by Diagnosis",
        labels={
            "diag_princ": "Diagnosis (ICD-10)",
            "sum_total_cost_corrected": "Total Cost Value (reais)",
            "description": "Diagnosis name",
            "chapter_description": "Chapter"
        }
    )
    st.plotly_chart(fig)

def chart_mortality_rate(df: pd.DataFrame, min_year_filter: int, max_year_filter: int, min_cases: int) -> None:
    """
    Creates a Bar Chart with the mortality rate by the ICD-10 diseases 
    given a minimum threshold for the cases.
    
    Args:
        df: Datasource as a DataFrame
        min_cases: Minimum cases threshold
        min_year_filter: Minimum year used in filtering the DataFrame
        max_year_filter: Maximum year used in filtering the DataFrame
    
    Returns:
        None
    """
    df_filtered = df[df["admission_year"].between(min_year_filter, max_year_filter)]
    df_agg = df_filtered.groupby(["diag_princ", "description", "chapter_description"], as_index=False).agg(
    sum_deaths=("sum_deaths", "sum"),
    count_cases=("count_cases", "sum"),
    )
    df_agg["mortality_rate"] = df_agg["sum_deaths"] / df_agg["count_cases"] * 100
    result = df_agg[df_agg["count_cases"] >= min_cases].nlargest(10, "mortality_rate")
    fig = px.bar(
        result,
        x="diag_princ",
        y="mortality_rate",
        hover_data=["description","chapter_description"],
        title="Mortality Rate by Diagnosis (%)",
        labels={
            "diag_princ": "Diagnosis (ICD-10)",
            "mortality_rate": "Mortality Rate",
            "description": "Diagnosis name",
            "chapter_description": "Chapter"
        }
    )
    st.plotly_chart(fig)


def chart_timeseries(df: pd.DataFrame, min_year_filter: int, max_year_filter: int, metric: str, granularity: str, comparision: bool, selected_states: list) -> None:
    """
    Creates a Line Chart accordingly to selected metric, granularity (month or year) and states (for comparision).
    
    Args:
        df: Datasource as a DataFrame
        min_year_filter: Minimum year used in filtering the DataFrame
        max_year_filter: Maximum year used in filtering the DataFrame
        metric: Selected metric
        granularity: Year or Month
        comparision: If it is a comparision chart (True)
        selected_states: List of pre-selected states used to filter the chart
    
    Returns:
        None
    """
    date_parts = df[['admission_year', 'admission_month']].rename(columns={'admission_year': 'year', 'admission_month': 'month'}).assign(day=1)
    df['date'] = pd.to_datetime(date_parts)
    df_filtered = df[df["admission_year"].between(min_year_filter, max_year_filter) & df["state"].isin(selected_states)]
    result = df_filtered
    group_cols = []
    line_color = None
    if granularity == "year":
        x_col = "admission_year"
        if comparision:
            line_color = "state"
            group_cols = ['admission_year', 'state']
        else:
            group_cols = ['admission_year']
    else:
        x_col = "date"
        if comparision:
            line_color = "state"
            group_cols = ['date', 'state']
        else:
            group_cols = ['date']
    if metric == "mortality_rate":
        result = result.groupby(group_cols)[["total_deaths", "total_hospitalizations"]].sum().reset_index()
        result["mortality_rate"] = result["total_deaths"] / result["total_hospitalizations"]
    else:
        result = result.groupby(group_cols)[metric].sum().reset_index()
    fig = px.line(
        result,
        x=x_col,
        y=metric,
        color = line_color,
        title=f"Times series according to {metric} by {granularity}"
    )
    st.plotly_chart(fig)

def chart_hospitalizations_map(df: pd.DataFrame, selected_year: int, geojson_data:dict) -> None:
    """
    Creates a Choropleth map, showing the hospitalization rate (hospitalizations per 100k inhabitants) 
    for each Brazilian State, accordingly to the selected year.

    Args:
        df: Datasource as a DataFrame
        selected_year: Selected year used to filter the map
        geojson_data: GEOJSON with Brazilian States poligons coordinates
    
    Returns:
        None
    """
    df_filtered = df[df["admission_year"] == selected_year].copy()
    df_filtered["hospitalizations_per_100k"] = df_filtered["hospitalizations_per_100k"].round(0).astype(int)
    fig = px.choropleth(
    df_filtered,
    geojson=geojson_data,
    locations="state",
    featureidkey="properties.sigla",
    color="hospitalizations_per_100k",
    #scope="south america",          
    title=f"Hospitalizations per 100k inhabitants, {selected_year}",
)
    fig.update_geos(fitbounds="locations", visible=False) 
    fig.update_layout(height=600, margin={"r": 0, "l": 0, "t": 40, "b": 0})
    st.plotly_chart(fig, use_container_width=True)

#Main

df = load_data()
geojson_states = load_geojson()

year_min = int(df["mart_monthly_trend"]["admission_year"].min())
year_max = int(df["mart_monthly_trend"]["admission_year"].max())
states = df["mart_monthly_trend"]["state"].unique().tolist()
selected_states = st.sidebar.multiselect("States",
                    options=states,
                    default=states)
year_range= st.sidebar.slider("Year Range",
                    min_value = year_min,
                    max_value = year_max,
                    value=(year_min, year_max))
st.header("By diagnosis")
st.subheader(f"By diagnosis — {year_range[0]}–{year_range[1]}")
col1, col2, col3 = st.columns(3)
with col1: chart_avg_length_of_stay(df["mart_avg_length_of_stay"], year_range[0], year_range[1])
with col2: chart_total_cost(df["mart_total_cost"], year_range[0], year_range[1])
with col3:
    with st.expander("Adjust threshold"):
        min_cases = st.slider("Minimum number of cases", min_value=10, max_value=1000, value=100)
    chart_mortality_rate(df["mart_mortality_rate"], year_range[0], year_range[1], min_cases)

st.header("Trends over time")
c1, c2, c3 = st.columns(3)
with c1: metric_selection = st.selectbox("Metric", ("total_hospitalizations", "total_deaths", "sum_total_cost_corrected", "mortality_rate"))
with c2: granularity_selection = st.radio("Granularity",("year","month"))
with c3: comparision_selection = st.toggle("Compare States")
chart_timeseries(
    df["mart_monthly_trend"],year_range[0], year_range[1],
    metric= metric_selection,
    granularity=granularity_selection,
    comparision=comparision_selection,
    selected_states=selected_states
)
st.header("Geographic distribution")
c_widget, c_chart = st.columns([1, 4])
with c_widget:
    year_map = st.slider("Year",
                min_value = 2025,
                max_value = year_max,
                value = year_max)
with c_chart:
    chart_hospitalizations_map(df["mart_hospitalizations_by_state"],
                selected_year=year_map,
                geojson_data=geojson_states)
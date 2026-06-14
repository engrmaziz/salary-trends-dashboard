from __future__ import annotations

import os
from pathlib import Path
from typing import Sequence

import pandas as pd
import plotly.express as px
import psycopg2
import streamlit as st


APP_TITLE = "Salary Insights"
TABLE_NAME = "salary_data"
ENV_PATH = Path(__file__).with_name(".env")

px.defaults.template = "plotly_dark"


def load_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url.strip()

    if ENV_PATH.exists():
        for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            if key.strip() == "DATABASE_URL":
                return value.strip().strip('"').strip("'")

    raise RuntimeError("DATABASE_URL was not found in the environment or .env file.")


def get_connection():
    return psycopg2.connect(load_database_url())


@st.cache_data(show_spinner=False)
def get_filter_options() -> tuple[list[str], list[str], int, int]:
    with get_connection() as connection:
        gender_df = pd.read_sql_query(
            f'SELECT DISTINCT "Gender" FROM {TABLE_NAME} WHERE "Gender" IS NOT NULL ORDER BY 1',
            connection,
        )
        education_df = pd.read_sql_query(
            f'SELECT DISTINCT "Education Level" FROM {TABLE_NAME} WHERE "Education Level" IS NOT NULL ORDER BY 1',
            connection,
        )
        range_df = pd.read_sql_query(
            f'SELECT MIN("Years of Experience") AS min_years, MAX("Years of Experience") AS max_years FROM {TABLE_NAME}',
            connection,
        )

    genders = gender_df["Gender"].dropna().astype(str).tolist()
    education_levels = education_df["Education Level"].dropna().astype(str).tolist()
    min_years = int(range_df.loc[0, "min_years"] or 0)
    max_years = int(range_df.loc[0, "max_years"] or 0)

    return genders, education_levels, min_years, max_years


@st.cache_data(show_spinner=False)
def get_filtered_data(
    genders: tuple[str, ...],
    education_levels: tuple[str, ...],
    experience_range: tuple[int, int],
) -> pd.DataFrame:
    if not genders or not education_levels:
        return pd.DataFrame(columns=["Age", "Gender", "Education Level", "Job Title", "Years of Experience", "Salary"])

    query = f'''
        SELECT
            "Age",
            "Gender",
            "Education Level",
            "Job Title",
            "Years of Experience",
            "Salary"
        FROM {TABLE_NAME}
        WHERE "Gender" = ANY(%s)
          AND "Education Level" = ANY(%s)
          AND "Years of Experience" BETWEEN %s AND %s
        ORDER BY "Salary" DESC, "Years of Experience" DESC
    '''

    params: Sequence[object] = (
        list(genders),
        list(education_levels),
        experience_range[0],
        experience_range[1],
    )

    with get_connection() as connection:
        return pd.read_sql_query(query, connection, params=params)


def format_currency(value: float) -> str:
    return f"PKR{value:,.0f}"


st.set_page_config(page_title=APP_TITLE, layout="wide")

st.markdown(
    """
    <style>
        .stApp {
            background: radial-gradient(circle at top left, rgba(27, 38, 59, 0.95), rgba(7, 10, 20, 1) 58%);
        }

        .block-container {
            padding-top: 1.25rem;
            padding-bottom: 2rem;
        }

        div[data-testid="stMetric"] {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 18px;
            padding: 1rem 1.1rem;
            backdrop-filter: blur(16px);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.22);
        }

        div[data-testid="stMetric"] label {
            color: rgba(255, 255, 255, 0.68) !important;
            font-size: 0.9rem !important;
        }

        div[data-testid="stMetric"] [data-testid="stMetricValue"] {
            color: #ffffff !important;
        }

        .hero {
            padding: 0.5rem 0 1rem 0;
        }

        .hero h1 {
            margin-bottom: 0.25rem;
        }

        .hero p {
            color: rgba(255, 255, 255, 0.72);
            font-size: 1rem;
            margin-top: 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Salary Insights</h1>
        <p>Explore salary patterns by experience, education, and gender using a compact bento-style dashboard.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

genders, education_levels, min_years, max_years = get_filter_options()

with st.sidebar:
    st.header("Filters")
    selected_genders = st.multiselect("Gender", options=genders, default=genders)
    selected_education_levels = st.multiselect("Education Level", options=education_levels, default=education_levels)
    selected_experience = st.slider(
        "Years of Experience",
        min_value=min_years,
        max_value=max_years,
        value=(min_years, max_years),
    )

filtered_df = get_filtered_data(
    tuple(selected_genders),
    tuple(selected_education_levels),
    tuple(selected_experience),
)

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

total_records = int(len(filtered_df))
average_salary = float(filtered_df["Salary"].mean())
highest_salary = float(filtered_df["Salary"].max())

st.markdown("### Overview")
kpi_cols = st.columns(3)
with kpi_cols[0]:
    st.metric("Total Records", f"{total_records:,}")
with kpi_cols[1]:
    st.metric("Average Salary", format_currency(average_salary))
with kpi_cols[2]:
    st.metric("Highest Salary", format_currency(highest_salary))

st.markdown("### Distribution")
chart_cols = st.columns(2)

avg_salary_by_education = (
    filtered_df.groupby("Education Level", as_index=False)["Salary"].mean().sort_values("Salary", ascending=False)
)
education_distribution = filtered_df["Education Level"].value_counts().reset_index()
education_distribution.columns = ["Education Level", "Count"]

with chart_cols[0]:
    bar_fig = px.bar(
        avg_salary_by_education,
        x="Education Level",
        y="Salary",
        title="Average Salary by Education Level",
        text_auto=".2s",
        color="Salary",
        color_continuous_scale="Blues",
        template="plotly_dark",
    )
    bar_fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        coloraxis_showscale=False,
    )
    st.plotly_chart(bar_fig, use_container_width=True)

with chart_cols[1]:
    pie_fig = px.pie(
        education_distribution,
        names="Education Level",
        values="Count",
        title="Education Level Distribution",
        hole=0.35,
        template="plotly_dark",
    )
    pie_fig.update_layout(
        height=420,
        margin=dict(l=10, r=10, t=60, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
    )
    st.plotly_chart(pie_fig, use_container_width=True)

st.markdown("### Experience vs Salary")
scatter_fig = px.scatter(
    filtered_df,
    x="Years of Experience",
    y="Salary",
    color="Gender",
    hover_data=["Age", "Education Level", "Job Title"],
    title="Years of Experience vs Salary",
    template="plotly_dark",
)
scatter_fig.update_layout(
    height=520,
    margin=dict(l=10, r=10, t=60, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(scatter_fig, use_container_width=True)

with st.expander("Show raw filtered data"):
    st.dataframe(filtered_df, use_container_width=True)

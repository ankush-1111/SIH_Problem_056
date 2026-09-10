import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load database config
load_dotenv()
DB_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@localhost:5432/sih_db")
engine = create_engine(DB_URL)

st.title("Pipeline Testing Dashboard")

# 1. Pipeline Audit Status
st.subheader("Recent Job Audits")
try:
    audits_query = "SELECT * FROM job_audits ORDER BY started_at DESC LIMIT 10"
    audits_df = pd.read_sql(audits_query, engine)
    st.table(audits_df)
except Exception as e:
    st.error(f"Error fetching job audits: {e}")

# 2. Calculated Indices
st.subheader("Latest Airfare Indices")
try:
    indices_query = "SELECT * FROM AirfareIndices ORDER BY date DESC LIMIT 10"
    indices_df = pd.read_sql(indices_query, engine)
    st.table(indices_df)
except Exception as e:
    st.error(f"Error fetching indices: {e}")

# Add a simple refresh button
if st.button('Refresh Data'):
    st.rerun()

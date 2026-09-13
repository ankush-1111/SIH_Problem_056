import streamlit as st
import pandas as pd
from config import (
    ALL_AVAILABLE_ROUTES,
    DEFAULT_ROUTES,
    ALL_BOOKING_WINDOWS,
    DEFAULT_WINDOWS
)
from api_client import (
    APIClientError,
    fetch_trend,
    fetch_heatmap,
    fetch_lead_time_curve,
    fetch_airline_comparison,
    fetch_contributors,
    fetch_benchmark,
    fetch_data_quality
)
from charts import (
    render_trend_chart,
    render_route_heatmap,
    render_lead_time_curve,
    render_airline_comparison,
    render_contributors,
    render_backtest
)
from components import (
    render_header,
    render_methodology_banner,
    render_kpi_cards,
    render_data_quality_view
)

# Set Streamlit Page Configuration
st.set_page_config(
    layout="wide",
    page_title="Real-time Airfare Price Index Dashboard",
    page_icon="✈️"
)

# Header & Methodology Metadata
render_header()
render_methodology_banner()

# Global Sidebar Filters
st.sidebar.header("Global Filters")

selected_routes = st.sidebar.multiselect(
    "Routes",
    ALL_AVAILABLE_ROUTES,
    default=DEFAULT_ROUTES,
    help="Select flight sectors to filter dashboard metrics."
)

selected_windows = st.sidebar.multiselect(
    "Booking Windows",
    ALL_BOOKING_WINDOWS,
    default=DEFAULT_WINDOWS,
    help="Advance purchase windows (days before departure)."
)

airline_choice = st.sidebar.selectbox(
    "Airline",
    ["All Airlines", "IndiGo", "Air India", "SpiceJet", "AeroNation", "Mock Air"],
    index=0
)

# Cache invalidation / Refresh button
if st.sidebar.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# 1. High-Level KPI Cards
try:
    trend_data = fetch_trend()
    latest = trend_data[0] if trend_data else None
    prev = trend_data[1] if len(trend_data) > 1 else None
    render_kpi_cards(latest, prev)
except APIClientError as e:
    st.warning(f"⚠️ Index metrics temporarily unavailable: {e}")
    render_kpi_cards(None, None)

st.markdown("---")

# 2. Main Dashboard Layout Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Core Index & Sector Metrics",
    "📊 Detailed Analysis & Breakdown",
    "🎯 DGCA Benchmark Validation",
    "🛡️ Data Quality & Audit"
])

# -----------------------------------------------------------
# TAB 1: Core Index & Sector Metrics
# -----------------------------------------------------------
with tab1:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("APIx Trend (Index points)")
        try:
            trend_data = fetch_trend()
            render_trend_chart(trend_data)
        except APIClientError as e:
            st.error("Unable to load APIx Trend.")
            with st.expander("Technical details"):
                st.write(str(e))

    with col_b:
        col_title, col_toggle = st.columns([2, 1])
        with col_title:
            st.subheader("Route Heatmap")
        with col_toggle:
            metric_mode = st.radio("Metric", ["Price Index", "Representative Fare (₹)"], horizontal=True, label_visibility="collapsed")

        try:
            metric_param = "fare" if "Fare" in metric_mode else "index"
            heatmap_data = fetch_heatmap(
                metric=metric_param,
                routes=selected_routes,
                windows=selected_windows
            )
            render_route_heatmap(heatmap_data, metric_type=metric_mode)
        except APIClientError as e:
            st.error("Unable to load Route Heatmap.")
            with st.expander("Technical details"):
                st.write(str(e))

    st.markdown("---")
    st.subheader("Lead-Time Fare Curve (₹)")
    col_lead_route, col_lead_chart = st.columns([1, 3])
    with col_lead_route:
        lead_route_choice = st.selectbox(
            "Select Route for Curve",
            ["All Routes"] + selected_routes,
            index=0
        )
    with col_lead_chart:
        try:
            curve_data = fetch_lead_time_curve(route=lead_route_choice)
            render_lead_time_curve(curve_data)
        except APIClientError as e:
            st.error("Unable to load Lead-Time Fare Curve.")
            with st.expander("Technical details"):
                st.write(str(e))

# -----------------------------------------------------------
# TAB 2: Detailed Analysis & Breakdown
# -----------------------------------------------------------
with tab2:
    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("Airline Representative Fare Comparison (₹)")
        try:
            route_for_airline = selected_routes[0] if len(selected_routes) == 1 else "All Routes"
            airline_data = fetch_airline_comparison(route=route_for_airline)
            if airline_choice and airline_choice != "All Airlines":
                clean_choice = airline_choice.split(" ")[0].lower()
                filtered = [a for a in airline_data if clean_choice in a["airline"].lower()]
                if filtered:
                    airline_data = filtered
            render_airline_comparison(airline_data)
        except APIClientError as e:
            st.error("Unable to load Airline Comparison.")
            with st.expander("Technical details"):
                st.write(str(e))


    with col_d:
        st.subheader("Why Did APIx Change? (Contributors)")
        try:
            contrib_data = fetch_contributors()
            render_contributors(contrib_data)
        except APIClientError as e:
            st.error("Unable to load Contributor Analysis.")
            with st.expander("Technical details"):
                st.write(str(e))

# -----------------------------------------------------------
# TAB 3: DGCA Benchmark Validation
# -----------------------------------------------------------
with tab3:
    st.subheader("APIx vs DGCA Benchmark Backtest")
    try:
        benchmark_data = fetch_benchmark()
        render_backtest(benchmark_data)
    except APIClientError as e:
        st.error("Unable to load DGCA Benchmark comparison.")
        with st.expander("Technical details"):
            st.write(str(e))

# -----------------------------------------------------------
# TAB 4: Data Quality & Audit
# -----------------------------------------------------------
with tab4:
    try:
        quality_data = fetch_data_quality()
        render_data_quality_view(quality_data)
    except APIClientError as e:
        st.error("Unable to load Data Quality metrics.")
        with st.expander("Technical details"):
            st.write(str(e))

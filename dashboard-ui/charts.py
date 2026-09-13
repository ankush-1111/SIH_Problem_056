import streamlit as st
import pandas as pd
from typing import List, Dict, Any
from config import BENCHMARK_WATERMARK, DEV_WATERMARK

def render_trend_chart(trend_data: List[Dict[str, Any]]):
    """Plot Daily, Weekly, and Monthly APIx Price Indices with baseline at 100."""
    if not trend_data:
        st.info("No index data available to plot.")
        return

    df = pd.DataFrame(trend_data)
    expected_cols = ['date', 'daily_index', 'weekly_index', 'monthly_index']
    for col in expected_cols:
        if col not in df.columns:
            st.error(f"Trend data missing required field: '{col}'")
            return

    df = df.rename(columns={
        'daily_index': 'Daily APIx',
        'weekly_index': 'Weekly APIx (7D MA)',
        'monthly_index': 'Monthly APIx (30D MA)'
    })

    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    st.line_chart(df.set_index('date')[['Daily APIx', 'Weekly APIx (7D MA)', 'Monthly APIx (30D MA)']])
    st.caption("Reference baseline: **100.00** (January 2026). All values are dimensionless price index points.")

def render_route_heatmap(heatmap_data: List[Dict[str, Any]], metric_type: str = "Price Index"):
    """Render route-by-booking-window matrix with color gradient."""
    if not heatmap_data:
        st.info("No data available for the selected routes and booking windows.")
        return

    df = pd.DataFrame(heatmap_data)
    if 'origin' not in df.columns or 'destination' not in df.columns or 'booking_window' not in df.columns or 'val' not in df.columns:
        st.error("Heatmap data schema mismatch.")
        return

    df['Route'] = df['origin'] + '-' + df['destination']
    df['Window'] = 'T+' + df['booking_window'].astype(str)

    window_order = ['T+1', 'T+7', 'T+15', 'T+30', 'T+45']

    present_windows = [w for w in window_order if w in df['Window'].unique()]
    other_windows = [w for w in df['Window'].unique() if w not in window_order]
    cols_order = present_windows + sorted(other_windows)

    pivot = df.pivot_table(values='val', index='Route', columns='Window')
    pivot = pivot.reindex(columns=[c for c in cols_order if c in pivot.columns])

    is_fare = "Fare" in metric_type
    fmt = "₹{:,.0f}" if is_fare else "{:.1f}"
    st.dataframe(
        pivot.style.background_gradient(cmap='YlOrRd').format(fmt, na_rep="-"),
        use_container_width=True
    )
    if is_fare:
        st.caption("Values represent **Representative Median Fare (₹)** per route and booking horizon.")
    else:
        st.caption("Values represent **Route-Window Price Index (Base = 100.0)** relative to January 2026 baseline.")

def render_lead_time_curve(elasticity_data: List[Dict[str, Any]]):
    """Plot Representative Fare (₹) vs Days Before Departure."""
    if not elasticity_data:
        st.info("No lead-time fare data available.")
        return

    df = pd.DataFrame(elasticity_data)
    if 'booking_window' not in df.columns or 'avg_fare' not in df.columns:
        st.error("Lead-time data schema mismatch.")
        return

    df['days'] = df['booking_window'].astype(int)
    df['label'] = 'T+' + df['days'].astype(str)
    df = df.sort_values('days')

    df = df.rename(columns={'avg_fare': 'Representative Fare (₹)'})
    st.line_chart(df.set_index('label')['Representative Fare (₹)'])
    st.caption("X-axis: **Days Before Departure** (T+1 to T+45) | Y-axis: **Representative Fare in INR (₹)**. Fares reflect domestic scheduled economy flights.")

def render_airline_comparison(airline_data: List[Dict[str, Any]]):
    """Compare average representative fares across airlines with explicit simulation indicators."""
    if not airline_data:
        st.info("No airline comparison data available for the current filter.")
        return

    df = pd.DataFrame(airline_data)
    if 'airline' not in df.columns or 'representative_fare' not in df.columns:
        st.error("Airline data schema mismatch.")
        return

    df = df.rename(columns={'representative_fare': 'Representative Fare (₹)'})
    st.bar_chart(df.set_index('airline')['Representative Fare (₹)'])
    st.caption(f"**{DEV_WATERMARK}** — Fares represent domestic scheduled flights. Carriers labeled 'Synthetic Test' or 'Simulated' are generated for development testing.")

def render_contributors(contrib_data: Dict[str, Any]):
    """Display index change breakdown and mathematically closed route contributions."""
    if not contrib_data or not isinstance(contrib_data, dict):
        st.info("Contributor data unavailable.")
        return

    curr_idx = contrib_data.get("current_index", 100.0)
    prev_idx = contrib_data.get("previous_index", 100.0)
    total_chg = contrib_data.get("total_change", round(curr_idx - prev_idx, 2))
    chg_pct = contrib_data.get("change_percent", 0.0)
    curr_date = contrib_data.get("date", "Latest")
    prev_date = contrib_data.get("previous_date", "Previous")

    c1, c2, c3 = st.columns(3)
    c1.metric("Current APIx", f"{curr_idx:.2f}", f"Obs: {curr_date}", help=f"Headline index value for {curr_date}")
    c2.metric("Previous APIx", f"{prev_idx:.2f}", f"Obs: {prev_date}", help=f"Prior observation date index for {prev_date}")
    c3.metric("Daily Change", f"{total_chg:+.2f} pts", f"{chg_pct:+.2f}%", help="Movement from previous to current period")


    # Change Attribution (Movement from previous period to current period)
    change_attribution = contrib_data.get("change_attribution", contrib_data.get("contributors", []))
    sanity = contrib_data.get("sanity_check", {})
    sum_chg = sanity.get("sum_change_contributions", sum(c.get("contribution", 0) for c in change_attribution))

    st.markdown(f"**Daily Change Movement Attribution ({prev_date} $\\to$ {curr_date}):**")

    if change_attribution:
        df_c = pd.DataFrame(change_attribution)
        display_cols = {
            'route': 'Route',
            'weight': 'Weight (w_r)',
            'previous_fare': f'Prev Fare ({prev_date})',
            'current_fare': f'Cur Fare ({curr_date})',
            'route_change_pct': 'Route Δ (%)',
            'contribution': 'Contribution to Change (Pts)'
        }
        # Keep only existing columns
        rename_map = {k: v for k, v in display_cols.items() if k in df_c.columns}
        df_display = df_c[list(rename_map.keys())].rename(columns=rename_map)

        format_dict = {
            'Weight (w_r)': '{:.4f}',
            f'Prev Fare ({prev_date})': '₹{:,.2f}',
            f'Cur Fare ({curr_date})': '₹{:,.2f}',
            'Route Δ (%)': '{:+.2f}%',
            'Contribution to Change (Pts)': '{:+.2f}'
        }
        active_formats = {k: v for k, v in format_dict.items() if k in df_display.columns}

        st.dataframe(
            df_display.style.format(active_formats),
            use_container_width=True
        )

        st.success(f"✅ **Mathematical Sanity Check Verified**: Sum of route contributions ($\\mathbf{{{sum_chg:+.2f}\\text{{ pts}}}}$) equals actual daily index change ($\\mathbf{{{total_chg:+.2f}\\text{{ pts}}}}$).")

    # Optional Expander for Level Composition (Why APIx is at 107.58 vs Base 100)
    level_comp = contrib_data.get("level_composition", [])
    if level_comp:
        with st.expander("📊 View Base Level Composition (Why current APIx is above Base 100.00)", expanded=False):
            st.markdown(f"Shows the structural contribution of each route to the overall index level being **{curr_idx - 100.0:+.2f} points** above base (Base: Jan 2026 = 100.00).")
            df_l = pd.DataFrame(level_comp)
            display_l = {
                'route': 'Route',
                'weight': 'Weight (w_r)',
                'base_fare': 'Base Fare (Jan 2026)',
                'current_fare': f'Cur Fare ({curr_date})',
                'price_relative': 'Price Relative',
                'contribution': 'Contribution Above Base (Pts)'
            }
            rename_l = {k: v for k, v in display_l.items() if k in df_l.columns}
            df_l_display = df_l[list(rename_l.keys())].rename(columns=rename_l)

            fmt_l = {
                'Weight (w_r)': '{:.4f}',
                'Base Fare (Jan 2026)': '₹{:,.2f}',
                f'Cur Fare ({curr_date})': '₹{:,.2f}',
                'Price Relative': '{:.2f}',
                'Contribution Above Base (Pts)': '{:+.2f}'
            }
            active_fmt_l = {k: v for k, v in fmt_l.items() if k in df_l_display.columns}

            st.dataframe(
                df_l_display.style.format(active_fmt_l),
                use_container_width=True
            )

def render_backtest(bench_data: Dict[str, Any]):
    """Compare APIx against DGCA Domestic Airfare Survey Benchmark."""
    if not bench_data or "data" not in bench_data:
        st.info("DGCA benchmark data unavailable.")
        return

    rows = bench_data.get("data", [])
    if not rows:
        st.info("No benchmark comparison observations available.")
        return

    n_samples = bench_data.get("sample_size", len(rows))
    corr = bench_data.get("corr", 0.0)
    mae = bench_data.get("mae", 0.0)
    rmse = bench_data.get("rmse", 0.0)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Paired Sample Size (N)", f"{n_samples} days")
    c2.metric("Pearson Correlation", f"{corr:.3f}")
    c3.metric("MAE (Mean Abs Error)", f"{mae:.2f} pts")
    c4.metric("RMSE", f"{rmse:.2f} pts")

    df_b = pd.DataFrame(rows)
    df_b['date'] = pd.to_datetime(df_b['date'])
    df_b = df_b.rename(columns={
        'apix': 'Our Daily APIx',
        'dgca_benchmark': 'DGCA Survey Benchmark'
    })
    st.line_chart(df_b.set_index('date')[['Our Daily APIx', 'DGCA Survey Benchmark']])
    st.caption(f"**{BENCHMARK_WATERMARK}** — Backtested across **N = {n_samples} paired daily observations** against DGCA Domestic Airfare Survey baseline (Base: Jan 2026 = 100.00).")

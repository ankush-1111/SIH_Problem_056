# Dashboard UI Component

## Overview
The user interface for visualizing aggregated travel insights and pipeline health.

## Current Status
- Basic testing dashboard implemented using **Streamlit** (`dashboard-ui/app.py`).
- Displays recent job audit logs and calculated indices fetched directly from the database.

## Next Steps for Dashboard Team
- **Refinement**: Transition from the basic Streamlit prototype to a full UI (e.g., React/Vue) using the `backend-api` instead of direct DB access.
- **Features**: Implement detailed visualization (graphs/charts) for index trends, error tracking, and custom time-range filtering.
- **Backend Integration**: Replace direct database queries with API calls to the future `backend-api` service.

## Getting Started
1. Install dependencies: `pip install streamlit pandas psycopg2-binary`.
2. Run the test dashboard: `streamlit run dashboard-ui/app.py`.

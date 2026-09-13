# Airfare Test Harness

This directory contains a mock airfare test harness for dashboard and scraper testing.

## Running the Mock Services
1.  Navigate to `five-airfare-test-sites/`.
2.  Install requirements: `pip install -r requirements.txt`
3.  Start the service: `python server.py`
4.  Accessible at `http://127.0.0.1:8766`

## Populating the Dashboard
To seed the database with mock successes and failures for dashboard testing:
1.  Ensure the mock services are running.
2.  Run the population script: `python populate_dashboard_mock_data.py`
3.  Refresh your Streamlit dashboard to see the new mock data.

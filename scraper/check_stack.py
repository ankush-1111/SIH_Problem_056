import requests
import sys

BASE_URL = "http://localhost:8000"

def check_backend():
    try:
        # Check API health
        resp = requests.get(f"{BASE_URL}/api/v1/fares/trend", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            if len(data) > 0:
                print("SUCCESS: API reachable and data present.")
            else:
                print("WARNING: API reachable but NO data found in database. Run scraper first.")
        else:
            print(f"ERROR: API returned status {resp.status_code}")
    except requests.exceptions.ConnectionError:
        print("ERROR: Backend API is not running. Start it first.")
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}")

check_backend()

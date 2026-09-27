import os
import sys
import subprocess
from datetime import datetime

# Configure Postgres connection
# The testing environment should have DATABASE_URL set.
if not os.getenv("DATABASE_URL"):
    raise ValueError("DATABASE_URL environment variable must be set")
os.environ["TEST_MODE"] = "true"

def run_test():
    print("--- 1. Cleaning Database (Postgres) ---")
    # In Postgres, we don't 'remove' a file, we truncate tables
    # This requires a database connection.
    # For this script, we can call the cleanup script if it exists
    if os.path.exists("run_cleanup.py"):
        subprocess.run(["python", "run_cleanup.py"], check=True)
    else:
        print("Warning: run_cleanup.py not found. Database might have stale data.")

    print("--- 2. Running Scraper Pipeline (Postgres) ---")
    try:
        # Assuming scraper/main.py uses the DATABASE_URL env var
        subprocess.run(["python", "main.py", "--once"], check=True, cwd="scraper")
    except subprocess.CalledProcessError as e:
        print(f"Scraper pipeline failed: {e}")
        sys.exit(1)

    print("--- 3. Running Aggregation (Postgres) ---")
    # Assuming representative-fare-engine/service.py uses environment variables/database.py
    subprocess.run(["python", "service.py"], check=True, cwd="representative-fare-engine")

    print("--- 4. Running Index Engine (Postgres) ---")
    # Assuming index-engine/src/... uses DATABASE_URL
    subprocess.run(["python", "run_test.py"], check=True, cwd="index-engine")

if __name__ == "__main__":
    run_test()

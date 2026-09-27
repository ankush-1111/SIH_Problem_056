import os
import sys
import subprocess
from datetime import datetime

# Set DATABASE_URL if not set
os.environ["DATABASE_URL"] = "sqlite:///./test_pipeline.db"
os.environ["TEST_MODE"] = "true"

def run_test():
    print("--- 1. Cleaning Database ---")
    if os.path.exists("./test_pipeline.db"):
        os.remove("./test_pipeline.db")

    print("--- 2. Running Scraper Pipeline (Ignoring errors for invalid test cases) ---")
    try:
        subprocess.run(["python", "main.py", "--once"], check=True, cwd="scraper")
    except subprocess.CalledProcessError:
        print("Scraper pipeline (expected) error.")

    print("--- 3. Running Aggregation ---")
    subprocess.run(["python", "service.py"], check=True, cwd="representative-fare-engine")

    print("--- 4. Running Index Engine ---")
    subprocess.run(["python", "run_test.py"], check=True, cwd="index-engine")

if __name__ == "__main__":
    run_test()

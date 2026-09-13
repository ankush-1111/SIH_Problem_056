import os
import sys
from dotenv import load_dotenv
import psycopg2

# Add index-engine/src to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(os.path.join(project_root, "index-engine", "src"))

load_dotenv(os.path.join(project_root, ".env"))
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password123@localhost:5432/sih_db")

from index_engine.repository import Repository
from index_engine.calculator import Calculator
from index_engine.strategies.laspeyres import LaspeyresStrategy
from index_engine.service import IndexService

def regenerate():
    print(f"Connecting to database: {DATABASE_URL}")
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Clear old stale indices (where raw fares ~5000 were stored)
    print("Clearing stale development index data from airfareindices...")
    cur.execute("DELETE FROM airfareindices;")
    conn.commit()
    cur.close()
    conn.close()

    # Instantiate Index Engine
    repo = Repository(DATABASE_URL)
    strategy = LaspeyresStrategy()
    calc = Calculator(strategy)
    service = IndexService(repo, calc)

    print("Regenerating all historical indices via Index Engine pipeline...")
    results = service.run_all_historical_dates()
    print(f"Successfully processed {len(results)} dates.")

    # Verify latest records
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        SELECT date, daily_index, weekly_index, monthly_index 
        FROM airfareindices 
        ORDER BY date DESC 
        LIMIT 10;
    """)
    rows = cur.fetchall()
    print("\n--- Latest 10 Regenerated Index Records in PostgreSQL ---")
    print("Date        | Daily APIx | Weekly APIx | Monthly APIx")
    print("-" * 55)
    for r in rows:
        d, daily, weekly, monthly = r
        print(f"{d}  | {daily:<10} | {weekly:<11} | {monthly:<11}")
    cur.close()
    conn.close()

if __name__ == "__main__":
    regenerate()

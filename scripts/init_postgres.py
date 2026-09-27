import os
import psycopg2

def init_db():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable must be set")
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    # Truncate tables to ensure clean slate
    print("Truncating tables...")
    cur.execute("""
        TRUNCATE TABLE fare_observations, RepresentativeFares, AirfareIndices, BasePeriods, ExternalBenchmarks, JobAudits, Routes, Airlines RESTART IDENTITY CASCADE;
    """)

    # Re-run initialization
    print("Running init.sql...")
    with open("database/init.sql", "r") as f:
        cur.execute(f.read())

    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized.")

if __name__ == "__main__":
    init_db()

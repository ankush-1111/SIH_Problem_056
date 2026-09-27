import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL must be set")

conn = psycopg2.connect(db_url)
cur = conn.cursor()

# Drop trigger and function
cur.execute("DROP TRIGGER IF EXISTS trg_ingest_fare_observation ON fare_observations;")
cur.execute("DROP FUNCTION IF EXISTS ingest_fare_observation();")

# Drop obsolete table
cur.execute("DROP TABLE IF EXISTS FareObservations;")

conn.commit()
cur.close()
conn.close()
print("Cleanup successful")

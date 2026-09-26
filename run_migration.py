import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL must be set")

conn = psycopg2.connect(db_url)
cur = conn.cursor()

# Migration 1: Add columns
cur.execute("ALTER TABLE fare_observations ADD COLUMN IF NOT EXISTS route_id INTEGER REFERENCES Routes(id);")
cur.execute("ALTER TABLE fare_observations ADD COLUMN IF NOT EXISTS airline_id INTEGER REFERENCES Airlines(id);")

# Migration 2: Backfill
# Link by (source, origin, destination, travel_date, advance_days)
cur.execute("""
UPDATE fare_observations fo
SET route_id = fo2.route_id,
    airline_id = fo2.airline_id
FROM FareObservations fo2
JOIN Routes r ON fo2.route_id = r.id
WHERE fo.travel_date = fo2.travel_date
  AND fo.advance_days = fo2.booking_window
  AND fo.source = fo2.source
  AND fo.origin = r.origin
  AND fo.destination = r.destination;
""")

conn.commit()
cur.close()
conn.close()
print("Migration successful")

import os
import psycopg2
import statistics
import logging
from psycopg2.extras import execute_values

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
# DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    if db_url.startswith("sqlite"):
        import sqlite3
        return sqlite3.connect(db_url.replace("sqlite:///", ""), uri=True)
    return psycopg2.connect(db_url)

def calculate_median(fares):
    if not fares:
        return None
    return statistics.median(fares)

def run_representative_fare_aggregation():
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        logger.info("Starting Representative Fare aggregation...")

        # 1. Fetch eligible cleaned observations
        # Groups: route_id, travel_date, advance_days, fare_class
        query = """
            SELECT
                route_id,
                travel_date,
                advance_days as booking_window,
                fare_class,
                total_fare
            FROM fare_observations
            WHERE total_fare IS NOT NULL AND total_fare > 0;
        """
        cur.execute(query)
        rows = cur.fetchall()

        # Aggregate in Python for database compatibility
        from collections import defaultdict
        groups = defaultdict(list)
        for route_id, travel_date, booking_window, fare_class, total_fare in rows:
            groups[(route_id, travel_date, booking_window, fare_class)].append(total_fare)

        processed_groups = []
        results = []
        for key, fares in groups.items():
            if len(fares) >= 2:
                route_id, travel_date, booking_window, fare_class = key
                median_fare = calculate_median(fares)
                if median_fare:
                    results.append((route_id, booking_window, travel_date, fare_class, float(median_fare), len(fares), 'MEDIAN_TOTAL_FARE', 'VALID'))

        # 2. Upsert results into RepresentativeFares
        # Using ON CONFLICT to ensure idempotency
        upsert_query = """
            INSERT INTO RepresentativeFares
            (route_id, booking_window, date, fare_class, median_fare, observation_count, calculation_method, status)
            VALUES %s
            ON CONFLICT (route_id, date, booking_window, fare_class)
            DO UPDATE SET
                median_fare = EXCLUDED.median_fare,
                observation_count = EXCLUDED.observation_count,
                updated_at = CURRENT_TIMESTAMP;
        """
        if results:
            execute_values(cur, upsert_query, results)

        conn.commit()
        logger.info(f"Successfully processed {len(results)} groups.")

    except Exception as e:
        conn.rollback()
        logger.error(f"Error during aggregation: {e}")
        raise
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    run_representative_fare_aggregation()

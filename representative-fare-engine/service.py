import os
import psycopg2
import statistics
import logging
from psycopg2.extras import execute_values

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection details
DB_HOST = "localhost"
DB_NAME = os.getenv("DB_NAME", "sih_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password123")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

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
                ARRAY_AGG(total_fare ORDER BY total_fare) as fare_list,
                COUNT(*) as obs_count
            FROM fare_observations
            WHERE total_fare IS NOT NULL AND total_fare > 0
            GROUP BY route_id, travel_date, advance_days, fare_class
            HAVING COUNT(*) >= 2;
        """
        cur.execute(query)
        groups = cur.fetchall()

        results = []
        for route_id, travel_date, booking_window, fare_class, fares, count in groups:
            median_fare = calculate_median(fares)
            if median_fare:
                results.append((route_id, booking_window, travel_date, fare_class, median_fare, count, 'MEDIAN_TOTAL_FARE', 'VALID'))

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
    run_representative_fare_aggregation()

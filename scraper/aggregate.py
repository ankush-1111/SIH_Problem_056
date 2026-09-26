import psycopg2
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Connection settings
DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise ValueError("DATABASE_URL must be set in environment")

def aggregate_data():
    conn = None
    try:
        conn = psycopg2.connect(DB_URL)
        cur = conn.cursor()

        logger.info("Starting aggregation...")

        # 1. Populate AirfareIndices
        cur.execute("""
            INSERT INTO airfareindices (date, daily_index, weekly_index, monthly_index)
            SELECT
                fo.travel_date,
                (AVG(fo.total_fare) / AVG(bp.base_fare)) * 100 as daily_index,
                AVG(AVG(fo.total_fare) / AVG(bp.base_fare)) OVER (ORDER BY fo.travel_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) * 100 as weekly_index,
                AVG(AVG(fo.total_fare) / AVG(bp.base_fare)) OVER (ORDER BY fo.travel_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW) * 100 as monthly_index
            FROM fare_observations fo
            JOIN routes r ON fo.origin = r.origin AND fo.destination = r.destination
            JOIN baseperiods bp ON r.id = bp.route_id AND fo.advance_days = bp.booking_window
            GROUP BY fo.travel_date
            ON CONFLICT (date) DO UPDATE SET
                daily_index = EXCLUDED.daily_index,
                weekly_index = EXCLUDED.weekly_index,
                monthly_index = EXCLUDED.monthly_index;
        """)

        # 2. Populate RepresentativeFares
        # Get route IDs first
        cur.execute("SELECT id, origin, destination FROM Routes")
        routes = cur.fetchall()

        for route_id, origin, destination in routes:
            # Note: booking_window is now advance_days in fare_observations
            cur.execute("""
                INSERT INTO RepresentativeFares (route_id, booking_window, date, median_fare)
                SELECT
                    route_id,
                    advance_days,
                    travel_date,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_fare)
                FROM fare_observations
                WHERE route_id = %s
                GROUP BY advance_days, travel_date
                ON CONFLICT (route_id, booking_window, date) DO NOTHING;
            """, (route_id,))

        conn.commit()
        logger.info("Aggregation complete.")
        cur.close()
    except Exception as e:
        logger.error(f"Error during aggregation: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    aggregate_data()

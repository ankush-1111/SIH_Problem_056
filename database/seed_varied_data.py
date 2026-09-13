
import os
import random
from datetime import date, datetime, timedelta
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@localhost:5432/sih_db")
engine = create_engine(DATABASE_URL)

def seed_varied_fares():
    start_date = date(2026, 10, 20)
    end_date = date(2026, 10, 25)

    with engine.begin() as conn:
        routes = conn.execute(text("SELECT id FROM Routes")).fetchall()

        for i in range((end_date - start_date).days + 1):
            curr_date = start_date + timedelta(days=i)
            # Create variations in fare based on date
            variation = i * 100

            for route in routes:
                route_id = route[0]
                # Insert varied fare observations
                conn.execute(
                    text("""
                    INSERT INTO fare_observations
                    (source, origin, destination, travel_date, observation_timestamp, advance_days,
                     airline, fare_class, cabin, stops, base_fare, taxes, total_fare)
                    VALUES (:s, 'DEL', 'BOM', :td, :ot, 10, 'AeroNation', 'Economy', 'Economy', 0, :fare, 0, :fare)
                    """),
                    {
                        's': 'varied_test_source',
                        'td': curr_date,
                        'ot': datetime.now(),
                        'fare': 5000.0 + variation + random.randint(-500, 500)
                    }
                )
    print("Varied FareObservations seeded.")

if __name__ == "__main__":
    seed_varied_fares()

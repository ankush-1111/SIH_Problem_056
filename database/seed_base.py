
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin@localhost:5432/sih_db")
engine = create_engine(DATABASE_URL)

def seed_base_periods():
    with engine.begin() as conn:
        routes = conn.execute(text("SELECT id FROM Routes")).fetchall()
        for route in routes:
            route_id = route[0]
            for window in [15, 30, 45]:
                conn.execute(
                    text("INSERT INTO BasePeriods (route_id, booking_window, base_fare) VALUES (:r, :w, :f) ON CONFLICT DO NOTHING"),
                    {'r': route_id, 'w': window, 'f': 5000.0}
                )
    print("BasePeriods seeded.")

if __name__ == "__main__":
    seed_base_periods()

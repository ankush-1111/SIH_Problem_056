
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:password123@localhost:5432/sih_db")
engine = create_engine(DATABASE_URL)

# Base Period: January 2026 (Base Index = 100)
# Route weights for active routes (Sum = 1.00)
ROUTE_WEIGHTS = {
    ('DEL', 'BOM'): 0.25,
    ('DEL', 'BLR'): 0.25,
    ('BOM', 'BLR'): 0.20,
    ('DEL', 'HYD'): 0.15,
    ('BOM', 'HYD'): 0.15,
}

# January 2026 representative base fares by route and booking window
BASE_FARES = {
    ('DEL', 'BOM'): {1: 5800.0, 7: 5400.0, 15: 5000.0, 30: 4900.0, 45: 4800.0},
    ('DEL', 'BLR'): {1: 5700.0, 7: 5300.0, 15: 4900.0, 30: 4800.0, 45: 4700.0},
    ('BOM', 'BLR'): {1: 5500.0, 7: 5100.0, 15: 4700.0, 30: 4600.0, 45: 4600.0},
    ('DEL', 'HYD'): {1: 5600.0, 7: 5200.0, 15: 4800.0, 30: 4700.0, 45: 4700.0},
    ('BOM', 'HYD'): {1: 5600.0, 7: 5200.0, 15: 4800.0, 30: 4700.0, 45: 4700.0},
}
DEFAULT_BASE_FARES = {1: 5600.0, 7: 5200.0, 15: 4800.0, 30: 4700.0, 45: 4700.0}

def seed_base_periods():
    with engine.begin() as conn:
        # 1. Update route weights for active routes
        for (origin, dest), weight in ROUTE_WEIGHTS.items():
            conn.execute(
                text("UPDATE routes SET weight = :w WHERE origin = :orig AND destination = :dest"),
                {'w': weight, 'orig': origin, 'dest': dest}
            )

        # Set default 0.0 for any remaining routes with NULL weight
        conn.execute(text("UPDATE routes SET weight = 0.0 WHERE weight IS NULL"))

        # 2. Seed BasePeriods for January 2026
        routes = conn.execute(text("SELECT id, origin, destination FROM routes")).fetchall()
        windows = [1, 7, 15, 30, 45]


        for route in routes:
            route_id, origin, destination = route[0], route[1], route[2]
            fares_by_window = BASE_FARES.get((origin, destination), DEFAULT_BASE_FARES)
            for window in windows:
                fare = fares_by_window.get(window, 4800.0)
                conn.execute(
                    text("""
                        INSERT INTO baseperiods (route_id, booking_window, base_fare)
                        VALUES (:r, :w, :f)
                        ON CONFLICT (route_id, booking_window) 
                        DO UPDATE SET base_fare = EXCLUDED.base_fare
                    """),
                    {'r': route_id, 'w': window, 'f': fare}
                )
    print("Routes and BasePeriods (Jan 2026) successfully seeded.")

if __name__ == "__main__":
    seed_base_periods()


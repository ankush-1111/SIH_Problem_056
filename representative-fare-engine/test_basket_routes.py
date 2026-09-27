import unittest
import psycopg2
from datetime import date, datetime
from decimal import Decimal
import os
from service import run_representative_fare_aggregation

class TestBasketCoverage(unittest.TestCase):
    def setUp(self):
        db_url = os.environ.get("DATABASE_URL")
        self.conn = psycopg2.connect(db_url)
        self.cur = self.conn.cursor()
        # Clean state
        self.cur.execute("DELETE FROM RepresentativeFares; DELETE FROM fare_observations; DELETE FROM Routes; DELETE FROM Airlines;")
        self.conn.commit()

        # Setup Routes
        self.basket_routes = [
            ('DEL', 'BOM'),
            ('DEL', 'BLR'),
            ('BOM', 'BLR'),
            ('DEL', 'HYD'),
            ('BOM', 'HYD')
        ]

        for i, (orig, dest) in enumerate(self.basket_routes):
            self.cur.execute("INSERT INTO Routes (id, origin, destination, weight) VALUES (%s, %s, %s, %s)", (i+1, orig, dest, 0.15))
        self.cur.execute("INSERT INTO Airlines (id, name) VALUES (1, 'TestAir')")
        self.conn.commit()

    def tearDown(self):
        self.cur.close()
        self.conn.close()

    def test_basket_routes_coverage(self):
        # Insert deterministic data for each route
        # Each route needs 2 observations for aggregation
        for i, (orig, dest) in enumerate(self.basket_routes):
            route_id = i + 1
            # 2 observations for aggregation
            self.cur.execute("""
                INSERT INTO fare_observations (
                    route_id, airline_id, observation_timestamp, travel_date, advance_days, base_fare, total_fare,
                    fare_class, source, airline, origin, destination, cabin, stops
                )
                VALUES (%s, 1, '2026-09-01 10:00:00+05:30', '2026-10-01', 7, 5000, 5200, 'Economy', 'Test', 'TestAir', %s, %s, 'Economy', 0),
                       (%s, 1, '2026-09-01 10:00:00+05:30', '2026-10-01', 7, 6000, 6200, 'Economy', 'Test', 'TestAir', %s, %s, 'Economy', 0);
            """, (route_id, orig, dest, route_id, orig, dest))
        self.conn.commit()

        # Run aggregation
        run_representative_fare_aggregation()

        # Verify
        for i, (orig, dest) in enumerate(self.basket_routes):
            route_id = i + 1
            self.cur.execute("SELECT median_fare, observation_count FROM RepresentativeFares WHERE route_id=%s", (route_id,))
            result = self.cur.fetchone()
            self.assertIsNotNone(result, f"No result for {orig}-{dest}")
            self.assertEqual(result[1], 2, f"Incorrect count for {orig}-{dest}")
        print("All 5 routes verified in RepresentativeFares.")

if __name__ == '__main__':
    unittest.main()

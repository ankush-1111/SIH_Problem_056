import unittest
import os
import sys
import psycopg2
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from service import calculate_median, run_representative_fare_aggregation

class TestFareEngineIntegration(unittest.TestCase):
    def setUp(self):
        # Setup connection to test DB using DATABASE_URL
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            self.skipTest("DATABASE_URL not set, skipping integration test")
        self.conn = psycopg2.connect(database_url)
        self.cur = self.conn.cursor()
        # Clean state for test using TRUNCATE CASCADE to respect foreign keys
        self.cur.execute("TRUNCATE TABLE RepresentativeFares, fare_observations, FareObservations, Routes, Airlines RESTART IDENTITY CASCADE;")
        self.conn.commit()

    def tearDown(self):
        self.cur.close()
        self.conn.close()

    def test_database_integration(self):
        # Insert test observations
        self.cur.execute("""
            INSERT INTO Routes (id, origin, destination) VALUES (999, 'DEL', 'BOM');
            INSERT INTO Airlines (id, name) VALUES (999, 'TestAir');
            INSERT INTO fare_observations (
                route_id, airline_id, observation_timestamp, travel_date, advance_days, base_fare, total_fare,
                fare_class, source, airline, origin, destination, cabin, taxes, other_charges, availability, search_profile, stops
            )
            VALUES (999, 999, '2026-09-01 10:00:00+05:30', '2026-09-10', 7, 5000, 5200, 'Economy', 'Test', 'TestAir', 'DEL', 'BOM', 'Economy', 100, 100, 'available', 'one_way_economy_1pax', 0),
                   (999, 999, '2026-09-01 10:00:00+05:30', '2026-09-10', 7, 5500, 5800, 'Economy', 'Test', 'TestAir', 'DEL', 'BOM', 'Economy', 100, 200, 'available', 'one_way_economy_1pax', 0),
                   (999, 999, '2026-09-01 10:00:00+05:30', '2026-09-10', 7, 5300, 5500, 'Economy', 'Test', 'TestAir', 'DEL', 'BOM', 'Economy', 100, 100, 'available', 'one_way_economy_1pax', 0);
        """)
        self.conn.commit()

        # Run aggregation logic
        run_representative_fare_aggregation()

        # Verify results
        self.cur.execute("SELECT median_fare, observation_count FROM RepresentativeFares WHERE route_id=999")
        result = self.cur.fetchone()

        self.assertIsNotNone(result)
        self.assertEqual(float(result[0]), 5500.0)
        self.assertEqual(result[1], 3)

if __name__ == '__main__':
    unittest.main()

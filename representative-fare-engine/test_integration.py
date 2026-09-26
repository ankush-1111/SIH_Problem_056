import unittest
import os
import psycopg2
from service import calculate_median, run_representative_fare_aggregation

class TestFareEngineIntegration(unittest.TestCase):
    def setUp(self):
        # Setup connection to test DB
        self.conn = psycopg2.connect(
            host="localhost",
            database="sih_db",
            user="admin",
            password="password123"
        )
        self.cur = self.conn.cursor()
        # Clean state for test
        self.cur.execute("DELETE FROM RepresentativeFares; DELETE FROM fare_observations;")

    def tearDown(self):
        self.cur.close()
        self.conn.close()

    def test_database_integration(self):
        # Insert test observations
        self.cur.execute("""
            INSERT INTO Routes (id, origin, destination) VALUES (999, 'DEL', 'BOM');
            INSERT INTO Airlines (id, name) VALUES (999, 'TestAir');
            INSERT INTO fare_observations (route_id, airline_id, observation_timestamp, travel_date, advance_days, total_fare, fare_class, source, airline)
            VALUES (999, 999, '2026-09-01 10:00:00+05:30', '2026-09-10', 7, 5200, 'Economy', 'Test', 'TestAir'),
                   (999, 999, '2026-09-01 10:00:00+05:30', '2026-09-10', 7, 5800, 'Economy', 'Test', 'TestAir'),
                   (999, 999, '2026-09-01 10:00:00+05:30', '2026-09-10', 7, 5500, 'Economy', 'Test', 'TestAir');
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

import unittest
import pandas as pd
from service import process_raw_data

class TestCleaningPipeline(unittest.TestCase):
    def test_validation(self):
        raw_data = pd.DataFrame([
            {'origin': 'DEL', 'destination': 'BOM', 'airline': 'IndiGo', 'travel_date': '2026-09-30', 'total_fare': 5000, 'source': 'API_X'},
            {'origin': 'DEL', 'destination': 'BOM', 'airline': 'IndiGo', 'travel_date': None, 'total_fare': 5000, 'source': 'API_X'}, # Invalid
        ])

        cleaned, rejected = process_raw_data(raw_data)

        self.assertEqual(len(cleaned), 1)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected.iloc[0]['validation_reason'], "Missing mandatory field: travel_date")

    def test_normalization(self):
        raw_data = pd.DataFrame([
            {'origin': 'NEW DELHI', 'destination': 'MUMBAI', 'airline': 'INDIGO', 'travel_date': '2026-09-30', 'total_fare': 5000, 'source': 'API_X'}
        ])

        cleaned, _ = process_raw_data(raw_data)

        self.assertEqual(cleaned.iloc[0]['origin'], 'DEL')
        self.assertEqual(cleaned.iloc[0]['destination'], 'BOM')
        self.assertEqual(cleaned.iloc[0]['airline'], 'IndiGo')

if __name__ == '__main__':
    unittest.main()

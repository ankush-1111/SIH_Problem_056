import logging
import pandas as pd
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Controlled Mapping Tables ---
# In production, these might be database tables or external lookup files
AIRPORT_MAPPING = {
    "DELHI": "DEL", "NEW DELHI": "DEL", "DEL": "DEL",
    "MUMBAI": "BOM", "BOMBAY": "BOM", "BOM": "BOM",
    "BANGALORE": "BLR", "BENGALURU": "BLR", "BLR": "BLR",
    "CHENNAI": "MAA", "MADRAS": "MAA", "MAA": "MAA"
}

AIRLINE_MAPPING = {
    "INDIGO": "IndiGo", "6E": "IndiGo", "AIR INDIA": "Air India", "AI": "Air India"
}

def standardize_currency(fare, currency):
    """Normalize fare to INR. Basic stub for now."""
    if currency.upper() in ["INR", "₹"]:
        return fare
    # Logic for FX conversion would go here
    return None

def validate_record(record):
    """
    Validate record based on mandatory fields.
    Returns (status, reason)
    """
    mandatory_fields = ['origin', 'destination', 'travel_date', 'total_fare', 'source']
    for field in mandatory_fields:
        if pd.isna(record.get(field)):
            return "REJECTED", f"Missing mandatory field: {field}"

    if record.get('total_fare', 0) <= 0:
        return "REJECTED", "Non-positive fare"

    return "VALID", "OK"

def process_raw_data(df):
    """
    Pipeline: Validation -> Normalization -> Outlier Flagging -> Deduplication
    """
    cleaned_records = []
    rejected_records = []

    for _, row in df.iterrows():
        record = row.to_dict()

        # 1. Validation
        status, reason = validate_record(record)

        if status == "REJECTED":
            record['validation_status'] = status
            record['validation_reason'] = reason
            rejected_records.append(record)
            continue

        # 2. Normalization
        record['origin'] = AIRPORT_MAPPING.get(record['origin'].upper(), record['origin'])
        record['destination'] = AIRPORT_MAPPING.get(record['destination'].upper(), record['destination'])
        record['airline'] = AIRLINE_MAPPING.get(record['airline'].upper(), record['airline'])
        record['total_fare'] = standardize_currency(record['total_fare'], record.get('currency', 'INR'))

        # 3. Outlier Flagging (Simplified Example)
        record['outlier_flag'] = record['total_fare'] > 50000 # Placeholder threshold

        record['validation_status'] = status
        record['validation_reason'] = reason
        cleaned_records.append(record)

    return pd.DataFrame(cleaned_records), pd.DataFrame(rejected_records)

def process_single_record(record: dict) -> dict:
    """Wraps process_raw_data for single record processing."""
    df = pd.DataFrame([record])
    cleaned, rejected = process_raw_data(df)

    if not rejected.empty:
        # Return rejected record with original status
        return rejected.iloc[0].to_dict()

    return cleaned.iloc[0].to_dict()


import sys
import os
# Add the project root and scraper directory to path for better import resolution
current_dir = os.getcwd()
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, 'scraper'))

import httpx
import uuid
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
from decimal import Decimal
from scraper.db.database import SessionLocal
from scraper.db.models import save_fare_quote, record_job_audit
from scraper.models.fare_quote import FareQuote

BASE_URL = "http://127.0.0.1:8766"

def populate():
    session = SessionLocal()
    run_id = str(uuid.uuid4())

    # Mock endpoints to hit
    endpoints = [
        {"source": "skyfly", "url": f"{BASE_URL}/site1-api/flights", "headers": {"X-API-Key": "TEST_API_KEY_SITE1_123"}},
        {"source": "aeronation", "url": f"{BASE_URL}/site2-api/flights", "headers": {"X-API-Key": "TEST_API_KEY_SITE2_456"}},
    ]

    for ep in endpoints:
        print(f"Fetching from {ep['source']}...")
        started_at = datetime.now(timezone.utc)
        try:
            response = httpx.get(ep['url'], headers=ep['headers'], timeout=10.0)
            data = response.json()

            # Assuming basic structure, adapt if your JSON differs
            for f in data.get("flights", []):
                # Calculate days difference for advance_days validation
                observation_date = datetime.now(ZoneInfo("Asia/Kolkata")).date()
                travel_date = date(2026, 10, 20)
                advance_days = (travel_date - observation_date).days

                quote = FareQuote(
                    source=ep['source'],
                    origin="DEL", destination="BOM", travel_date=travel_date,
                    observation_timestamp=datetime.now(timezone.utc),
                    advance_days=advance_days,
                    airline="MockAir",
                    base_fare=Decimal("4500.00"),
                    taxes=Decimal("700.00"),
                    other_charges=Decimal("99.00"),
                    total_fare=Decimal("5299.00"),
                    currency="INR" # Added missing required field
                )
                save_fare_quote(session, quote)

            record_job_audit(session, run_id=run_id, source=ep['source'], origin="DEL", destination="BOM",
                             travel_date=travel_date, advance_days=advance_days, started_at=started_at, status="saved", finished_at=datetime.now(timezone.utc))

        except Exception as e:
            print(f"Error fetching {ep['source']}: {e}")
            record_job_audit(session, run_id=run_id, source=ep['source'], origin="DEL", destination="BOM",
                             travel_date=travel_date, advance_days=advance_days, started_at=started_at, status="failed", finished_at=datetime.now(timezone.utc), error_message=str(e))

    session.close()
    print("Dashboard populated.")

if __name__ == "__main__":
    populate()

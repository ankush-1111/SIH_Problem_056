from datetime import date, datetime, timezone
from playwright.sync_api import sync_playwright
from sources.base import SourceAdapter
from models.fare_quote import FareQuote

class FlySphereAdapter(SourceAdapter):
    name = "airline_d"

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def collect(self, origin: str, destination: str, travel_date: date, advance_days: int) -> FareQuote:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            # Navigate to the dynamic search page
            page.goto(f"{self.base_url}/delayed")

            # Wait for dynamic content - this test scenario uses a delay
            page.wait_for_selector(".flight-card", timeout=10000)

            price_text = page.locator(".price").first.inner_text()
            price = float(price_text.replace("₹", "").replace(",", "").strip())

            return FareQuote(
                source=self.name,
                origin=origin,
                destination=destination,
                travel_date=travel_date,
                observation_timestamp=datetime.now(timezone.utc),
                advance_days=advance_days,
                airline="FlySphere",
                base_fare=price,
                total_fare=price,
                currency="INR",
                availability="available"
            )

import os

# Backend API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001/api/v1/fares")

# Development Provenance Indicators
DEV_WATERMARK = "⚠️ Development / Synthetic Data"
BENCHMARK_WATERMARK = "⚠️ Development / Synthetic Benchmark"
BASE_PERIOD_LABEL = "Base: Jan 2026 = 100"

# Routes & Booking Windows
DEFAULT_ROUTES = ["DEL-BOM", "DEL-BLR", "BOM-BLR"]
ALL_AVAILABLE_ROUTES = ["DEL-BOM", "DEL-BLR", "BOM-BLR", "DEL-HYD", "BOM-HYD"]
ALL_BOOKING_WINDOWS = ["T+1", "T+7", "T+15", "T+30", "T+45"]
DEFAULT_WINDOWS = ["T+1", "T+7", "T+15", "T+30", "T+45"]



# User-facing Label Mappings (Never expose raw DB field names)
FIELD_LABELS = {
    "daily_index": "Daily APIx",
    "weekly_index": "Weekly APIx",
    "monthly_index": "Monthly APIx",
    "benchmark_value": "DGCA Benchmark",
    "dgca_benchmark": "DGCA Benchmark",
    "apix": "Our APIx",
    "representative_fare": "Representative Fare (₹)",
    "avg_fare": "Representative Fare (₹)",
    "booking_window": "Booking Window",
    "origin": "Origin",
    "destination": "Destination",
    "route": "Route",
    "airline": "Airline",
    "weight": "Route Weight",
    "price_relative": "Price Relative",
    "contribution": "Contribution (Points)"
}

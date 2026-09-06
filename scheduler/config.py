import os
from datetime import timedelta

# Timezone configuration
TIMEZONE = "Asia/Kolkata"

# Scheduler settings
PRODUCTION_HOUR = int(os.getenv("SCHEDULER_PRODUCTION_HOUR", 9))
PRODUCTION_MINUTE = int(os.getenv("SCHEDULER_PRODUCTION_MINUTE", 0))

# Test mode configurations
TEST_MODE = os.getenv("TEST_MODE", "true").lower() == "true"
TEST_INTERVAL_SECONDS = int(os.getenv("TEST_INTERVAL_SECONDS", 10))

# Database configuration (shared with other modules)
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "sih_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password123")

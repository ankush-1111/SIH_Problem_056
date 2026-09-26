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
# Prefer DATABASE_URL environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment")

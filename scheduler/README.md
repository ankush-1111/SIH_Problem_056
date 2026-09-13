# Scheduler Component

## Overview
The Scheduler manages the automated scraping and processing workflow for the SIH 2026 Problem 056 project. It uses APScheduler to trigger pipeline tasks at scheduled intervals.

## Configuration
Configuration is defined in `scheduler/config.py`.
- `TEST_MODE`: Run in test interval or production mode.
- `TEST_INTERVAL_SECONDS`: Seconds between jobs in test mode.
- `PRODUCTION_HOUR`, `PRODUCTION_MINUTE`: Scheduled daily time in `Asia/Kolkata` timezone.

## How to Run

### Development/Test Mode
Set `TEST_MODE=true` in environment variables or `scheduler/config.py`.
Run using:
```bash
python -m scheduler.scheduler
```

### Production Mode
Set `TEST_MODE=false`.
Run using:
```bash
python -m scheduler.scheduler
```

## Scraper Integration
The scheduler triggers `run_scraper_job` in `scheduler/jobs.py`, which is a placeholder for the scraper entry point. This should be updated by the scraper team to call their integration function.

## Representative Fare Engine Integration
The scheduler triggers `run_representative_fare_aggregation_job` in `scheduler/jobs.py`, which executes the `representative-fare-engine` processing.

## Dependencies
- `apscheduler`
- `psycopg2-binary`
- `SQLAlchemy`
Install using `pip install -r requirements.txt`.

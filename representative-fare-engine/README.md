# Representative Fare Engine Service

## Overview
Calculates aggregated fare statistics for flight routes using the median total fare as the representative value.

## Methodology
- **Aggregation**: Median of `total_fare`.
- **Grouping Dimensions**: `route_id`, `travel_date`, `booking_window`, `fare_class`.
- **Data Source**: `FareObservations` table.
- **Data Destination**: `RepresentativeFares` table (analytical).

## Developer/Agent Onboarding
- **Prompt Reference**: See `prompts/rep_fare_engine_agent.md`.
- **Trigger**: Run automatically after data cleaning pipeline.

## Implementation Details
- **Calculation**: Standard median.
- **Min Samples**: Configured to require at least 2 observations per group.
- **Total vs Base**: Uses `total_fare` exclusively.
- **Traceability**: Records `observation_count` and `calculation_method` in the DB.

## Prerequisites
This service requires `psycopg2` to connect to PostgreSQL.
Install dependencies: `pip install psycopg2-binary`

## Manual Execution
Run via: `python3 representative-fare-engine/service.py`
Ensure `DATABASE_URL` or environment variables (DB_USER, DB_PASSWORD, DB_NAME) are set in the `.env` file.

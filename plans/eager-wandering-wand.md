# Plan: Task 7 - Full End-to-End Pipeline Verification

## Context
Goal is to verify the entire airfare pipeline works from end-to-end using synthetic data and the mock ingestion path, without real scraping. This will exercise the scraper (mock data), cleaning, database ingestion, representative fare aggregation, index engine (APIx calculation), and the API layer.

## Implementation Steps
### 1. Synthetic Data & Pipeline Prep
- **Modify Configuration for Test**: 
  - Add `airline_b` as a `scraping_permitted=True` source in `scraper/config/sources.py` (temporarily enabled for synthetic test data).
  - Update `scraper/main.py` `ADAPTERS` to include a `MockAirlineBAdapter` that returns deterministic fares (different from `airline_a` to enable aggregation) if needed, or simply leverage `MockAirlineAAdapter` by making it configurable. Actually, it's easier to create a `MockAirlineXAdapter` and add it to `main.py` and `SOURCES`.
- **Synthetic Data Generation**: Create a script `scripts/prepare_test.py` that populates `fare_observations` with a mix of:
  - 2+ observations per route/window (for aggregation).
  - 1+ invalid/malformed observation to test `process_single_record()` rejection.

### 2. Pipeline Execution
- **Execute Stages**:
  - Run `scraper/main.py --once`.
  - Run `representative-fare-engine/service.py` to aggregate representative fares.
  - Run `index-engine/run_test.py` to calculate APIx.
  - Run `backend-api/app.py` (or exercise API endpoints using `httpx`).

### 3. Verification & Trace
- **Pipeline Verification**:
  - Use SQL tools/scripts to count records at each pipeline stage (Raw -> Cleaned -> Representative -> Index).
  - Run FastAPI ingestion tests/queries and verify expected APIx outputs.
- **Fail-Safe Tests**:
  - Verify invalid record was NOT inserted into `fare_observations` (queried from `job_audits` or database).
- **Security Regressions**:
  - Check `DATABASE_URL` sourcing and absence of hardcoded credentials.
- **Reporting**:
  - Produce the trace count report as requested.
  - Final report for the user.

## Critical Files
- `scraper/config/sources.py`
- `scraper/main.py`
- `scraper/db/models.py`
- `representative-fare-engine/service.py`
- `index-engine/run_test.py`
- `backend-api/app.py`

## Verification
- Running `run_all.sh` (or executing individual steps sequentially and recording outputs for the report).
- Validating counts against expected counts based on synthetic data generation.
- Checking `fare_observations` and `RepresentativeFares` for data normalization completeness.

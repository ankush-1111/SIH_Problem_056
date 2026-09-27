# Plan: Wiring cleaning-normalization into the ingestion pipeline

## Context
The goal is to ensure all data ingested into `fare_observations` table is normalized (airport codes, airline names, currency) and validated using the `cleaning-normalization` service before it is saved. Currently, validation is done via `scraper/core/validation.py` (which checks sanity), but full normalization/cleaning is missing.

## Recommended Approach
1. Modify `cleaning-normalization/service.py` to add a new function `process_single_record(record: dict) -> dict` that wraps `process_raw_data` to handle single records.
2. In `scraper/main.py`, update `run_job` to call this new `process_single_record` on the `quote.model_dump()` before calling `is_sane_fare` and saving.

## Critical Files
- `cleaning-normalization/service.py`: Add `process_single_record` function.
- `scraper/main.py`: Call `process_single_record` in `run_job`.

## Verification
- Run `scraper/main.py --once` with a mock source and verify if the data is normalized in the `fare_observations` table (e.g., check if 'NEW DELHI' was converted to 'DEL').
- Run `cleaning-normalization/test_service.py` to ensure existing functionality is not broken.

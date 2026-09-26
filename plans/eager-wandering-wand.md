# Task 1: Unify Database Schema

## Context
The current PostgreSQL setup defines two competing tables for fare observations: `fare_observations` (lowercase) and `FareObservations` (PascalCase), with a trigger on the former to populate the latter. This causes schema drift where the trigger-populated table misses ~9 critical fields, breaking downstream services that expect them. We must consolidate these into one authoritative schema.

## Dependency Map
fare source
→ insertion (via app/trigger)
→ fare_observations (the source of truth)
→ cleaning
→ representative fare (service.py)
→ index engine

## Proposed Approach
1. Redefine `FareObservations` (the PascalCase version, which seems to be the one consumers expect) to include ALL critical fields originally in `fare_observations`.
2. Update the application code (producers) to write directly into the unified table.
3. Remove the `fare_observations` table entirely and drop the trigger function `trg_ingest_fare_observation`.
4. Run necessary migrations/updates.

## Critical Files
- `database/init.sql` (schema definitions)
- `representative-fare-engine/service.py` (consumer)
- `scraper/aggregate.py` (consumer)
- Scraper ingestion logic (producers)

## Verification
- Initialize DB from new schema.
- Insert synthetic record with all fields.
- Verify read/write through the unified table.
- Run `representative-fare-engine` tests.

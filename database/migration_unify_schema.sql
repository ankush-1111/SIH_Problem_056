-- Add route_id and airline_id to fare_observations
ALTER TABLE fare_observations ADD COLUMN IF NOT EXISTS route_id INTEGER REFERENCES Routes(id);
ALTER TABLE fare_observations ADD COLUMN IF NOT EXISTS airline_id INTEGER REFERENCES Airlines(id);

-- Backfill route_id, airline_id from already populated FareObservations (which was populated by the trigger from fare_observations originally)
UPDATE fare_observations fo
SET route_id = fo2.route_id,
    airline_id = fo2.airline_id
FROM FareObservations fo2
WHERE fo.id = fo2.id; -- Wait, IDs might not match across both tables because trigger ingest might have different IDs?
-- NO, the FareObservations table in init.sql has id SERIAL PRIMARY KEY, so it will have its own IDs.
-- I need to link by the key that makes them unique: source, origin, destination, travel_date, advance_days.

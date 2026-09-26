-- Add route_id and airline_id to fare_observations
ALTER TABLE fare_observations ADD COLUMN IF NOT EXISTS route_id INTEGER REFERENCES Routes(id);
ALTER TABLE fare_observations ADD COLUMN IF NOT EXISTS airline_id INTEGER REFERENCES Airlines(id);

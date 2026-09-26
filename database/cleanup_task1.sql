-- Drop trigger and function associated with the obsolete table
DROP TRIGGER IF EXISTS trg_ingest_fare_observation ON fare_observations;
DROP FUNCTION IF EXISTS ingest_fare_observation();

-- Drop obsolete table
DROP TABLE IF EXISTS FareObservations;

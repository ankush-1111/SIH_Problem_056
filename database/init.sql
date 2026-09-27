-- Create Tables
CREATE TABLE IF NOT EXISTS Airlines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Routes (
    id SERIAL PRIMARY KEY,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    weight NUMERIC(10, 4),
    UNIQUE(origin, destination)
);

CREATE TABLE IF NOT EXISTS fare_observations (
    id SERIAL PRIMARY KEY,
    source VARCHAR(100) NOT NULL,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    travel_date DATE NOT NULL,
    observation_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    advance_days INTEGER NOT NULL,
    airline VARCHAR(255) NOT NULL,
    flight_number VARCHAR(50),
    fare_class VARCHAR(50) NOT NULL,
    cabin VARCHAR(50) NOT NULL,
    fare_family VARCHAR(50),
    stops INTEGER NOT NULL DEFAULT 0,
    departure_time VARCHAR(20),
    arrival_time VARCHAR(20),
    base_fare NUMERIC(12, 2) NOT NULL,
    taxes NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    other_charges NUMERIC(12, 2) NOT NULL DEFAULT 0.00,
    total_fare NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'INR',
    availability VARCHAR(50) NOT NULL DEFAULT 'available',
    search_profile VARCHAR(50) NOT NULL DEFAULT 'one_way_economy_1pax',
    route_id INTEGER REFERENCES Routes(id),
    airline_id INTEGER REFERENCES Airlines(id)
);

CREATE TABLE IF NOT EXISTS FareObservations (
    id SERIAL PRIMARY KEY,
    route_id INTEGER REFERENCES Routes(id),
    airline_id INTEGER REFERENCES Airlines(id),
    search_date DATE,
    travel_date DATE,
    booking_window INTEGER,
    base_fare NUMERIC(15, 2),
    tax NUMERIC(15, 2),
    udf NUMERIC(15, 2),
    conv_fee NUMERIC(15, 2),
    total_fare NUMERIC(15, 2),
    fare_class VARCHAR(50),
    source VARCHAR(100),
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS RepresentativeFares (
    id SERIAL PRIMARY KEY,
    route_id INTEGER REFERENCES Routes(id),
    booking_window INTEGER,
    date DATE,
    fare_class VARCHAR(50),
    median_fare NUMERIC(15, 2),
    observation_count INTEGER,
    calculation_method VARCHAR(50),
    status VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(route_id, date, booking_window, fare_class)
);

CREATE TABLE IF NOT EXISTS AirfareIndices (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    daily_index NUMERIC(15, 4),
    weekly_index NUMERIC(15, 4),
    monthly_index NUMERIC(15, 4)
);

CREATE TABLE IF NOT EXISTS BasePeriods (
    route_id INTEGER REFERENCES Routes(id),
    booking_window INTEGER,
    base_fare NUMERIC(15, 2),
    PRIMARY KEY (route_id, booking_window)
);

CREATE TABLE IF NOT EXISTS ExternalBenchmarks (
    id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    date DATE NOT NULL,
    benchmark_value NUMERIC(10, 4) NOT NULL,
    UNIQUE (source_name, date)
);

CREATE TABLE IF NOT EXISTS JobAudits (
    id SERIAL PRIMARY KEY,
    run_id VARCHAR(36) NOT NULL,
    source VARCHAR(100) NOT NULL,
    origin VARCHAR(3) NOT NULL,
    destination VARCHAR(3) NOT NULL,
    travel_date DATE NOT NULL,
    advance_days INTEGER NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    finished_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) NOT NULL,
    error_message TEXT
);


-- Trigger function to ingest data
CREATE OR REPLACE FUNCTION ingest_fare_observation()
RETURNS TRIGGER AS $$
DECLARE
    v_route_id INTEGER;
    v_airline_id INTEGER;
BEGIN
    -- Get or create route
    INSERT INTO Routes (origin, destination)
    VALUES (NEW.origin, NEW.destination)
    ON CONFLICT (origin, destination) DO UPDATE SET origin = EXCLUDED.origin
    RETURNING id INTO v_route_id;

    -- Get or create airline
    INSERT INTO Airlines (name)
    VALUES (NEW.airline)
    ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
    RETURNING id INTO v_airline_id;

    -- Insert into FareObservations
    INSERT INTO FareObservations (
        route_id,
        airline_id,
        search_date,
        travel_date,
        booking_window,
        base_fare,
        tax,
        total_fare,
        fare_class,
        source
    )
    VALUES (
        v_route_id,
        v_airline_id,
        NEW.observation_timestamp::DATE,
        NEW.travel_date,
        NEW.advance_days,
        NEW.base_fare,
        NEW.taxes,
        NEW.total_fare,
        NEW.fare_class,
        NEW.source
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_ingest_fare_observation ON fare_observations;
CREATE TRIGGER trg_ingest_fare_observation
AFTER INSERT ON fare_observations
FOR EACH ROW
EXECUTE FUNCTION ingest_fare_observation();


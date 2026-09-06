-- Create Tables
CREATE TABLE IF NOT EXISTS Airlines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS Routes (
    id SERIAL PRIMARY KEY,
    origin VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    weight NUMERIC(10, 4)
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
    median_fare NUMERIC(15, 2)
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

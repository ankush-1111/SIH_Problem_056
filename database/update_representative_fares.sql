DROP TABLE IF EXISTS RepresentativeFares;

CREATE TABLE RepresentativeFares (
    id SERIAL PRIMARY KEY,
    route_id INTEGER REFERENCES Routes(id),
    booking_window INTEGER,
    date DATE,
    fare_class VARCHAR(50),
    median_fare NUMERIC(15, 2),
    observation_count INTEGER,
    calculation_method VARCHAR(50),
    status VARCHAR(20),
    currency VARCHAR(10) DEFAULT 'INR',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT rep_fare_unique_grouping UNIQUE (route_id, date, booking_window, fare_class)
);
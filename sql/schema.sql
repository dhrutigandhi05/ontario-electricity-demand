CREATE TABLE IF NOT EXISTS demand_hourly (
    timestamp TIMESTAMP PRIMARY KEY,
    market_demand INTEGER NOT NULL,
    ontario_demand INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS weather_hourly (
    timestamp TIMESTAMP NOT NULL,
    station VARCHAR(50) NOT NULL,
    temperature DOUBLE PRECISION,

    PRIMARY KEY (timestamp, station)
);
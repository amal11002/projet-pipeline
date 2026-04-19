CREATE TABLE IF NOT EXISTS weather_processed (
    city VARCHAR(100),
    timestamp TIMESTAMP,
    avg_temp FLOAT,
    is_anomaly BOOLEAN
);
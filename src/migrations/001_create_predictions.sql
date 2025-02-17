-- Drop the table if it already exists
DROP TABLE IF EXISTS predictions;

-- Create the predictions table
CREATE TABLE predictions (
    id SERIAL PRIMARY KEY,
    company VARCHAR(255) NOT NULL,
    designation VARCHAR(255) NOT NULL,
    current_ctc FLOAT NOT NULL,
    total_yoe FLOAT NOT NULL,
    designation_yoe FLOAT NOT NULL,
    performance_rating VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
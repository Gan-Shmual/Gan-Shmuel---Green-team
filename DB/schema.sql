DROP DATABASE IF EXISTS weight;

-- Create the database
CREATE DATABASE weight;

-- Switch to the new database
USE weight;

-- Table to store registered containers and their tara weight
CREATE TABLE containers (
    id VARCHAR(255) PRIMARY KEY,
    weight_kg INT,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Create the table with the CORRECT column names
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    datetime DATETIME,
    direction VARCHAR(10),
    truck_id VARCHAR(50),       -- Python calls this 'truck_id', not 'truck'
    containers VARCHAR(255),    -- This was the missing column causing the error!
    bruto_kg INT,              -- Python calls this 'bruto_kg'
    truck_tara_kg INT,         -- Python calls this 'truck_tara_kg'
    neto_kg INT,               -- Python calls this 'neto_kg'
    produce VARCHAR(50),
    session_id INT
);


-- A linking table to handle the many-to-many relationship
-- between transactions and containers. This is more robust
-- than a comma-separated list.
CREATE TABLE transaction_containers (
    transaction_id INT,
    container_id VARCHAR(255),
    PRIMARY KEY (transaction_id, container_id),
    FOREIGN KEY (transaction_id) REFERENCES transactions(id),
    FOREIGN KEY (container_id) REFERENCES containers(id)
);

-- Insert Data (Updated to match the new column names)
INSERT INTO transactions (datetime, direction, truck_id, containers, bruto_kg, truck_tara_kg, neto_kg, produce, session_id) 
VALUES ('2025-11-21 08:30:00', 'in', '77-123-45', 'CNT-101', 15000, 5000, 10000, 'Oranges', 1001);

INSERT INTO transactions (datetime, direction, truck_id, containers, bruto_kg, truck_tara_kg, neto_kg, produce, session_id) 
VALUES ('2025-11-21 10:15:00', 'out', '77-123-45', 'CNT-101', 5000, 5000, 0, 'na', 1001);

INSERT INTO transactions (datetime, direction, truck_id, containers, bruto_kg, truck_tara_kg, neto_kg, produce, session_id) 
VALUES ('2025-11-21 12:00:00', 'in', '88-999-00', 'CNT-202', 30000, 12000, 18000, 'Tomatoes', 1002);
-- Drop the database if it exists to start fresh during development
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

-- Table to store individual weighing transactions
CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL,
    datetime DATETIME NOT NULL,
    direction VARCHAR(10) NOT NULL, -- 'in', 'out', 'none'
    truck_id VARCHAR(50), -- Can be NULL if not a truck
    bruto_kg INT NOT NULL,
    truck_tara_kg INT,
    neto_kg INT, -- Can be NULL if container tara is unknown
    produce VARCHAR(50),
    -- Indexing for faster lookups by session_id
    INDEX (session_id)
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
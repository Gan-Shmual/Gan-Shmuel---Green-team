DROP DATABASE IF EXISTS weight;

-- Create the database
CREATE DATABASE weight;

-- Switch to the new database
USE weight;

-- Table to store registered containers and their tara weight
CREATE TABLE IF NOT EXISTS `containers_registered` (
  `container_id` varchar(15) NOT NULL,
  `weight` int(12) DEFAULT NULL,
  `unit` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`container_id`)
) ENGINE=MyISAM AUTO_INCREMENT=10001 ;

-- Create the table with the CORRECT column names
CREATE TABLE IF NOT EXISTS `transactions` (
  `id` int(12) NOT NULL AUTO_INCREMENT,
  `datetime` datetime DEFAULT NULL,
  `direction` varchar(10) DEFAULT NULL,
  `truck` varchar(50) DEFAULT NULL,
  `containers` varchar(10000) DEFAULT NULL,
  `bruto` int(12) DEFAULT NULL,
  `truckTara` int(12) DEFAULT NULL,
  --   "neto": <int> or "na" // na if some of containers unknown
  `neto` int(12) DEFAULT NULL,
  `produce` varchar(50) DEFAULT NULL,
  `session_id` INT(12) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=10001 ;




-- Insert Data (Updated to match the new column names)
INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce, session_id) 
VALUES ('2025-11-21 08:30:00', 'in', '77-123-45', 'CNT-101', 15000, 5000, 10000, 'Oranges', 1001);

INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce, session_id) 
VALUES ('2025-11-21 10:15:00', 'out', '77-123-45', 'CNT-101', 5000, 5000, 0, 'na', 1001);

INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce, session_id) 
VALUES ('2025-11-21 12:00:00', 'in', '88-999-00', 'CNT-202', 30000, 12000, 18000, 'Tomatoes', 1002);

INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce, session_id) 
VALUES (NOW(), 'in', 'T-123', 'CNT-100', 15000, 5000, 10000, 'Oranges', 1003);

INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce, session_id) 
VALUES (NOW(), 'out', 'T-123', 'CNT-100', 5000, 5000, 0, 'na', 1003);

INSERT INTO transactions (datetime, direction, truck, containers, bruto, truckTara, neto, produce, session_id) 
VALUES (NOW(), 'in', 'T-999', 'CNT-555''CNT-101', 30000, 12000, 18000, 'Tomatoes', 1004);


INSERT INTO `containers_registered` (`container_id`, `weight`, `unit`) VALUES
('CNT-100', 500, 'kg'),
('CNT-101', 600, 'kg'),
('CNT-202', 600, 'kg'),
('CNT-555', 450, 'kg');

CREATE DATABASE citypulse;

USE citypulse;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    age INT,
    gender VARCHAR(10)
);
ALTER TABLE users 
ADD COLUMN password VARCHAR(255) NOT NULL;

CREATE TABLE civic_issues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,

    category VARCHAR(50) NOT NULL,       -- civic / water / electricity / transport / animal
    issue_type VARCHAR(100) NOT NULL,    -- Road Damage / Power Cut / Garbage

    description TEXT,
    image VARCHAR(255),

    lat VARCHAR(50),
    lon VARCHAR(50),
    manual_location VARCHAR(255),        -- 🔥 USER CAN TYPE LOCATION

    assigned_admin INT,
    status VARCHAR(20) DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



CREATE TABLE emergencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    emergency_type VARCHAR(50),
    lat DOUBLE,
    lon DOUBLE,
    manual_location VARCHAR(255),
    status VARCHAR(20) DEFAULT 'SUBMITTED',
    assigned_admin INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE emergencies
ADD COLUMN image VARCHAR(255) DEFAULT NULL;


CREATE TABLE women_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    lat DECIMAL(10,8),
    lon DECIMAL(11,8),
    status VARCHAR(20) DEFAULT 'SOS',
    assigned_police INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
;



CREATE TABLE admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    lat DECIMAL(10,6),
    lon DECIMAL(10,6)
);

INSERT INTO admins(name, role, phone, password, lat, lon) VALUES 
('Municipal Admin','Municipal','1234567890','municipal123',18.5204,73.8567),
('Police Admin','Police','1234567891','police123',18.5204,73.8567),
('Ambulance Admin','Ambulance','1234567892','ambulance123',18.5204,73.8567),
('Fire Admin','Fire','1234567893','fire123',18.5204,73.8567);


CREATE TABLE admin_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT,
    type VARCHAR(50), -- 'Civic', 'Emergency', 'Alert'
    reference_id INT, -- ID from civic_issues, emergencies, women_alerts
    is_new BOOLEAN DEFAULT TRUE
);

ALTER TABLE civic_issues ADD COLUMN department VARCHAR(50);







CREATE TABLE live_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    lat VARCHAR(50),
    lon VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


SELECT ci.id, ci.image, ci.lat, ci.lon, ci.user_id,
       u.name, u.phone
FROM civic_issues ci
JOIN users u ON ci.user_id = u.id
WHERE ci.id = 1;



CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_type VARCHAR(20),   -- civic | emergency | women
    request_id INT,
    sender VARCHAR(10),         -- user | admin
    sender_id INT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE civic_issues ADD status VARCHAR(20) DEFAULT 'SUBMITTED';
ALTER TABLE emergencies ADD status VARCHAR(20) DEFAULT 'SUBMITTED';





ALTER TABLE women_alerts ADD status VARCHAR(20) DEFAULT 'SOS';

------=====================================================================================================================





-- Create Database
CREATE DATABASE IF NOT EXISTS citypulse;
USE citypulse;

-- USERS TABLE
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    age INT,
    gender VARCHAR(10),
    password VARCHAR(255) NOT NULL
);

-- CIVIC ISSUES TABLE
CREATE TABLE IF NOT EXISTS civic_issues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    category VARCHAR(50) NOT NULL,       -- civic / water / electricity / transport / animal
    issue_type VARCHAR(100) NOT NULL,    -- Road Damage / Power Cut / Garbage
    description TEXT,
    image VARCHAR(255),
    lat VARCHAR(50),
    lon VARCHAR(50),
    manual_location VARCHAR(255),
    assigned_admin INT,
    department VARCHAR(50),
    status VARCHAR(20) DEFAULT 'SUBMITTED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- EMERGENCIES TABLE
CREATE TABLE IF NOT EXISTS emergencies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    emergency_type VARCHAR(50),          -- Medical / Fire
    lat DOUBLE,
    lon DOUBLE,
    manual_location VARCHAR(255),
    image VARCHAR(255),
    assigned_admin INT,
    status VARCHAR(20) DEFAULT 'SUBMITTED',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- WOMEN ALERTS TABLE
CREATE TABLE IF NOT EXISTS women_alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    lat DECIMAL(10,8),
    lon DECIMAL(11,8),
    status VARCHAR(20) DEFAULT 'SOS',
    assigned_police INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- ADMINS TABLE
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    role VARCHAR(50) NOT NULL,           -- Municipal / Police / Ambulance / Fire
    phone VARCHAR(20) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    lat DECIMAL(10,6),
    lon DECIMAL(10,6)
);

-- Sample Admins
INSERT INTO admins(name, role, phone, password, lat, lon) VALUES 
('Municipal Admin','Municipal','1234567890','municipal123',18.5204,73.8567),
('Police Admin','Police','1234567891','police123',18.5204,73.8567),
('Ambulance Admin','Ambulance','1234567892','ambulance123',18.5204,73.8567),
('Fire Admin','Fire','1234567893','fire123',18.5204,73.8567);

-- ADMIN NOTIFICATIONS TABLE
CREATE TABLE IF NOT EXISTS admin_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    admin_id INT,
    type VARCHAR(50),       -- 'Civic', 'Emergency', 'Alert'
    reference_id INT,       -- ID from civic_issues, emergencies, women_alerts
    is_new BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (admin_id) REFERENCES admins(id) ON DELETE CASCADE
);

-- LIVE LOCATIONS TABLE
CREATE TABLE IF NOT EXISTS live_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    lat VARCHAR(50),
    lon VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- CHAT MESSAGES TABLE
CREATE TABLE chat_messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_type VARCHAR(20),
    request_id INT,
    sender VARCHAR(20),
    sender_id INT,
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE chat_messages 
MODIFY created_at DATETIME DEFAULT CURRENT_TIMESTAMP;


-- Example Query for Civic Issue with User Info
SELECT ci.id, ci.image, ci.lat, ci.lon, ci.user_id,
       u.name, u.phone
FROM civic_issues ci
JOIN users u ON ci.user_id = u.id
WHERE ci.id = 1;
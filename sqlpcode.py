-- 1. Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS CMMS;
USE CMMS; -- Switch to the CMMS database

-- 2. Create core tables (matches ER diagram and attribute requirements, with foreign key constraints)
-- Chemical table (CHEMICAL: Chem_id, Name, Type, isHarmful)
CREATE TABLE IF NOT EXISTS CHEMICAL (
    Chem_id INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(50) NOT NULL,
    Type VARCHAR(30) NOT NULL,
    isHarmful BOOLEAN NOT NULL DEFAULT FALSE,
    UNIQUE KEY uk_chem_name (Name) -- Prevent duplicate chemical names
);

-- External company table (EXTERNAL_COMPANY)
CREATE TABLE IF NOT EXISTS EXTERNAL_COMPANY (
    CompanyID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(50) NOT NULL,
    ContactID VARCHAR(20),
    ContactPhone VARCHAR(15),
    UNIQUE KEY uk_company_name (Name)
);

-- Executive officer table (EXECUTIVE_OFFICER)
CREATE TABLE IF NOT EXISTS EXECUTIVE_OFFICER (
    OfficerID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(50) NOT NULL,
    Sex ENUM('Male', 'Female', 'Other'),
    Position VARCHAR(30),
    HireDate DATE
);

-- Manager table (MANAGER: 1-to-1 with Executive Officer, has worker limit)
CREATE TABLE IF NOT EXISTS MANAGER (
    ManagerID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(50) NOT NULL,
    Sex ENUM('Male', 'Female', 'Other'),
    OfficerID INT UNIQUE, -- 1-to-1 relation, ensure uniqueness
    MaxWorkers INT DEFAULT 20, -- Maximum number of workers allowed
    FOREIGN KEY (OfficerID) REFERENCES EXECUTIVE_OFFICER(OfficerID)
);

-- Worker table (WORKER: 1-to-N with Manager)
CREATE TABLE IF NOT EXISTS WORKER (
    WorkerID INT PRIMARY KEY AUTO_INCREMENT,
    Name VARCHAR(50) NOT NULL,
    Sex ENUM('Male', 'Female', 'Other'),
    ManagerID INT,
    HireDate DATE,
    FOREIGN KEY (ManagerID) REFERENCES MANAGER(ManagerID)
);

-- Campus area table (CAMPUS_AREA)
CREATE TABLE IF NOT EXISTS CAMPUS_AREA (
    AreaID INT PRIMARY KEY AUTO_INCREMENT,
    Location VARCHAR(100) NOT NULL UNIQUE, -- e.g., "East Campus", "West Campus"
    Description VARCHAR(200)
);

-- Building table (BUILDING: 1-to-N with Area, supervised by Manager)
CREATE TABLE IF NOT EXISTS BUILDING (
    BuildingID INT PRIMARY KEY AUTO_INCREMENT,
    AreaID INT,
    BuildingName VARCHAR(50) NOT NULL UNIQUE, -- e.g., "Lab Building A"
    Floors INT, -- Number of floors in the building
    ManagerID INT, -- Manager in charge
    FOREIGN KEY (AreaID) REFERENCES CAMPUS_AREA(AreaID),
    FOREIGN KEY (ManagerID) REFERENCES MANAGER(ManagerID)
);

-- Activity table (ACTIVITY: includes Weather_related, aging_repair, Cleaning)
CREATE TABLE IF NOT EXISTS ACTIVITY (
    Act_id INT PRIMARY KEY AUTO_INCREMENT,
    ActivityName VARCHAR(100) NOT NULL,
    Weather_related BOOLEAN DEFAULT FALSE, -- Weather-related activities
    aging_repair BOOLEAN DEFAULT FALSE,    -- Aging repair activities
    Cleaning BOOLEAN DEFAULT FALSE,         -- Cleaning activities
    StartTime DATETIME NOT NULL,
    EndTime DATETIME NOT NULL,
    IsUnavailable BOOLEAN DEFAULT FALSE,    -- Whether the area is unavailable
    Progress ENUM('Pending', 'In Progress', 'Completed') DEFAULT 'Pending', -- Activity progress (added)
    CompanyID INT, -- Outsourced company (optional)
    ManagerID INT, -- Manager in charge
    FOREIGN KEY (CompanyID) REFERENCES EXTERNAL_COMPANY(CompanyID),
    FOREIGN KEY (ManagerID) REFERENCES MANAGER(ManagerID)
);

-- Junction table for Activity-Chemical (M-to-N relation)
CREATE TABLE IF NOT EXISTS ACTIVITY_CHEMICAL (
    Act_id INT,
    Chem_id INT,
    UsageAmount VARCHAR(20) NOT NULL, -- Amount of chemical used (e.g., "5L", "10kg")
    PRIMARY KEY (Act_id, Chem_id),
    FOREIGN KEY (Act_id) REFERENCES ACTIVITY(Act_id),
    FOREIGN KEY (Chem_id) REFERENCES CHEMICAL(Chem_id)
);

-- Junction table for Activity-Worker (M-to-N relation)
CREATE TABLE IF NOT EXISTS ACTIVITY_WORKER (
    Act_id INT,
    WorkerID INT,
    PRIMARY KEY (Act_id, WorkerID),
    FOREIGN KEY (Act_id) REFERENCES ACTIVITY(Act_id),
    FOREIGN KEY (WorkerID) REFERENCES WORKER(WorkerID)
);

-- Admin table (for login authentication)
CREATE TABLE IF NOT EXISTS ADMIN (
    AdminID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(30) NOT NULL UNIQUE,
    Password VARCHAR(64) NOT NULL -- Reserved for encryption (used in advanced features later)
);

-- Insert default admin (username: admin, password: admin123; can be encrypted later)
INSERT IGNORE INTO ADMIN (Username, Password) VALUES ('admin', 'admin123');
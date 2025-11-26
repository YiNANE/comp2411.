-- 1. Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS CMMS;
USE CMMS; -- Switch to the CMMS database

-- 2. Create core tables (matches ER diagram and attribute requirements, with foreign key constraints)
-- Chemical table (CHEMICAL: Chem_id, Name, Type, isHarmful)
CREATE TABLE IF NOT EXISTS CHEMICAL (
    Chem_id INT PRIMARY KEY AUTO_INCREMENT,
	Name VARCHAR(50) NOT NULL,
	isHarmful BOOLEAN NOT NULL DEFAULT FALSE,
	UNIQUE KEY uk_chem_id (Chem_id)
);

-- Executive officer table (EXECUTIVE_OFFICER)
CREATE TABLE IF NOT EXISTS EXECUTIVE_OFFICER (
	OSsn INT PRIMARY KEY AUTO_INCREMENT,
	Name VARCHAR(50) NOT NULL,
	Sex ENUM('Male', 'Female'),
	MaxManagers INT DEFAULT 5  # Limit of managers
);

-- Manager table (MANAGER: 1-to-1 with Executive Officer, has worker limit)
CREATE TABLE IF NOT EXISTS MANAGER (
    MSsn INT PRIMARY KEY AUTO_INCREMENT,
	Name VARCHAR(50) NOT NULL,
	Sex ENUM('Male', 'Female'),
	OSsn INT UNIQUE,
	MaxWorkers INT DEFAULT 20,  # Limit of workers
	FOREIGN KEY (OSsn) REFERENCES EXECUTIVE_OFFICER(OSsn)
);

-- Worker table (WORKER: 1-to-N with Manager)
CREATE TABLE IF NOT EXISTS WORKER (
    WSsn INT PRIMARY KEY AUTO_INCREMENT,
	Name VARCHAR(50) NOT NULL,
	Sex ENUM('Male', 'Female'),
	MSsn INT,
	FOREIGN KEY (MSsn) REFERENCES MANAGER(MSsn)
);

-- External company table (EXTERNAL_COMPANY)
CREATE TABLE IF NOT EXISTS EXTERNAL_COMPANY (
    Com_ID INT PRIMARY KEY AUTO_INCREMENT,
	Name VARCHAR(50) NOT NULL,
	MSsn INT,
	UNIQUE KEY uk_company_id (Com_ID),
	FOREIGN KEY (MSsn) REFERENCES MANAGER(MSsn)
);

-- Campus area table (CAMPUS_AREA)
CREATE TABLE IF NOT EXISTS CAMPUS_AREA (
    Area_id INT PRIMARY KEY AUTO_INCREMENT,
	Location VARCHAR(100) NOT NULL UNIQUE
);

-- Gate table (GATE)
CREATE TABLE IF NOT EXISTS GATE (
	GNo INT PRIMARY KEY AUTO_INCREMENT,
	Area_id INT,
	FOREIGN KEY (Area_id) REFERENCES CAMPUS_AREA(Area_id)
);

-- Square table (SQUARE)
CREATE TABLE IF NOT EXISTS SQUARE (
	SNo INT PRIMARY KEY AUTO_INCREMENT,
	Area_id INT,
	FOREIGN KEY (Area_id) REFERENCES CAMPUS_AREA(Area_id)
);

-- Building table (BUILDING: 1-to-N with Area, supervised by Manager)
CREATE TABLE IF NOT EXISTS BUILDING (
    BNo INT PRIMARY KEY AUTO_INCREMENT,
	Area_id INT,
	MSsn INT,
	FOREIGN KEY (Area_id) REFERENCES CAMPUS_AREA(Area_id),
	FOREIGN KEY (MSsn) REFERENCES MANAGER(MSsn)
);

-- Level table (LEVEL)
CREATE TABLE IF NOT EXISTS LEVEL (
	LNo INT PRIMARY KEY AUTO_INCREMENT,
	BNo INT,
	FOREIGN KEY (BNo) REFERENCES BUILDING(BNo),
	UNIQUE KEY uk_building_level (BNo, LNo)
);

-- Room table (ROOM)
CREATE TABLE IF NOT EXISTS ROOM (
	RNo INT PRIMARY KEY AUTO_INCREMENT,
	LNo INT,
	BNo INT,
	IsAvailable BOOLEAN DEFAULT TRUE,
	FOREIGN KEY (LNo) REFERENCES LEVEL(LNo),
	FOREIGN KEY (BNo) REFERENCES LEVEL(BNo),
	UNIQUE KEY uk_level_room (RNo, LNo, BNo)
);

-- Corridor table (CORRIDOR)
CREATE TABLE IF NOT EXISTS CORRIDOR (
	CNo INT PRIMARY KEY AUTO_INCREMENT,
	LNo INT,
	BNo INT,
	FOREIGN KEY (LNo) REFERENCES LEVEL(LNo),
	UNIQUE KEY uk_level_corridor (CNo, LNO, BNO)
);

-- Activity table (ACTIVITY: includes Weather_related, aging_repair, Cleaning)
CREATE TABLE IF NOT EXISTS ACTIVITY (
    Act_id INT PRIMARY KEY AUTO_INCREMENT,
	Tools VARCHAR(100),
	Description TEXT,
	Weather_related BOOLEAN DEFAULT FALSE,
	Aging_repair BOOLEAN DEFAULT FALSE,
	Cleaning BOOLEAN DEFAULT FALSE,
	StartTime DATETIME NOT NULL,
	EndTime DATETIME NOT NULL,
	IsUnusable BOOLEAN DEFAULT FALSE,
	Com_id INT,  # Relate to External Company (outsourced activities)
	FOREIGN KEY (Com_id) REFERENCES EXTERNAL_COMPANY(Com_id)
);

-- Junction table for Activity-Chemical (M-to-N relation)
CREATE TABLE IF NOT EXISTS ACTIVITY_CHEMICAL (
    Act_id INT,
    Chem_id INT,
    PRIMARY KEY (Act_id, Chem_id),
    FOREIGN KEY (Act_id) REFERENCES ACTIVITY(Act_id),
    FOREIGN KEY (Chem_id) REFERENCES CHEMICAL(Chem_id)
);

-- Exists table (EXISTS)
CREATE TABLE IF NOT EXISTS ACTIVITY_AREA (
	Act_id INT,
	Area_id INT,
	PRIMARY KEY (Act_id, Area_id),
	FOREIGN KEY (Act_id) REFERENCES ACTIVITY(Act_id),
	FOREIGN KEY (Area_id) REFERENCES CAMPUS_AREA(Area_id)
);

-- Junction table for Activity-Worker (M-to-N relation)
CREATE TABLE IF NOT EXISTS ACTIVITY_WORKER (
    Act_id INT,
	WSsn INT,
	PRIMARY KEY (Act_id, WSsn),
	FOREIGN KEY (Act_id) REFERENCES ACTIVITY(Act_id),
	FOREIGN KEY (WSsn) REFERENCES WORKER(WSsn)
);

-- Admin table (for login authentication)
CREATE TABLE IF NOT EXISTS ADMIN (
    AdminID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(30) NOT NULL UNIQUE,
    Password VARCHAR(64) NOT NULL -- Reserved for encryption (used in advanced features later)
);

-- Insert default admin (username: admin, password: admin123; can be encrypted later)
INSERT IGNORE INTO ADMIN (Username, Password) VALUES ('admin', 'admin123');
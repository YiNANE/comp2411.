-- =========================================================
-- CMMS Data Seeding Script
-- Extracted from original test.sql (insertion part only)
-- Run AFTER cmms_schema.sql
-- =========================================================

USE CMMS;

-- Insert Executive Officers
INSERT INTO EXECUTIVE_OFFICER (OSsn, Name, Sex, MaxManagers) VALUES 
(1001, 'Zhang Wei', 'Male', 5),
(1002, 'Li Fang', 'Female', 6);

-- Insert Managers (1:1 relationship with Executive Officers)
INSERT INTO MANAGER (MSsn, Name, Sex, OSsn, MaxWorkers) VALUES 
(2001, 'Wang Ming', 'Male', 1001, 20),
(2002, 'Liu Hong', 'Female', 1002, 15);

-- Insert Workers (1:N relationship with Managers)
INSERT INTO WORKER (WSsn, Name, Sex, MSsn) VALUES 
(3001, 'Chen Qiang', 'Male', 2001),
(3002, 'Yang Li', 'Female', 2001),
(3003, 'Zhao Gang', 'Male', 2002);

-- Insert External Companies
INSERT INTO EXTERNAL_COMPANY (Com_ID, Name, MSsn) VALUES 
(4001, 'Cleaning Service Co.', 2001),
(4002, 'Maintenance Engineering Co.', 2002);

-- Insert Campus Areas
INSERT INTO CAMPUS_AREA (Area_id, Location) VALUES 
(1, 'North Campus'),
(2, 'South Campus'),
(3, 'Central Square');

-- Insert Gates (1:N relationship with Areas)
INSERT INTO GATE (GNo, Area_id) VALUES 
(1, 1), (2, 1), (3, 2);

-- Insert Squares (1:N relationship with Areas)
INSERT INTO SQUARE (SNo, Area_id) VALUES 
(1, 3), (2, 3);

-- Insert Buildings (1:N relationship with Areas and Managers)
INSERT INTO BUILDING (BNo, Area_id, MSsn) VALUES 
(1, 1, 2001),  -- Building 1 in North Campus managed by Wang Ming
(2, 1, 2001),  -- Building 2 in North Campus managed by Wang Ming
(3, 2, 2002);  -- Building 3 in South Campus managed by Liu Hong

-- Insert Levels (1:N relationship with Buildings)
INSERT INTO LEVEL (LNo, BNo) VALUES 
(1, 1), (2, 1), (3, 1),  -- Building 1 has 3 levels
(1, 2), (2, 2),          -- Building 2 has 2 levels
(1, 3);                  -- Building 3 has 1 level

-- Insert Rooms (1:N relationship with Levels)
INSERT INTO ROOM (RNo, LNo, BNo, IsAvailable) VALUES 
(101, 1, 1, TRUE), (102, 1, 1, TRUE),
(201, 2, 1, FALSE),  -- Unavailable room
(301, 3, 1, TRUE);

-- Insert Corridors (1:N relationship with Levels)
INSERT INTO CORRIDOR (CNo, LNo, BNo) VALUES 
(1, 1, 1), (2, 2, 1), (3, 1, 2);

-- Insert Chemicals
INSERT INTO CHEMICAL (Chem_id, Name, isHarmful) VALUES 
(5001, 'Disinfectant', FALSE),
(5002, 'Hydrochloric Acid', TRUE),      -- Harmful chemical
(5003, 'Cleaning Agent', FALSE),
(5004, 'Paint Thinner', TRUE);          -- Harmful chemical

-- Insert Activities (1:N relationship with External Companies)
INSERT INTO ACTIVITY (Act_id, Tools, Description, Weather_related, Aging_repair, Cleaning, StartTime, EndTime, IsUnusable, Com_id) VALUES 
(6001, 'Broom, Mop', 'Routine Cleaning', FALSE, FALSE, TRUE, '2025-11-01 09:00:00', '2025-11-01 12:00:00', FALSE, 4001),
(6002, 'Wrench, Screwdriver', 'Window Repair', FALSE, TRUE, FALSE, '2025-11-02 14:00:00', '2025-11-02 17:00:00', TRUE, 4002),  -- Area unusable
(6003, 'Water Pipe, Pump', 'Rainwater Cleanup', TRUE, FALSE, TRUE, '2025-11-03 10:00:00', '2025-11-03 15:00:00', FALSE, NULL),   -- Internal activity
(6004, 'Brush, Paint', 'Wall Refurbishment', FALSE, TRUE, FALSE, '2025-11-04 08:00:00', '2025-11-04 16:00:00', FALSE, 4002);

-- Activity-Chemical Relationships (M:N)
INSERT INTO ACTIVITY_CHEMICAL (Act_id, Chem_id) VALUES 
(6001, 5001), (6001, 5003),  -- Cleaning activity uses Disinfectant and Cleaning Agent
(6002, 5002),                -- Repair activity uses Hydrochloric Acid
(6004, 5004);                -- Refurbishment activity uses Paint Thinner

-- Activity-Area Relationships (M:N)
INSERT INTO ACTIVITY_AREA (Act_id, Area_id) VALUES 
(6001, 1),  -- Cleaning activity in North Campus
(6002, 1),  -- Repair activity in North Campus
(6003, 2),  -- Rainwater cleanup in South Campus
(6004, 3);  -- Wall refurbishment in Central Square

-- Activity-Worker Relationships (M:N)
INSERT INTO ACTIVITY_WORKER (Act_id, WSsn) VALUES 
(6001, 3001), (6001, 3002),  -- Cleaning activity has 2 workers
(6002, 3001),                -- Repair activity has 1 worker
(6003, 3003),                -- Rainwater cleanup has 1 worker
(6004, 3002), (6004, 3003);  -- Refurbishment activity has 2 workers



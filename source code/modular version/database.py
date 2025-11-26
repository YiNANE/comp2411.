"""
Database Connection and Table Creation Module
Responsible for database connection, table creation and other database initialization work
"""
import pymysql
from pymysql.err import OperationalError
from config import DB_CONFIG


class DatabaseManager:
    """Database manager, responsible for connection and table creation"""
    
    def __init__(self, host=None, user=None, password=None, db=None, port=None, charset=None):
        """Initialize database connection parameters"""
        self.host = host or DB_CONFIG['host']
        self.user = user or DB_CONFIG['user']
        self.password = password or DB_CONFIG['password']
        self.db = db or DB_CONFIG['db']
        self.port = port or DB_CONFIG['port']
        self.charset = charset or DB_CONFIG['charset']
        self.conn = None
        self.cursor = None

    def connect(self):
        """Establish database connection, create database if it doesn't exist"""
        try:
            # Connect to MySQL server first (without specifying database)
            temp_conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                charset=self.charset
            )
            temp_cursor = temp_conn.cursor()
            # Create database if not exists
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.db}")
            temp_conn.close()

            # Connect to target database
            self.conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                db=self.db,
                port=self.port,
                charset=self.charset,
                cursorclass=pymysql.cursors.DictCursor
            )
            self.cursor = self.conn.cursor()
            print("Database connection successful.")
        except OperationalError as e:
            print(f"Database connection failed: {e}")
            raise

    def create_tables(self):
        # Create all required tables for CMMS (based on ER diagram and attribute requirements)
        create_table_sqls = [
            # 1. Chemical Reagent Table (CHEMICAL) - Attributes: Chem_id, Name, isHarmful
            """
            CREATE TABLE IF NOT EXISTS CHEMICAL (
                Chem_id INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(50) NOT NULL,
                isHarmful BOOLEAN NOT NULL DEFAULT FALSE,
                UNIQUE KEY uk_chem_id (Chem_id)
            );
            """,
            # 2. Executive Officer Table (EXECUTIVE_OFFICER) - Attributes: OSsn, Name, Sex
            """
            CREATE TABLE IF NOT EXISTS EXECUTIVE_OFFICER (
                OSsn INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(50) NOT NULL,
                Sex ENUM('Male', 'Female'),
                MaxManagers INT DEFAULT 5  # Manager limit
            );
            """,
            # 3. Manager Table (MANAGER) - Attributes: MSsn, Name, Sex, ESsn, 1:1 relation with Executive Officer, 1:N manage Workers
            """
            CREATE TABLE IF NOT EXISTS MANAGER (
                MSsn INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(50) NOT NULL,
                Sex ENUM('Male', 'Female'),
                OSsn INT UNIQUE,
                MaxWorkers INT DEFAULT 20,  # Worker limit
                FOREIGN KEY (OSsn) REFERENCES EXECUTIVE_OFFICER(OSsn)
            );
            """,
            # 4. Worker Table (WORKER) - Attributes: WSsn, Name, Sex, MSsn, 1:1 relation with Manager
            """
            CREATE TABLE IF NOT EXISTS WORKER (
                WSsn INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(50) NOT NULL,
                Sex ENUM('Male', 'Female'),
                MSsn INT,
                FOREIGN KEY (MSsn) REFERENCES MANAGER(MSsn)
            );
            """,
            # 5. External Company Table (EXTERNAL_COMPANY) - Attributes: Com_id, Name, MSsn
            """
            CREATE TABLE IF NOT EXISTS EXTERNAL_COMPANY (
                Com_ID INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(50) NOT NULL,
                MSsn INT,
                UNIQUE KEY uk_company_id (Com_ID),
                FOREIGN KEY (MSsn) REFERENCES MANAGER(MSsn)
            );
            """,
            # 6. Campus Area Table (CAMPUS_AREA) - Attributes: Area_id, Location
            """
            CREATE TABLE IF NOT EXISTS CAMPUS_AREA (
                Area_id INT PRIMARY KEY AUTO_INCREMENT,
                Location VARCHAR(100) NOT NULL UNIQUE
            );
            """,
            # 7. Gate Table (GATE) - Attributes: Area_id, GNo, 1:N relation with Campus Area
            """
            CREATE TABLE IF NOT EXISTS GATE (
                GNo INT PRIMARY KEY AUTO_INCREMENT,
                Area_id INT,
                FOREIGN KEY (Area_id) REFERENCES CAMPUS_AREA(Area_id)
            );
            """,
            # 8. Square Table (SQUARE) - Attributes: Area_id, BNo, 1:N relation with Campus Area
            """
            CREATE TABLE IF NOT EXISTS SQUARE (
                SNo INT PRIMARY KEY AUTO_INCREMENT,
                Area_id INT,
                FOREIGN KEY (Area_id) REFERENCES CAMPUS_AREA(Area_id)
            );
            """,
            # 9. Building Table (BUILDING) - Attributes: Area_id, BNo, MSsn, 1:N relation with Campus Area, managed by Manager
            """
            CREATE TABLE IF NOT EXISTS BUILDING (
                BNo INT PRIMARY KEY AUTO_INCREMENT,
                Area_id INT,
                MSsn INT,
                FOREIGN KEY (Area_id) REFERENCES CAMPUS_AREA(Area_id),
                FOREIGN KEY (MSsn) REFERENCES MANAGER(MSsn)
            );
            """,
            # 10. Level Table (LEVEL) - Attributes: LNo, BNo, 1:N relation with Building
            """
            CREATE TABLE IF NOT EXISTS LEVEL (
                LNo INT PRIMARY KEY AUTO_INCREMENT,
                BNo INT,
                FOREIGN KEY (BNo) REFERENCES BUILDING(BNo),
                UNIQUE KEY uk_building_level (BNo, LNo)
            );
            """,
            # 11. Room Table (ROOM) - Attributes: RNo, LNo, BNo, 1:N relation with Level
            """
            CREATE TABLE IF NOT EXISTS ROOM (
                RNo INT PRIMARY KEY AUTO_INCREMENT,
                LNo INT,
                BNo INT,
                IsAvailable BOOLEAN DEFAULT TRUE,
                FOREIGN KEY (LNo) REFERENCES LEVEL(LNo),
                FOREIGN KEY (BNo) REFERENCES LEVEL(BNo),
                UNIQUE KEY uk_level_room (RNo, LNo, BNo)
            );
            """,
            # 12. Corridor Table (CORRIDOR) - Attributes: CNo, LNo, BNo, 1:N relation with Level
            """
            CREATE TABLE IF NOT EXISTS CORRIDOR (
                CNo INT PRIMARY KEY AUTO_INCREMENT,
                LNo INT,
                BNo INT,
                FOREIGN KEY (LNo) REFERENCES LEVEL(LNo),
                UNIQUE KEY uk_level_corridor (CNo, LNO, BNO)
            );
            """,
            # 13. Activity Table (ACTIVITY) - Attributes: Act_id, Tools, Time, Com_id, Description, Weather_related, Aging_repair, Cleaning
            """
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
            """,
            # 14. Activity-Chemical Intermediate Table (M:N relation)
            """
            CREATE TABLE IF NOT EXISTS ACTIVITY_CHEMICAL (
                Act_id INT,
                Chem_id INT,
                PRIMARY KEY (Act_id, Chem_id),
                FOREIGN KEY (Act_id) REFERENCES ACTIVITY(Act_id),
                FOREIGN KEY (Chem_id) REFERENCES CHEMICAL(Chem_id)
            );
            """,
            # 15. Activity-Campus Area Intermediate Table (M:N relation)
            """
            CREATE TABLE IF NOT EXISTS ACTIVITY_AREA (
                Act_id INT,
                Area_id INT,
                PRIMARY KEY (Act_id, Area_id),
                FOREIGN KEY (Act_id) REFERENCES ACTIVITY(Act_id),
                FOREIGN KEY (Area_id) REFERENCES CAMPUS_AREA(Area_id)
            );
            """,
            # 16. Activity-Worker Intermediate Table (M:N relation)
            """
            CREATE TABLE IF NOT EXISTS ACTIVITY_WORKER (
                Act_id INT,
                WSsn INT,
                PRIMARY KEY (Act_id, WSsn),
                FOREIGN KEY (Act_id) REFERENCES ACTIVITY(Act_id),
                FOREIGN KEY (WSsn) REFERENCES WORKER(WSsn)
            );
            """,
            # 17. Admin Table (System Administrator, similar to DBA)
            """
            CREATE TABLE IF NOT EXISTS ADMIN (
                AdminID INT PRIMARY KEY AUTO_INCREMENT,
                Username VARCHAR(30) NOT NULL UNIQUE,
                Password VARCHAR(30) NOT NULL  # Simplified design, need encryption in actual projects
            );
            """
        ]

        try:
            for sql in create_table_sqls:
                self.cursor.execute(sql)
            self.conn.commit()
            print("All tables created/verified successfully.")
            # Insert default admin (username: admin, password: admin123)
            self.cursor.execute("INSERT IGNORE INTO ADMIN (Username, Password) VALUES ('admin', 'admin123')")
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            print(f"Failed to create tables: {e}")

    def reconnect(self):
        """Auto reconnect when connection is lost"""
        try:
            self.conn.ping(reconnect=True)
        except:
            self.connect()

    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.open:
            self.conn.close()
            print("\nDatabase connection closed")

import pymysql
from pymysql.err import OperationalError, IntegrityError, ProgrammingError
from datetime import datetime

class CMMS:
    def __init__(self, host='localhost', user='root', password='Hedao20060629', db='CMMS', port=3306, charset='utf8mb4'):
        # Initialize database connection, automatically create database and tables
        self.host = host
        self.user = user
        self.password = password
        self.db = db
        self.port = port
        self.charset = charset
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()  # Auto create required tables

    def _connect(self):
        # Establish database connection, create if not exists
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

    def _create_tables(self):
        # Create all required tables for CMMS (based on ER diagram and attribute requirements)
        create_table_sqls = [
            # 1. Chemical Reagent Table (CHEMICAL) - Attributes: Chem_id, Name, Type, isHarmful
            """
            CREATE TABLE IF NOT EXISTS CHEMICAL (
                Chem_id INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(50) NOT NULL,
                Type VARCHAR(30) NOT NULL,
                isHarmful BOOLEAN NOT NULL DEFAULT FALSE,
                UNIQUE KEY uk_chem_name (Name)
            );
            """,
            # 2. External Company Table (EXTERNAL_COMPANY)
            """
            CREATE TABLE IF NOT EXISTS EXTERNAL_COMPANY (
                CompanyID INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(50) NOT NULL,
                ContactID VARCHAR(20),
                ContactPhone VARCHAR(15),
                UNIQUE KEY uk_company_name (Name)
            );
            """,
            # 3. Executive Officer Table (EXECUTIVE_OFFICER)
            """
            CREATE TABLE IF NOT EXISTS EXECUTIVE_OFFICER (
                OfficerID INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(50) NOT NULL,
                Sex ENUM('Male', 'Female', 'Other'),
                Position VARCHAR(30),
                HireDate DATE
            );
            """,
            # 4. Manager Table (MANAGER) - 1:1 relation with Executive Officer, 1:N manage Workers
            """
            CREATE TABLE IF NOT EXISTS MANAGER (
                ManagerID INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(50) NOT NULL,
                Sex ENUM('Male', 'Female', 'Other'),
                OfficerID INT UNIQUE,
                MaxWorkers INT DEFAULT 20,  # Limit of workers
                FOREIGN KEY (OfficerID) REFERENCES EXECUTIVE_OFFICER(OfficerID)
            );
            """,
            # 5. Worker Table (WORKER)
            """
            CREATE TABLE IF NOT EXISTS WORKER (
                WorkerID INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(50) NOT NULL,
                Sex ENUM('Male', 'Female', 'Other'),
                ManagerID INT,
                HireDate DATE,
                FOREIGN KEY (ManagerID) REFERENCES MANAGER(ManagerID)
            );
            """,
            # 6. Campus Area Table (CAMPUS_AREA)
            """
            CREATE TABLE IF NOT EXISTS CAMPUS_AREA (
                AreaID INT PRIMARY KEY AUTO_INCREMENT,
                Location VARCHAR(100) NOT NULL UNIQUE,
                Description VARCHAR(200)
            );
            """,
            # 7. Gate Table (GATE) - 1:N relation with Campus Area
            """
            CREATE TABLE IF NOT EXISTS GATE (
                GateID INT PRIMARY KEY AUTO_INCREMENT,
                AreaID INT,
                GateName VARCHAR(30) NOT NULL,
                FOREIGN KEY (AreaID) REFERENCES CAMPUS_AREA(AreaID)
            );
            """,
            # 8. Square Table (SQUARE) - 1:N relation with Campus Area
            """
            CREATE TABLE IF NOT EXISTS SQUARE (
                SquareID INT PRIMARY KEY AUTO_INCREMENT,
                AreaID INT,
                SquareName VARCHAR(50) NOT NULL UNIQUE,
                FOREIGN KEY (AreaID) REFERENCES CAMPUS_AREA(AreaID)
            );
            """,
            # 9. Building Table (BUILDING) - 1:N relation with Campus Area, managed by Manager
            """
            CREATE TABLE IF NOT EXISTS BUILDING (
                BuildingID INT PRIMARY KEY AUTO_INCREMENT,
                AreaID INT,
                BuildingName VARCHAR(50) NOT NULL UNIQUE,
                Floors INT,
                ManagerID INT,
                FOREIGN KEY (AreaID) REFERENCES CAMPUS_AREA(AreaID),
                FOREIGN KEY (ManagerID) REFERENCES MANAGER(ManagerID)
            );
            """,
            # 10. Level Table (LEVEL) - 1:N relation with Building
            """
            CREATE TABLE IF NOT EXISTS LEVEL (
                LevelID INT PRIMARY KEY AUTO_INCREMENT,
                BuildingID INT,
                LevelNum VARCHAR(10) NOT NULL,  # e.g. "3F", "B1"
                FOREIGN KEY (BuildingID) REFERENCES BUILDING(BuildingID),
                UNIQUE KEY uk_building_level (BuildingID, LevelNum)
            );
            """,
            # 11. Room Table (ROOM) - 1:N relation with Level
            """
            CREATE TABLE IF NOT EXISTS ROOM (
                RoomID INT PRIMARY KEY AUTO_INCREMENT,
                LevelID INT,
                RoomNum VARCHAR(20) NOT NULL,
                IsAvailable BOOLEAN DEFAULT TRUE,
                RoomType VARCHAR(30),  # e.g. "Laboratory", "Meeting Room"
                FOREIGN KEY (LevelID) REFERENCES LEVEL(LevelID),
                UNIQUE KEY uk_level_room (LevelID, RoomNum)
            );
            """,
            # 12. Corridor Table (CORRIDOR) - 1:N relation with Level
            """
            CREATE TABLE IF NOT EXISTS CORRIDOR (
                CorridorID INT PRIMARY KEY AUTO_INCREMENT,
                LevelID INT,
                CorridorName VARCHAR(50) NOT NULL,
                FOREIGN KEY (LevelID) REFERENCES LEVEL(LevelID),
                UNIQUE KEY uk_level_corridor (LevelID, CorridorName)
            );
            """,
            # 13. Activity Table (ACTIVITY) - Attributes: Weather_related, aging_repair, Cleaning
            """
            CREATE TABLE IF NOT EXISTS ACTIVITY (
                Act_id INT PRIMARY KEY AUTO_INCREMENT,
                ActivityName VARCHAR(100) NOT NULL,
                Weather_related BOOLEAN DEFAULT FALSE,
                aging_repair BOOLEAN DEFAULT FALSE,
                Cleaning BOOLEAN DEFAULT FALSE,
                StartTime DATETIME NOT NULL,
                EndTime DATETIME NOT NULL,
                IsUnavailable BOOLEAN DEFAULT FALSE,
                CompanyID INT,  # Relate to External Company (outsourced activities)
                ManagerID INT,  # Relate to Manager (responsible person)
                FOREIGN KEY (CompanyID) REFERENCES EXTERNAL_COMPANY(CompanyID),
                FOREIGN KEY (ManagerID) REFERENCES MANAGER(ManagerID)
            );
            """,
            # 14. Activity-Chemical Intermediate Table (M:N relation)
            """
            CREATE TABLE IF NOT EXISTS ACTIVITY_CHEMICAL (
                Act_id INT,
                Chem_id INT,
                UsageAmount VARCHAR(20),  # Usage quantity
                PRIMARY KEY (Act_id, Chem_id),
                FOREIGN KEY (Act_id) REFERENCES ACTIVITY(Act_id),
                FOREIGN KEY (Chem_id) REFERENCES CHEMICAL(Chem_id)
            );
            """,
            # 15. Activity-Campus Area Intermediate Table (M:N relation)
            """
            CREATE TABLE IF NOT EXISTS ACTIVITY_AREA (
                Act_id INT,
                AreaID INT,
                PRIMARY KEY (Act_id, AreaID),
                FOREIGN KEY (Act_id) REFERENCES ACTIVITY(Act_id),
                FOREIGN KEY (AreaID) REFERENCES CAMPUS_AREA(AreaID)
            );
            """,
            # 16. Activity-Worker Intermediate Table (M:N relation)
            """
            CREATE TABLE IF NOT EXISTS ACTIVITY_WORKER (
                Act_id INT,
                WorkerID INT,
                PRIMARY KEY (Act_id, WorkerID),
                FOREIGN KEY (Act_id) REFERENCES ACTIVITY(Act_id),
                FOREIGN KEY (WorkerID) REFERENCES WORKER(WorkerID)
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

    def _reconnect(self):
        # Auto reconnect when connection is lost
        try:
            self.conn.ping(reconnect=True)
        except:
            self._connect()

    # ------------------------------
    # Core CRUD Functions (for all tables)
    # ------------------------------
    def insert(self, table_name: str, data: dict) -> bool:
        # Insert record (general)
        if not data:
            print("insert() must receive data!")
            return False
        self._reconnect()
        try:
            fields = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            sql = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"
            self.cursor.execute(sql, tuple(data.values()))
            self.conn.commit()
            print(f"Insert successful! New record ID: {self.cursor.lastrowid}")
            return True
        except IntegrityError as e:
            self.conn.rollback()
            print(f"Insert failed: {e}")
            return False
        except Exception as e:
            self.conn.rollback()
            print(f"Insert failed: {e}")
            return False

    def delete(self, table_name: str, condition: dict) -> bool:
        # Delete record (general, disallow unconditional delete)
        if not condition:
            print("delete() must receive condition!")
            return False
        self._reconnect()
        try:
            # Cascade delete related records in intermediate tables
            if table_name == "ACTIVITY":
                act_ids = self._get_matched_ids(table_name, condition, "Act_id")
                if act_ids:
                    self.cursor.execute(f"DELETE FROM ACTIVITY_CHEMICAL WHERE Act_id IN ({','.join(map(str, act_ids))})")
                    self.cursor.execute(f"DELETE FROM ACTIVITY_AREA WHERE Act_id IN ({','.join(map(str, act_ids))})")
                    self.cursor.execute(f"DELETE FROM ACTIVITY_WORKER WHERE Act_id IN ({','.join(map(str, act_ids))})")

            where_clause = " AND ".join([f"{k}=%s" for k in condition.keys()])
            sql = f"DELETE FROM {table_name} WHERE {where_clause}"
            affected_rows = self.cursor.execute(sql, tuple(condition.values()))
            self.conn.commit()
            if affected_rows > 0:
                print(f"Delete successful! {affected_rows} record(s) deleted")
                return True
            else:
                print("Delete failed: No matching records found")
                return False
        except Exception as e:
            self.conn.rollback()
            print(f"Delete failed: {e}")
            return False

    def list_all(self, table_name: str, fields: str = '*') -> list:
        # Query all records in table (general)
        self._reconnect()
        try:
            sql = f"SELECT {fields} FROM {table_name}"
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            print(f"Query successful! {len(results)} record(s) found")
            return results
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    def list(self, table_name: str, condition: dict = None, fields: str = '*') -> list:
        # Query records by condition (general)
        self._reconnect()
        try:
            if condition:
                where_clause = " AND ".join([f"{k}=%s" for k in condition.keys()])
                sql = f"SELECT {fields} FROM {table_name} WHERE {where_clause}"
                self.cursor.execute(sql, tuple(condition.values()))
            else:
                sql = f"SELECT {fields} FROM {table_name}"
                self.cursor.execute(sql)
            results = self.cursor.fetchall()
            print(f"Query successful! {len(results)} matching record(s) found")
            return results
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    def update(self, table_name: str, data: dict, condition: dict) -> bool:
        # Update record (general)
        if not data or not condition:
            print("update() must receive update data and condition!")
            return False
        self._reconnect()
        try:
            set_clause = ", ".join([f"{k}=%s" for k in data.keys()])
            where_clause = " AND ".join([f"{k}=%s" for k in condition.keys()])
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            values = tuple(data.values()) + tuple(condition.values())
            affected_rows = self.cursor.execute(sql, values)
            self.conn.commit()
            if affected_rows > 0:
                print(f"Update successful! {affected_rows} record(s) updated")
                return True
            else:
                print("Update failed: No matching records found")
                return False
        except Exception as e:
            self.conn.rollback()
            print(f"Update failed: {e}")
            return False

    def _get_matched_ids(self, table_name: str, condition: dict, id_field: str) -> list:
        # Helper function: Get list of primary key IDs matching condition
        where_clause = " AND ".join([f"{k}=%s" for k in condition.keys()])
        sql = f"SELECT {id_field} FROM {table_name} WHERE {where_clause}"
        self.cursor.execute(sql, tuple(condition.values()))
        return [row[id_field] for row in self.cursor.fetchall()]

    # ------------------------------
    # Project-Specific Functions
    # ------------------------------
    def search_cleaning_activities(self, start_date: str, end_date: str, building_name: str = None) -> list:
        # Query cleaning activities within specified time period (including area availability and harmful chemicals)
        self._reconnect()
        try:
            # Build conditions
            conditions = ["A.Cleaning = 1", "A.StartTime >= %s", "A.EndTime <= %s"]
            params = [start_date, end_date]
            if building_name:
                conditions.append("B.BuildingName = %s")
                params.append(building_name)

            where_clause = " AND ".join(conditions)
            # Join query: Activity + Building + Chemical
            sql = f"""
                SELECT A.Act_id, A.ActivityName, A.StartTime, A.EndTime, A.IsUnavailable,
                       B.BuildingName, GROUP_CONCAT(C.Name) AS UsedChemicals,
                       MAX(C.isHarmful) AS HasHarmfulChem
                FROM ACTIVITY A
                LEFT JOIN BUILDING B ON A.ManagerID = B.ManagerID
                LEFT JOIN ACTIVITY_CHEMICAL AC ON A.Act_id = AC.Act_id
                LEFT JOIN CHEMICAL C ON AC.Chem_id = C.Chem_id
                WHERE {where_clause}
                GROUP BY A.Act_id, A.ActivityName, A.StartTime, A.EndTime, A.IsUnavailable, B.BuildingName
            """
            self.cursor.execute(sql, tuple(params))
            results = self.cursor.fetchall()
            print(f"Cleaning activity query successful! {len(results)} record(s) found")
            return results
        except Exception as e:
            print(f"Cleaning activity query failed: {e}")
            return []

    def generate_worker_activity_report(self) -> list:
        # Generate worker activity assignment report (admin only)
        self._reconnect()
        try:
            sql = f"""
                SELECT W.WorkerID, W.Name AS WorkerName, M.Name AS ManagerName,
                       COUNT(AW.Act_id) AS ActivityCount,
                       GROUP_CONCAT(DISTINCT A.ActivityName) AS ActivityNames
                FROM WORKER W
                LEFT JOIN MANAGER M ON W.ManagerID = M.ManagerID
                LEFT JOIN ACTIVITY_WORKER AW ON W.WorkerID = AW.WorkerID
                LEFT JOIN ACTIVITY A ON AW.Act_id = A.Act_id
                GROUP BY W.WorkerID, W.Name, M.Name
                ORDER BY ActivityCount DESC
            """
            self.cursor.execute(sql)
            results = self.cursor.fetchall()
            print("Worker activity report generated successfully.")
            return results
        except Exception as e:
            print(f"Report generation failed: {e}")
            return []

    # ------------------------------
    # Role Login and Function Interfaces
    # ------------------------------
    def admin_login(self, username: str, password: str) -> bool:
        # Admin login
        self._reconnect()
        self.cursor.execute("SELECT * FROM ADMIN WHERE Username=%s AND Password=%s", (username, password))
        return self.cursor.fetchone() is not None

    def manager_login(self, manager_id: int) -> bool:
        # Manager login (verify via ManagerID)
        self._reconnect()
        self.cursor.execute("SELECT * FROM MANAGER WHERE ManagerID=%s", (manager_id,))
        return self.cursor.fetchone() is not None

    def worker_login(self, worker_id: int) -> bool:
        # Worker login (verify via WorkerID)
        self._reconnect()
        self.cursor.execute("SELECT * FROM WORKER WHERE WorkerID=%s", (worker_id,))
        return self.cursor.fetchone() is not None

    # ------------------------------
    # Destructor: Close connection
    # ------------------------------
    def __del__(self):
        if self.cursor:
            self.cursor.close()
        if self.conn and self.conn.open:
            self.conn.close()
            print("\nDatabase connection closed")

# ------------------------------
# Main Program: User Interface
# ------------------------------
def main():
    # Initialize CMMS system
    cmms = CMMS(password='Hedao20060629')  # Replace with your MySQL password

    print("\n===== Campus Maintenance Management System (CMMS) =====")
    while True:
        print("\nSelect user role:")
        print("1. System Administrator (Admin)")
        print("2. Manager")
        print("3. Worker")
        print("4. Exit System")
        choice = input("Enter selection (1-4): ")

        if choice == "1":
            # Admin functions
            username = input("Enter admin username: ")
            password = input("Enter admin password: ")
            if cmms.admin_login(username, password):
                print(f"\nWelcome, {username}!")
                while True:
                    print("\nAdmin Function Menu:")
                    print("1. Insert Record (All Tables)")
                    print("2. Delete Record (All Tables)")
                    print("3. Query Record (All Tables)")
                    print("4. Update Record (All Tables)")
                    print("5. Query Cleaning Activities (Specify Time Period)")
                    print("6. Generate Worker Activity Report")
                    print("7. Exit Admin Interface")
                    admin_choice = input("Enter selection (1-7): ")

                    if admin_choice == "7":
                        print("Exit admin interface")
                        break

                    # 1. Insert Record
                    elif admin_choice == "1":
                        table = input("Enter table name to insert (e.g. CHEMICAL, ACTIVITY): ")
                        data = {}
                        if table == "CHEMICAL":
                            data = {
                                "Name": input("Enter chemical name: "),
                                "Type": input("Enter chemical type: "),
                                "isHarmful": input("Is harmful (True/False): ").lower() == "true"
                            }
                        elif table == "ACTIVITY":
                            data = {
                                "ActivityName": input("Enter activity name: "),
                                "Weather_related": input("Weather related (True/False): ").lower() == "true",
                                "aging_repair": input("Aging repair (True/False): ").lower() == "true",
                                "Cleaning": input("Is cleaning activity (True/False): ").lower() == "true",
                                "StartTime": input("Enter start time (Format: YYYY-MM-DD HH:MM:SS): "),
                                "EndTime": input("Enter end time (Format: YYYY-MM-DD HH:MM:SS): "),
                                "ManagerID": int(input("Enter responsible manager ID: "))
                            }
                        else:
                            print("Quick insert not supported for this table, please construct data manually")
                            continue
                        cmms.insert(table, data)

                    # 2. Delete Record
                    elif admin_choice == "2":
                        table = input("Enter table name to delete: ")
                        condition = {}
                        if table == "ACTIVITY":
                            condition["Act_id"] = int(input("Enter activity ID to delete: "))
                        else:
                            id_field = input(f"Enter primary key field name of {table} (e.g. Chem_id, WorkerID): ")
                            id_value = input(f"Enter {id_field} value to delete: ")
                            condition[id_field] = id_value
                        cmms.delete(table, condition)

                    # 3. Query Record
                    elif admin_choice == "3":
                        table = input("Enter table name to query: ")
                        fields = input("Enter fields to query (default *, separate multiple with commas): ") or "*"
                        if input("Query with condition (Y/N): ").lower() == "y":
                            condition = {}
                            key = input("Enter condition field name: ")
                            value = input("Enter condition value: ")
                            condition[key] = value
                            results = cmms.list(table, condition, fields)
                        else:
                            results = cmms.list_all(table, fields)
                        print("Query results: ", results)

                    # 4. Update Record
                    elif admin_choice == "4":
                        table = input("Enter table name to update: ")
                        condition_key = input("Enter update condition field name: ")
                        condition_value = input("Enter update condition value: ")
                        data_key = input("Enter field name to update: ")
                        data_value = input("Enter new value: ")
                        cmms.update(table, {data_key: data_value}, {condition_key: condition_value})

                    # 5. Query Cleaning Activities
                    elif admin_choice == "5":
                        start = input("Enter start time (YYYY-MM-DD HH:MM:SS): ")
                        end = input("Enter end time (YYYY-MM-DD HH:MM:SS): ")
                        building = input("Enter building name (optional, press enter to skip): ") or None
                        activities = cmms.search_cleaning_activities(start, end, building)
                        for act in activities:
                            print(f"\nActivity ID: {act['Act_id']}")
                            print(f"Activity Name: {act['ActivityName']}")
                            print(f"Time: {act['StartTime']} - {act['EndTime']}")
                            print(f"Related Building: {act['BuildingName'] or 'None'}")
                            print(f"Area Unavailable: {'Yes' if act['IsUnavailable'] else 'No'}")
                            print(f"Chemicals Used: {act['UsedChemicals'] or 'None'}")
                            print(f"Contains Harmful Chemicals: {'Yes' if act['HasHarmfulChem'] else 'No'}")

                    # 6. Generate Report
                    elif admin_choice == "6":
                        report = cmms.generate_worker_activity_report()
                        print("\n===== Worker Activity Assignment Report =====")
                        for item in report:
                            print(f"\nWorker ID: {item['WorkerID']}")
                            print(f"Name: {item['WorkerName']}")
                            print(f"Manager: {item['ManagerName'] or 'None'}")
                            print(f"Number of Activities: {item['ActivityCount']}")
                            print(f"Activities Participated: {item['ActivityNames'] or 'None'}")

                    else:
                        print("Invalid input, please try again!")
            else:
                print("Invalid username or password!")

        elif choice == "2":
            # Manager functions
            manager_id = int(input("Enter manager ID: "))
            if cmms.manager_login(manager_id):
                print(f"\nWelcome, Manager ID: {manager_id}!")
                while True:
                    print("\nManager Function Menu:")
                    print("1. View Responsible Activities")
                    print("2. Assign Worker to Activity")
                    print("3. View Subordinate Workers")
                    print("4. Exit Manager Interface")
                    manager_choice = input("Enter selection (1-4): ")

                    if manager_choice == "4":
                        break
                    elif manager_choice == "1":
                        activities = cmms.list("ACTIVITY", {"ManagerID": manager_id})
                        print("Your responsible activities: ", activities)
                    elif manager_choice == "2":
                        act_id = int(input("Enter activity ID: "))
                        worker_id = int(input("Enter worker ID: "))
                        cmms.insert("ACTIVITY_WORKER", {"Act_id": act_id, "WorkerID": worker_id})
                    elif manager_choice == "3":
                        workers = cmms.list("WORKER", {"ManagerID": manager_id})
                        print("Your subordinate workers: ", workers)
                    else:
                        print("Invalid input!")
            else:
                print("Manager ID does not exist!")

        elif choice == "3":
            # Worker functions
            worker_id = int(input("Enter worker ID: "))
            if cmms.worker_login(worker_id):
                print(f"\nWelcome, Worker ID: {worker_id}!")
                while True:
                    print("\nWorker Function Menu:")
                    print("1. View Assigned Activities")
                    print("2. Exit Worker Interface")
                    worker_choice = input("Enter selection (1-2): ")

                    if worker_choice == "2":
                        break
                    elif worker_choice == "1":
                        # Join query for activity details
                        cmms._reconnect()
                        sql = """
                            SELECT A.Act_id, A.ActivityName, A.StartTime, A.EndTime, A.Cleaning,
                                   A.aging_repair, A.Weather_related
                            FROM ACTIVITY A
                            JOIN ACTIVITY_WORKER AW ON A.Act_id = AW.Act_id
                            WHERE AW.WorkerID = %s
                        """
                        cmms.cursor.execute(sql, (worker_id,))
                        activities = cmms.cursor.fetchall()
                        print("Activities assigned to you: ", activities)
                    else:
                        print("Invalid input!")
            else:
                print("Worker ID does not exist!")

        elif choice == "4":
            print("===== Thank you for using, goodbye! =====")
            break

        else:
            print("Invalid input, please try again!")

if __name__ == "__main__":
    main()
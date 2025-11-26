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
                MaxManagers INT DEFAULT 5  # Limit of managers
            );
            """,
            # 3. Manager Table (MANAGER) - Attributes: MSsn, Name, Sex, ESsn, 1:1 relation with Executive Officer, 1:N manage Workers
            """
            CREATE TABLE IF NOT EXISTS MANAGER (
                MSsn INT PRIMARY KEY AUTO_INCREMENT,
                Name VARCHAR(50) NOT NULL,
                Sex ENUM('Male', 'Female'),
                OSsn INT UNIQUE,
                MaxWorkers INT DEFAULT 20,  # Limit of workers
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

    def _reconnect(self):
        # Auto reconnect when connection is lost
        try:
            self.conn.ping(reconnect=True)
        except:
            self._connect()

    # ------------------------------
    # Core CRUD Functions (for all tables)
    # ------------------------------
    def insert(self, table_name: str, data_list: list) -> bool:
        """
        Insert records
        Args:
            table_name: Name of the table to insert into
            data_list: List of dictionaries, each dictionary represents one record
        Returns:
            bool: True if all records inserted successfully, False otherwise
        """
        if not data_list or not isinstance(data_list, list):
            print("insert() must receive a list of data dictionaries!")
            return False
        
        if len(data_list) == 0:
            print("insert() received empty list!")
            return False
        
        self._reconnect()
        try:
            # Validate that all records have the same fields
            first_record_keys = set(data_list[0].keys())
            for i, record in enumerate(data_list[1:], start=1):
                if set(record.keys()) != first_record_keys:
                    print(f"Error: Record {i+1} has different fields than the first record!")
                    return False
            
            # Build SQL for insert
            fields = ", ".join(data_list[0].keys())
            placeholders = ", ".join(["%s"] * len(data_list[0]))
            sql = f"INSERT INTO {table_name} ({fields}) VALUES ({placeholders})"
            
            # Prepare all values as tuples
            values_list = [tuple(record.values()) for record in data_list]
            
            # Executeh insert using executemany for better performance
            affected_rows = self.cursor.executemany(sql, values_list)
            self.conn.commit()
            
            print(f"Insert successful! {affected_rows} record(s) inserted")
            if self.cursor.lastrowid and self.cursor.lastrowid != 0:
                print(f"Last inserted record ID: {self.cursor.lastrowid}")
            return True
        except IntegrityError as e:
            self.conn.rollback()
            print(f"Insert failed (integrity error): {e}")
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
                conditions.append("B.BNo = %s")
                params.append(building_name)

            where_clause = " AND ".join(conditions)
            # Join query: Activity + Building + Chemical
            sql = f"""
                SELECT A.Act_id, A.Description, A.Com_id, A.Tools, A.StartTime, A.EndTime, A.IsUnusable,
                       B.BNo, GROUP_CONCAT(C.Name) AS UsedChemicals,
                       MAX(C.isHarmful) AS HasHarmfulChem
                FROM ACTIVITY A
                LEFT JOIN ACTIVITY_AREA AA ON A.Act_id = AA.Act_id
                LEFT JOIN CAMPUS_AREA CA ON AA.Area_id = CA.Area_id
                LEFT JOIN BUILDING B ON CA.Area_id = B.Area_id
                LEFT JOIN ACTIVITY_CHEMICAL AC ON A.Act_id = AC.Act_id
                LEFT JOIN CHEMICAL C ON AC.Chem_id = C.Chem_id
                WHERE {where_clause}
                GROUP BY A.Act_id, A.Description, A.Tools, A.StartTime, A.EndTime, A.IsUnusable, B.BNo
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
                SELECT W.WSsn AS WorkerID, M.MSsn AS ManagerID,
                       COUNT(AW.Act_id) AS ActivityCount,
                       GROUP_CONCAT(DISTINCT A.Act_id) AS ActivityID
                FROM WORKER W
                LEFT JOIN MANAGER M ON W.MSsn = M.MSsn
                LEFT JOIN ACTIVITY_WORKER AW ON W.WSsn = AW.WSsn
                LEFT JOIN ACTIVITY A ON AW.Act_id = A.Act_id
                GROUP BY W.WSsn, M.MSsn
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
        # Manager login (verify via MSsn)
        self._reconnect()
        self.cursor.execute("SELECT * FROM MANAGER WHERE MSsn=%s", (manager_id,))
        return self.cursor.fetchone() is not None

    def worker_login(self, worker_id: int) -> bool:
        # Worker login (verify via WSsn)
        self._reconnect()
        self.cursor.execute("SELECT * FROM WORKER WHERE WSsn=%s", (worker_id,))
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
    """
    Main entry point for the CMMS application.
    Provides role-based access to system functionalities.
    """
    # Initialize CMMS system
    cmms = CMMS(password='euoqlwto')  # Replace with your MySQL password

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
                        table = input("Enter table name for insert (e.g. CHEMICAL, ACTIVITY): ")
                        print(f"\nInsert for table: {table}")
                        print("Enter records one by one. Type 'done' when finished.")
                        
                        data_list = []
                        record_count = 0

                        while True:
                            record_count += 1
                            print(f"\n--- Record {record_count} ---")
                            data = {}

                            if table == "CHEMICAL":
                                data = {
                                    "Chem_id": input("Enter chemical ID (e.g. XXXX): "),
                                    "Name": input("Enter chemical name: "),
                                    "isHarmful": input("Is harmful (True/False): ").lower() == "true"
                                }
                            
                            elif table == "EXECUTIVE_OFFICER":
                                data = {
                                    "OSsn": input("Enter officer SSN (e.g. AAAGGSSSS): "),
                                    "Name": input("Enter officer name: "),
                                    "Sex": input("Enter sex (Male/Female): ").capitalize(),
                                    "MaxManagers": int(input("Enter max managers (default 5): ") or 5)
                                }
                                
                            elif table == "MANAGER":
                                data = {
                                    "MSsn": input("Enter manager SSN (e.g. AAAGGSSSS): "),
                                    "Name": input("Enter manager name: "),
                                    "OSsn": input("Enter officer SSN (e.g. AAAGGSSSS): "),
                                    "Sex": input("Enter sex (Male/Female): ").capitalize(),
                                    "MaxWorkers": int(input("Enter max workers (default 20): ") or 20)
                                }
                                
                            elif table == "WORKER":
                                data = {
                                    "WSsn": input("Enter worker SSN (e.g. AAAGGSSSS): "),
                                    "Name": input("Enter worker name: "),
                                    "MSsn": input("Enter manager SSN (e.g. AAAGGSSSS): "),
                                    "Sex": input("Enter sex (Male/Female): ").capitalize()
                                }

                            elif table == "EXTERNAL_COMPANY":
                                data = {
                                    "Com_ID": input("Enter external company ID (e.g. XXXX): "),
                                    "Name": input("Enter external company name: "),
                                    "MSsn": input("Enter responsible manager SSN: ")
                                }
                                
                            elif table == "CAMPUS_AREA":
                                data = {
                                    "Area_id": input("Enter area ID (e.g. XX): "),
                                    "Location": input("Enter area location: ")
                                    }
                                
                            elif table == "GATE":
                                data = {
                                    "GNo": input("Enter gate number (e.g. XX): "),
                                    "Area_id": int(input("Enter area ID: "))
                                }
                                
                            elif table == "SQUARE":
                                data = {
                                    "SNo": input("Enter square number (e.g. XX):"),
                                    "Area_id": int(input("Enter area ID: "))
                                }
                                
                            elif table == "BUILDING":
                                data = {
                                    "BNo": input("Enter building number (e.g. XX): "),
                                    "Area_id": int(input("Enter area ID: ")),
                                    "MSsn": int(input("Enter manager SSN: "))
                                }
                                
                            elif table == "LEVEL":
                                data = {
                                    "LNo": input("Enter level number (e.g. XX): "),
                                    "BNo": int(input("Enter building number: "))
                                }
                                
                            elif table == "ROOM":
                                data = {
                                    "RNo": input("Enter room number (e.g. XXX): "),
                                    "LNo": int(input("Enter level number: ")),
                                    "BNo": int(input("Enter building number: ")),
                                    "IsAvailable": input("Is available (True/False): ").lower() == "true"
                                }
                                
                            elif table == "CORRIDOR":
                                data = {
                                    "CNo": input("Enter corridor number (e.g. XX): "),
                                    "LNo": int(input("Enter level number: ")),
                                    "BNo": int(input("Enter building number: "))

                                }

                            elif table == "ACTIVITY":
                                data = {
                                    "Act_id": input("Enter activity id (e.g. XXXX): "),
                                    "Description": input("Enter description: "),
                                    "Com_id": input("Enter external company id: "),
                                    "Tools": input("Enter used tools: "),
                                    "Weather_related": input("Weather related (True/False): ").lower() == "true",
                                    "Aging_repair": input("Aging repair (True/False): ").lower() == "true",
                                    "Cleaning": input("Is cleaning activity (True/False): ").lower() == "true",
                                    "StartTime": input("Enter start time (Format: YYYY-MM-DD HH:MM:SS): "),
                                    "EndTime": input("Enter end time (Format: YYYY-MM-DD HH:MM:SS): "),
                                }
                                # Convert empty string to None for CompanyID
                                if data["Com_id"] == "":
                                    data["Com_id"] = None

                            elif table == "ACTIVITY_CHEMICAL":
                                data = {
                                    "Act_id": int(input("Enter activity ID: ")),
                                    "Chem_id": int(input("Enter chemical ID: ")),
                                }
                                    
                            elif table == "ACTIVITY_AREA":
                                data = {
                                    "Act_id": int(input("Enter activity ID: ")),
                                    "Area_id": int(input("Enter area ID: "))
                                }
                                    
                            elif table == "ACTIVITY_WORKER":
                                data = {
                                    "Act_id": int(input("Enter activity ID: ")),
                                    "WSsn": int(input("Enter worker SSN: "))
                                }
                        
                            else:
                                print(f"Quick insert not supported for this table {table}, please construct data manually")
                                record_count -= 1
                                continue
                        
                            data_list.append(data)
                            
                            continue_input = input("Add another record? (Y/N): ").lower()
                            if continue_input != 'y':
                                break
                        
                        if len(data_list) > 0:
                            print(f"\nInserting {len(data_list)} record(s)...")
                            cmms.insert(table, data_list)
                        else:
                            print("No records to insert!")

                    # 2. Delete Record
                    elif admin_choice == "2":
                        table = input("Enter table name to delete: ")
                        condition = {}
                        if table == "ACTIVITY":
                            condition["Act_id"] = int(input("Enter activity ID to delete: "))
                        else:
                            id_field = input(f"Enter primary key field name of {table} (e.g. Chem_id, WSsn): ")
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
                        building = input("Enter building number (optional, press enter to skip): ") or None
                        activities = cmms.search_cleaning_activities(start, end, building)
                        for act in activities:
                            print(f"\nActivity ID: {act['Act_id']}")
                            print(f"Description: {act['Description']}")
                            print(f"External Company ID: {act['Com_id']}")
                            print(f"Time: {act['StartTime']} - {act['EndTime']}")
                            print(f"Related Building: {act['BNo'] or 'None'}")
                            print(f"Area Unavailable: {'Yes' if act['IsUnusable'] else 'No'}")
                            print(f"Tools Used: {act['Tools'] or 'None'}")
                            print(f"Chemicals Used: {act['UsedChemicals'] or 'None'}")
                            print(f"Contains Harmful Chemicals: {'Yes' if act['HasHarmfulChem'] else 'No'}")

                    # 6. Generate Report
                    elif admin_choice == "6":
                        report = cmms.generate_worker_activity_report()
                        print("\n===== Worker Activity Assignment Report =====")
                        for item in report:
                            print(f"\nWorker ID: {item['WorkerID']}")
                            print(f"Manager: {item['ManagerID'] or 'None'}")
                            print(f"Number of Activities: {item['ActivityCount']}")
                            print(f"Activities Participated: {item['ActivityID'] or 'None'}")

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
                        cmms._reconnect()
                        try:
                            sql = """
                                SELECT A.* 
                                FROM ACTIVITY A
                                LEFT JOIN EXTERNAL_COMPANY EC ON A.Com_id = EC.Com_ID
                                LEFT JOIN ACTIVITY_AREA AA ON A.Act_id = AA.Act_id
                                LEFT JOIN BUILDING B ON AA.Area_id = B.Area_id
                                WHERE EC.MSsn = %s OR B.MSsn = %s
                            """
                            cmms.cursor.execute(sql, (manager_id, manager_id))
                            activities = cmms.cursor.fetchall()
                            print("Your responsible activities: ")
                            for act in activities:
                                print(f"Activity ID: {act['Act_id']}, Description: {act['Description']}")
                            if not activities:
                                print("No activities found.")
                        except Exception as e:
                            print(f"Error fetching activities: {e}")
                    elif manager_choice == "2":
                        act_id = int(input("Enter activity ID: "))
                        worker_id = int(input("Enter worker ID: "))
                        worker = cmms.list("WORKER", {"WSsn": worker_id, "MSsn": manager_id})
                        if worker:
                            cmms.insert("ACTIVITY_WORKER", {"Act_id": act_id, "WSsn": worker_id})
                    elif manager_choice == "3":
                        workers = cmms.list("WORKER", {"MSsn": manager_id})
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
                            SELECT A.Act_id, A.StartTime, A.EndTime, A.Cleaning,
                                   A.aging_repair, A.Weather_related
                            FROM ACTIVITY A
                            JOIN ACTIVITY_WORKER AW ON A.Act_id = AW.Act_id
                            WHERE AW.WSsn = %s
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
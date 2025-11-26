"""
Admin Interface Module
Provides admin function menu and interaction
"""


class AdminUI:
    """Admin interface class"""
    
    def __init__(self, cmms):
        """Initialize, requires CMMS instance"""
        self.cmms = cmms

    def show_menu(self):
        """Show admin menu and handle user input"""
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
                self._handle_insert()

            # 2. Delete Record
            elif admin_choice == "2":
                self._handle_delete()

            # 3. Query Record
            elif admin_choice == "3":
                self._handle_query()

            # 4. Update Record
            elif admin_choice == "4":
                self._handle_update()

            # 5. Query Cleaning Activities
            elif admin_choice == "5":
                self._handle_search_cleaning()

            # 6. Generate Report
            elif admin_choice == "6":
                self._handle_generate_report()

            else:
                print("Invalid input, please try again!")

    def _handle_insert(self):
        """Handle insert records"""
        table = input("Enter table name for insert (e.g. CHEMICAL, ACTIVITY): ")
        print(f"\nInsert for table: {table}")
        print("Enter records one by one. Type 'done' when finished.")
        
        data_list = []
        record_count = 0
        
        while True:
            record_count += 1
            print(f"\n--- Record {record_count} ---")
            data = self._get_insert_data(table)
            
            if data is None:
                print("Invalid record data, skipping...")
                record_count -= 1
                continue
            
            data_list.append(data)
            
            continue_input = input("Add another record? (Y/N): ").lower()
            if continue_input != 'y':
                break
        
        if len(data_list) > 0:
            print(f"\nInserting {len(data_list)} record(s)...")
            self.cmms.insert(table, data_list)
        else:
            print("No records to insert!")

    def _get_insert_data(self, table: str) -> dict:
        """Get insert data based on table name"""
        data = {}
        if table == "CHEMICAL":
            data = {
                "Chem_id": input("Enter chemical ID: "),
                "Name": input("Enter chemical name: "),
                "isHarmful": input("Is harmful (True/False): ").lower() == "true"
            }
        elif table == "EXECUTIVE_OFFICER":
            data = {
                "OSsn": input("Enter officer SSN (e.g. SSSS): "),
                "Name": input("Enter officer name: "),
                "Sex": input("Enter sex (Male/Female): ").capitalize(),
                "MaxManagers": int(input("Enter max managers (default 5): ") or 5)
            }
        elif table == "MANAGER":
            data = {
                "MSsn": input("Enter manager SSN (e.g. SSSS): "),
                "Name": input("Enter manager name: "),
                "OSsn": input("Enter officer SSN (e.g. SSSS): "),
                "Sex": input("Enter sex (Male/Female): ").capitalize(),
                "MaxWorkers": int(input("Enter max workers (default 20): ") or 20)
            }
        elif table == "WORKER":
            data = {
                "WSsn": input("Enter worker SSN (e.g. SSSS): "),
                "Name": input("Enter worker name: "),
                "MSsn": input("Enter manager SSN (e.g. SSSS): "),
                "Sex": input("Enter sex (Male/Female): ").capitalize()
            }
        elif table == "EXTERNAL_COMPANY":
            data = {
                "Com_ID": input("Enter external company ID: "),
                "Name": input("Enter external company name: "),
                "MSsn": input("Enter responsible manager SSN: ")
            }
        elif table == "CAMPUS_AREA":
            data = {
                "Area_id": input("Enter area ID: "),
                "Location": input("Enter area location: ")
            }
        elif table == "GATE":
            data = {
                "GNo": input("Enter gate number: "),
                "Area_id": int(input("Enter area ID: "))
            }
        elif table == "SQUARE":
            data = {
                "SNo": input("Enter square number: "),
                "Area_id": int(input("Enter area ID: "))
            }
        elif table == "BUILDING":
            data = {
                "BNo": input("Enter building number: "),
                "Area_id": int(input("Enter area ID: ")),
                "MSsn": int(input("Enter manager SSN: "))
            }
        elif table == "LEVEL":
            data = {
                "LNo": input("Enter level number: "),
                "BNo": int(input("Enter building number: "))
            }
        elif table == "ROOM":
            data = {
                "RNo": input("Enter room number: "),
                "LNo": int(input("Enter level number: ")),
                "BNo": int(input("Enter building number: ")),
                "IsAvailable": input("Is available (True/False): ").lower() == "true"
            }
        elif table == "CORRIDOR":
            data = {
                "CNo": input("Enter corridor number: "),
                "LNo": int(input("Enter level number: ")),
                "BNo": int(input("Enter building number: "))
            }
        elif table == "ACTIVITY":
            data = {
                "Act_id": input("Enter activity id: "),
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
            return None
        return data

    def _handle_delete(self):
        """Handle delete record"""
        table = input("Enter table name to delete: ")
        condition = {}
        if table == "ACTIVITY":
            condition["Act_id"] = int(input("Enter activity ID to delete: "))
        else:
            id_field = input(f"Enter primary key field name of {table} (e.g. Chem_id, WSsn): ")
            id_value = input(f"Enter {id_field} value to delete: ")
            condition[id_field] = id_value
        self.cmms.delete(table, condition)

    def _handle_query(self):
        """Handle query record"""
        table = input("Enter table name to query: ")
        fields = input("Enter fields to query (default *, separate multiple with commas): ") or "*"
        if input("Query with condition (Y/N): ").lower() == "y":
            condition = {}
            key = input("Enter condition field name: ")
            value = input("Enter condition value: ")
            condition[key] = value
            results = self.cmms.list(table, condition, fields)
        else:
            results = self.cmms.list_all(table, fields)
        print("Query results: ", results)

    def _handle_update(self):
        """Handle update record"""
        table = input("Enter table name to update: ")
        condition_key = input("Enter update condition field name: ")
        condition_value = input("Enter update condition value: ")
        data_key = input("Enter field name to update: ")
        data_value = input("Enter new value: ")
        self.cmms.update(table, {data_key: data_value}, {condition_key: condition_value})

    def _handle_search_cleaning(self):
        """Handle search cleaning activities"""
        start = input("Enter start time (YYYY-MM-DD HH:MM:SS): ")
        end = input("Enter end time (YYYY-MM-DD HH:MM:SS): ")
        building = input("Enter building number (optional, press enter to skip): ") or None
        activities = self.cmms.search_cleaning_activities(start, end, building)
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

    def _handle_generate_report(self):
        """Handle generate report"""
        report = self.cmms.generate_worker_activity_report()
        print("\n===== Worker Activity Assignment Report =====")
        for item in report:
            print(f"\nWorker ID: {item['WorkerID']}")
            print(f"Manager: {item['ManagerID'] or 'None'}")
            print(f"Number of Activities: {item['ActivityCount']}")
            print(f"Activities Participated: {item['ActivityID'] or 'None'}")

"""
Business Services Module
Provides project-specific business logic functionality
"""


class BusinessServices:
    """Business services class"""
    
    def __init__(self, db_manager):
        """Initialize, requires database manager"""
        self.db_manager = db_manager

    def search_cleaning_activities(self, start_date: str, end_date: str, building_name: str = None) -> list:
        """Query cleaning activities within specified time period (including area availability and harmful chemicals)"""
        self.db_manager.reconnect()
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
            self.db_manager.cursor.execute(sql, tuple(params))
            results = self.db_manager.cursor.fetchall()
            print(f"Cleaning activity query successful! {len(results)} record(s) found")
            return results
        except Exception as e:
            print(f"Cleaning activity query failed: {e}")
            return []

    def generate_worker_activity_report(self) -> list:
        """Generate worker activity assignment report (admin only)"""
        self.db_manager.reconnect()
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
            self.db_manager.cursor.execute(sql)
            results = self.db_manager.cursor.fetchall()
            print("Worker activity report generated successfully.")
            return results
        except Exception as e:
            print(f"Report generation failed: {e}")
            return []

    def get_manager_activities(self, manager_id: int) -> list:
        """Get activities responsible by manager"""
        self.db_manager.reconnect()
        try:
            sql = """
                SELECT A.* 
                FROM ACTIVITY A
                LEFT JOIN EXTERNAL_COMPANY EC ON A.Com_id = EC.Com_ID
                LEFT JOIN ACTIVITY_AREA AA ON A.Act_id = AA.Act_id
                LEFT JOIN BUILDING B ON AA.Area_id = B.Area_id
                WHERE EC.MSsn = %s OR B.MSsn = %s
            """
            self.db_manager.cursor.execute(sql, (manager_id, manager_id))
            activities = self.db_manager.cursor.fetchall()
            return activities
        except Exception as e:
            print(f"Error fetching activities: {e}")
            return []

    def get_worker_activities(self, worker_id: int) -> list:
        """Get activities assigned to worker"""
        self.db_manager.reconnect()
        try:
            sql = """
                SELECT A.Act_id, A.StartTime, A.EndTime, A.Cleaning,
                       A.aging_repair, A.Weather_related
                FROM ACTIVITY A
                JOIN ACTIVITY_WORKER AW ON A.Act_id = AW.Act_id
                WHERE AW.WSsn = %s
            """
            self.db_manager.cursor.execute(sql, (worker_id,))
            activities = self.db_manager.cursor.fetchall()
            return activities
        except Exception as e:
            print(f"Error fetching activities: {e}")
            return []

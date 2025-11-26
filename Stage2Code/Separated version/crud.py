"""
CRUD Operations Module
Provides general database CRUD functionality
"""
from pymysql.err import IntegrityError


class CRUDOperations:
    """CRUD operations class"""
    
    def __init__(self, db_manager):
        """Initialize, requires database manager"""
        self.db_manager = db_manager

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
        
        self.db_manager.reconnect()
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
            affected_rows = self.db_manager.cursor.executemany(sql, values_list)
            self.db_manager.conn.commit()
            
            print(f"Insert successful! {affected_rows} record(s) inserted")
            if self.db_manager.cursor.lastrowid and self.db_manager.cursor.lastrowid != 0:
                print(f"Last inserted record ID: {self.db_manager.cursor.lastrowid}")
            return True
        except IntegrityError as e:
            self.db_manager.conn.rollback()
            print(f"Insert failed (integrity error): {e}")
            return False
        except Exception as e:
            self.db_manager.conn.rollback()
            print(f"Insert failed: {e}")
            return False

    def delete(self, table_name: str, condition: dict) -> bool:
        """Delete record (general, disallow unconditional delete)"""
        if not condition:
            print("delete() must receive condition!")
            return False
        self.db_manager.reconnect()
        try:
            # Cascade delete related records in intermediate tables
            if table_name == "ACTIVITY":
                act_ids = self._get_matched_ids(table_name, condition, "Act_id")
                if act_ids:
                    self.db_manager.cursor.execute(
                        f"DELETE FROM ACTIVITY_CHEMICAL WHERE Act_id IN ({','.join(map(str, act_ids))})"
                    )
                    self.db_manager.cursor.execute(
                        f"DELETE FROM ACTIVITY_AREA WHERE Act_id IN ({','.join(map(str, act_ids))})"
                    )
                    self.db_manager.cursor.execute(
                        f"DELETE FROM ACTIVITY_WORKER WHERE Act_id IN ({','.join(map(str, act_ids))})"
                    )

            where_clause = " AND ".join([f"{k}=%s" for k in condition.keys()])
            sql = f"DELETE FROM {table_name} WHERE {where_clause}"
            affected_rows = self.db_manager.cursor.execute(sql, tuple(condition.values()))
            self.db_manager.conn.commit()
            if affected_rows > 0:
                print(f"Delete successful! {affected_rows} record(s) deleted")
                return True
            else:
                print("Delete failed: No matching records found")
                return False
        except Exception as e:
            self.db_manager.conn.rollback()
            print(f"Delete failed: {e}")
            return False

    def list_all(self, table_name: str, fields: str = '*') -> list:
        """Query all records in table (general)"""
        self.db_manager.reconnect()
        try:
            sql = f"SELECT {fields} FROM {table_name}"
            self.db_manager.cursor.execute(sql)
            results = self.db_manager.cursor.fetchall()
            print(f"Query successful! {len(results)} record(s) found")
            return results
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    def list(self, table_name: str, condition: dict = None, fields: str = '*') -> list:
        """Query records by condition (general)"""
        self.db_manager.reconnect()
        try:
            if condition:
                where_clause = " AND ".join([f"{k}=%s" for k in condition.keys()])
                sql = f"SELECT {fields} FROM {table_name} WHERE {where_clause}"
                self.db_manager.cursor.execute(sql, tuple(condition.values()))
            else:
                sql = f"SELECT {fields} FROM {table_name}"
                self.db_manager.cursor.execute(sql)
            results = self.db_manager.cursor.fetchall()
            print(f"Query successful! {len(results)} matching record(s) found")
            return results
        except Exception as e:
            print(f"Query failed: {e}")
            return []

    def update(self, table_name: str, data: dict, condition: dict) -> bool:
        """Update record (general)"""
        if not data or not condition:
            print("update() must receive update data and condition!")
            return False
        self.db_manager.reconnect()
        try:
            set_clause = ", ".join([f"{k}=%s" for k in data.keys()])
            where_clause = " AND ".join([f"{k}=%s" for k in condition.keys()])
            sql = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
            values = tuple(data.values()) + tuple(condition.values())
            affected_rows = self.db_manager.cursor.execute(sql, values)
            self.db_manager.conn.commit()
            if affected_rows > 0:
                print(f"Update successful! {affected_rows} record(s) updated")
                return True
            else:
                print("Update failed: No matching records found")
                return False
        except Exception as e:
            self.db_manager.conn.rollback()
            print(f"Update failed: {e}")
            return False

    def _get_matched_ids(self, table_name: str, condition: dict, id_field: str) -> list:
        """Helper function: Get list of primary key IDs matching condition"""
        where_clause = " AND ".join([f"{k}=%s" for k in condition.keys()])
        sql = f"SELECT {id_field} FROM {table_name} WHERE {where_clause}"
        self.db_manager.cursor.execute(sql, tuple(condition.values()))
        return [row[id_field] for row in self.db_manager.cursor.fetchall()]

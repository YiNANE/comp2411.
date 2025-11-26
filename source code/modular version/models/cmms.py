"""
CMMS Main Class Module
Integrates all functional modules and provides a unified interface
"""
from database import DatabaseManager
from crud import CRUDOperations
from services import BusinessServices
from auth import Authentication


class CMMS:
    """Campus Maintenance Management System main class"""
    
    def __init__(self, host=None, user=None, password=None, db=None, port=None, charset=None):
        """Initialize CMMS system, automatically create database and tables"""
        # Initialize database manager
        self.db_manager = DatabaseManager(host, user, password, db, port, charset)
        self.db_manager.connect()
        self.db_manager.create_tables()
        
        # Initialize all functional modules
        self.crud = CRUDOperations(self.db_manager)
        self.services = BusinessServices(self.db_manager)
        self.auth = Authentication(self.db_manager)

    # ------------------------------
    # CRUD Operation Interfaces (delegated to CRUDOperations)
    # ------------------------------
    def insert(self, table_name: str, data_list: list) -> bool:
        """Insert records"""
        return self.crud.insert(table_name, data_list)

    def delete(self, table_name: str, condition: dict) -> bool:
        """Delete record"""
        return self.crud.delete(table_name, condition)

    def list_all(self, table_name: str, fields: str = '*') -> list:
        """Query all records"""
        return self.crud.list_all(table_name, fields)

    def list(self, table_name: str, condition: dict = None, fields: str = '*') -> list:
        """Query records by condition"""
        return self.crud.list(table_name, condition, fields)

    def update(self, table_name: str, data: dict, condition: dict) -> bool:
        """Update record"""
        return self.crud.update(table_name, data, condition)

    # ------------------------------
    # Business Service Interfaces (delegated to BusinessServices)
    # ------------------------------
    def search_cleaning_activities(self, start_date: str, end_date: str, building_name: str = None) -> list:
        """Search cleaning activities"""
        return self.services.search_cleaning_activities(start_date, end_date, building_name)

    def generate_worker_activity_report(self) -> list:
        """Generate worker activity report"""
        return self.services.generate_worker_activity_report()

    def get_manager_activities(self, manager_id: int) -> list:
        """Get activities responsible by manager"""
        return self.services.get_manager_activities(manager_id)

    def get_worker_activities(self, worker_id: int) -> list:
        """Get activities assigned to worker"""
        return self.services.get_worker_activities(worker_id)

    # ------------------------------
    # Authentication Interfaces (delegated to Authentication)
    # ------------------------------
    def admin_login(self, username: str, password: str) -> bool:
        """Admin login"""
        return self.auth.admin_login(username, password)

    def manager_login(self, manager_id: int) -> bool:
        """Manager login"""
        return self.auth.manager_login(manager_id)

    def worker_login(self, worker_id: int) -> bool:
        """Worker login"""
        return self.auth.worker_login(worker_id)

    # ------------------------------
    # Destructor: Close connection
    # ------------------------------
    def __del__(self):
        """Destructor, close database connection"""
        if hasattr(self, 'db_manager'):
            self.db_manager.close()

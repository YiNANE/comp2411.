"""
Authentication Module
Provides user login verification functionality
"""


class Authentication:
    """Authentication class"""
    
    def __init__(self, db_manager):
        """Initialize, requires database manager"""
        self.db_manager = db_manager

    def admin_login(self, username: str, password: str) -> bool:
        """Admin login"""
        self.db_manager.reconnect()
        self.db_manager.cursor.execute(
            "SELECT * FROM ADMIN WHERE Username=%s AND Password=%s", 
            (username, password)
        )
        return self.db_manager.cursor.fetchone() is not None

    def manager_login(self, manager_id: int) -> bool:
        """Manager login (verify via MSsn)"""
        self.db_manager.reconnect()
        self.db_manager.cursor.execute("SELECT * FROM MANAGER WHERE MSsn=%s", (manager_id,))
        return self.db_manager.cursor.fetchone() is not None

    def worker_login(self, worker_id: int) -> bool:
        """Worker login (verify via WSsn)"""
        self.db_manager.reconnect()
        self.db_manager.cursor.execute("SELECT * FROM WORKER WHERE WSsn=%s", (worker_id,))
        return self.db_manager.cursor.fetchone() is not None

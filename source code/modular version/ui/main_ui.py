"""
Main Interface Module
Provides main menu and role selection
"""
from ui.admin_ui import AdminUI
from ui.manager_ui import ManagerUI
from ui.worker_ui import WorkerUI


class MainUI:
    """Main interface class"""
    
    def __init__(self, cmms):
        """Initialize, requires CMMS instance"""
        self.cmms = cmms
        self.admin_ui = AdminUI(cmms)
        self.manager_ui = ManagerUI(cmms)
        self.worker_ui = WorkerUI(cmms)

    def run(self):
        """Run main program"""
        print("\n===== Campus Maintenance Management System (CMMS) =====")
        while True:
            print("\nSelect user role:")
            print("1. System Administrator (Admin)")
            print("2. Manager")
            print("3. Worker")
            print("4. Exit System")
            choice = input("Enter selection (1-4): ")

            if choice == "1":
                self._handle_admin()
            elif choice == "2":
                self._handle_manager()
            elif choice == "3":
                self._handle_worker()
            elif choice == "4":
                print("===== Thank you for using, goodbye! =====")
                break
            else:
                print("Invalid input, please try again!")

    def _handle_admin(self):
        """Handle admin login"""
        username = input("Enter admin username: ")
        password = input("Enter admin password: ")
        if self.cmms.admin_login(username, password):
            print(f"\nWelcome, {username}!")
            self.admin_ui.show_menu()
        else:
            print("Invalid username or password!")

    def _handle_manager(self):
        """Handle manager login"""
        manager_id = int(input("Enter manager ID: "))
        if self.cmms.manager_login(manager_id):
            print(f"\nWelcome, Manager ID: {manager_id}!")
            self.manager_ui.show_menu(manager_id)
        else:
            print("Manager ID does not exist!")

    def _handle_worker(self):
        """Handle worker login"""
        worker_id = int(input("Enter worker ID: "))
        if self.cmms.worker_login(worker_id):
            print(f"\nWelcome, Worker ID: {worker_id}!")
            self.worker_ui.show_menu(worker_id)
        else:
            print("Worker ID does not exist!")

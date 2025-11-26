"""
Manager Interface Module
Provides manager function menu and interaction
"""


class ManagerUI:
    """Manager interface class"""
    
    def __init__(self, cmms):
        """Initialize, requires CMMS instance"""
        self.cmms = cmms

    def show_menu(self, manager_id: int):
        """Show manager menu and handle user input"""
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
                self._handle_view_activities(manager_id)
            elif manager_choice == "2":
                self._handle_assign_worker(manager_id)
            elif manager_choice == "3":
                self._handle_view_workers(manager_id)
            else:
                print("Invalid input!")

    def _handle_view_activities(self, manager_id: int):
        """Handle view responsible activities"""
        activities = self.cmms.get_manager_activities(manager_id)
        print("Your responsible activities: ")
        for act in activities:
            print(f"Activity ID: {act['Act_id']}, Description: {act['Description']}")
        if not activities:
            print("No activities found.")

    def _handle_assign_worker(self, manager_id: int):
        """Handle assign worker to activity"""
        act_id = int(input("Enter activity ID: "))
        worker_id = int(input("Enter worker ID: "))
        worker = self.cmms.list("WORKER", {"WSsn": worker_id, "MSsn": manager_id})
        if worker:
            self.cmms.insert("ACTIVITY_WORKER", {"Act_id": act_id, "WSsn": worker_id})
        else:
            print("This worker is not under your management!")

    def _handle_view_workers(self, manager_id: int):
        """Handle view subordinate workers"""
        workers = self.cmms.list("WORKER", {"MSsn": manager_id})
        print("Your subordinate workers: ", workers)

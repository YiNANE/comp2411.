"""
Worker Interface Module
Provides worker function menu and interaction
"""


class WorkerUI:
    """Worker interface class"""
    
    def __init__(self, cmms):
        """Initialize, requires CMMS instance"""
        self.cmms = cmms

    def show_menu(self, worker_id: int):
        """Show worker menu and handle user input"""
        while True:
            print("\nWorker Function Menu:")
            print("1. View Assigned Activities")
            print("2. Exit Worker Interface")
            worker_choice = input("Enter selection (1-2): ")

            if worker_choice == "2":
                break
            elif worker_choice == "1":
                self._handle_view_activities(worker_id)
            else:
                print("Invalid input!")

    def _handle_view_activities(self, worker_id: int):
        """Handle view assigned activities"""
        activities = self.cmms.get_worker_activities(worker_id)
        print("Activities assigned to you: ", activities)

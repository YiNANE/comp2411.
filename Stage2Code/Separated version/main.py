"""
Main Program Entry Point
Start CMMS system
"""
from models.cmms import CMMS
from ui.main_ui import MainUI
from config import DB_CONFIG


def main():
    """
    CMMS application main entry point
    Provides role-based access to system functionalities
    """
    # Initialize CMMS system
    cmms = CMMS(password=DB_CONFIG['password'])

    # Create and run main interface
    main_ui = MainUI(cmms)
    main_ui.run()


if __name__ == "__main__":
    main()

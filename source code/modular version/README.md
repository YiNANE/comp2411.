# CMMS Campus Maintenance Management System - Modular Version

## Project Structure

```
Group44Stage2SourceCode/
├── main.py                 # Main program entry point
├── config.py               # Database configuration
├── database.py             # Database connection and table creation
├── crud.py                 # CRUD operations module
├── services.py             # Business services module
├── auth.py                 # Authentication module
├── models/                 # Model module
│   ├── __init__.py
│   └── cmms.py            # CMMS main class
└── ui/                     # User interface module
    ├── __init__.py
    ├── main_ui.py         # Main interface
    ├── admin_ui.py        # Admin interface
    ├── manager_ui.py      # Manager interface
    └── worker_ui.py       # Worker interface
```

## Module Description

### 1. config.py
- Contains database connection configuration information
- Centralized management of database connection parameters

### 2. database.py
- `DatabaseManager` class: Responsible for database connection, table creation and other initialization work
- Provides `connect()`, `create_tables()`, `reconnect()`, `close()` methods

### 3. crud.py
- `CRUDOperations` class: Provides general database CRUD functionality
- Methods: `insert()`, `delete()`, `list()`, `list_all()`, `update()`

### 4. services.py
- `BusinessServices` class: Provides project-specific business logic
- Methods:
  - `search_cleaning_activities()` - Query cleaning activities
  - `generate_worker_activity_report()` - Generate worker activity report
  - `get_manager_activities()` - Get activities responsible by manager
  - `get_worker_activities()` - Get activities assigned to worker

### 5. auth.py
- `Authentication` class: Provides user login verification functionality
- Methods: `admin_login()`, `manager_login()`, `worker_login()`

### 6. models/cmms.py
- `CMMS` class: Main class that integrates all functional modules
- Provides unified interface, delegates to various functional modules

### 7. ui/ directory
- `main_ui.py` - Main interface, handles role selection
- `admin_ui.py` - Admin interface, provides admin function menu
- `manager_ui.py` - Manager interface, provides manager function menu
- `worker_ui.py` - Worker interface, provides worker function menu

### 8. main.py
- Program entry point
- Initializes CMMS system and starts main interface

## Usage

1. Ensure required dependencies are installed:
```bash
pip install pymysql
```

2. Modify database configuration information in `config.py`

3. Run the program:
```bash
python main.py
```

## Modularization Advantages

1. **Clear Code Organization**: Modules divided by functionality, easy to understand and maintain
2. **Comprehensive Database Design**: Complete entity coverage, logical relationship design, data integrity assurance
3. **Separation of Concerns**: Each module responsible for specific functionality, follows single responsibility principle
4. **Easy to Extend**: New features can be added in corresponding modules
5. **Easy to Test**: Modules can be tested independently
6. **Code Reusability**: Modules can be reused in other projects

## System Limitations and Improvement Suggestions

1. **Security**: Plain text password storage poses security risks, lack of input validation and SQL injection protection; password encryption storage, input validation
2. **User Interface**: Pure command-line interface with poor user experience, lack of data visualization functions; develop web interface or desktop GUI application, add data charts and statistical visualizations, implement more detailed error descriptions and solution prompts
3. **Performance Optimization**: Poor performance with large data volume queries; add performance indexes
4. **System Integration**: No API interfaces for external calls, does not support data import/export

## Notes

- Original file `pythonMYsql.py` is preserved as reference
- All functionality remains unchanged, only code structure is reorganized
- Database configuration is centrally managed in `config.py`

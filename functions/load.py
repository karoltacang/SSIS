from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton
from PyQt6.QtCore import QCoreApplication
from functions.db_operations import get_db_manager

def load_mysql_data(table: QTableWidget, table_name: str):
    """Load data from MySQL database into table widget"""
    data_list = []
    db = get_db_manager()
    
    try:
        # Get data based on table type
        if table_name == "students":
            data = db.get_students_paginated()['data']
            headers = ["ID Number", "First Name", "Last Name", "Year Level", "Gender", "Program", "Options"]
        elif table_name == "programs":
            data = db.get_programs_paginated()['data']
            headers = ["Program Code", "Program Name", "College", "Options"]
        elif table_name == "colleges":
            data = db.get_colleges_paginated()['data']
            headers = ["College Code", "College Name", "Options"]
        else:
            return []
        
        # Set up table
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(len(data))
        
        # Populate table
        for row_idx, record in enumerate(data):
            row_dict = {}
            
            if table_name == "students":
                values = [
                    record.get('id_number'),
                    record.get('first_name'),
                    record.get('last_name'),
                    record.get('year_level'),
                    record.get('gender'),
                    record.get('program_code')
                ]
                keys = ["ID Number", "First Name", "Last Name", "Year Level", "Gender", "Program"]
            elif table_name == "programs":
                values = [
                    record.get('program_code'),
                    record.get('program_name'),
                    record.get('college_code')
                ]
                keys = ["Program Code", "Program Name", "College"]
            elif table_name == "colleges":
                values = [
                    record.get('college_code'),
                    record.get('college_name')
                ]
                keys = ["College Code", "College Name"]

            for col_idx, (key, value) in enumerate(zip(keys, values)):
                safe_value = str(value if value is not None else "")
                table.setItem(row_idx, col_idx, QTableWidgetItem(safe_value))
                row_dict[key] = safe_value

            # Add options button with proper capture
            options_button = QPushButton("⋮")
            def connect_button(t, b, r):
                b.clicked.connect(lambda _, t=t, b=b, r=r: t.show_options_menu(b, r))
            connect_button(table, options_button, row_idx)

            table.setCellWidget(row_idx, len(keys), options_button)
            data_list.append(row_dict)

            
    except Exception as e:
        print(f"Error loading data for {table_name}: {e}")
        return []
    
    return data_list

def load_data(main_window):
    """Load all data into main window tables"""
    try:
        main_window.studentsData = load_mysql_data(main_window.studentsTable, "students")
        main_window.programsData = load_mysql_data(main_window.programsTable, "programs")
        main_window.collegesData = load_mysql_data(main_window.collegesTable, "colleges")
        print("All data loaded successfully from MySQL")
    except Exception as e:
        print(f"Error loading data: {e}")
        raise
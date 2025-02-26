#reading, writing, deleting

import csv
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton
from PyQt6.QtCore import QCoreApplication

def load_csv_data(table: QTableWidget, file_path: str):
    
    data_list = []

    with open(file_path, newline='', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        header = [h.strip() for h in reader.fieldnames]
        table.setHorizontalHeaderLabels(header)
        
        data = list(reader)
        table.setRowCount(len(data))
        
        for row_idx, row in enumerate(data): 
            row_dict = {}
            for col_idx, key in enumerate(reader.fieldnames):
                value = row.get(key, "").strip()
                table.setItem(row_idx, col_idx, QTableWidgetItem(value))
                
                options_button = QPushButton("⋮")
                options_button.clicked.connect(lambda _, t=table, b=options_button, r=row_idx: t.show_options_menu(b, r))

                table.setCellWidget(row_idx, len(header), options_button)
                
                row_dict[key] = value
                
            data_list.append(row_dict)

    return data_list

def load_data(main_window):
    main_window.studentsData = load_csv_data(main_window.studentsTable, "data/students.csv")
    main_window.programsData = load_csv_data(main_window.programsTable, "data/programs.csv")
    main_window.collegesData = load_csv_data(main_window.collegesTable, "data/colleges.csv")
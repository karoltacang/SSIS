from PyQt6.QtWidgets import QMainWindow, QComboBox, QHeaderView, QTableWidget, QMessageBox
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6 import uic
from functions.load import load_data
from CustomTable import CustomTable
from functions.edit import EditEntry


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/mainWindow.ui", self)
        self.studentsData = []
        self.programsData = []
        self.collegesData = []
        
        for table, path in [
            (self.studentsTable, "data/students.csv"),
            (self.programsTable, "data/programs.csv"),
            (self.collegesTable, "data/colleges.csv"),
        ]:
            table.__class__ = CustomTable
            table.file_path = path
            table.main_window = self
        
        load_data(self)
        
        headers = self.get_current_table_headers()
        self.populate_sort_by(headers)
        
        self.display_counter()
        self.set_custom_column_widths()
        
        self.studentsTable.cellEntered.connect(lambda row, _: self.highlight_row(row))
        self.programsTable.cellEntered.connect(lambda row, _: self.highlight_row(row))
        self.collegesTable.cellEntered.connect(lambda row, _: self.highlight_row(row))
        
        self.addButton.setCurrentIndex(0)
        self.addButton.currentIndexChanged.connect(self.open_add_dialogue)
        
        self.searchInput.textChanged.connect(self.search_table)
        
        self.sortBy.currentIndexChanged.connect(self.sort_table)
        self.sortOrder.currentIndexChanged.connect(self.sort_table)
        self.tabWidget.currentChanged.connect(self.tab_changed)

    def display_counter(self):
        self.studentCount.setText(f"Number of Students: {self.studentsTable.rowCount()}")
        self.programCount.setText(f"Number of Programs: {self.programsTable.rowCount()}")
        self.collegeCount.setText(f"Number of Colleges: {self.collegesTable.rowCount()}")
        
    def open_edit_dialogue(self, table, row):
        table = self.get_current_table()
        if table:
            row_data = table.get_row_data(row)
            edit_dialog = EditEntry(table.file_path, row_data, table, row, mode="edit")
            edit_dialog.exec()
           
        header = self.get_current_table().horizontalHeader() 
        print(header)
        
    def open_add_dialogue(self):
        entry_type = self.addButton.currentText()

        if entry_type == "Add...":
            return

        file_path_map = {
            "Add New Student": "data/students.csv",
            "Add New Program": "data/programs.csv",
            "Add New College": "data/colleges.csv"
        }

        file_path = file_path_map.get(entry_type)

        if not file_path:
            return
        
        parent_table = self.get_current_table()
        
        add_dialog = EditEntry(file_path, None, self.get_current_table(), None, mode="add")
        add_dialog.main_window = self
        add_dialog.exec()
        self.addButton.setCurrentIndex(0)
        
    def search_table(self):
        query = self.searchInput.text().strip().lower()
        table = self.get_current_table()
        
        if not table or not query:
            for row in range(table.rowCount()):
                table.setRowHidden(row, False)
            return
        
        for row in range(table.rowCount()):
            row_matches = False
            
            for col in range(table.columnCount()):
                item = table.item(row, col)
                
                if item and query in item.text().strip().lower():
                    row_matches = True
                    break
                
            table.setRowHidden(row, not row_matches)
        
    def sort_table(self):
        table = self.get_current_table()
        
        selected_field = self.sortBy.currentText()
        selected_order = self.sortOrder.currentText()
        headers = self.get_current_table_headers()
        
        if selected_field == "Sort By..." or selected_field not in headers:
            return
        
        column_index = headers.index(selected_field)
        
        order = Qt.SortOrder.AscendingOrder if selected_order == "Ascending" else Qt.SortOrder.DescendingOrder
        
        table.sortItems(column_index, order)
        
    def highlight_row(self, row):
        table = self.get_current_table()
        if table:
            table.selectRow(row)
        
    def set_custom_column_widths(self):
        
        tables = [self.studentsTable, self.programsTable, self.collegesTable]
        
        for table in tables:
            header = table.horizontalHeader()
            header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

            if table == self.studentsTable:
                table.setColumnWidth(6, 30) 
                
            if table == self.programsTable:
                table.setColumnWidth(1, 680)  
                table.setColumnWidth(3, 30) 
                
            elif table == self.collegesTable:
                table.setColumnWidth(1, 800)  
                table.setColumnWidth(2, 30)  
            
            for col in range(table.columnCount()):
                if not (table == self.studentsTable and col in [6]) and not (table == self.programsTable and col in [1, 3]) and not (table == self.collegesTable and col in [1, 2]):
                    header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
    
    def populate_sort_by(self, headers):
        self.sortBy.clear()
        self.sortBy.addItem("Sort By...")
        
        for header in headers:
            self.sortBy.addItem(header)
        
        self.sortBy.setCurrentIndex(0)
                    
    def get_current_table(self):
        current_tab = self.tabWidget.currentIndex() 
        tab_table_map = {
            0: self.studentsTable,  
            1: self.programsTable,  
            2: self.collegesTable  
        }

        table = tab_table_map.get(current_tab, None)
        return table
    
    def get_current_table_headers(self):
        table = self.get_current_table()
        headers = []

        for col in range(table.columnCount() - 1):
            header_item = table.horizontalHeaderItem(col)    
            headers.append(header_item.text())
                
        return headers
    
    def tab_changed(self, index):
        headers = self.get_current_table_headers()
        self.populate_sort_by(headers)
        
        self.sortOrder.setCurrentIndex(0)
        
    def confirm_action(self, message):
        reply = QMessageBox.question(self, "Confirm Action", message, 
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                    QMessageBox.StandardButton.No)
        return reply == QMessageBox.StandardButton.Yes
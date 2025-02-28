from PyQt6.QtWidgets import QMainWindow, QComboBox, QHeaderView, QTableWidget, QMessageBox
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QIcon
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
        
        self.table_widgets = [self.studentsTable, self.programsTable, self.collegesTable]
        self.file_paths = ["data/students.csv", "data/programs.csv", "data/colleges.csv"]

        for table, path in zip(self.table_widgets, self.file_paths):
            table.__class__ = CustomTable
            table.file_path = path
            table.main_window = self
        
        try:
            load_data(self)
        except Exception as e:
            self.show_error(f"An error occurred while loading data: {e}")
        
        headers = self.get_current_table_headers()
        self.populate_combo_boxes(headers)
        
        self.display_counter()
        self.set_custom_column_widths()
        
        for table in self.table_widgets:    
            table.cellEntered.connect(lambda row, _: self.highlight_row(row))
        
        self.addButton.setCurrentIndex(0)
        self.addButton.currentIndexChanged.connect(self.open_add_dialogue)
        
        self.searchInput.returnPressed.connect(self.search_table)
        self.searchBy.currentIndexChanged.connect(self.search_table)
        
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
            edit_dialog = EditEntry(table.file_path, row_data, table, row, mode="edit", main_window=self)
            edit_dialog.exec()
           
        header = self.get_current_table().horizontalHeader() 
        
    def open_add_dialogue(self):
        entry_type = self.addButton.currentText()

        if entry_type == "Add...":
            return

        entry_types = ["Add New Student", "Add New Program", "Add New College"]

        if entry_type in entry_types:
            index = entry_types.index(entry_type)
            file_path = self.file_paths[index]
            table_widget = self.table_widgets[index]

        if not file_path:
            return
        
        add_dialog = EditEntry(file_path, None, table_widget, None, mode="add", main_window=self)
        add_dialog.main_window = self
        add_dialog.exec()
        
        self.addButton.blockSignals(True)
        self.addButton.setCurrentIndex(0)
        self.addButton.blockSignals(False)
    
    def search_table(self):
        
        query = self.searchInput.text().strip().lower()
        table = self.get_current_table()
        
        search_by_field = self.searchBy.currentText()
        headers = self.get_current_table_headers()
        
        if not table or not query:
            for row in range(table.rowCount()):
                table.setRowHidden(row, False)
            return
        
        if search_by_field == "Search All":
            for row in range(table.rowCount()):
                row_matches = False
                for col in range(table.columnCount()):
                    item = table.item(row, col)
                    if item and query in item.text().strip().lower():
                        row_matches = True
                        break
                table.setRowHidden(row, not row_matches)
            
        else:
            if search_by_field in headers:
                column_index = headers.index(search_by_field) 
           
                for row in range(table.rowCount()):
                    item = table.item(row, column_index)
                    row_matches = item and query in item.text().strip().lower()
                    table.setRowHidden(row, not row_matches)
                    
    
    def reset_search(self):
        self.searchInput.clear()
        table = self.get_current_table()

        if table:
            for row in range(table.rowCount()):
                table.setRowHidden(row, False)
        
    def sort_table(self):
        table = self.get_current_table()
        
        selected_field = self.sortBy.currentText()
        selected_order = self.sortOrder.currentText()
        headers = self.get_current_table_headers()
        
        if selected_order == "Order..." or selected_field not in headers:
            return
        
        column_index = headers.index(selected_field)
        
        order = Qt.SortOrder.AscendingOrder if selected_order == "Ascending" else Qt.SortOrder.DescendingOrder
        
        table.sortItems(column_index, order)
        
    def highlight_row(self, row):
        table = self.get_current_table()
        if table:
            table.selectRow(row)
        
    def populate_combo_boxes(self, headers):
        
        self.sortBy.clear()
        self.searchBy.clear()
        
        self.sortBy.addItem("Sort By...")
        self.searchBy.addItem("Search All")
        
        for header in headers:
            self.sortBy.addItem(header)
            self.searchBy.addItem(header)
        
        self.sortBy.setCurrentIndex(0)
        self.searchBy.setCurrentIndex(0)
                    
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
    
    def tab_changed(self):
        headers = self.get_current_table_headers()
        self.populate_combo_boxes(headers)
        self.reset_search()
        self.sortOrder.setCurrentIndex(0)
        
    def confirm_action(self, message):
        reply = QMessageBox.question(self, "Confirm Action", message, 
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                    QMessageBox.StandardButton.No)
        return reply == QMessageBox.StandardButton.Yes
    
    def set_custom_column_widths(self):
        
        for table in self.table_widgets:
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
from PyQt6.QtWidgets import QMainWindow, QComboBox, QHeaderView, QTableWidget, QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6.QtGui import QIcon
from functions.load import load_data
from CustomTable import CustomTable
from controllers.college_controller import EditCollege
from controllers.program_controller import EditProgram
from controllers.student_controller import EditStudent
from functions.db_operations import get_db_manager
from ui.mainWindow import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # Initialize database connection
        try:
            self.db = get_db_manager()
        except Exception as e:
            self.show_error(f"Database connection failed: {e}")
            return
        
        self.studentsData = []
        self.programsData = []
        self.collegesData = []
        
        # Table configuration
        self.table_widgets = [self.studentsTable, self.programsTable, self.collegesTable]
        self.table_names = ["students", "programs", "colleges"]

        # Set up custom table classes
        for table, table_name in zip(self.table_widgets, self.table_names):
            table.__class__ = CustomTable
            table.table_name = table_name
            table.main_window = self
        
        # Load data from database
        try:
            load_data(self)
        except Exception as e:
            self.show_error(f"An error occurred while loading data: {e}")
        
        # Initialize UI components
        headers = self.get_current_table_headers()
        self.populate_combo_boxes(headers)
        
        self.current_page = 1
        self.total_pages = 1  # Will be updated when loading data
        self.items_per_page = 10  # Should match your LIMIT in SQL
        
        self.load_current_page()  # Load data and populate table
        self.update_button_states()  # Enable/disable prev/next buttons
        self.update_page_info()
        
        # Connect pagination buttons
        self.firstPageButton.clicked.connect(self.go_to_first_page)
        self.previousButton.clicked.connect(self.go_to_previous_page)
        self.nextButton.clicked.connect(self.go_to_next_page)
        self.lastPageButton.clicked.connect(self.go_to_last_page)
        
        self.display_counter()
        self.set_custom_column_widths()
        
        # Connect signals
        for table in self.table_widgets:
            table.cellEntered.connect(lambda row, _: self.highlight_row(row))
        
        self.addButton.clicked.connect(self.open_add_dialogue)
        
        self.searchInput.returnPressed.connect(self.search_table)
        self.searchBy.currentIndexChanged.connect(self.search_table)
        
        self.sortOrder.currentIndexChanged.connect(self.sort_table)
        self.sortBy.currentIndexChanged.connect(self.sort_table)
        
        self.tabWidget.currentChanged.connect(self.tab_changed)

    def display_counter(self):
        """Display record counts"""
        self.studentCount.setText(f"Number of Students: {self.db.get_total_student_count()}")
        self.programCount.setText(f"Number of Programs: {self.db.get_total_program_count()}")
        self.collegeCount.setText(f"Number of Colleges: {self.db.get_total_college_count()}")
        
    def open_edit_dialogue(self, table, row):
        """Open edit dialog for selected row"""
        if table:
            row_data = table.get_row_data(row)
            table_name = getattr(table, 'table_name', '')
            
            # Use specialized dialog classes based on table name
            if table_name == "students":
                edit_dialog = EditStudent(
                    row_data=row_data,
                    parent_table=table,
                    row_index=row,
                    mode="edit",
                    main_window=self
                )
            elif table_name == "programs":
                edit_dialog = EditProgram(
                    row_data=row_data,
                    parent_table=table,
                    row_index=row,
                    mode="edit",
                    main_window=self
                )
            elif table_name == "colleges":
                edit_dialog = EditCollege(
                    row_data=row_data,
                    parent_table=table,
                    row_index=row,
                    mode="edit",
                    main_window=self
                )
            else:
                self.show_error(f"Unknown table type: {table_name}")
                return
                
            if edit_dialog.exec():
                # Refresh data after successful edit
                load_data(self)
           
    def open_add_dialogue(self):
        """Open add dialog for new entry"""
        table = self.get_current_table()
        table_name = getattr(table, 'table_name', '')

        if table_name == "students":
            add_dialog = EditStudent(
                row_data=None,
                parent_table=table,
                row_index=None,
                mode="add",
                main_window=self
            )
        elif table_name == "programs":
            add_dialog = EditProgram(
                row_data=None,
                parent_table=table,
                row_index=None,
                mode="add",
                main_window=self
            )
        elif table_name == "colleges":
            add_dialog = EditCollege(
                row_data=None,
                parent_table=table,
                row_index=None,
                mode="add",
                main_window=self
            )
        else:
            self.show_error(f"Unknown table type: {table_name}")
            return

        if add_dialog.exec():
            load_data(self)
            self.display_counter()

        
    def search_table(self):
        table = self.get_current_table()
        if not table:
            return

        table_name = getattr(table, 'table_name', '')
        search_column = self.searchBy.currentText()
        search_query = self.searchInput.text().strip()

        # Reset to first page when searching
        self.current_page = 1

        if not search_query:
            self.reset_search()
            return

        sort_field = None if self.sortBy.currentText() == "Sort By..." else self.sortBy.currentText()
        sort_order = 'ASC' if self.sortOrder.currentText() == "Ascending" else 'DESC'

        try:
            if table_name == "students":
                data, total_filtered = self.db.search_students(
                    page=self.current_page,
                    search_field=search_column,
                    search_value=search_query,
                    sort_field=sort_field,
                    sort_order=sort_order
                )

                self.total_pages = max(1, (total_filtered + self.items_per_page - 1) // self.items_per_page)
                self.programsData = data
                self.populate_table(self.studentsTable, data)

            elif table_name == "programs":
                data, total_filtered = self.db.search_programs(
                    page=self.current_page,
                    search_field=search_column,
                    search_value=search_query,
                    sort_field=sort_field,
                    sort_order=sort_order
                )

                self.total_pages = max(1, (total_filtered + self.items_per_page - 1) // self.items_per_page)
                self.programsData = data
                self.populate_table(self.programsTable, data)

            elif table_name == "colleges":
                data, total_filtered = self.db.search_colleges(
                    page=self.current_page,
                    search_field=search_column,
                    search_value=search_query,
                    sort_field=sort_field,
                    sort_order=sort_order
                )

                self.total_pages = max(1, (total_filtered + self.items_per_page - 1) // self.items_per_page)
                self.programsData = data
                self.populate_table(self.collegesTable, data)

            self.update_page_info()
            self.update_button_states()

        except Exception as e:
            self.show_error(f"Search failed: {e}")

    def sort_table(self):
        # Similar to search_table but without resetting current_page
        table = self.get_current_table()
        if not table:
            return
        
        table_name = getattr(table, 'table_name', '')
        selected_field = self.sortBy.currentText()
        selected_order = self.sortOrder.currentText()
        
        if selected_field == "Sort By..." or selected_order == "Order...":
            return
        
        sort_order = "ASC" if selected_order == "Ascending" else "DESC"
        search_query = self.searchInput.text().strip()
        search_field = self.searchBy.currentText() if self.searchBy.currentText() != "Search All" else None

        try:
            if table_name == "students":
                data, total_filtered = self.db.search_students(
                    page=self.current_page,
                    search_field=search_field,
                    search_value=search_query if search_query else None,
                    sort_field=selected_field,
                    sort_order=sort_order
                )
                self.studentsData = data
                self.total_pages = max(1, (total_filtered + self.items_per_page - 1) // self.items_per_page)
                self.populate_table(self.studentsTable, data)

            elif table_name == "programs":
                data, total_filtered = self.db.search_programs(
                    page=self.current_page,
                    search_field=search_field,
                    search_value=search_query if search_query else None,
                    sort_field=selected_field,
                    sort_order=sort_order
                )
                self.programsData = data
                self.total_pages = max(1, (total_filtered + self.items_per_page - 1) // self.items_per_page)
                self.populate_table(self.programsTable, data)

            elif table_name == "colleges":
                data, total_filtered = self.db.search_colleges(
                    page=self.current_page,
                    search_field=search_field,
                    search_value=search_query if search_query else None,
                    sort_field=selected_field,
                    sort_order=sort_order
                )
                self.collegesData = data
                self.total_pages = max(1, (total_filtered + self.items_per_page - 1) // self.items_per_page)
                self.populate_table(self.collegesTable, data)

            self.update_page_info()

        except Exception as e:
            self.show_error(f"Sort failed: {e}")
            
    def update_page_info(self):
        """Update the page information label"""
        self.pageInfo.setText(f"Page {self.current_page} of {self.total_pages}")

    def update_button_states(self):
        """Enable/disable pagination buttons based on current page"""
        self.firstPageButton.setEnabled(self.current_page > 1)
        self.previousButton.setEnabled(self.current_page > 1)
        self.nextButton.setEnabled(self.current_page < self.total_pages)
        self.lastPageButton.setEnabled(self.current_page < self.total_pages)

    def go_to_first_page(self):
        """Go to the first page"""
        if self.current_page != 1:
            self.current_page = 1
            self.load_current_page()

    def go_to_previous_page(self):
        """Go to the previous page"""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_current_page()

    def go_to_next_page(self):
        """Go to the next page"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_current_page()

    def go_to_last_page(self):
        """Go to the last page"""
        if self.current_page != self.total_pages:
            self.current_page = self.total_pages
            self.load_current_page()

    def load_current_page(self):
        """Load data for the current page"""
        table = self.get_current_table()
        if not table:
            return

        table_name = getattr(table, 'table_name', '')
        search_column = self.searchBy.currentText() if self.searchBy.currentText() != "Search All" else None
        search_query = self.searchInput.text().strip()
        sort_field = None if self.sortBy.currentText() == "Sort By..." else self.sortBy.currentText()
        sort_order = 'ASC' if table_name in ['programs', 'colleges'] else 'DESC'

        try:
            if table_name == "students":
                data, total_filtered = self.db.search_students(
                    page=self.current_page,
                    search_field=search_column,
                    search_value=search_query if search_query else None,
                    sort_field=sort_field,
                    sort_order=sort_order
                )
                self.studentsData = data
                self.populate_table(self.studentsTable, data)

            elif table_name == "programs":
                data, total_filtered = self.db.search_programs(
                    page=self.current_page,
                    search_field=search_column,
                    search_value=search_query if search_query else None,
                    sort_field=sort_field,
                    sort_order=sort_order
                )
                self.programsData = data
                self.populate_table(self.programsTable, data)

            elif table_name == "colleges":
                data, total_filtered = self.db.search_colleges(
                    page=self.current_page,
                    search_field=search_column,
                    search_value=search_query if search_query else None,
                    sort_field=sort_field,
                    sort_order=sort_order
                )
                self.collegesData = data
                self.populate_table(self.collegesTable, data)

            self.update_page_info()
            self.update_button_states()

        except Exception as e:
            self.show_error(f"Failed to load page: {e}")

    def reset_search(self):
        """Reset search filters and reload data"""
        self.current_page = 1
        self.searchInput.clear()
        
        try:
            table = self.get_current_table()
            table_name = getattr(table, 'table_name', '')
            
            if table_name == "students":
                total = self.db.get_total_student_count()
                self.total_pages = max(1, (total + self.items_per_page - 1) // self.items_per_page)
                data, total_filtered = self.db.search_students(page=self.current_page)
                self.studentsData = data
                self.populate_table(self.studentsTable, data)
                
            elif table_name == "programs":
                total = self.db.get_total_program_count()
                self.total_pages = max(1, (total + self.items_per_page - 1) // self.items_per_page)
                data, total_filtered = self.db.search_programs(page=self.current_page)
                self.programsData = data
                self.populate_table(self.programsTable, data)
                
            elif table_name == "colleges":
                total = self.db.get_total_college_count()
                self.total_pages = max(1, (total + self.items_per_page - 1) // self.items_per_page)
                data, total_filtered = self.db.search_colleges(page=self.current_page)
                self.collegesData = data
                self.populate_table(self.collegesTable, data)
                
            self.update_page_info()
            self.update_button_states()
            
        except Exception as e:
            self.show_error(f"Failed to reload data: {e}")
            
    def highlight_row(self, row):
        """Highlight selected row"""
        table = self.get_current_table()
        if table:
            table.selectRow(row)
        
    def populate_combo_boxes(self, headers):
        """Populate search and sort combo boxes"""
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
        """Get currently active table"""
        current_tab = self.tabWidget.currentIndex() 
        tab_table_map = {
            0: self.studentsTable,  
            1: self.programsTable,  
            2: self.collegesTable  
        }

        table = tab_table_map.get(current_tab, None)
        return table
    
    def get_current_table_headers(self):
        """Get headers of current table"""
        table = self.get_current_table()
        headers = []

        if table:
            for col in range(table.columnCount() - 1):  # Exclude options column
                header_item = table.horizontalHeaderItem(col)
                if header_item:
                    headers.append(header_item.text())
                
        return headers
    
    def tab_changed(self):
        """Handle tab change"""
        headers = self.get_current_table_headers()
        self.populate_combo_boxes(headers)
        self.reset_search()
        self.sortOrder.setCurrentIndex(0)
                
    def populate_table(self, table, data):
        table.clearContents()
        table.setRowCount(0)

        if not data:
            return

        # Get column order from the first row's keys if data is dictionaries
        if isinstance(data[0], dict):
            columns = list(data[0].keys())
            # Set table column headers if needed
            if table.columnCount() == 0 or table.horizontalHeaderItem(0) is None:
                table.setColumnCount(len(columns))
                table.setHorizontalHeaderLabels(columns)
        
        table.setRowCount(len(data))
        
        for row_idx, row_data in enumerate(data):
            if isinstance(row_data, dict):
                # Handle dictionary rows
                for col_idx, col_name in enumerate(columns):
                    value = row_data.get(col_name, '')
                    table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            elif isinstance(row_data, (tuple, list)):
                # Handle sequence rows (original behavior)
                for col_idx, value in enumerate(row_data):
                    table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            else:
                print(f"Warning: Unsupported row type {type(row_data)} at row {row_idx}")
                
        if isinstance(table, CustomTable):
            table.add_option_buttons()
        
    def confirm_action(self, message):
        """Show confirmation dialog"""
        reply = QMessageBox.question(
            self, 
            "Confirm Action", 
            message, 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.No
        )
        return reply == QMessageBox.StandardButton.Yes
    
    def show_error(self, message):
        """Show error message"""
        QMessageBox.critical(self, "Error", message)
    
    def set_custom_column_widths(self):
        """Set custom column widths for tables"""
        for table in self.table_widgets:
            header = table.horizontalHeader()
            header.setDefaultAlignment(Qt.AlignmentFlag.AlignLeft)

            if table == self.studentsTable:
                table.setColumnWidth(6, 30)  # Options column
                
            elif table == self.programsTable:
                table.setColumnWidth(1, 680)  # Program Name
                table.setColumnWidth(3, 30)   # Options column
                
            elif table == self.collegesTable:
                table.setColumnWidth(1, 800)  # College Name
                table.setColumnWidth(2, 30)   # Options column
            
            # Set other columns to stretch
            for col in range(table.columnCount()):
                if not (table == self.studentsTable and col in [6]) and \
                   not (table == self.programsTable and col in [1, 3]) and \
                   not (table == self.collegesTable and col in [1, 2]):
                    header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
    
    def closeEvent(self, event):
        """Handle application close event"""
        try:
            # Close database connection
            self.db.close_connection()
        except:
            pass
        event.accept()
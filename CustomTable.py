from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QMenu
from PyQt6.QtCore import QPoint
from controllers.college_controller import delete_college
from controllers.program_controller import delete_program
from controllers.student_controller import delete_student

class CustomTable(QTableWidget):
    def __init__(self, parent=None, table_name="", main_window=None):
        super().__init__(parent)

        self.table_name = table_name
        self.main_window = main_window

    def show_options_menu(self, button, row):
        """Show context menu for table row options"""
        menu = QMenu(button)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ccc;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: rgba(0, 0, 0, 0.1);
            }
        """)
        
        # Get unique ID from first column
        unique_id = self.item(row, 0).text() if self.item(row, 0) else None

        if unique_id:
            parent_window = self.window()
            menu.addAction("Edit", lambda: parent_window.open_edit_dialogue(self, row))
            if self.table_name == "students":
                menu.addAction("Delete", lambda: delete_student(self.main_window, unique_id))
            elif self.table_name == "programs":
                menu.addAction("Delete", lambda: delete_program(self.main_window, unique_id))
            elif self.table_name == "colleges":
                menu.addAction("Delete", lambda: delete_college(self.main_window, unique_id))

            

            pos = button.mapToGlobal(QPoint(0, button.height()))
            menu.exec(pos)
        
    def add_option_buttons(self):
        """Add option buttons to all rows"""
        for row in range(self.rowCount()):
            # Remove existing button first
            self.removeCellWidget(row, self.columnCount() - 1) 
            
            # Create new options button
            options_button = QPushButton("⋮")
            options_button.setFixedSize(35, 35)
            options_button.clicked.connect(
                lambda _, t=self, b=options_button, r=row: t.show_options_menu(b, r)
            )

            self.setCellWidget(row, self.columnCount() - 1, options_button)
                
    def get_row_data(self, row):
        """Get data from specified row"""
        row_data = {}
        
        for col in range(self.columnCount() - 1):  # Exclude options column
            header_item = self.horizontalHeaderItem(col)
            if header_item:
                column_name = header_item.text() 
                cell_item = self.item(row, col)
                row_data[column_name] = cell_item.text() if cell_item else ""

        return row_data
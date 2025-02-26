from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton, QMenu
from PyQt6.QtCore import QPoint
from functions.edit import EditEntry
from functions.delete import delete_row_from_table

class CustomTable(QTableWidget):
    def __init__(self, parent=None, file_path=""):
        super().__init__(parent)

        self.file_path = file_path
        self.main_window = None

        self.itemChanged.connect(self.add_option_buttons)

    def show_options_menu(self, button, row):

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
        
        unique_id = self.item(row, 0).text() if self.item(row, 0) else None

        if unique_id:
            parent_window = self.window()
            menu.addAction("Edit", lambda: parent_window.open_edit_dialogue(self, row))
            menu.addAction("Delete", lambda: delete_row_from_table(self.main_window, self.file_path, unique_id, row))

            pos = button.mapToGlobal(QPoint(0, button.height()))
            menu.exec(pos)
        
    def add_option_buttons(self):
        for row in range(self.rowCount()):
            self.removeCellWidget(row, self.columnCount() - 1) 
            options_button = QPushButton("⋮")
            options_button.setFixedSize(35, 35)
            options_button.clicked.connect(lambda _, t=self, b=options_button, r=row: t.show_options_menu(b, r))

            self.setCellWidget(row, self.columnCount() - 1, options_button)
                
    def get_row_data(self, row):
        row_data = {}
        
        for col in range(self.columnCount()):
            header_item = self.horizontalHeaderItem(col)
            if header_item:
                column_name = header_item.text() 
                cell_item = self.item(row, col)
                row_data[column_name] = cell_item.text() if cell_item else ""

        return row_data
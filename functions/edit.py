from PyQt6.QtWidgets import QDialog, QTableWidgetItem, QCompleter, QLineEdit, QComboBox, QSpinBox
from PyQt6.QtCore import Qt, QCoreApplication
from PyQt6 import uic
from functions.csv_operations import edit_row_in_csv, add_row_to_csv

DEPENDENCY_MAP = {
    "data/colleges.csv": {"file": "data/programs.csv", "parent_key": "College", "child_key": "Program Code"},
    "data/programs.csv": {"file": "data/students.csv", "parent_key": "Program", "child_key": "ID Number"}
}

class EditEntry(QDialog):
    def __init__(self, file_path, row_data=None, parent_table=None, row_index=None, mode="edit"):
        super().__init__()
        
        self.file_path = file_path
        self.main_window = None
        self.parent_table = parent_table
        self.row_index = row_index
        self.row_data = row_data
        self.mode = mode
        
        if "students" in file_path:
            uic.loadUi("ui/editStudent.ui", self)
            self.unique_id_field = "ID Number"
        elif "programs" in file_path:
            uic.loadUi("ui/editProgram.ui", self)
            self.unique_id_field = "Program Code"
        elif "colleges" in file_path:
            uic.loadUi("ui/editCollege.ui", self)
            self.unique_id_field = "College Code"
        else:
            raise ValueError("Unknown entry type")

        if mode == "edit":
            self.loadEditUi(row_data)
            
        self.buttonBox.accepted.connect(self.save_changes)
        self.buttonBox.rejected.connect(self.reject)

    def loadEditUi(self, row_data):
        for key, value in row_data.items():
            widget = getattr(self, self.get_widget_name(key), None)
            if widget:
                if isinstance(widget, QLineEdit):
                    widget.setText(value)
                elif isinstance(widget, QSpinBox):
                    widget.setValue(int(value))
                elif isinstance(widget, QComboBox):
                    widget.setCurrentText(value)

    def save_changes(self):
        
        new_data = self.row_data if self.mode == "edit" else {key: "" for key in self.get_fields()}
        
        for key in new_data:
            widget = getattr(self, self.get_widget_name(key), None)

            if isinstance(widget, QLineEdit):
                new_data[key] = widget.text() 

            elif isinstance(widget, QSpinBox):
                new_data[key] = str(widget.value())  

            elif isinstance(widget, QComboBox):
                new_data[key] = widget.currentText()

        if self.mode == "add":
                add_row_to_csv(self.file_path, list(new_data.values()))
                self.add_row_to_table(new_data)
                self.main_window.display_counter()
                
        else:
            edit_row_in_csv(self.file_path, self.row_data[self.unique_id_field], list(new_data.values()))
            self.update_table_row(new_data)

        self.accept()
        
    def add_row_to_table(self, new_data):
        if self.parent_table:
            row_pos = self.parent_table.rowCount()
            self.parent_table.insertRow(row_pos)
            for col, value in enumerate(new_data.values()):
                self.parent_table.setItem(row_pos, col, QTableWidgetItem(value)) 
        
        self.parent_table.add_option_buttons()
                
    def update_table_row(self, new_data):
        for col, value in enumerate(new_data.values()): 
            self.parent_table.item(self.row_index, col).setText(value)  

    def get_widget_name(self, field_name):
        formatted_key = field_name.strip().replace(" ", "")
        return formatted_key[0].lower() + formatted_key[1:] + "Input"
    
    def get_fields(self):
        if "students" in self.file_path:
            return ["ID Number", "First Name", "Last Name", "Year Level", "Gender", "Program"]
        elif "programs" in self.file_path:
            return ["Program Code", "Program Name", "College"]
        elif "colleges" in self.file_path:
            return ["College Code", "College Name"]
        return []
    
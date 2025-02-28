import re
from PyQt6.QtWidgets import QDialog, QTableWidgetItem, QCompleter, QLineEdit, QComboBox, QSpinBox, QTableWidget, QPushButton, QLabel, QMessageBox
from PyQt6.QtCore import Qt, QCoreApplication, pyqtSignal
from PyQt6 import uic
from functions.csv_operations import edit_row_in_csv, add_row_to_csv, read_csv, write_csv

DEPENDENCY_MAP = {
    "data/colleges.csv": {"file": "data/programs.csv", "table": "programsTable", "key": "College Code", "child_key": "College"},
    "data/programs.csv": {"file": "data/students.csv", "table": "studentsTable", "key": "Program Code", "child_key": "Program"}
}

class EditEntry(QDialog):
    
    save_button_state_changed = pyqtSignal(bool)
    def __init__(self, file_path, row_data=None, parent_table=None, row_index=None, mode="edit", main_window=None):
        super().__init__()
        
        self.file_path = file_path
        self.main_window = main_window
        self.parent_table = parent_table
        self.row_index = row_index
        self.row_data = row_data
        self.mode = mode
        
        if "students" in file_path:
            uic.loadUi("ui/editStudent.ui", self)
            self.unique_id_field = "ID Number"
            self.populate_code_combobox("data/programs.csv", self.programInput, "Program Code")
        elif "programs" in file_path:
            uic.loadUi("ui/editProgram.ui", self)
            self.unique_id_field = "Program Code"
            self.populate_code_combobox("data/colleges.csv", self.collegeInput, "College Code")
        elif "colleges" in file_path:
            uic.loadUi("ui/editCollege.ui", self)
            self.unique_id_field = "College Code"
        else:
            raise ValueError("Unknown entry type")
        
        self.errorLabel = self.findChild(QLabel, "error")
        self.saveButton = self.findChild(QPushButton, "save")
        self.cancelButton = self.findChild(QPushButton, "cancel")
        
        self.saveButton.clicked.connect(self.save_changes)
        self.cancelButton.clicked.connect(self.reject)

        if mode == "edit":
            self.populate_dialogue_data(row_data)
            self.errorLabel.hide()
            
        self.connect_field_signals()
        self.update_save_button_state()

    def populate_dialogue_data(self, row_data):
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
        
        if self.mode == "add":
            if not self.main_window.confirm_action("Are you sure you want to add this entry?"):
                return
        elif self.mode == "edit":
            if not self.main_window.confirm_action("Are you sure you want to save these changes?"):
                return
            
        self.accept()
            
        header, rows = read_csv(self.file_path)
        
        if self.mode == "edit":
            old_data = None
            for row in rows:
                if row[0] == self.row_data[self.unique_id_field]:
                    old_data = dict(zip(header, row))
                    break
    
        new_data = {key: "" for key in self.get_fields()}
        
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
                QMessageBox.information(self, "Success", "Entry added successfully!")
                
        else:
            self.edit(self.file_path, self.row_data[self.unique_id_field], old_data, new_data)
            QMessageBox.information(self, "Success", "Entry editted successfully!")
        
    def get_data_map(self, file_path, code_column):
 
        try:
            header, rows = read_csv(file_path)
            if not header or not rows:
                print(f"Empty CSV file: {file_path}")
                return {}
                
            code_index = header.index(code_column)
            return {row[code_index]: row[code_index] for row in rows}
            
        except ValueError as e:
            print(f"Column error in {file_path}: {str(e)}")
            return {}
        except Exception as e:
            print(f"Error reading {file_path}: {str(e)}")
            return {}

    def populate_code_combobox(self, file_path, combo_box: QComboBox, code_column):
        
        data_map = self.get_data_map(file_path, code_column)
        codes = sorted(data_map.keys())
        combo_box.valid_codes = set(codes)

        combo_box.addItems(codes)

        completer = QCompleter(codes, combo_box)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        combo_box.setCompleter(completer)
        combo_box.setEditable(True)
        combo_box.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        
        combo_box.currentTextChanged.connect(self.update_save_button_state)
        
    def edit(self, file_path, unique_id, old_data, new_data):
         
        changed_value_keys = [key for key in old_data if old_data[key] != new_data[key]]
        
        edit_row_in_csv(file_path, unique_id, list(new_data.values()))
        self.update_table_row(new_data, self.parent_table, self.row_index)
        
        if file_path == "data/students.csv":
            return
        
        for key in changed_value_keys:
            
            child_file = DEPENDENCY_MAP[file_path]["file"]
            parent_key = DEPENDENCY_MAP[file_path]["key"]
            child_key = DEPENDENCY_MAP[file_path]["child_key"]
            child_table_name = DEPENDENCY_MAP[file_path]["table"]
            
            if parent_key in key:
                header, rows = read_csv(child_file)
                
                child_table = self.main_window.tabWidget.findChild(QTableWidget, child_table_name)
                
                row_index = 0
                for row in rows:
                    if row[header.index(child_key)] == unique_id:
                        row[header.index(child_key)] = new_data[parent_key]
                        
                        new_child_data = {header[i]: row[i] for i in range(len(header))}  
                        self.update_table_row(new_child_data, child_table, row_index)
                                            
                    row_index += 1
                
                write_csv(child_file, header, rows)

    def add_row_to_table(self, new_data):
        if self.parent_table:
            row_pos = self.parent_table.rowCount()
            self.parent_table.insertRow(row_pos)
            for col, value in enumerate(new_data.values()):
                self.parent_table.setItem(row_pos, col, QTableWidgetItem(value)) 
        
        self.parent_table.add_option_buttons()
                
    def update_table_row(self, new_data, table, row_index):
        for col, value in enumerate(new_data.values()): 
            table.item(row_index, col).setText(value)  

    def get_widget_name(self, field_name):
        formatted_key = field_name.strip().replace(" ", "")
        return formatted_key[0].lower() + formatted_key[1:] + "Input"
    
    def get_fields(self):
        field_mappings = {
            "students": ["ID Number", "First Name", "Last Name", "Year Level", "Gender", "Program"],
            "programs": ["Program Code", "Program Name", "College"],
            "colleges": ["College Code", "College Name"]
        }
        for key, fields in field_mappings.items():
            if key in self.file_path:
                return fields
        return []
    
    def connect_field_signals(self):
        fields = self.get_fields()
        for key in self.get_fields():
            widget = getattr(self, self.get_widget_name(key), None)
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.update_save_button_state)
            elif isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self.update_save_button_state)
            elif isinstance(widget, QComboBox):
                widget.currentIndexChanged.connect(self.update_save_button_state)
                
    def validate_all_fields(self):
        
        is_valid = True
        found_empty_field = False
        error_messages = []
        fields = self.get_fields()

        pk_field = next((f for f in ["ID Number", "Program Code", "College Code"] if f in fields), None)
        pk_value = None
        if pk_field:
            widget = getattr(self, self.get_widget_name(pk_field), None)
            if isinstance(widget, QLineEdit):
                pk_value = widget.text().strip()

        for key in fields:
            
            widget = getattr(self, self.get_widget_name(key), None)
            
            if isinstance(widget, QLineEdit):
                current_text = widget.text().strip()
                
                if not current_text:
                    is_valid = False
                    found_empty_field = True
                    
                if key != "ID Number":
                    if not re.match(r'^[A-Za-z\s\-]+$', current_text):
                        is_valid = False
                        error_messages.append(f"{key} must contain only letters")
                        
                if key == "ID Number" and len(widget.text().replace("-", "")) != 8:
                    is_valid = False
                    error_messages.append("ID Number must contain 8 digits")
                    
            elif isinstance(widget, QSpinBox):
                if widget.value() == 0:
                    is_valid = False
                    error_messages.append("Year level cannot be 0")
                    
            elif isinstance(widget, QComboBox):
                current_text = widget.currentText().strip()
                
                if not current_text or (not widget.isEditable() and widget.currentIndex() == 0):
                    is_valid = False
                    found_empty_field = True
                elif hasattr(widget, 'valid_codes'): 
                    is_valid_code = False
                    for code in widget.valid_codes:
                        if code.lower() == current_text.lower():
                            if code != current_text:
                                widget.setCurrentText(code)
                            is_valid_code = True
                            break
                    
                    if not is_valid_code:
                        is_valid = False
                        error_messages.append(f"Please choose a valid {key}.")
                
        if found_empty_field:
            self.errorLabel.setText("Please input all necessary information")
        elif error_messages:
            self.errorLabel.setText("\n".join(error_messages))
        self.errorLabel.setVisible(not is_valid)
            
        if is_valid and pk_field and pk_value and self.duplicate_check(pk_field, pk_value):
            if self.duplicate_check(pk_field, pk_value):
                self.errorLabel.setText(f"{pk_field} already exists in records.")
                self.errorLabel.setVisible(True)
            is_valid = False

        self.saveButton.setEnabled(is_valid)
        
        return is_valid
    
    def duplicate_check(self, field_name, field_value):
    
        file_mappings = {
            "ID Number": ("data/students.csv", "ID Number"),
            "Program Code": ("data/programs.csv", "Program Code"),
            "College Code": ("data/colleges.csv", "College Code")
        }
        if field_name not in file_mappings:
            return False
            
        file_path, unique_field = file_mappings[field_name]
        header, rows = read_csv(file_path)
        if not header:
            return False
        
        field_index = header.index(unique_field)
        current_id = getattr(self, 'row_data', {}).get(unique_field, "") if self.mode == "edit" else None
        
        for row in rows:
            existing_value = row[field_index]
            
            if existing_value == field_value:
                if not current_id or existing_value != current_id:
                    return True
        return False
    
    def update_save_button_state(self):
        is_valid = self.validate_all_fields()
        self.save_button_state_changed.emit(is_valid)
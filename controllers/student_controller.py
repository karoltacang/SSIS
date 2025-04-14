"""Student-specific operations for add, edit, and delete functionality"""

import re
from PyQt6.QtWidgets import QDialog, QTableWidgetItem, QCompleter, QLineEdit, QComboBox, QSpinBox, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from ui.editStudent import Ui_EditStudentDialog
from functions.db_operations import get_db_manager
from functions.load import load_data

class EditStudent(QDialog):
    """Dialog for adding/editing student records"""
    
    save_button_state_changed = pyqtSignal(bool)
    
    def __init__(self, row_data=None, parent_table=None, row_index=None, mode="edit", main_window=None):
        super().__init__()
        self.ui = Ui_EditStudentDialog()
        self.ui.setupUi(self)
        
        self.main_window = main_window
        self.parent_table = parent_table
        self.row_index = row_index
        self.row_data = row_data
        self.mode = mode
        self.db = get_db_manager()
        
        # Find UI elements
        self.errorLabel = self.findChild(QLabel, "error")
        self.saveButton = self.findChild(QPushButton, "save")
        self.cancelButton = self.findChild(QPushButton, "cancel")
        
        self.iDNumberInput = self.ui.iDNumberInput
        self.firstNameInput = self.ui.firstNameInput
        self.lastNameInput = self.ui.lastNameInput
        self.yearLevelInput = self.ui.yearLevelInput
        self.genderInput = self.ui.genderInput
        self.programInput = self.ui.programInput
        
        # Populate program dropdown
        self.populate_program_dropdown()
        
        # Connect signals
        self.saveButton.clicked.connect(self.save_changes)
        self.cancelButton.clicked.connect(self.reject)
        
        # Populate data for edit mode
        if mode == "edit" and row_data:
            self.populate_dialogue_data(row_data)
            
        if self.errorLabel:
            self.errorLabel.hide()
            
        self.connect_field_signals()
        self.update_save_button_state()

    def populate_program_dropdown(self):
        """Populate program combobox with available programs"""
        try:
            programs = self.db.get_program_codes()
            
            self.programInput.valid_codes = set(programs)
            self.programInput.clear()
            self.programInput.addItems(sorted(programs))
            
            # Set up completer
            completer = QCompleter(programs, self.programInput)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.programInput.setCompleter(completer)
            self.programInput.setEditable(True)
            self.programInput.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            
            self.programInput.currentTextChanged.connect(self.update_save_button_state)
            
        except Exception as e:
            print(f"Error populating program dropdown: {e}")

    def populate_dialogue_data(self, row_data):
        """Populate dialog fields with existing student data"""
        self.iDNumberInput.setText(str(row_data.get("ID Number", "")))
        self.firstNameInput.setText(str(row_data.get("First Name", "")))
        self.lastNameInput.setText(str(row_data.get("Last Name", "")))
        
        try:
            self.yearLevelInput.setValue(int(row_data.get("Year Level", 0)))
        except (ValueError, TypeError):
            self.yearLevelInput.setValue(1)
            
        self.genderInput.setCurrentText(str(row_data.get("Gender", "")))
        self.programInput.setCurrentText(str(row_data.get("Program", "")))

    def collect_form_data(self):
        """Collect data from student form fields"""
        return {
            "ID Number": self.iDNumberInput.text().strip(),
            "First Name": self.firstNameInput.text().strip(),
            "Last Name": self.lastNameInput.text().strip(),
            "Year Level": self.yearLevelInput.value(),
            "Gender": self.genderInput.currentText().strip(),
            "Program": self.programInput.currentText().strip()
        }

    def save_changes(self):
        """Save student changes to database"""
        if self.mode == "add":
            if not self.main_window.confirm_action("Are you sure you want to add this student?"):
                return
        elif self.mode == "edit":
            if not self.main_window.confirm_action("Are you sure you want to save these changes?"):
                return
        
        try:
            new_data = self.collect_form_data()
            
            # Convert to database format
            db_data = {
                "id_number": new_data["ID Number"],
                "first_name": new_data["First Name"],
                "last_name": new_data["Last Name"],
                "year_level": new_data["Year Level"],
                "gender": new_data["Gender"],
                "program_code": new_data["Program"]
            }
            
            if self.mode == "add":
                result = self.db.add_record("student", db_data)
                if result > 0:
                    QMessageBox.information(self, "Success", "Student added successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add student")
            else:  # edit mode
                old_id = self.row_data["ID Number"]
                result = self.db.update_record("student", "id_number", old_id, db_data)
                if result > 0:
                    QMessageBox.information(self, "Success", "Student updated successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update student")
                    
        except Exception as e:
            print(f"Error saving student: {e}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def connect_field_signals(self):
        """Connect field change signals for validation"""
        self.iDNumberInput.textChanged.connect(self.update_save_button_state)
        self.firstNameInput.textChanged.connect(self.update_save_button_state)
        self.lastNameInput.textChanged.connect(self.update_save_button_state)
        self.yearLevelInput.valueChanged.connect(self.update_save_button_state)
        self.genderInput.currentIndexChanged.connect(self.update_save_button_state)
        self.programInput.currentIndexChanged.connect(self.update_save_button_state)

    def validate_all_fields(self):
        """Validate all student form fields"""
        is_valid = True
        found_empty_field = False
        error_messages = []
        
        # Get form data
        form_data = self.collect_form_data()
        
        id_number = form_data["ID Number"]
        first_name = form_data["First Name"]
        last_name = form_data["Last Name"]
        year_level = form_data["Year Level"]
        gender = form_data["Gender"]
        program = form_data["Program"]
        
        # Check for empty fields
        if not all([id_number, first_name, last_name, gender, program]):
            is_valid = False
            found_empty_field = True
        
        # Validate ID Number format (8 digits)
        if id_number and len(id_number.replace("-", "")) != 8:
            is_valid = False
            error_messages.append("ID Number must contain 8 digits")
        
        # Validate names (letters only)
        if first_name and not re.match(r'^[A-Za-z\s\-]+$', first_name):
            is_valid = False
            error_messages.append("First Name must contain only letters")
            
        if last_name and not re.match(r'^[A-Za-z\s\-]+$', last_name):
            is_valid = False
            error_messages.append("Last Name must contain only letters")
        
        # Validate year level
        if year_level == 0:
            is_valid = False
            error_messages.append("Year level cannot be 0")
        
        # Validate program code
        if program and hasattr(self.programInput, 'valid_codes'):
            is_valid_code = any(code.lower() == program.lower() for code in self.programInput.valid_codes)
            if not is_valid_code:
                is_valid = False
                error_messages.append("Please choose a valid Program.")
        
        # Set error messages
        if found_empty_field:
            if self.errorLabel:
                self.errorLabel.setText("Please input all necessary information")
        elif error_messages:
            if self.errorLabel:
                self.errorLabel.setText("\n".join(error_messages))
        
        if self.errorLabel:
            self.errorLabel.setVisible(not is_valid)
        
        # Check for duplicate ID
        if is_valid and self.mode=="add" and id_number and self.check_duplicate_id(id_number):
            if self.errorLabel:
                self.errorLabel.setText("ID Number already exists in records.")
                self.errorLabel.setVisible(True)
            is_valid = False

        self.saveButton.setEnabled(is_valid)
        return is_valid

    def check_duplicate_id(self, id_number):
        """Check for duplicate student ID"""
        try:
            current_id = None
            if self.mode == "edit" and self.row_data:
                current_id = self.row_data.get("ID Number")
            
            return self.db.check_record_exists("Student", "id_number", id_number, current_id)
        except Exception as e:
            print(f"Error checking for duplicate ID: {e}")
            return False

    def update_save_button_state(self):
        """Update save button state based on validation"""
        is_valid = self.validate_all_fields()
        self.save_button_state_changed.emit(is_valid)


def delete_student(main_window, id_number):
    """Delete student record"""
    if not id_number:
        QMessageBox.warning(main_window, "Error", "No student ID provided")
        return
    
    confirm_msg = f"Delete student with id number {id_number}?"
    
    if not main_window.confirm_action(confirm_msg):
        return
    
    try:
        db = get_db_manager()
        result = db.delete_record("student", "id_number", id_number)
        
        if result > 0:
            load_data(main_window)
            main_window.display_counter()
            QMessageBox.information(
                main_window, 
                "Success", 
                f"Student with ID number {id_number} deleted successfully."
            )
        else:
            QMessageBox.warning(main_window, "Error", "Student not found or could not be deleted")
            
    except Exception as e:
        error_msg = f"Error deleting student {id_number}: {str(e)}"
        print(error_msg)
        QMessageBox.critical(main_window, "Error", error_msg)

"""Program-specific operations for add, edit, and delete functionality"""

import re
from PyQt6.QtWidgets import QDialog, QCompleter, QLineEdit, QComboBox, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from ui.editProgram import Ui_EditProgramDialog
from functions.db_operations import get_db_manager
from functions.load import load_data

class EditProgram(QDialog):
    """Dialog for adding/editing program records"""
    
    save_button_state_changed = pyqtSignal(bool)
    
    def __init__(self, row_data=None, parent_table=None, row_index=None, mode="edit", main_window=None):
        super().__init__()
        self.ui = Ui_EditProgramDialog()
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
        
        self.programCodeInput = self.ui.programCodeInput
        self.programNameInput = self.ui.programNameInput
        self.collegeInput = self.ui.collegeInput
        
        # Populate college dropdown
        self.populate_college_dropdown()
        
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

    def populate_college_dropdown(self):
        """Populate college combobox with available colleges"""
        try:
            colleges = self.db.get_college_codes()
            
            self.collegeInput.valid_codes = set(colleges)
            self.collegeInput.clear()
            self.collegeInput.addItems(sorted(colleges))
            
            # Set up completer
            completer = QCompleter(colleges, self.collegeInput)
            completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
            completer.setFilterMode(Qt.MatchFlag.MatchContains)
            self.collegeInput.setCompleter(completer)
            self.collegeInput.setEditable(True)
            self.collegeInput.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
            
            self.collegeInput.currentTextChanged.connect(self.update_save_button_state)
            
        except Exception as e:
            print(f"Error populating college dropdown: {e}")

    def populate_dialogue_data(self, row_data):
        """Populate dialog fields with existing program data"""
        self.programCodeInput.setText(str(row_data.get("Program Code", "")))
        self.programNameInput.setText(str(row_data.get("Program Name", "")))
        self.collegeInput.setCurrentText(str(row_data.get("College", "")))

    def collect_form_data(self):
        """Collect data from program form fields"""
        return {
            "Program Code": self.programCodeInput.text().strip(),
            "Program Name": self.programNameInput.text().strip(),
            "College": self.collegeInput.currentText().strip()
        }

    def save_changes(self):
        """Save program changes to database"""
        if self.mode == "add":
            if not self.main_window.confirm_action("Are you sure you want to add this program?"):
                return
        elif self.mode == "edit":
            if not self.main_window.confirm_action("Are you sure you want to save these changes?"):
                return
        
        try:
            new_data = self.collect_form_data()
            
            # Convert to database format
            db_data = {
                "program_code": new_data["Program Code"],
                "program_name": new_data["Program Name"],
                "college_code": new_data["College"]
            }
            
            if self.mode == "add":
                result = self.db.add_record("program", db_data)
                if result > 0:
                    QMessageBox.information(self, "Success", "Program added successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add program")
            else:  # edit mode
                old_id = self.row_data["Program Code"]
                result = self.db.update_record("program", "program_code", old_id, db_data)
                if result > 0:
                    QMessageBox.information(self, "Success", "Program updated successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update program")
                    
        except Exception as e:
            print(f"Error saving program: {e}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def connect_field_signals(self):
        """Connect field change signals for validation"""
        self.programCodeInput.textChanged.connect(self.update_save_button_state)
        self.programNameInput.textChanged.connect(self.update_save_button_state)
        self.collegeInput.currentIndexChanged.connect(self.update_save_button_state)

    def validate_all_fields(self):
        """Validate all program form fields"""
        is_valid = True
        found_empty_field = False
        error_messages = []
        
        # Get form data
        program_code = self.programCodeInput.text().strip()
        program_name = self.programNameInput.text().strip()
        college = self.collegeInput.currentText().strip()
        
        # Check for empty fields
        if not all([program_code, program_name, college]):
            is_valid = False
            found_empty_field = True
        
        # Validate program name (letters only)
        if program_name and not re.match(r'^[A-Za-z\s\-]+$', program_name):
            is_valid = False
            error_messages.append("Program Name must contain only letters")
        
        # Validate college code
        if college and hasattr(self.collegeInput, 'valid_codes'):
            is_valid_code = any(code.lower() == college.lower() for code in self.collegeInput.valid_codes)
            if not is_valid_code:
                is_valid = False
                error_messages.append("Please choose a valid College.")
        
        # Set error messages
        if found_empty_field:
            if self.errorLabel:
                self.errorLabel.setText("Please input all necessary information")
        elif error_messages:
            if self.errorLabel:
                self.errorLabel.setText("\n".join(error_messages))
        
        if self.errorLabel:
            self.errorLabel.setVisible(not is_valid)
        
        # Check for duplicate program code
        if is_valid and self.mode=="add" and program_code and self.check_duplicate_code(program_code):
            if self.errorLabel:
                self.errorLabel.setText("Program Code already exists in records.")
                self.errorLabel.setVisible(True)
            is_valid = False

        self.saveButton.setEnabled(is_valid)
        return is_valid

    def check_duplicate_code(self, program_code):
        """Check for duplicate program code"""
        try:
            current_id = None
            if self.mode == "edit" and self.row_data:
                current_id = self.row_data.get("Program Code")
            
            return self.db.check_record_exists("Program", "program_code", program_code, current_id)
        except Exception as e:
            print(f"Error checking for duplicate program code: {e}")
            return False

    def update_save_button_state(self):
        """Update save button state based on validation"""
        is_valid = self.validate_all_fields()
        self.save_button_state_changed.emit(is_valid)


def delete_program(main_window, program_code):
    """Delete program record with ON DELETE SET NULL handling"""
    if not program_code:
        QMessageBox.warning(main_window, "Error", "No program code provided")
        return
    
    confirm_msg = f"Delete program {program_code}? Related student records will have their program codes set to NULL."
    
    if not main_window.confirm_action(confirm_msg):
        return
    
    try:
        db = get_db_manager()

        result = db.delete_record("Program", "program_code", program_code)
        
        if result > 0:
            load_data(main_window)
            main_window.display_counter()
            QMessageBox.information(
                main_window, 
                "Success", 
                f"Program {program_code} deleted successfully. Related students' program codes set to NULL."
            )
        else:
            QMessageBox.warning(main_window, "Error", "Program not found or could not be deleted")
            
    except Exception as e:
        error_msg = f"Error deleting program {program_code}: {str(e)}"
        print(error_msg)
        QMessageBox.critical(main_window, "Error", error_msg)

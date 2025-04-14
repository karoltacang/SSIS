"""College-specific operations for add, edit, and delete functionality"""

import re
from PyQt6.QtWidgets import QDialog, QLabel, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal
from ui.editCollege import Ui_EditCollegeDialog
from functions.db_operations import get_db_manager
from functions.load import load_data

class EditCollege(QDialog):
    """Dialog for adding/editing college records"""
    
    save_button_state_changed = pyqtSignal(bool)
    
    def __init__(self, row_data=None, parent_table=None, row_index=None, mode="edit", main_window=None):
        super().__init__()
        self.ui = Ui_EditCollegeDialog()
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
        
        self.collegeCodeInput = self.ui.collegeCodeInput
        self.collegeNameInput = self.ui.collegeNameInput
        
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

    def populate_dialogue_data(self, row_data):
        """Populate dialog fields with existing college data"""
        self.collegeCodeInput.setText(str(row_data.get("College Code", "")))
        self.collegeNameInput.setText(str(row_data.get("College Name", "")))

    def collect_form_data(self):
        """Collect data from college form fields"""
        return {
            "College Code": self.collegeCodeInput.text().strip(),
            "College Name": self.collegeNameInput.text().strip()
        }

    def save_changes(self):
        """Save college changes to database"""
        if self.mode == "add":
            if not self.main_window.confirm_action("Are you sure you want to add this college?"):
                return
        elif self.mode == "edit":
            if not self.main_window.confirm_action("Are you sure you want to save these changes?"):
                return
        
        try:
            new_data = self.collect_form_data()
            
            # Convert to database format
            db_data = {
                "college_code": new_data["College Code"],
                "college_name": new_data["College Name"]
            }
            
            if self.mode == "add":
                result = self.db.add_record("college", db_data)
                if result > 0:
                    QMessageBox.information(self, "Success", "College added successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to add college")
            else:  # edit mode
                old_id = self.row_data["College Code"]
                result = self.db.update_record("college", "college_code", old_id, db_data)
                if result > 0:
                    QMessageBox.information(self, "Success", "College updated successfully!")
                    self.accept()
                else:
                    QMessageBox.warning(self, "Error", "Failed to update college")
                    
        except Exception as e:
            print(f"Error saving college: {e}")
            QMessageBox.warning(self, "Error", f"An error occurred: {str(e)}")

    def connect_field_signals(self):
        """Connect field change signals for validation"""
        self.collegeCodeInput.textChanged.connect(self.update_save_button_state)
        self.collegeNameInput.textChanged.connect(self.update_save_button_state)

    def validate_all_fields(self):
        """Validate all college form fields"""
        is_valid = True
        found_empty_field = False
        error_messages = []
        
        # Get form data
        college_code = self.collegeCodeInput.text().strip()
        college_name = self.collegeNameInput.text().strip()
        
        # Check for empty fields
        if not all([college_code, college_name]):
            is_valid = False
            found_empty_field = True
        
        # Validate college name (letters only)
        if college_name and not re.match(r'^[A-Za-z\s\-]+$', college_name):
            is_valid = False
            error_messages.append("College Name must contain only letters")
        
        # Set error messages
        if found_empty_field:
            if self.errorLabel:
                self.errorLabel.setText("Please input all necessary information")
        elif error_messages:
            if self.errorLabel:
                self.errorLabel.setText("\n".join(error_messages))
        
        if self.errorLabel:
            self.errorLabel.setVisible(not is_valid)
        
        # Check for duplicate college code
        if is_valid and self.mode=="add" and college_code and self.check_duplicate_code(college_code):
            if self.errorLabel:
                self.errorLabel.setText("College Code already exists in records.")
                self.errorLabel.setVisible(True)
            is_valid = False

        self.saveButton.setEnabled(is_valid)
        return is_valid

    def check_duplicate_code(self, college_code):
        """Check for duplicate college code"""
        try:
            current_id = None
            if self.mode == "edit" and self.row_data:
                current_id = self.row_data.get("College Code")
            
            return self.db.check_record_exists("college", "college_code", college_code, current_id)
        except Exception as e:
            print(f"Error checking for duplicate college code: {e}")
            return False

    def update_save_button_state(self):
        """Update save button state based on validation"""
        is_valid = self.validate_all_fields()
        self.save_button_state_changed.emit(is_valid)


def delete_college(main_window, college_code):
    """Delete college record with ON DELETE SET NULL handling"""
    if not college_code:
        QMessageBox.warning(main_window, "Error", "No college code provided")
        return
    
    confirm_msg = (
        f"Delete college {college_code}? Related programs will have their college codes set to NULL."
    )
    
    if not main_window.confirm_action(confirm_msg):
        return
    
    try:
        db = get_db_manager()
        result = db.delete_record("college", "college_code", college_code)
        
        if result > 0:
            load_data(main_window)
            main_window.display_counter()
            QMessageBox.information(
                main_window,
                "Success",
                f"College {college_code} deleted successfully. Related programs' college codes set to NULL."
            )
        else:
            QMessageBox.warning(main_window, "Error", "College not found or could not be deleted")
            
    except Exception as e:
        error_msg = f"Error deleting college {college_code}: {str(e)}"
        print(error_msg)
        QMessageBox.critical(main_window, "Error", error_msg)

from PyQt6.QtWidgets import QMessageBox
from functions.csv_operations import delete_row_from_csv, read_csv, write_csv
from functions.load import load_data

DEPENDENCY_MAP = {
    "data/colleges.csv": {"file": "data/programs.csv", "parent_key": "College", "child_key": "Program Code"},
    "data/programs.csv": {"file": "data/students.csv", "parent_key": "Program", "child_key": "ID Number"}
}

def delete(file_path, unique_id):
    
    if file_path not in DEPENDENCY_MAP:
        result = delete_row_from_csv(file_path, unique_id)
        return result

    child_file = DEPENDENCY_MAP[file_path]["file"]
    parent_key = DEPENDENCY_MAP[file_path]["parent_key"]
    child_key = DEPENDENCY_MAP[file_path]["child_key"]

    header, rows = read_csv(child_file)
    header = [h.strip() for h in header]

    if parent_key not in header:
        print(f"Error: Parent key '{parent_key}' not found in {child_file}")
        return False

    updated_rows = []
    for row in rows:
        row_dict = dict(zip(header, row))
        if row_dict.get(parent_key) == unique_id:
            row_dict[parent_key] = "NULL"
        updated_rows.append([row_dict.get(h, "") for h in header])

    if not write_csv(child_file, header, updated_rows):
        return False

    return delete_row_from_csv(file_path, unique_id)

def delete_row_from_table(main_window, file_path, unique_id, row):
    if not file_path:
        return


    confirm = main_window.confirm_action(f"Are you sure you want to delete {unique_id}?")
        
    if not confirm:
        return

    success = delete(file_path, unique_id)
    
    if success:
        load_data(main_window)
        main_window.display_counter()
        
        QMessageBox.information(main_window, "Success", "Deletion completed successfully")
    else:
        QMessageBox.warning(main_window, "Error", "Failed to complete deletion")
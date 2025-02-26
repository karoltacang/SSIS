from functions.csv_operations import delete_row_from_csv, read_csv, write_csv
from functions.load import load_data

DEPENDENCY_MAP = {
    "data/colleges.csv": {"file": "data/programs.csv", "parent_key": "College", "child_key": "Program Code"},
    "data/programs.csv": {"file": "data/students.csv", "parent_key": "Program", "child_key": "ID Number"}
}

def delete(file_path, unique_id):
    if file_path not in DEPENDENCY_MAP:
        return

    child_file = DEPENDENCY_MAP[file_path]["file"]
    parent_key = DEPENDENCY_MAP[file_path]["parent_key"]
    child_key = DEPENDENCY_MAP[file_path]["child_key"]

    header, rows = read_csv(child_file)
    header = [h.strip() for h in header]
    
    child_data = [dict(zip(header, row)) for row in rows]
    
    if child_key not in header:
        print(f"Error: Child key '{child_key}'  not found in {DEPENDENCY_MAP[file_path]['file']}")
        return
    elif parent_key not in header:
        print(f"Error: Parent key'{parent_key}' not found in {DEPENDENCY_MAP[file_path]['file']}")
        return

    to_delete = [row[child_key] for row in child_data if row[parent_key] == unique_id]
    
    updated_child_data = [row for row in child_data if row[parent_key] != unique_id]
    write_csv(child_file, header, [[row[key] for key in header] for row in updated_child_data])

    for child_id in to_delete:
        delete(child_file, child_id)
        
    delete_row_from_csv(file_path, unique_id)

def delete_row_from_table(main_window, file_path, unique_id, row):
    if not file_path:
        return

    confirm = main_window.confirm_action(f"Delete {unique_id}? This will remove related records.")
    if not confirm:
        return

    delete(file_path, unique_id)

    load_data(main_window)
    main_window.display_counter()
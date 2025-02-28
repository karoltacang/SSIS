import csv

def read_csv(file_path):

    with open(file_path, "r", newline="", encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        header = next(reader, None) 
        rows = list(reader) 
    return header, rows

def write_csv(file_path, header, rows):

    with open(file_path, "w", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)
        
    return True

def delete_row_from_csv(file_path, row_identifier):

    header, rows = read_csv(file_path)
    filtered_rows = [row for row in rows if row and row[0] != row_identifier]
    write_csv(file_path, header, filtered_rows)
    
    return True

def edit_row_in_csv(file_path, row_identifier, new_data_list):

    header, rows = read_csv(file_path)
    updated_rows = [new_data_list if row and row[0] == row_identifier else row for row in rows]   
    write_csv(file_path, header, updated_rows)
    
    return True

def add_row_to_csv(file_path, new_data_list):

    with open(file_path, "a", newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerow(new_data_list)
        
    return True

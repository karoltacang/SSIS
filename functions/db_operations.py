from mysql.connector import Error
from functions.connection import get_connection
from typing import List, Dict, Optional, Tuple

class DatabaseManager:
    def execute_query(self, query: str, params=None, fetch=False):
        """Generic query execution method using your connector"""
        with get_connection() as cursor:
            cursor.execute(query, params or ())
            if fetch:
                return cursor.fetchall()
            return cursor.rowcount

    def add_record(self, table_name: str, data):
        """Insert a new record"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        return self.execute_query(query, tuple(data.values())) == 1

    def update_record(self, table_name: str, id_field: str, id_value: str, data):
        """Update an existing record"""
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {id_field} = %s"
        params = list(data.values()) + [id_value]
        return self.execute_query(query, params) == 1

    def delete_record(self, table_name: str, id_field: str, id_value: str):
        """Delete a record"""
        query = f"DELETE FROM {table_name} WHERE {id_field} = %s"
        return self.execute_query(query, (id_value,)) == 1
    
    def check_record_exists(self, table_name: str, field: str, value: str, exclude_id=None):
        """Check if a record exists in a table, optionally excluding a specific ID."""
        id_fields = {
            'student': 'id_number',
            'program': 'program_code',
            'college': 'college_code'
        }

        query = f"SELECT COUNT(*) as count FROM {table_name} WHERE {field} = %s"
        params = [value]

        if exclude_id:
            id_field = id_fields.get(table_name.lower(), 'id')
            query += f" AND {id_field} != %s"
            params.append(exclude_id)

        result = self.execute_query(query, params, fetch=True)
        return bool(result and result[0]['count'])
    
    def search_students(self, page=1, search_field=None, search_value=None, sort_field='id_number', sort_order='DESC'):
        field_map = {
            'ID Number': 'id_number',
            'First Name': 'first_name',
            'Last Name': 'last_name',
            'Program': 'program_code',
            'Year Level': 'year_level',
            'Gender': 'gender'
        }

        sort_field_db = field_map.get(sort_field, 'id_number')
        sort_order = sort_order.upper() if sort_order in ['ASC', 'DESC'] else 'DESC'

        limit = 10
        offset = (page - 1) * limit
        base_query = "FROM student"
        params = []

        if search_field and search_value:
            search_field_db = field_map.get(search_field)
            if search_field_db:
                base_query += f" WHERE {search_field_db} LIKE %s"
                params.append(f"%{search_value}%")

        # Data query
        data_query = f"SELECT * {base_query} ORDER BY {sort_field_db} {sort_order} LIMIT %s OFFSET %s"
        data_params = params + [limit, offset]
        data = self.execute_query(data_query, data_params, fetch=True)

        # Filtered count
        count_query = f"SELECT COUNT(*) as total {base_query}"
        total_filtered = self.execute_query(count_query, params, fetch=True)[0]['total']

        return data, total_filtered

    def search_programs(self, page=1, search_field=None, search_value=None, sort_field='program_code', sort_order='ASC'):
        field_map = {
            'Program Code': 'program_code',
            'Name': 'name',
            'College': 'college_code'
        }

        sort_field_db = field_map.get(sort_field, 'program_code')
        sort_order = sort_order.upper() if sort_order in ['ASC', 'DESC'] else 'ASC'

        limit = 10
        offset = (page - 1) * limit

        # --- Base query ---
        base_query = "FROM program"
        params = []

        # --- Apply filter if needed ---
        if search_field and search_value:
            search_field_db = field_map.get(search_field)
            if search_field_db:
                base_query += f" WHERE {search_field_db} LIKE %s"
                params.append(f"%{search_value}%")

        # --- Get filtered results ---
        data_query = f"SELECT * {base_query} ORDER BY {sort_field_db} {sort_order} LIMIT %s OFFSET %s"
        data_params = params + [limit, offset]
        data = self.execute_query(data_query, data_params, fetch=True)

        # --- Get total (filtered) count ---
        count_query = f"SELECT COUNT(*) as total {base_query}"
        count = self.execute_query(count_query, params, fetch=True)
        total_filtered = count[0]['total'] if count else 0

        return data, total_filtered

    def search_colleges(self, page=1, search_field=None, search_value=None, sort_field='college_code', sort_order='ASC'):
        field_map = {
            'College Code': 'college_code',
            'Name': 'name'
        }

        sort_field_db = field_map.get(sort_field, 'college_code')
        sort_order = sort_order.upper() if sort_order in ['ASC', 'DESC'] else 'ASC'

        limit = 10
        offset = (page - 1) * limit
        base_query = "FROM college"
        params = []

        if search_field and search_value:
            search_field_db = field_map.get(search_field)
            if search_field_db:
                base_query += f" WHERE {search_field_db} LIKE %s"
                params.append(f"%{search_value}%")

        data_query = f"SELECT * {base_query} ORDER BY {sort_field_db} {sort_order} LIMIT %s OFFSET %s"
        data_params = params + [limit, offset]
        data = self.execute_query(data_query, data_params, fetch=True)

        count_query = f"SELECT COUNT(*) as total {base_query}"
        total_filtered = self.execute_query(count_query, params, fetch=True)[0]['total']

        return data, total_filtered


    def get_students_paginated(self, page=1, per_page=10) -> Dict:
        offset = (page - 1) * per_page

        count_query = "SELECT COUNT(*) as total FROM student"
        total = self.execute_query(count_query, [], fetch=True)[0]['total']

        if total == 0:
            return {'data': [], 'total': 0, 'pages': 0}

        data_query = f"""
            SELECT s.*
            FROM student s
            INNER JOIN (
                SELECT id_number
                FROM student
                ORDER BY id_number DESC
                LIMIT %s OFFSET %s
            ) AS paginated_students USING (id_number)
            ORDER BY id_number DESC
        """
        params = [per_page, offset]

        data = self.execute_query(data_query, params, fetch=True)

        return {
            'data': data,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }


    def get_programs_paginated(self, page=1, per_page=10) -> Dict:
        offset = (page - 1) * per_page

        count_query = "SELECT COUNT(*) as total FROM program"
        total = self.execute_query(count_query, [], fetch=True)[0]['total']

        if total == 0:
            return {'data': [], 'total': 0, 'pages': 0}

        data_query = f"""
            SELECT p.*
            FROM program p
            INNER JOIN (
                SELECT program_code
                FROM program
                ORDER BY program_code ASC
                LIMIT %s OFFSET %s
            ) AS paginated_programs USING (program_code)
            ORDER BY program_code ASC
        """
        params = [per_page, offset]

        data = self.execute_query(data_query, params, fetch=True)

        return {
            'data': data,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }


    def get_colleges_paginated(self, page=1, per_page=10) -> Dict:
        offset = (page - 1) * per_page

        count_query = "SELECT COUNT(*) as total FROM college"
        total = self.execute_query(count_query, [], fetch=True)[0]['total']

        if total == 0:
            return {'data': [], 'total': 0, 'pages': 0}

        data_query = f"""
            SELECT c.*
            FROM college c
            INNER JOIN (
                SELECT college_code
                FROM college
                ORDER BY college_code ASC
                LIMIT %s OFFSET %s
            ) AS paginated_colleges USING (college_code)
            ORDER BY college_code ASC
        """
        params = [per_page, offset]

        data = self.execute_query(data_query, params, fetch=True)

        return {
            'data': data,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }


    def get_college_codes(self):
        """Get all college codes for dropdown"""
        query = "SELECT college_code FROM college ORDER BY college_code"
        results = self.execute_query(query, fetch=True)
        return [row['college_code'] for row in results]

    def get_program_codes(self):
        """Get all program codes for dropdown"""
        query = "SELECT program_code FROM program ORDER BY program_code"
        results = self.execute_query(query, fetch=True)
        return [row['program_code'] for row in results]
    
    def get_total_student_count(self):
        query = "SELECT COUNT(*) as total FROM student"
        result = self.execute_query(query, fetch=True)
        return result[0]['total'] if result else 0

    def get_total_program_count(self):
        query = "SELECT COUNT(*) as total FROM program"
        result = self.execute_query(query, fetch=True)
        return result[0]['total'] if result else 0

    def get_total_college_count(self):
        query = "SELECT COUNT(*) as total FROM college"
        result = self.execute_query(query, fetch=True)
        return result[0]['total'] if result else 0

# Singleton instance pattern remains the same
_db_manager = None

def get_db_manager():
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
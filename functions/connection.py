import mysql.connector
from contextlib import contextmanager
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='mypassword',
            database='ssis'
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
    
@contextmanager
def get_connection():
    """Context manager that handles connection/cursor lifecycle"""
    conn = create_connection()
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        yield cursor
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            
    pass
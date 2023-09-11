#database.py

import sqlite3

# Function to initialize the database and create the table
def initialize_database():
    # Establishes a connection to the SQLite database
    conn = sqlite3.connect('app.db')
    # Execute SQL commands
    cursor = conn.cursor()

    # Create the 'uploaded_files' table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS uploaded_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_filename TEXT,
            converted_filename TEXT,
            comments TEXT
        )
    ''')

    # Changes are commited to database
    conn.commit()
    # Connection is closed 
    conn.close()

# Function to insert a new record into the database
def insert_file(original_filename, converted_filename, comments):
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO uploaded_files (original_filename, converted_filename, comments)
        VALUES (?, ?, ?)
    ''', (original_filename, converted_filename, comments))

    conn.commit()
    conn.close()

# Function to retrieve all records from the database
def get_all_files():
    conn = sqlite3.connect('app.db')
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM uploaded_files')
    files = cursor.fetchall()

    conn.close()
    return files

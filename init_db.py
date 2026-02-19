#!/usr/bin/env python3
"""
Initialize SQLite database from schema file
"""

import sqlite3
import os

# Get the database path
basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'quizapp.db')
schema_path = os.path.join(basedir, 'DB', 'quizappstructure_sqlite.sql')

# Read schema file
with open(schema_path, 'r', encoding='utf-8') as f:
    schema = f.read()

# Connect to database and execute schema
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Execute schema (split by semicolons)
for statement in schema.split(';'):
    statement = statement.strip()
    if statement:
        try:
            cursor.execute(statement)
        except sqlite3.OperationalError as e:
            # Ignore "table already exists" errors
            if 'already exists' not in str(e).lower():
                print(f"Warning: {e}")

conn.commit()
conn.close()

print(f"Database initialized at: {db_path}")

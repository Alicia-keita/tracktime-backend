import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import psycopg2

try:
    conn = psycopg2.connect(
        database='Pointage',
        user='postgres',
        password='root',
        host='localhost',
        port='5432'
    )
    print("Connection successful!")
    conn.close()
except Exception as e:
    print(f"Error: {e}")

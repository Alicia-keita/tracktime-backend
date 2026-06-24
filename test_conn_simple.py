import psycopg2

try:
    conn = psycopg2.connect(
        dbname='Pointage',
        user='postgres',
        password='root',
        host='localhost',
        port='5432'
    )
    print("OK")
    conn.close()
except Exception as e:
    print("FAIL:", str(e))

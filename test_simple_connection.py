# -*- coding: utf-8 -*-
import psycopg2
from psycopg2 import OperationalError

def test_connection():
    try:
        # Test de connexion avec les paramètres actuels
        connection = psycopg2.connect(
            database='Pointage',
            user='postgres', 
            password='root',
            host='localhost',
            port='5432',
            client_encoding='utf8'
        )
        print("Connexion reussie a PostgreSQL!")
        
        # Verifier si la base de donnees existe
        cursor = connection.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"Version PostgreSQL: {version[0]}")
        
        # Lister les tables
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
        tables = cursor.fetchall()
        print(f"Tables existantes: {len(tables)}")
        for table in tables:
            print(f"  - {table[0]}")
        
        cursor.close()
        connection.close()
        return True
        
    except OperationalError as e:
        print(f"Erreur de connexion: {e}")
        return False
    except Exception as e:
        print(f"Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    test_connection()

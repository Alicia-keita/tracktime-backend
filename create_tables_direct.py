#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Initialiser Django
django.setup()

from django.db import connection
from django.core.management import call_command

def create_tables():
    try:
        print("Tentative de connexion a la base de donnees...")
        
        # Test de connexion
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            print("Connexion reussie!")
        
        # Creer les tables
        print("Creation des tables...")
        call_command('migrate', run_syncdb=True, verbosity=2)
        
        print("Tables creees avec succes!")
        
        # Lister les tables
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            print(f"\nTables creees ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")
                
    except Exception as e:
        print(f"Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_tables()

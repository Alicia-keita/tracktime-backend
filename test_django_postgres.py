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

def test_django_connection():
    try:
        print("Test de connexion Django à PostgreSQL...")
        
        # Test de connexion
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Connexion réussie !")
            print(f"Version PostgreSQL: {version[0]}")
        
        # Lister les tables
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            print(f"\n📊 Tables trouvées ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")
                
        print("\n🎉 Django est maintenant connecté à PostgreSQL avec succès !")
        return True
                
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_django_connection()

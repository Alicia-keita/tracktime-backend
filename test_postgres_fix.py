#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de test de connexion PostgreSQL avec differentes configurations d'encodage
"""
import os
import sys

# Forcer l'encodage UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PGCLIENTENCODING'] = 'UTF8'

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_postgres_connection():
    try:
        import django
        django.setup()
        
        from django.db import connection
        
        print("🔍 Test de connexion Django a PostgreSQL...")
        print(f"📊 Configuration: {connection.settings_dict['ENGINE']}")
        
        # Test simple
        with connection.cursor() as cursor:
            cursor.execute("SELECT 'Connexion reussie!' as message, version() as version")
            result = cursor.fetchone()
            print(f"✅ {result[0]}")
            print(f"📊 PostgreSQL: {result[1][:50]}...")
        
        # Lister les tables
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            print(f"\n📋 Tables trouvees ({len(tables)}):")
            for table in tables:
                print(f"  - {table[0]}")
        
        print("\n🎉 SUCCES ! Django est connecte a PostgreSQL!")
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        print(f"\n💡 Type d'erreur: {type(e).__name__}")
        
        if "utf-8" in str(e).lower() and "codec" in str(e).lower():
            print("\n🔧 C'est bien l'erreur d'encodage!")
            print("\n💡 SOLUTIONS PROPOSEES:")
            print("   1. Executez: chcp 65001 (dans PowerShell)")
            print("   2. Configurez les variables d'environnement:")
            print("      $env:PYTHONIOENCODING='utf-8'")
            print("      $env:PGCLIENTENCODING='UTF8'")
            print("   3. Ou utilisez le fichier start_django_postgres.bat")
        
        return False

if __name__ == "__main__":
    success = test_postgres_connection()
    sys.exit(0 if success else 1)

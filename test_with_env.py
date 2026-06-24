#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

# Forcer l'encodage UTF-8
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PGCLIENTENCODING'] = 'utf8'

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.db import connection

def test_with_encoding():
    try:
        print("Test avec encodage forcé...")
        
        # Test de connexion
        with connection.cursor() as cursor:
            cursor.execute("SELECT 'Test réussi !' AS message, version() AS version;")
            result = cursor.fetchone()
            print(f"✅ {result[0]}")
            print(f"📊 PostgreSQL: {result[1]}")
        
        # Lister les tables
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
            count = cursor.fetchone()[0]
            print(f"📋 Nombre de tables: {count}")
                
        print("\n🎉 La connexion fonctionne maintenant !")
        return True
                
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False

if __name__ == "__main__":
    test_with_encoding()

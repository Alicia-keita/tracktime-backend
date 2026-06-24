#!/usr/bin/env python
import os
import sys

# Configuration minimale
os.environ['DJANGO_SETTINGS_MODULE'] = 'attendance_system.settings'

# Forcer l'encodage au niveau le plus bas
if sys.platform.startswith('win'):
    import locale
    try:
        locale.setlocale(locale.LC_ALL, 'French_France.UTF8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF8')
        except:
            pass

# Ajouter le chemin
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import django
    django.setup()
    
    from django.db import connection
    
    print("Test de connexion Django...")
    
    # Test simple
    cursor = connection.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    
    if result[0] == 1:
        print("✅ Connexion réussie à PostgreSQL !")
        
        # Lister les tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        print(f"📊 Tables trouvées ({len(tables)}):")
        for table in tables:
            print(f"  - {table[0]}")
    else:
        print("❌ Erreur de connexion")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("Type d'erreur:", type(e).__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de diagnostic pour le problème d'encodage PostgreSQL
"""
import os
import sys

print("🔍 Diagnostic du problème d'encodage PostgreSQL\n")

# 1. Vérifier l'encodage Python
print("1. Encodage Python par défaut:")
print(f"   sys.getdefaultencoding(): {sys.getdefaultencoding()}")
print(f"   sys.stdout.encoding: {sys.stdout.encoding}")
print(f"   sys.stderr.encoding: {sys.stderr.encoding}")

# 2. Vérifier les variables d'environnement
print("\n2. Variables d'environnement liées à l'encodage:")
env_vars = ['PYTHONIOENCODING', 'PGCLIENTENCODING', 'LC_ALL', 'LANG', 'PGDATABASE', 'PGHOST']
for var in env_vars:
    value = os.environ.get(var, 'Non définie')
    print(f"   {var}: {value}")

# 3. Vérifier la locale
print("\n3. Informations de locale:")
try:
    import locale
    print(f"   Locale par défaut: {locale.getdefaultlocale()}")
    print(f"   LC_ALL: {locale.getlocale()}")
except Exception as e:
    print(f"   Erreur locale: {e}")

# 4. Tester la connexion PostgreSQL directe
print("\n4. Test de connexion directe avec psycopg2:")
try:
    import psycopg2
    print("   psycopg2 version:", psycopg2.__version__)
    
    # Test avec différents paramètres d'encodage
    conn_params = {
        'dbname': 'Pointage',
        'user': 'postgres',
        'password': 'root',
        'host': 'localhost',
        'port': '5432',
        'options': '-c client_encoding=UTF8'
    }
    
    print("\n   Test avec options UTF8...")
    conn = psycopg2.connect(**conn_params)
    cur = conn.cursor()
    cur.execute("SELECT 'Connexion réussie!' as message, version() as version")
    result = cur.fetchone()
    print(f"   ✅ {result[0]}")
    print(f"   📊 PostgreSQL: {result[1][:50]}...")
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"   ❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n5. Test de connexion avec chaîne DSN:")
try:
    import psycopg2
    dsn = "dbname=Pointage user=postgres password=root host=localhost port=5432 client_encoding=UTF8"
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    cur.execute("SELECT 'DSN Connexion OK!' as message")
    result = cur.fetchone()
    print(f"   ✅ {result[0]}")
    cur.close()
    conn.close()
except Exception as e:
    print(f"   ❌ Erreur DSN: {e}")

print("\n📋 Résumé:")
print("   Si les tests ci-dessus réussissent, le problème est dans la configuration Django.")
print("   Si les tests échouent, le problème est au niveau système/psycopg2.")

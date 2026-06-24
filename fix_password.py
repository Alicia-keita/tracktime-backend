import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

import psycopg2
from psycopg2 import sql

# D'abord, connecter à postgres pour changer le mot de passe
try:
    # Essayer avec l'encodage latin1 pour contourner le problème
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="Eva0422",
        database="postgres",
        client_encoding='LATIN1'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Changer le mot de passe pour un sans caractères spéciaux
    new_password = "postgres123"
    cursor.execute(f"ALTER USER postgres WITH PASSWORD '{new_password}';")
    print(f"✅ Mot de passe changé pour: {new_password}")
    
    # Créer la base de données Pointage
    try:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier("Pointage")))
        print("✅ Base de données 'Pointage' créée!")
    except psycopg2.errors.DuplicateDatabase:
        print("ℹ️ La base de données 'Pointage' existe déjà")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")

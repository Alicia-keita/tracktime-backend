import psycopg2
from psycopg2 import sql

# Connexion à PostgreSQL (base par défaut postgres)
try:
    conn = psycopg2.connect(
        host="localhost",
        port="5432",
        user="postgres",
        password="Eva0422",
        database="postgres",
        client_encoding='utf8'
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Créer la base de données "Pointage"
    cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier("Pointage")))
    print("✅ Base de données 'Pointage' créée avec succès!")
    
    cursor.close()
    conn.close()
    
except psycopg2.errors.DuplicateDatabase:
    print("ℹ️ La base de données 'Pointage' existe déjà")
except Exception as e:
    print(f"❌ Erreur: {e}")

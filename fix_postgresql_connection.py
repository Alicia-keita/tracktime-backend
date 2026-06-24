#!/usr/bin/env python
"""
Solution alternative pour la connexion PostgreSQL
"""

import os
import sys
import subprocess

def create_postgresql_user():
    """Créer un utilisateur PostgreSQL dédié"""
    print("👤 Création d'un utilisateur PostgreSQL dédié...")
    
    # Script SQL pour créer l'utilisateur
    sql_commands = """
-- Créer un utilisateur dédié pour le projet
CREATE USER pointage_user WITH PASSWORD 'pointage123';

-- Donner les permissions sur la base de données
GRANT ALL PRIVILEGES ON DATABASE pointage TO pointage_user;

-- Donner les permissions sur le schéma public
GRANT ALL ON SCHEMA public TO pointage_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pointage_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pointage_user;

-- Donner les permissions par défaut pour les futures tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO pointage_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO pointage_user;
"""
    
    with open('create_user.sql', 'w', encoding='utf-8') as f:
        f.write(sql_commands)
    
    print("✅ Fichier SQL créé: create_user.sql")
    print("\n📋 Étapes manuelles:")
    print("1. Ouvrir pgAdmin")
    print("2. Se connecter en tant que postgres")
    print("3. Ouvrir l'éditeur de requête (F6)")
    print("4. Copier-coller le contenu de create_user.sql")
    print("5. Exécuter la requête")

def update_settings_with_new_user():
    """Mettre à jour settings.py avec le nouvel utilisateur"""
    print("\n📝 Mise à jour de settings.py...")
    
    new_config = """
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pointage',
        'USER': 'pointage_user',
        'PASSWORD': 'pointage123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
"""
    
    try:
        with open('attendance_system/settings.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Trouver et remplacer la configuration DATABASES
        import re
        pattern = r'DATABASES\s*=\s*{[^}]+}'
        new_content = re.sub(pattern, new_config.strip(), content, flags=re.DOTALL)
        
        if new_content != content:
            with open('attendance_system/settings.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            print("✅ Configuration mise à jour avec le nouvel utilisateur")
        else:
            print("⚠️  Configuration non trouvée dans settings.py")
            
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")

def test_connection_simple():
    """Test simple de connexion"""
    print("\n🔍 Test de connexion simple...")
    
    test_script = """
import psycopg2
try:
    conn = psycopg2.connect(
        dbname='pointage',
        user='pointage_user',
        password='pointage123',
        host='localhost',
        port='5432'
    )
    print("✅ Connexion réussie!")
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"Version PostgreSQL: {version[0]}")
    conn.close()
except Exception as e:
    print(f"❌ Erreur de connexion: {e}")
"""
    
    with open('test_connection.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ Script de test créé: test_connection.py")

def create_alternative_solution():
    """Solution alternative: revenir temporairement à SQLite"""
    print("\n🔄 Solution alternative: SQLite temporaire...")
    
    sqlite_config = """
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
"""
    
    print("Si PostgreSQL ne fonctionne pas, vous pouvez:")
    print("1. Revenir temporairement à SQLite")
    print("2. Créer les tables avec SQLite")
    print("3. Exporter les données")
    print("4. Importer dans PostgreSQL plus tard")
    
    with open('sqlite_config.txt', 'w', encoding='utf-8') as f:
        f.write(sqlite_config)

if __name__ == '__main__':
    print("🔧 SOLUTION CONNEXION POSTGRESQL")
    print("=" * 50)
    
    create_postgresql_user()
    update_settings_with_new_user()
    test_connection_simple()
    create_alternative_solution()
    
    print("\n🎯 PLAN D'ACTION:")
    print("\n1️⃣ Exécuter create_user.sql dans pgAdmin:")
    print("   - Se connecter en tant que postgres")
    print("   - Exécuter les commandes SQL")
    
    print("\n2️⃣ Tester la connexion:")
    print("   python test_connection.py")
    
    print("\n3️⃣ Si ça fonctionne:")
    print("   python manage.py makemigrations")
    print("   python manage.py migrate")
    
    print("\n4️⃣ Si ça ne fonctionne pas:")
    print("   - Revenir à SQLite temporairement")
    print("   - Résoudre les problèmes PostgreSQL plus tard")
    
    print("\n📋 Fichiers créés:")
    print("- create_user.sql: Commandes SQL pour créer l'utilisateur")
    print("- test_connection.py: Test de connexion simple")
    print("- sqlite_config.txt: Configuration SQLite de secours")

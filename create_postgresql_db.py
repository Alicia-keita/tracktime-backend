#!/usr/bin/env python
"""
Script pour créer la base de données PostgreSQL 'pointage' et tester la connexion
"""

import subprocess
import sys
import psycopg2
from psycopg2 import OperationalError

def test_postgresql_connection():
    """Tester la connexion à PostgreSQL"""
    print("🔍 Test de connexion PostgreSQL...")
    
    # Configurations possibles
    configs = [
        {'user': 'postgres', 'password': 'password', 'host': 'localhost', 'port': '5432'},
        {'user': 'postgres', 'password': 'postgres', 'host': 'localhost', 'port': '5432'},
        {'user': 'postgres', 'password': 'admin', 'host': 'localhost', 'port': '5432'},
        {'user': 'postgres', 'password': '', 'host': 'localhost', 'port': '5432'},
    ]
    
    for config in configs:
        try:
            conn = psycopg2.connect(
                dbname='postgres',  # Base par défaut pour se connecter
                user=config['user'],
                password=config['password'],
                host=config['host'],
                port=config['port']
            )
            print(f"✅ Connexion réussie avec :")
            print(f"   Utilisateur: {config['user']}")
            print(f"   Hôte: {config['host']}")
            print(f"   Port: {config['port']}")
            
            # Créer la base de données pointage
            create_database(conn, config)
            conn.close()
            return config
            
        except OperationalError as e:
            print(f"❌ Échec avec {config['user']}/{config['password']}: {e}")
            continue
    
    print("\n❌ Aucune configuration n'a fonctionné")
    return None

def create_database(conn, config):
    """Créer la base de données pointage"""
    try:
        conn.autocommit = True  # Nécessaire pour CREATE DATABASE
        cursor = conn.cursor()
        
        # Vérifier si la base existe déjà
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'pointage'")
        exists = cursor.fetchone()
        
        if exists:
            print("✅ La base de données 'pointage' existe déjà")
        else:
            # Créer la base de données
            cursor.execute("CREATE DATABASE pointage")
            print("✅ Base de données 'pointage' créée avec succès")
        
        # Lister toutes les bases
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
        databases = cursor.fetchall()
        print("\n📊 Bases de données disponibles :")
        for db in databases:
            db_name = db[0]
            if db_name == 'pointage':
                print(f"   🎯 {db_name} ← Votre base !")
            else:
                print(f"   📁 {db_name}")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de la base: {e}")

def test_django_connection():
    """Tester la connexion Django à PostgreSQL"""
    print("\n🔧 Test de connexion Django...")
    
    try:
        import os
        import django
        from pathlib import Path
        
        # Configuration Django
        BASE_DIR = Path(__file__).resolve().parent
        sys.path.append(str(BASE_DIR))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
        django.setup()
        
        from django.db import connection
        
        # Tester la connexion
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Django connecté à PostgreSQL")
            print(f"   Version: {version[0]}")
            
            # Lister les tables
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")
            tables = cursor.fetchall()
            print(f"   Tables trouvées: {len(tables)}")
            
            if tables:
                print("   📋 Tables dans la base 'pointage':")
                for table in tables:
                    print(f"      - {table[0]}")
            else:
                print("   📋 Aucune table (nouvelle base)")
        
    except Exception as e:
        print(f"❌ Erreur de connexion Django: {e}")
        print("   Vérifiez la configuration dans settings.py")

def update_settings_password(config):
    """Mettre à jour le mot de passe dans settings.py"""
    print(f"\n📝 Mise à jour du mot de passe dans settings.py...")
    
    try:
        with open('attendance_system/settings.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer le mot de passe
        old_password = "'password'"
        new_password = f"'{config['password']}'"
        
        if old_password in content:
            content = content.replace(old_password, new_password)
            
            with open('attendance_system/settings.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Mot de passe mis à jour: {config['password']}")
        else:
            print("⚠️  Mot de passe non trouvé dans settings.py")
            
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")

if __name__ == '__main__':
    print("🗄️ CRÉATION AUTOMATIQUE DE LA BASE POSTGRESQL")
    print("=" * 60)
    
    # Étape 1: Tester la connexion
    config = test_postgresql_connection()
    
    if config:
        # Étape 2: Mettre à jour settings.py
        update_settings_password(config)
        
        # Étape 3: Tester Django
        test_django_connection()
        
        print("\n🎉 Configuration terminée !")
        print("\n📋 Prochaines étapes:")
        print("1. python manage.py makemigrations")
        print("2. python manage.py migrate")
        print("3. python manage.py runserver")
        
    else:
        print("\n❌ Impossible de se connecter à PostgreSQL")
        print("\n📋 Solutions possibles:")
        print("1. Vérifiez que PostgreSQL est installé")
        print("2. Vérifiez que le service PostgreSQL est démarré")
        print("3. Vérifiez le mot de passe de l'utilisateur postgres")
        print("4. Essayez de vous connecter avec pgAdmin manuellement")

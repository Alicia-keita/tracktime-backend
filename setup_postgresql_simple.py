#!/usr/bin/env python
"""
Script simple pour créer la base de données PostgreSQL 'pointage'
"""

import subprocess
import sys

def create_database_manually():
    """Guide pour créer manuellement la base de données"""
    print("🗄️ CRÉATION MANUELLE DE LA BASE POSTGRESQL")
    print("=" * 50)
    
    print("\n📋 Étapes manuelles :")
    print("\n1️⃣ Ouvrir pgAdmin ou psql")
    print("   - pgAdmin: Cliquez sur 'Servers' → 'Create' → 'Database'")
    print("   - psql: Ouvrir un terminal et taper 'psql -U postgres'")
    
    print("\n2️⃣ Exécuter la commande SQL:")
    print("   CREATE DATABASE pointage;")
    
    print("\n3️⃣ Vérifier que la base est créée:")
    print("   \\l  (dans psql)")
    print("   ou dans pgAdmin, rafraîchir la liste des bases")
    
    print("\n4️⃣ Mettre à jour settings.py avec le bon mot de passe:")
    print("""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pointage',
        'USER': 'postgres',
        'PASSWORD': 'votre_vrai_mot_de_passe',  # ← MODIFIER ICI
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
    """)
    
    print("\n🔍 Si pgAdmin ne montre pas la base:")
    print("   1. Clic droit sur 'Databases' → 'Refresh'")
    print("   2. Vérifiez que vous êtes connecté au bon serveur")
    print("   3. Vérifiez les permissions de l'utilisateur")
    
    print("\n📋 Prochaines étapes après création:")
    print("1. python manage.py makemigrations")
    print("2. python manage.py migrate")
    print("3. python manage.py runserver")

def check_postgresql_service():
    """Vérifier si PostgreSQL est en cours d'exécution"""
    print("\n🔍 Vérification du service PostgreSQL...")
    
    try:
        # Vérifier si PostgreSQL est en cours d'exécution
        result = subprocess.run(['net', 'start'], capture_output=True, text=True)
        
        if 'postgresql' in result.stdout.lower():
            print("✅ Service PostgreSQL est en cours d'exécution")
        else:
            print("❌ Service PostgreSQL n'est pas en cours d'exécution")
            print("\n📋 Pour démarrer PostgreSQL:")
            print("   - Windows: Services → PostgreSQL → Démarrer")
            print("   - Linux: sudo systemctl start postgresql")
            print("   - macOS: brew services start postgresql")
            
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")

def create_sql_commands():
    """Créer un fichier SQL avec les commandes nécessaires"""
    sql_commands = """
-- Commands SQL pour créer la base de données pointage
-- Exécuter ces commandes dans pgAdmin ou psql

-- 1. Créer la base de données
CREATE DATABASE pointage;

-- 2. Vérifier que la base est créée
\\l

-- 3. Se connecter à la nouvelle base
\\c pointage

-- 4. Vérifier que nous sommes dans la bonne base
SELECT current_database();

-- 5. (Optionnel) Créer un utilisateur dédié
CREATE USER pointage_user WITH PASSWORD 'pointage123';
GRANT ALL PRIVILEGES ON DATABASE pointage TO pointage_user;
"""
    
    with open('create_pointage_db.sql', 'w', encoding='utf-8') as f:
        f.write(sql_commands)
    
    print("✅ Fichier SQL créé: create_pointage_db.sql")

if __name__ == '__main__':
    create_database_manually()
    check_postgresql_service()
    create_sql_commands()
    
    print("\n🎯 SOLUTIONS RAPIDES:")
    print("\n1️⃣ Via pgAdmin:")
    print("   - Ouvrir pgAdmin")
    print("   - Clic droit sur 'Databases' → 'Create' → 'Database'")
    print("   - Nom: pointage")
    print("   - Cliquez sur 'Save'")
    
    print("\n2️⃣ Via psql (terminal):")
    print("   psql -U postgres")
    print("   CREATE DATABASE pointage;")
    print("   \\l")
    
    print("\n3️⃣ Via SQL (exécuter create_pointage_db.sql):")
    print("   - Ouvrez le fichier dans pgAdmin")
    print("   - Exécutez les commandes SQL")
    
    print("\n🔧 Après création de la base:")
    print("1. Mettre à jour le mot de passe dans settings.py")
    print("2. python manage.py makemigrations")
    print("3. python manage.py migrate")
    print("4. python manage.py runserver")

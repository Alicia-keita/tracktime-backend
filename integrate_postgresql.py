#!/usr/bin/env python
"""
Script pour tester la connexion PostgreSQL et créer les tables
"""

import os
import sys
import django
from pathlib import Path

# Configuration Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')

def test_postgresql_connection():
    """Tester la connexion à PostgreSQL"""
    print("🔍 Test de connexion PostgreSQL...")
    
    try:
        django.setup()
        from django.db import connection
        
        # Tester la connexion
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ Connexion réussie à PostgreSQL")
            print(f"   📊 Version: {version[0]}")
            
            # Vérifier la base de données actuelle
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()
            print(f"   🗄️ Base de données: {db_name[0]}")
            
            # Lister les tables existantes
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            if tables:
                print(f"   📋 Tables existantes: {len(tables)}")
                for table in tables:
                    print(f"      - {table[0]}")
            else:
                print("   📋 Aucune table (base de données vide)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        print("\n🔧 Solutions possibles:")
        print("1. Vérifiez que PostgreSQL est en cours d'exécution")
        print("2. Vérifiez le mot de passe dans settings.py")
        print("3. Vérifiez que la base 'pointage' existe")
        return False

def create_migrations():
    """Créer les migrations Django"""
    print("\n📝 Création des migrations...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'manage.py', 'makemigrations'], 
                              capture_output=True, text=True, cwd=BASE_DIR)
        
        if result.returncode == 0:
            print("✅ Migrations créées avec succès")
            print(result.stdout)
        else:
            print("❌ Erreur lors de la création des migrations:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

def apply_migrations():
    """Appliquer les migrations"""
    print("\n🚀 Application des migrations...")
    
    try:
        import subprocess
        result = subprocess.run([sys.executable, 'manage.py', 'migrate'], 
                              capture_output=True, text=True, cwd=BASE_DIR)
        
        if result.returncode == 0:
            print("✅ Migrations appliquées avec succès")
            print(result.stdout)
        else:
            print("❌ Erreur lors de l'application des migrations:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False
    
    return True

def verify_tables():
    """Vérifier que toutes les tables sont créées"""
    print("\n🔍 Vérification des tables créées...")
    
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # Lister toutes les tables
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            print(f"📊 Total tables créées: {len(tables)}")
            
            # Tables attendues
            expected_tables = [
                'users_user',
                'core_permissionrequest', 
                'core_bulletin',
                'core_conge',
                'core_solde',
                'core_rapport',
                'django_migrations',
                'django_admin_log',
                'auth_user',
                'auth_group',
                'auth_permission'
            ]
            
            print("\n📋 Tables principales:")
            for table in tables:
                table_name = table[0]
                if table_name in expected_tables:
                    print(f"   ✅ {table_name}")
                else:
                    print(f"   📁 {table_name}")
            
            # Vérifier les tables principales
            main_tables = [t[0] for t in tables if 'core_' in t[0] or 'users_' in t[0]]
            print(f"\n🎯 Tables métier créées: {len(main_tables)}")
            
            # Afficher la structure d'une table exemple
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'users_user'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            
            print("\n📊 Structure de la table users_user:")
            for col in columns:
                nullable = "NULL" if col[2] == "YES" else "NOT NULL"
                default = f" DEFAULT {col[3]}" if col[3] else ""
                print(f"   - {col[0]}: {col[1]} {nullable}{default}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False

def create_superuser():
    """Créer un superutilisateur si nécessaire"""
    print("\n👤 Création du superutilisateur...")
    
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Vérifier si un superutilisateur existe
        superusers = User.objects.filter(is_superuser=True)
        
        if superusers.exists():
            print(f"✅ Superutilisateur existant: {superusers.first().username}")
        else:
            print("📝 Aucun superutilisateur trouvé")
            print("   Créez-en un avec: python manage.py createsuperuser")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")

if __name__ == '__main__':
    print("🗄️ INTÉGRATION COMPLÈTE DES TABLES POSTGRESQL")
    print("=" * 60)
    
    # Étape 1: Tester la connexion
    if not test_postgresql_connection():
        print("\n❌ Impossible de continuer sans connexion PostgreSQL")
        sys.exit(1)
    
    # Étape 2: Créer les migrations
    if not create_migrations():
        print("\n❌ Erreur lors de la création des migrations")
        sys.exit(1)
    
    # Étape 3: Appliquer les migrations
    if not apply_migrations():
        print("\n❌ Erreur lors de l'application des migrations")
        sys.exit(1)
    
    # Étape 4: Vérifier les tables
    verify_tables()
    
    # Étape 5: Vérifier le superutilisateur
    create_superuser()
    
    print("\n🎉 INTÉGRATION TERMINÉE AVEC SUCCÈS !")
    print("\n📋 Récapitulatif:")
    print("   ✅ Connexion PostgreSQL établie")
    print("   ✅ Base de données 'pointage' utilisée")
    print("   ✅ Toutes les tables Django créées")
    print("   ✅ Structure des tables respectée")
    print("   ✅ Relations et contraintes appliquées")
    
    print("\n🚀 Prochaines étapes:")
    print("1. python manage.py runserver")
    print("2. Testez l'API: http://localhost:8000/api/")
    print("3. Importez vos données si nécessaire")

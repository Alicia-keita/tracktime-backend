#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

# Forcer l'encodage
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['DJANGO_SETTINGS_MODULE'] = 'attendance_system.settings'

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_django_postgresql():
    try:
        import django
        django.setup()
        
        from django.db import connection, transaction
        from django.contrib.auth import get_user_model
        
        print("🔍 Test 1: Connexion à PostgreSQL...")
        
        # Test de connexion simple
        with connection.cursor() as cursor:
            cursor.execute("SELECT version(), current_database(), current_user;")
            result = cursor.fetchone()
            print(f"✅ Connecté à: {result[1]}")
            print(f"👤 Utilisateur: {result[2]}")
            print(f"📊 Version: {result[0][:50]}...")
        
        print("\n🔍 Test 2: Lister les tables...")
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name, column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'public' 
                ORDER BY table_name, ordinal_position;
            """)
            tables_info = cursor.fetchall()
            
            current_table = None
            for table, column in tables_info:
                if table != current_table:
                    print(f"\n📋 Table: {table}")
                    current_table = table
                print(f"   - {column}")
        
        print("\n🔍 Test 3: Test CRUD avec le modèle User...")
        User = get_user_model()
        
        # Compter les utilisateurs existants
        user_count = User.objects.count()
        print(f"👥 Utilisateurs existants: {user_count}")
        
        # Vérifier si l'admin existe
        try:
            admin_user = User.objects.get(username='admin')
            print(f"✅ Admin trouvé: {admin_user.email}")
            print(f"🔐 Rôle: {admin_user.role}")
        except User.DoesNotExist:
            print("❌ Admin non trouvé")
        
        print("\n🔍 Test 4: Test d'écriture/lecture...")
        with transaction.atomic():
            # Créer un utilisateur test
            test_user = User.objects.create_user(
                username='test_user',
                email='test@example.com',
                password='test123',
                first_name='Test',
                last_name='User',
                role='employe',
                service='Test Service'
            )
            print(f"✅ Utilisateur test créé: ID {test_user.id}")
            
            # Lire l'utilisateur
            read_user = User.objects.get(username='test_user')
            print(f"✅ Utilisateur lu: {read_user.get_full_name()}")
            
            # Supprimer l'utilisateur test
            test_user.delete()
            print("✅ Utilisateur test supprimé")
        
        print("\n🎉 Tous les tests réussis ! Django est parfaitement connecté à PostgreSQL !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_django_postgresql()

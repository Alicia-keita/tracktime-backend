#!/usr/bin/env python
import os
import sys

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("🔍 Recherche de l'utilisateur 'Eva' dans la base de données...")

try:
    # Chercher l'utilisateur Eva
    eva_user = User.objects.get(username='Eva')
    
    print("✅ Utilisateur 'Eva' trouvé !")
    print(f"📋 ID: {eva_user.id}")
    print(f"👤 Username: {eva_user.username}")
    print(f"📧 Email: {eva_user.email}")
    print(f"👨‍💼 First Name: {eva_user.first_name}")
    print(f"👩‍💼 Last Name: {eva_user.last_name}")
    print(f"🔐 Is Staff: {eva_user.is_staff}")
    print(f"👑 Is Superuser: {eva_user.is_superuser}")
    print(f"📅 Date Joined: {eva_user.date_joined}")
    
    # Vérifier les champs personnalisés
    if hasattr(eva_user, 'role'):
        print(f"🎭 Role: {eva_user.role}")
    if hasattr(eva_user, 'service'):
        print(f"🏢 Service: {eva_user.service}")
    if hasattr(eva_user, 'badge_rfid'):
        print(f"📱 Badge RFID: {eva_user.badge_rfid}")
    if hasattr(eva_user, 'face_id'):
        print(f"👤 Face ID: {eva_user.face_id}")
        
except User.DoesNotExist:
    print("❌ L'utilisateur 'Eva' n'existe pas dans la base de données")
    
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n📊 Tous les utilisateurs dans la base :")
all_users = User.objects.all()
for user in all_users:
    print(f"  - {user.username} ({user.email}) - Staff: {user.is_staff}")

print(f"\n📈 Total d'utilisateurs: {all_users.count()}")

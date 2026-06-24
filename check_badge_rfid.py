#!/usr/bin/env python
"""
Script pour vérifier les badge_rfid des utilisateurs
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("📋 Liste des utilisateurs et leurs badge_rfid:")
print("=" * 60)

users = User.objects.all()
print(f"Total utilisateurs: {users.count()}")

for user in users:
    print(f"Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Badge RFID: {user.badge_rfid}")
    print(f"  Role: {user.role}")
    print(f"  Service: {user.service}")
    print("-" * 40)

# Vérifier les UID MQTT reçus
print("\n🔍 Vérification des UID MQTT reçus:")
uids_to_check = ["217013220", "1992385737"]

for uid in uids_to_check:
    try:
        user = User.objects.get(badge_rfid=uid)
        print(f"✅ UID {uid} → Trouvé: {user.username}")
    except User.DoesNotExist:
        print(f"❌ UID {uid} → Non trouvé dans la base")

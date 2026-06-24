#!/usr/bin/env python
"""
Script pour assigner les badge_rfid aux utilisateurs
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

# Mapping des UID des cartes d'échantillon -> Username (pour test)
RFID_MAPPING = {
    "217013220": "Amadou",   # Carte échantillon 1
    "1992385737": "hawa",    # Carte échantillon 2
    # Pour fatou, on utilisera temporairement la même carte qu'Amadou ou une autre
    # Awa est superuser, pas de carte RFID
}

print("🔄 Assignation des badge_rfid aux utilisateurs:")
print("=" * 60)

for rfid_code, username in RFID_MAPPING.items():
    try:
        user = User.objects.get(username=username)
        user.badge_rfid = rfid_code
        user.save()
        print(f"✅ {username} → Badge RFID: {rfid_code}")
    except User.DoesNotExist:
        print(f"❌ Utilisateur {username} non trouvé")

print("\n📋 Vérification après mise à jour:")
for user in User.objects.all():
    print(f"{user.username}: {user.badge_rfid}")

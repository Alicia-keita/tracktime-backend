#!/usr/bin/env python
"""
Corriger le statut de fatou - version 2
"""
import os
import sys
import django
from pathlib import Path
from datetime import time

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from core.pointage import Pointage
from django.contrib.auth import get_user_model

User = get_user_model()

print("🔧 Correction du statut (version 2):")
print("=" * 60)

# Récupérer le pointage de fatou
try:
    user = User.objects.get(username='fatou')
    pointage = Pointage.objects.filter(employee=user, date='2026-05-04').first()
    
    if pointage:
        print(f"Pointage ID: {pointage.id}")
        print(f"Avant: statut = {pointage.statut}")
        print(f"Heure d'arrivée: {pointage.heure_arrivee}")
        
        # Forcer la mise à jour avec update()
        Pointage.objects.filter(id=pointage.id).update(statut='retard')
        
        # Recharger pour vérifier
        pointage.refresh_from_db()
        print(f"Après: statut = {pointage.statut}")
        print("✅ Statut corrigé avec succès!")
    else:
        print("❌ Aucun pointage trouvé pour fatou aujourd'hui")
        
except User.DoesNotExist:
    print("❌ Utilisateur fatou non trouvé")
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

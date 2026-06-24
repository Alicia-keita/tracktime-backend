#!/usr/bin/env python
"""
Corriger le statut de fatou
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

print("🔧 Correction du statut de fatou:")
print("=" * 60)

# Récupérer le pointage de fatou
try:
    user = User.objects.get(username='fatou')
    pointage = Pointage.objects.filter(employee=user, date='2026-05-04').first()
    
    if pointage:
        print(f"Avant: statut = {pointage.statut}")
        print(f"Heure d'arrivée: {pointage.heure_arrivee}")
        
        # Calculer le bon statut
        # Heure de référence: 9h00
        heure_reference = time(9, 0)
        
        if pointage.heure_arrivee:
            if pointage.heure_arrivee <= heure_reference:
                pointage.statut = 'present'
                print("✅ Nouveau statut: Présent (arrivée avant 9h)")
            else:
                pointage.statut = 'retard'
                print("✅ Nouveau statut: Retard (arrivée après 9h)")
            pointage.save()
        else:
            print("❌ Pas d'heure d'arrivée")
    else:
        print("❌ Aucun pointage trouvé pour fatou aujourd'hui")
        
except User.DoesNotExist:
    print("❌ Utilisateur fatou non trouvé")
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n📋 Vérification après correction:")
pointages = Pointage.objects.all()
for p in pointages:
    print(f"{p.employee.username}: {p.statut} (arrivée: {p.heure_arrivee})")

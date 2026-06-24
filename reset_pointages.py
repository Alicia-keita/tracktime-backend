#!/usr/bin/env python
"""
Réinitialiser les pointages d'aujourd'hui pour tester avec les bonnes heures
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from core.pointage import Pointage
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

print("🗑️ Réinitialisation des pointages d'aujourd'hui:")
print("=" * 60)

today = timezone.localtime(timezone.now()).date()
pointages = Pointage.objects.filter(date=today)

if pointages.count() > 0:
    for p in pointages:
        print(f"Suppression: {p.employee.username} - {p.date}")
    pointages.delete()
    print(f"✅ {pointages.count()} pointage(s) supprimé(s)")
else:
    print("ℹ️ Aucun pointage à supprimer")

print("\n📋 Pointages restants:")
remaining = Pointage.objects.all()
for p in remaining:
    print(f"{p.employee.username}: {p.date} - {p.heure_arrivee}")

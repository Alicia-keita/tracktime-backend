#!/usr/bin/env python
"""
Script pour vérifier les données de pointage dans la base
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

User = get_user_model()

print("📋 Données de pointage dans la base:")
print("=" * 80)

pointages = Pointage.objects.all()
print(f"Total pointages: {pointages.count()}")

for p in pointages:
    print(f"\n👤 Employé: {p.employee.username}")
    print(f"📅 Date: {p.date} (type: {type(p.date)})")
    print(f"🕐 Heure arrivée: {p.heure_arrivee} (type: {type(p.heure_arrivee)})")
    print(f"☕ Début pause: {p.debut_pause} (type: {type(p.debut_pause)})")
    print(f"🏁 Fin pause: {p.fin_pause} (type: {type(p.fin_pause)})")
    print(f"🚪 Heure départ: {p.heure_depart} (type: {type(p.heure_depart)})")
    print(f"📊 Statut: {p.statut}")
    print(f"⏱️ Heures travaillées: {p.heures_travaillees}")
    print("-" * 80)

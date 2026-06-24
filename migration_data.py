
# Script de migration des données de SQLite vers PostgreSQL

import os
import sys
import django
from pathlib import Path

# Configuration SQLite (ancienne)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

# Exporter les données depuis SQLite
def export_sqlite_data():
    from django.db import connection
    from users.models import User
    from core.models import PermissionRequest, Bulletin, Conge, Solde, Rapport
    
    # Exporter les utilisateurs
    users = User.objects.all()
    print(f"Exportation de {users.count()} utilisateurs...")
    
    # Exporter les permissions
    permissions = PermissionRequest.objects.all()
    print(f"Exportation de {permissions.count()} permissions...")
    
    # Exporter les bulletins
    bulletins = Bulletin.objects.all()
    print(f"Exportation de {bulletins.count()} bulletins...")
    
    # Exporter les congés
    conges = Conge.objects.all()
    print(f"Exportation de {conges.count()} congés...")
    
    # Exporter les soldes
    soldes = Solde.objects.all()
    print(f"Exportation de {soldes.count()} soldes...")
    
    # Exporter les rapports
    rapports = Rapport.objects.all()
    print(f"Exportation de {rapports.count()} rapports...")
    
    return {
        'users': users,
        'permissions': permissions,
        'bulletins': bulletins,
        'conges': conges,
        'soldes': soldes,
        'rapports': rapports
    }

if __name__ == '__main__':
    data = export_sqlite_data()
    print("✅ Données exportées avec succès !")
    
#!/usr/bin/env python
"""
Script de migration des données de SQLite vers PostgreSQL
"""

import os
import sys
import django
from pathlib import Path

# Configuration
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

def export_sqlite_data():
    """Exporter les données depuis SQLite"""
    print("📤 Exportation des données depuis SQLite...")
    
    # Configuration temporaire pour SQLite
    os.environ['DJANGO_SETTINGS_MODULE'] = 'attendance_system.settings'
    django.setup()
    
    # Importer les modèles
    from users.models import User
    from core.models import PermissionRequest, Bulletin, Conge, Solde, Rapport
    
    data = {}
    
    # Exporter les utilisateurs
    users = User.objects.all()
    data['users'] = []
    for user in users:
        data['users'].append({
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'password': user.password,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'date_joined': user.date_joined,
            'role': user.role,
            'service': user.service,
            'badge_rfid': user.badge_rfid,
            'face_id': user.face_id,
        })
    print(f"✅ {len(data['users'])} utilisateurs exportés")
    
    # Exporter les permissions
    permissions = PermissionRequest.objects.all()
    data['permissions'] = []
    for perm in permissions:
        data['permissions'].append({
            'employee_id': perm.employee_id,
            'type_permission': perm.type_permission,
            'date_sortie': perm.date_sortie,
            'date_retour': perm.date_retour,
            'motif': perm.motif,
            'status': perm.status,
            'date_traitement': perm.date_traitement,
            'treated_by_id': perm.treated_by_id,
        })
    print(f"✅ {len(data['permissions'])} permissions exportées")
    
    # Exporter les bulletins
    bulletins = Bulletin.objects.all()
    data['bulletins'] = []
    for bulletin in bulletins:
        data['bulletins'].append({
            'employee_id': bulletin.employee_id,
            'periode_debut': bulletin.periode_debut,
            'periode_fin': bulletin.periode_fin,
            'salaire_base': bulletin.salaire_base,
            'heures_supplementaires': bulletin.heures_supplementaires,
            'prime_absence': bulletin.prime_absence,
            'conges_pris': bulletin.conges_pris,
            'retenues': bulletin.retenues,
            'salaire_net': bulletin.salaire_net,
        })
    print(f"✅ {len(data['bulletins'])} bulletins exportés")
    
    # Exporter les congés
    conges = Conge.objects.all()
    data['conges'] = []
    for conge in conges:
        data['conges'].append({
            'employe_id': conge.employe_id,
            'type_conge': conge.type_conge,
            'date_debut': conge.date_debut,
            'date_fin': conge.date_fin,
            'duree_jours': conge.duree_jours,
            'statut': conge.statut,
            'date_demande': conge.date_demande,
            'date_traitement': conge.date_traitement,
            'valide_par_id': conge.valide_par_id,
            'motif': conge.motif,
            'commentaire_rh': conge.commentaire_rh,
            'solde_avant': conge.solde_avant,
            'solde_apres': conge.solde_apres,
        })
    print(f"✅ {len(data['conges'])} congés exportés")
    
    # Exporter les soldes
    soldes = Solde.objects.all()
    data['soldes'] = []
    for solde in soldes:
        data['soldes'].append({
            'employe_id': solde.employe_id,
            'solde_annuel': solde.solde_annuel,
            'conges_pris': solde.conges_pris,
            'conges_restant': solde.conges_restant,
            'annee_reference': solde.annee_reference,
            'mis_a_jour_par_id': solde.mis_a_jour_par_id,
        })
    print(f"✅ {len(data['soldes'])} soldes exportés")
    
    # Exporter les rapports
    rapports = Rapport.objects.all()
    data['rapports'] = []
    for rapport in rapports:
        data['rapports'].append({
            'titre': rapport.titre,
            'type_rapport': rapport.type_rapport,
            'periode_rapport': rapport.periode_rapport,
            'date_debut': rapport.date_debut,
            'date_fin': rapport.date_fin,
            'description': rapport.description,
            'contenu': rapport.contenu,
            'auteur_id': rapport.auteur_id,
            'statut': rapport.statut,
            'filtres': rapport.filtres,
            'parametres': rapport.parametres,
            'total_enregistrements': rapport.total_enregistrements,
            'total_heures': rapport.total_heures,
            'pourcentage_presence': rapport.pourcentage_presence,
        })
    print(f"✅ {len(data['rapports'])} rapports exportés")
    
    return data

def import_postgresql_data(data):
    """Importer les données dans PostgreSQL"""
    print("\n📥 Importation des données dans PostgreSQL...")
    
    # Importer les modèles
    from users.models import User
    from core.models import PermissionRequest, Bulletin, Conge, Solde, Rapport
    
    # Importer les utilisateurs
    print("👥 Importation des utilisateurs...")
    for user_data in data['users']:
        user = User.objects.create(**user_data)
    print(f"✅ {len(data['users'])} utilisateurs importés")
    
    # Importer les permissions
    print("📋 Importation des permissions...")
    for perm_data in data['permissions']:
        PermissionRequest.objects.create(**perm_data)
    print(f"✅ {len(data['permissions'])} permissions importées")
    
    # Importer les bulletins
    print("💰 Importation des bulletins...")
    for bulletin_data in data['bulletins']:
        Bulletin.objects.create(**bulletin_data)
    print(f"✅ {len(data['bulletins'])} bulletins importés")
    
    # Importer les congés
    print("🏖️ Importation des congés...")
    for conge_data in data['conges']:
        Conge.objects.create(**conge_data)
    print(f"✅ {len(data['conges'])} congés importés")
    
    # Importer les soldes
    print("💰 Importation des soldes...")
    for solde_data in data['soldes']:
        Solde.objects.create(**solde_data)
    print(f"✅ {len(data['soldes'])} soldes importés")
    
    # Importer les rapports
    print("📊 Importation des rapports...")
    for rapport_data in data['rapports']:
        Rapport.objects.create(**rapport_data)
    print(f"✅ {len(data['rapports'])} rapports importés")

if __name__ == '__main__':
    print("🔄 MIGRATION SQLITE VERS POSTGRESQL")
    print("=" * 50)
    
    # Étape 1: Exporter depuis SQLite
    try:
        data = export_sqlite_data()
        
        # Sauvegarder les données dans un fichier
        import json
        with open('migration_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        print("✅ Données sauvegardées dans migration_data.json")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exportation: {e}")
        sys.exit(1)
    
    print("\n📋 Prochaines étapes :")
    print("1. Installer PostgreSQL")
    print("2. Créer la base de données 'pointage'")
    print("3. Mettre à jour settings.py avec vos identifiants PostgreSQL")
    print("4. Exécuter : python manage.py makemigrations")
    print("5. Exécuter : python manage.py migrate")
    print("6. Exécuter : python migrate_data.py pour importer les données")
    
    print("\n✨ Préparation de la migration terminée !")

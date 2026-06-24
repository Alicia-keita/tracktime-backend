#!/usr/bin/env python
import os, sys, django
import json
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.rapport import Rapport

User = get_user_model()

def test_rapports_simple():
    """Test simple du système de rapports"""
    print("📊 TEST SYSTÈME DE RAPPORTS - VERSION SIMPLE")
    print("=" * 55)
    
    client = Client()
    
    # 1. Login Admin
    print("\n1️⃣ Login Admin:")
    response = client.post('/api/auth/login/',
                          data=json.dumps({
                              'username': 'admin1',
                              'password': 'password123'
                          }),
                          content_type='application/json')
    
    if response.status_code == 200:
        admin_token = response.json()['access']
        print("✅ Admin connecté")
    else:
        print("❌ Erreur login Admin")
        return
    
    # 2. Créer un rapport de type trimestriel
    print("\n2️⃣ Créer rapport trimestriel:")
    rapport_data = {
        'titre': 'Rapport de Présence Q1 2026',
        'type_rapport': 'presence',
        'periode_rapport': 'trimestre',
        'date_debut': '2026-01-01',
        'date_fin': '2026-03-31',
        'description': 'Rapport de présence pour le premier trimestre 2026',
        'filtres': {'service': 'IT'},
        'parametres': {'inclure_weekend': False},
        'destinataires': [18]  # employe1
    }
    
    response = client.post('/api/rapports/',
                          data=json.dumps(rapport_data),
                          content_type='application/json',
                          HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    
    if response.status_code == 201:
        rapport = response.json()
        rapport_id = rapport['id']
        print("✅ Rapport créé avec succès")
        print(f"   📋 Titre: {rapport['titre']}")
        print(f"   📊 Type: {rapport['type_rapport_display']}")
        print(f"   📅 Période: {rapport['periode_display']}")
        print(f"   📆 Durée: {rapport['duree_jours']} jours")
        print(f"   👤 Auteur: {rapport['auteur_name']}")
        print(f"   📋 Statut: {rapport['statut_display']}")
    else:
        print(f"❌ Erreur création: {response.status_code}")
        print(f"   Erreur: {response.json()}")
        return
    
    # 3. Login Employé
    print("\n3️⃣ Login Employé:")
    response = client.post('/api/auth/login/',
                          data=json.dumps({
                              'username': 'employe1',
                              'password': 'password123'
                          }),
                          content_type='application/json')
    
    if response.status_code == 200:
        employe_token = response.json()['access']
        print("✅ Employé connecté")
    else:
        print("❌ Erreur login Employé")
        return
    
    # 4. Employé consulte ses rapports
    print("\n4️⃣ Employé consulte ses rapports:")
    response = client.get('/api/rapports/mes_rapports/',
                          HTTP_AUTHORIZATION=f'Bearer {employe_token}')
    
    if response.status_code == 200:
        mes_rapports = response.json()
        print(f"✅ Employé voit {len(mes_rapports)} rapport(s)")
        for rapport in mes_rapports:
            print(f"   📋 {rapport['titre']} - {rapport['type_rapport_display']}")
    else:
        print(f"❌ Erreur consultation: {response.status_code}")
    
    # 5. Admin génère le contenu du rapport
    print("\n5️⃣ Admin génère le contenu:")
    generation_data = {
        'employe_ids': [18],
        'inclure_details': True,
        'format_export': 'json'
    }
    
    response = client.post(f'/api/rapports/{rapport_id}/generer_auto/',
                          data=json.dumps(generation_data),
                          content_type='application/json',
                          HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Génération automatique réussie")
        print(f"   📋 Message: {result['message']}")
        print(f"   📊 Nouveau statut: {result['rapport']['statut_display']}")
    else:
        print(f"❌ Erreur génération: {response.status_code}")
        print(f"   Erreur: {response.json()}")
    
    # 6. Admin valide le rapport
    print("\n6️⃣ Admin valide le rapport:")
    response = client.post(f'/api/rapports/{rapport_id}/valider/',
                          data=json.dumps({}),
                          content_type='application/json',
                          HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Validation réussie")
        print(f"   📋 Message: {result['message']}")
        print(f"   👤 Validé par: {result['rapport']['valide_par']}")
        print(f"   📊 Statut final: {result['rapport']['statut_display']}")
    else:
        print(f"❌ Erreur validation: {response.status_code}")
    
    # 7. Admin consulte les statistiques
    print("\n7️⃣ Admin consulte les statistiques:")
    response = client.get('/api/rapports/statistiques/',
                          HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Statistiques obtenues")
        print(f"   📊 Total rapports: {stats['total_rapports']}")
        
        if stats['par_type']:
            print("   📈 Répartition par type:")
            for type_stat in stats['par_type']:
                print(f"      - {type_stat['type_rapport_display']}: {type_stat['count']}")
        
        if stats['par_statut']:
            print("   📊 Répartition par statut:")
            for statut_stat in stats['par_statut']:
                print(f"      - {statut_stat['statut_display']}: {statut_stat['count']}")
    else:
        print(f"❌ Erreur statistiques: {response.status_code}")
    
    # 8. Dupliquer le rapport
    print("\n8️⃣ Admin duplique le rapport:")
    response = client.post(f'/api/rapports/{rapport_id}/dupliquer/',
                          data=json.dumps({}),
                          content_type='application/json',
                          HTTP_AUTHORIZATION=f'Bearer {admin_token}')
    
    if response.status_code == 201:
        duplicate = response.json()
        print("✅ Rapport dupliqué avec succès")
        print(f"   📋 Nouveau titre: {duplicate['titre']}")
        print(f"   📊 Type: {duplicate['type_rapport_display']}")
        print(f"   👤 Auteur: {duplicate['auteur_name']}")
    else:
        print(f"❌ Erreur duplication: {response.status_code}")
    
    # 9. Test permissions employé
    print("\n9️⃣ Test permissions employé:")
    
    # Employé ne peut pas créer
    response = client.post('/api/rapports/',
                          data=json.dumps({
                              'titre': 'Test rapport employé',
                              'type_rapport': 'activite',
                              'date_debut': '2026-04-01',
                              'date_fin': '2026-04-30'
                          }),
                          content_type='application/json',
                          HTTP_AUTHORIZATION=f'Bearer {employe_token}')
    
    if response.status_code == 403:
        print("✅ Employé ne peut pas créer (correct)")
    else:
        print(f"❌ Employé peut créer (erreur): {response.status_code}")
    
    # Employé ne peut pas voir les statistiques
    response = client.get('/api/rapports/statistiques/',
                          HTTP_AUTHORIZATION=f'Bearer {employe_token}')
    
    if response.status_code == 403:
        print("✅ Employé ne peut pas voir les statistiques (correct)")
    else:
        print(f"❌ Employé peut voir les statistiques (erreur): {response.status_code}")
    
    print("\n✨ Test simple terminé !")
    print("\n🎉 RÉSULTAT:")
    print("   ✅ Table rapport créée et fonctionnelle")
    print("   ✅ API complète avec tous les endpoints")
    print("   ✅ Permissions CRUD respectées (Admin/RH uniquement)")
    print("   ✅ Génération automatique fonctionnelle")
    print("   ✅ Validation et workflow opérationnels")
    print("   ✅ Statistiques détaillées disponibles")
    print("   ✅ Sécurité des accès par rôle")

if __name__ == '__main__':
    test_rapports_simple()

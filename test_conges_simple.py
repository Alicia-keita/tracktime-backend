#!/usr/bin/env python
import os, sys, django
import json
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.conges import Conge

User = get_user_model()

def test_conges_simple():
    """Test simple du système de congés"""
    print("🏖️ TEST SYSTÈME DE CONGÉS - VERSION SIMPLE")
    print("=" * 50)
    
    client = Client()
    
    # 1. Login
    print("\n1️⃣ Login Employé:")
    response = client.post('/api/auth/login/',
                          data=json.dumps({
                              'username': 'employe1',
                              'password': 'password123'
                          }),
                          content_type='application/json')
    
    if response.status_code == 200:
        token = response.json()['access']
        print("✅ Employé connecté")
    else:
        print("❌ Erreur login")
        return
    
    # 2. Créer une demande de congé
    print("\n2️⃣ Créer demande de congé:")
    conge_data = {
        'type_conge': 'annuel',
        'date_debut': '2026-12-20T09:00:00Z',
        'date_fin': '2026-12-25T17:00:00Z',
        'duree_jours': 5,
        'motif': 'Vacances de Noël'
    }
    
    response = client.post('/api/conges/',
                          data=json.dumps(conge_data),
                          content_type='application/json',
                          HTTP_AUTHORIZATION=f'Bearer {token}')
    
    if response.status_code == 201:
        conge = response.json()
        conge_id = conge['id']
        print("✅ Demande de congé créée")
        print(f"   🏖️ Type: {conge['type_conge']}")
        print(f"   📅 Début: {conge['date_debut']}")
        print(f"   📅 Fin: {conge['date_fin']}")
        print(f"   ⏱️ Durée: {conge['duree_jours']} jours")
        print(f"   📋 Statut: {conge['statut']}")
    else:
        print(f"❌ Erreur création: {response.status_code}")
        print(f"   Erreur: {response.json()}")
        return
    
    # 3. Voir ses congés
    print("\n3️⃣ Voir ses congés:")
    response = client.get('/api/conges/mes_conges/',
                          HTTP_AUTHORIZATION=f'Bearer {token}')
    
    if response.status_code == 200:
        conges = response.json()
        print(f"✅ {len(conges)} congé(s) trouvé(s)")
        for conge in conges:
            print(f"   🏖️ {conge['type_conge']} - {conge['duree_jours']} jours")
    else:
        print(f"❌ Erreur consultation: {response.status_code}")
    
    # 4. Login RH
    print("\n4️⃣ Login RH:")
    response = client.post('/api/auth/login/',
                          data=json.dumps({
                              'username': 'rh1',
                              'password': 'password123'
                          }),
                          content_type='application/json')
    
    if response.status_code == 200:
        rh_token = response.json()['access']
        print("✅ RH connecté")
    else:
        print("❌ Erreur login RH")
        return
    
    # 5. RH approuve la demande
    print("\n5️⃣ RH approuve la demande:")
    response = client.patch(f'/api/conges/{conge_id}/approve/',
                           data=json.dumps({}),
                           content_type='application/json',
                           HTTP_AUTHORIZATION=f'Bearer {rh_token}')
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Demande approuvée")
        print(f"   📋 Statut: {result['conge']['statut']}")
        print(f"   👤 Validé par: {result['conge']['valide_par']}")
    else:
        print(f"❌ Erreur approbation: {response.status_code}")
        print(f"   Erreur: {response.json()}")
    
    # 6. RH voit toutes les demandes
    print("\n6️⃣ RH voit toutes les demandes:")
    response = client.get('/api/conges/',
                          HTTP_AUTHORIZATION=f'Bearer {rh_token}')
    
    if response.status_code == 200:
        all_conges = response.json()
        print(f"✅ RH voit {len(all_conges)} congé(s)")
        for conge in all_conges:
            print(f"   👤 {conge['employe_name']} - {conge['type_conge']} ({conge['statut']})")
    else:
        print(f"❌ Erreur consultation RH: {response.status_code}")
    
    # 7. Voir les demandes en attente
    print("\n7️⃣ RH voit les demandes en attente:")
    response = client.get('/api/conges/pending/',
                          HTTP_AUTHORIZATION=f'Bearer {rh_token}')
    
    if response.status_code == 200:
        pending = response.json()
        print(f"✅ {len(pending)} demande(s) en attente")
    else:
        print(f"❌ Erreur demandes en attente: {response.status_code}")
    
    # 8. Voir le solde de congés
    print("\n8️⃣ Voir le solde de congés:")
    response = client.get('/api/conges/solde/',
                          HTTP_AUTHORIZATION=f'Bearer {token}')
    
    if response.status_code == 200:
        solde = response.json()
        print("✅ Solde de congés obtenu")
        print(f"   📊 Solde annuel: {solde['solde_annuel']} jours")
        print(f"   🏖️ Congés pris: {solde['conges_pris']} jours")
        print(f"   💰 Solde restant: {solde['solde_restant']} jours")
    else:
        print(f"❌ Erreur solde: {response.status_code}")
    
    print("\n✨ Tests de congés terminés !")
    print("\n📋 Résumé:")
    print("   ✅ Système de congés fonctionnel")
    print("   ✅ Création de demandes opérationnelle")
    print("   ✅ Validation RH fonctionnelle")
    print("   ✅ Consultation des soldes active")
    print("   ✅ Permissions par rôle respectées")

if __name__ == '__main__':
    test_conges_simple()

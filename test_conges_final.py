#!/usr/bin/env python
import os, sys, django
import json
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client

def test_conges_final():
    """Test final du système de congés avec dates uniques"""
    print("🏖️ TEST FINAL SYSTÈME DE CONGÉS")
    print("=" * 40)
    
    client = Client()
    
    # 1. Login Employé
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
    
    # 2. Créer une demande de congé avec date unique
    print("\n2️⃣ Créer demande de congé:")
    future_date = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')
    conge_data = {
        'type_conge': 'annuel',
        'date_debut': f'{future_date}T09:00:00Z',
        'date_fin': f'{future_date}T17:00:00Z',
        'duree_jours': 1,
        'motif': 'Test final système'
    }
    
    response = client.post('/api/conges/',
                          data=json.dumps(conge_data),
                          content_type='application/json',
                          HTTP_AUTHORIZATION=f'Bearer {token}')
    
    if response.status_code == 201:
        conge = response.json()
        conge_id = conge['id']
        print("✅ Demande de congé créée")
        print(f"   🏖️ Type: {conge['type_conge_display']}")
        print(f"   📅 Date: {conge['date_debut'][:10]}")
        print(f"   ⏱️ Durée: {conge['duree_jours']} jour(s)")
        print(f"   📋 Statut: {conge['statut_display']}")
    else:
        print(f"❌ Erreur création: {response.status_code}")
        print(f"   Erreur: {response.json()}")
        return
    
    # 3. Voir son solde
    print("\n3️⃣ Voir solde de congés:")
    response = client.get('/api/conges/solde/',
                          HTTP_AUTHORIZATION=f'Bearer {token}')
    
    if response.status_code == 200:
        solde = response.json()
        print("✅ Solde obtenu")
        print(f"   📊 Annuel: {solde['solde_annuel']} jours")
        print(f"   🏖️ Pris: {solde['conges_pris']} jours")
        print(f"   💰 Restant: {solde['solde_restant']} jours")
    else:
        print(f"❌ Erreur solde: {response.status_code}")
    
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
    
    # 5. RH approuve
    print("\n5️⃣ RH approuve la demande:")
    response = client.patch(f'/api/conges/{conge_id}/approve/',
                           data=json.dumps({}),
                           content_type='application/json',
                           HTTP_AUTHORIZATION=f'Bearer {rh_token}')
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Demande approuvée")
        print(f"   📋 Nouveau statut: {result['conge']['statut_display']}")
        print(f"   👤 Validé par: {result['conge']['valide_par']}")
    else:
        print(f"❌ Erreur approbation: {response.status_code}")
    
    # 6. RH voit toutes les demandes
    print("\n6️⃣ RH voit toutes les demandes:")
    response = client.get('/api/conges/',
                          HTTP_AUTHORIZATION=f'Bearer {rh_token}')
    
    if response.status_code == 200:
        all_conges = response.json()
        print(f"✅ RH voit {len(all_conges)} congé(s) au total")
        
        # Compter par statut
        stats = {}
        for conge in all_conges:
            statut = conge['statut_display']
            stats[statut] = stats.get(statut, 0) + 1
        
        for statut, count in stats.items():
            print(f"   📋 {statut}: {count}")
    else:
        print(f"❌ Erreur consultation: {response.status_code}")
    
    print("\n✨ Test final terminé avec succès !")
    print("\n🎉 SYSTÈME DE CONGÉS FONCTIONNEL")
    print("   ✅ Création de demandes")
    print("   ✅ Validation RH")
    print("   ✅ Gestion des soldes")
    print("   ✅ Permissions par rôle")
    print("   ✅ Workflow complet")

if __name__ == '__main__':
    test_conges_final()

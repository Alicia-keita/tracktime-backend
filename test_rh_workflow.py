#!/usr/bin/env python
import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

def test_rh_workflow():
    """Tester le workflow complet RH : réception et traitement des demandes"""
    client = Client()
    base_url = '/api/permissions/'
    
    print("🔄 WORKFLOW RH - RÉCEPTION ET TRAITEMENT DES DEMANDES")
    print("=" * 60)
    
    # 1. Connexion RH
    print("\n1️⃣ Connexion RH...")
    response = client.post('/api/login/', 
                          data=json.dumps({'username': 'rh1', 'password': 'password123'}),
                          content_type='application/json')
    
    if response.status_code == 200:
        token = response.json()['access']
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        print("✅ RH connecté avec succès")
    else:
        print("❌ Erreur connexion RH")
        return
    
    # 2. Voir toutes les demandes (perspective RH)
    print("\n2️⃣ Voir toutes les demandes de permission...")
    response = client.get(base_url, **headers)
    
    if response.status_code == 200:
        all_requests = response.json()
        print(f"✅ Total des demandes: {len(all_requests)}")
        
        for req in all_requests:
            print(f"   📋 ID {req['id']}: {req['employee_name']} - {req['type_permission_display']} ({req['status_display']})")
    else:
        print(f"❌ Erreur: {response.status_code}")
    
    # 3. Voir uniquement les demandes en attente (ce que RH doit traiter)
    print("\n3️⃣ Voir les demandes en attente de traitement...")
    response = client.get(base_url + 'pending/', **headers)
    
    if response.status_code == 200:
        pending_requests = response.json()
        print(f"✅ Demandes en attente: {len(pending_requests)}")
        
        if not pending_requests:
            print("   ℹ️  Aucune demande en attente")
            return
        
        # Afficher les détails de chaque demande en attente
        for req in pending_requests:
            print(f"\n   📝 DEMANDE #{req['id']}:")
            print(f"      👤 Employé: {req['employee_first_name']} {req['employee_last_name']} ({req['employee_name']})")
            print(f"      📅 Type: {req['type_permission_display']}")
            print(f"      ⏰ Période: {req['date_sortie']} → {req['date_retour']}")
            print(f"      💭 Motif: {req['motif']}")
            print(f"      📊 Statut: {req['status_display']}")
            print(f"      🕐 Demandé le: {req['date_demande']}")
        
        # 4. Traiter la première demande en attente
        first_request = pending_requests[0]
        request_id = first_request['id']
        
        print(f"\n4️⃣ Traitement de la demande #{request_id}...")
        print("   Options disponibles:")
        print("   a) Approuver")
        print("   b) Rejeter")
        print("   c) Ignorer")
        
        # Pour la démo, nous allons approuver
        choice = 'a'  # Automatique pour la démo
        
        if choice == 'a':
            print(f"\n   ✅ Approuver la demande #{request_id}...")
            approve_data = {
                'commentaire_rh': f'Demande approuvée par {client.session.get("user", "RH")} - Bonnes vacances !'
            }
            
            response = client.patch(f"{base_url}{request_id}/approve/",
                                  data=json.dumps(approve_data),
                                  content_type='application/json',
                                  **headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result['message']}")
                
                # Afficher la demande mise à jour
                updated_request = result['permission_request']
                print(f"   📊 Nouveau statut: {updated_request['status_display']}")
                print(f"   👤 Traité par: {updated_request['rh_traitant_name']}")
                print(f"   💬 Commentaire: {updated_request['commentaire_rh']}")
                print(f"   🕐 Traité le: {updated_request['date_traitement']}")
            else:
                print(f"   ❌ Erreur approbation: {response.json()}")
                
        elif choice == 'b':
            print(f"\n   ❌ Rejeter la demande #{request_id}...")
            reject_data = {
                'commentaire_rh': 'Demande rejetée - Période critique pour le service'
            }
            
            response = client.patch(f"{base_url}{request_id}/reject/",
                                  data=json.dumps(reject_data),
                                  content_type='application/json',
                                  **headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ {result['message']}")
            else:
                print(f"   ❌ Erreur rejet: {response.json()}")
    
    # 5. Vérifier l'état final
    print("\n5️⃣ Vérification de l'état final...")
    response = client.get(base_url + 'pending/', **headers)
    
    if response.status_code == 200:
        remaining_pending = response.json()
        print(f"✅ Demandes restantes en attente: {len(remaining_pending)}")
    
    print("\n✨ Workflow RH terminé !")

def check_rh_notifications():
    """Simuler la vérification des notifications RH"""
    print("\n🔔 SYSTÈME DE NOTIFICATION RH")
    print("=" * 40)
    
    client = Client()
    
    # Connexion RH
    response = client.post('/api/login/', 
                          data=json.dumps({'username': 'rh1', 'password': 'password123'}),
                          content_type='application/json')
    
    if response.status_code == 200:
        token = response.json()['access']
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        
        # Vérifier s'il y a de nouvelles demandes
        response = client.get('/api/permissions/pending/', **headers)
        
        if response.status_code == 200:
            pending = response.json()
            
            if pending:
                print(f"🔔 NOUVELLES NOTIFICATIONS: {len(pending)} demande(s) en attente")
                for req in pending:
                    print(f"   📢 {req['employee_name']} a demandé {req['type_permission_display']}")
            else:
                print("✅ Aucune nouvelle notification")
    
    print("\n💡 Le RH peut vérifier régulièrement: GET /api/permissions/pending/")

if __name__ == '__main__':
    test_rh_workflow()
    check_rh_notifications()

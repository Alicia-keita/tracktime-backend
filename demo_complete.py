import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
import json
from datetime import datetime, timedelta

print("🔄 DÉMO COMPLÈTE : CRÉATION ET TRAITEMENT DEMANDE")
print("=" * 55)

# Étape 1: Employé crée une demande
print("\n1️⃣ Employé crée une demande...")
client = Client()

# Login employé
response = client.post('/api/login/', 
                      data=json.dumps({'username': 'employe1', 'password': 'password123'}),
                      content_type='application/json')

if response.status_code == 200:
    token_emp = response.json()['access']
    
    # Créer demande
    permission_data = {
        'type_permission': 'leave',
        'date_sortie': (datetime.now() + timedelta(days=2)).isoformat() + 'Z',
        'date_retour': (datetime.now() + timedelta(days=4)).isoformat() + 'Z',
        'motif': 'Vacances familiales importantes'
    }
    
    response = client.post('/api/permissions/',
                          data=json.dumps(permission_data),
                          content_type='application/json',
                          HTTP_AUTHORIZATION=f'Bearer {token_emp}')
    
    if response.status_code == 201:
        created_request = response.json()
        print(f"✅ Demande créée - ID: {created_request['id']}")
        print(f"   👤 Employé: {created_request['employee_name']}")
        print(f"   📅 Période: {created_request['date_sortie']} → {created_request['date_retour']}")
        print(f"   📊 Statut: {created_request['status_display']}")
        request_id = created_request['id']
    else:
        print(f"❌ Erreur création: {response.json()}")
        exit()

# Étape 2: RH vérifie les demandes en attente
print("\n2️⃣ RH vérifie les demandes en attente...")

# Login RH
response = client.post('/api/login/', 
                      data=json.dumps({'username': 'rh1', 'password': 'password123'}),
                      content_type='application/json')

if response.status_code == 200:
    token_rh = response.json()['access']
    
    # Vérifier les demandes en attente
    response = client.get('/api/permissions/pending/',
                         HTTP_AUTHORIZATION=f'Bearer {token_rh}')
    
    if response.status_code == 200:
        pending = response.json()
        print(f"📋 Demandes en attente trouvées: {len(pending)}")
        
        for req in pending:
            print(f"\n   📝 DEMANDE #{req['id']}:")
            print(f"      👤 Employé: {req['employee_first_name']} {req['employee_last_name']}")
            print(f"      📅 Type: {req['type_permission_display']}")
            print(f"      ⏰ Période: {req['date_sortie'][:10]} → {req['date_retour'][:10]}")
            print(f"      💭 Motif: {req['motif']}")
            print(f"      📊 Statut: {req['status_display']}")
            print(f"      🕐 Demandé le: {req['date_demande'][:19]}")
            
            # Étape 3: RH traite la demande
            print(f"\n3️⃣ RH traite la demande #{req['id']}...")
            
            # Pour la démo, on approuve si c'est un congé, sinon on rejette
            if req['type_permission'] == 'leave':
                print("   ✅ Approuver la demande...")
                approve_data = {'commentaire_rh': 'Congé approuvé - Profitez bien de vos vacances !'}
                
                response = client.patch(f'/api/permissions/{req["id"]}/approve/',
                                      data=json.dumps(approve_data),
                                      content_type='application/json',
                                      HTTP_AUTHORIZATION=f'Bearer {token_rh}')
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ {result['message']}")
                    updated = result['permission_request']
                    print(f"   📊 Nouveau statut: {updated['status_display']}")
                    print(f"   👤 Traité par: {updated['rh_traitant_name']}")
                    print(f"   💬 Commentaire: {updated['commentaire_rh']}")
                    print(f"   🕐 Traité le: {updated['date_traitement'][:19]}")
                else:
                    print(f"   ❌ Erreur: {response.json()}")
            else:
                print("   ❌ Rejeter la demande...")
                reject_data = {'commentaire_rh': 'Demande rejetée - Veuillez contacter directement votre manager'}
                
                response = client.patch(f'/api/permissions/{req["id"]}/reject/',
                                      data=json.dumps(reject_data),
                                      content_type='application/json',
                                      HTTP_AUTHORIZATION=f'Bearer {token_rh}')
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"   ✅ {result['message']}")

# Étape 4: Vérification finale
print("\n4️⃣ Vérification finale...")
response = client.get('/api/permissions/pending/',
                     HTTP_AUTHORIZATION=f'Bearer {token_rh}')

if response.status_code == 200:
    remaining = response.json()
    print(f"✅ Demandes restantes en attente: {len(remaining)}")

print("\n✨ Démonstration terminée !")
print("\n💡 Le RH peut maintenant:")
print("   - Vérifier: GET /api/permissions/pending/")
print("   - Approuver: PATCH /api/permissions/{id}/approve/")
print("   - Rejeter: PATCH /api/permissions/{id}/reject/")

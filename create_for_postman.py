import os, sys, django
import json
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client

print("🆕 CRÉATION D'UNE NOUVELLE DEMANDE POUR POSTMAN")
print("=" * 50)

# Client pour simuler la requête
client = Client()

# 1. Login employé
print("\n1️⃣ Connexion employé...")
response = client.post('/api/login/', 
                      data=json.dumps({'username': 'employe1', 'password': 'password123'}),
                      content_type='application/json')

if response.status_code == 200:
    token = response.json()['access']
    print("✅ Employé connecté")
    
    # 2. Créer une nouvelle demande
    print("\n2️⃣ Création d'une nouvelle demande...")
    
    permission_data = {
        'type_permission': 'absence',  # Type différent pour varier
        'date_sortie': (datetime.now() + timedelta(days=1)).isoformat() + 'Z',
        'date_retour': (datetime.now() + timedelta(days=1, hours=2)).isoformat() + 'Z',
        'motif': 'Rendez-vous médical important'
    }
    
    response = client.post('/api/permissions/',
                          data=json.dumps(permission_data),
                          content_type='application/json',
                          HTTP_AUTHORIZATION=f'Bearer {token}')
    
    if response.status_code == 201:
        created_request = response.json()
        print(f"✅ Nouvelle demande créée avec succès !")
        print(f"   📋 ID: {created_request['id']}")
        print(f"   👤 Employé: {created_request['employee_name']}")
        print(f"   📅 Type: {created_request['type_permission_display']}")
        print(f"   ⏰ Période: {created_request['date_sortie'][:19]} → {created_request['date_retour'][:19]}")
        print(f"   💭 Motif: {created_request['motif']}")
        print(f"   📊 Statut: {created_request['status_display']}")
        print(f"   🕐 Demandé le: {created_request['date_demande'][:19]}")
        
        print(f"\n🌐 MAINTENANT VOUS POUVEZ VOIR CETTE DEMANDE DANS POSTMAN :")
        print(f"   GET http://127.0.0.1:8000/api/permissions/pending/")
        print(f"   Authorization: Bearer <TOKEN_RH>")
        print(f"   \n   📋 Vous devriez voir la demande ID {created_request['id']}")
        
        # 3. Vérifier immédiatement que la demande est bien en attente
        print(f"\n3️⃣ Vérification que la demande est bien en attente...")
        
        # Login RH pour vérifier
        rh_response = client.post('/api/login/', 
                                data=json.dumps({'username': 'rh1', 'password': 'password123'}),
                                content_type='application/json')
        
        if rh_response.status_code == 200:
            rh_token = rh_response.json()['access']
            
            check_response = client.get('/api/permissions/pending/',
                                       HTTP_AUTHORIZATION=f'Bearer {rh_token}')
            
            if check_response.status_code == 200:
                pending = check_response.json()
                print(f"✅ Confirmation: {len(pending)} demande(s) en attente trouvée(s)")
                
                for req in pending:
                    if req['id'] == created_request['id']:
                        print(f"   🎯 Demande ID {req['id']} trouvée en attente !")
                        print(f"   👤 {req['employee_name']} - {req['type_permission_display']}")
                        print(f"   💭 {req['motif']}")
                        break
            else:
                print(f"❌ Erreur vérification: {check_response.status_code}")
        
    else:
        print(f"❌ Erreur création: {response.json()}")
else:
    print(f"❌ Erreur connexion: {response.status_code}")

print(f"\n✨ Prêt pour Postman !")
print(f"💡 Utilisez les identifiants RH (rh1/password123) pour voir la demande en attente")

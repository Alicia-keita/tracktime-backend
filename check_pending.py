import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
import json

# Login RH
client = Client()
response = client.post('/api/login/', 
                      data=json.dumps({'username': 'rh1', 'password': 'password123'}),
                      content_type='application/json')

if response.status_code == 200:
    token = response.json()['access']
    print('✅ Token RH obtenu')
    
    # Vérifier les demandes en attente
    response = client.get('/api/permissions/pending/', 
                         HTTP_AUTHORIZATION=f'Bearer {token}')
    
    if response.status_code == 200:
        pending = response.json()
        print(f'📋 Demandes en attente: {len(pending)}')
        
        if pending:
            for req in pending:
                print(f'   📝 ID {req["id"]}: {req["employee_name"]} - {req["type_permission_display"]}')
                print(f'      📅 {req["date_sortie"]} → {req["date_retour"]}')
                print(f'      💭 {req["motif"]}')
                
                # Exemple d'approbation automatique pour la démo
                if req["id"] == 3:  # Approuver la demande 3
                    print(f'   ✅ Approuver la demande {req["id"]}...')
                    approve_response = client.patch(f'/api/permissions/{req["id"]}/approve/',
                                                  data=json.dumps({'commentaire_rh': 'Approuvé via test !'}),
                                                  content_type='application/json',
                                                  HTTP_AUTHORIZATION=f'Bearer {token}')
                    
                    if approve_response.status_code == 200:
                        print(f'      ✅ {approve_response.json()["message"]}')
        else:
            print('   ℹ️  Aucune demande en attente')
    else:
        print(f'❌ Erreur: {response.status_code}')
else:
    print('❌ Erreur login')

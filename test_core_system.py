#!/usr/bin/env python
import os, sys, django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client

print('TEST SYSTEME CORE UNIQUE')
print('=' * 40)

# 1. Login RH
client = Client()
response = client.post('/api/login/', 
                      data=json.dumps({'username': 'rh1', 'password': 'password123'}),
                      content_type='application/json')

if response.status_code == 200:
    token = response.json()['access']
    print('[OK] Login RH réussi')
    
    # 2. Créer une permission
    perm_data = {
        'type_permission': 'leave',
        'date_sortie': '2026-04-10T09:00:00Z',
        'date_retour': '2026-04-12T17:00:00Z',
        'motif': 'Test système core'
    }
    
    response = client.post('/api/permissions/',
                          data=json.dumps(perm_data),
                          content_type='application/json',
                          HTTP_AUTHORIZATION=f'Bearer {token}')
    
    if response.status_code == 201:
        print('[OK] Permission créée')
        
        # 3. Générer un bulletin
        bulletin_data = {
            'employee': 18,
            'periode_debut': '2026-04-01',
            'periode_fin': '2026-04-30'
        }
        
        response = client.post('/api/bulletins/generate/',
                              data=json.dumps(bulletin_data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer {token}')
        
        if response.status_code == 201:
            result = response.json()
            print('[OK] Bulletin généré')
            print('   Salaire net: ' + str(result['bulletin']['salaire_net']) + ' €')
        else:
            print('[ERROR] Erreur bulletin: ' + str(response.status_code))
    else:
        print('[ERROR] Erreur permission: ' + str(response.status_code))
else:
    print('[ERROR] Erreur login')

print('[DONE] Test terminé!')

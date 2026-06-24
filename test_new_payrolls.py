#!/usr/bin/env python
import os, sys, django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client

print('🔄 TEST NOUVELLE APPLICATION PAYROLLS')
print('=' * 50)

# 1. Login RH
client = Client()
response = client.post('/api/login/', 
                      data=json.dumps({'username': 'rh1', 'password': 'password123'}),
                      content_type='application/json')

if response.status_code == 200:
    token = response.json()['access']
    print('✅ RH connecté')
    
    # 2. Générer bulletin
    payroll_data = {
        'employee': 18,
        'periode_debut': '2026-04-01',
        'periode_fin': '2026-04-30'
    }
    
    response = client.post('/api/payrolls/generate/',
                          data=json.dumps(payroll_data),
                          content_type='application/json',
                          HTTP_AUTHORIZATION=f'Bearer {token}')
    
    if response.status_code == 201:
        result = response.json()
        print('✅ Bulletin généré avec succès!')
        print(f'   📋 ID: {result["bulletin"]["id"]}')
        print(f'   👤 Employé: {result["bulletin"]["employee_name"]}')
        print(f'   💰 Salaire net: {result["bulletin"]["salaire_net"]} €')
    else:
        print(f'❌ Erreur: {response.status_code} - {response.json()}')
else:
    print('❌ Erreur login RH')

print('✨ Test terminé!')

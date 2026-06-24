#!/usr/bin/env python
import os, sys, django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client

def debug_conge_creation():
    """Debug de la création de congé"""
    print("🔍 DEBUG CRÉATION CONGÉ")
    print("=" * 30)
    
    client = Client()
    
    # Login
    response = client.post('/api/auth/login/',
                          data=json.dumps({
                              'username': 'employe1',
                              'password': 'password123'
                          }),
                          content_type='application/json')
    
    token = response.json()['access']
    
    # Créer une demande de congé
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
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 201:
        print("✅ Succès:")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print("❌ Erreur:")
        print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == '__main__':
    debug_conge_creation()

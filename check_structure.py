#!/usr/bin/env python
import os, sys, django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client

def check_response_structure():
    """Vérifier la structure de la réponse API"""
    print("🔍 VÉRIFICATION STRUCTURE RÉPONSE")
    print("=" * 40)
    
    client = Client()
    
    # Login
    response = client.post('/api/auth/login/',
                          data=json.dumps({
                              'username': 'employe1',
                              'password': 'password123'
                          }),
                          content_type='application/json')
    
    token = response.json()['access']
    
    # Tenter de créer un congé
    conge_data = {
        'type_conge': 'formation',
        'date_debut': '2027-01-15T09:00:00Z',
        'date_fin': '2027-01-15T17:00:00Z',
        'duree_jours': 1,
        'motif': 'Test structure'
    }
    
    response = client.post('/api/conges/',
                          data=json.dumps(conge_data),
                          content_type='application/json',
                          HTTP_AUTHORIZATION=f'Bearer {token}')
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 400:
        print("❌ Erreur 400:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    elif response.status_code == 201:
        print("✅ Succès 201:")
        response_data = response.json()
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        print(f"\n📋 Clés disponibles: {list(response_data.keys())}")
    else:
        print(f"🔄 Autre statut: {response.status_code}")
        print(response.content.decode())

if __name__ == '__main__':
    check_response_structure()

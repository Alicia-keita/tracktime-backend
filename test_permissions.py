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

def create_test_users():
    """Créer des utilisateurs de test si ils n'existent pas"""
    users_data = [
        {'username': 'employe1', 'password': 'password123', 'role': 'employe', 'first_name': 'Jean', 'last_name': 'Dupont'},
        {'username': 'rh1', 'password': 'password123', 'role': 'rh', 'first_name': 'Marie', 'last_name': 'Durand'},
        {'username': 'admin1', 'password': 'password123', 'role': 'admin', 'first_name': 'Pierre', 'last_name': 'Martin'},
    ]
    
    for user_data in users_data:
        if not User.objects.filter(username=user_data['username']).exists():
            User.objects.create_user(
                username=user_data['username'],
                password=user_data['password'],
                role=user_data['role'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                email=f"{user_data['username']}@example.com",
                service='IT'
            )
            print(f"✅ Utilisateur {user_data['username']} créé")
        else:
            print(f"ℹ️  Utilisateur {user_data['username']} existe déjà")

def get_token(client, username, password):
    """Obtenir un token JWT"""
    response = client.post('/api/login/', 
                          data=json.dumps({'username': username, 'password': password}),
                          content_type='application/json')
    if response.status_code == 200:
        return response.json()['access']
    return None

def test_permissions():
    """Tester les permissions du système"""
    client = Client()
    base_url = '/api/permissions/'
    
    print("\n🧪 TEST DES PERMISSIONS - DEMANDE DE PERMISSION")
    print("=" * 50)
    
    # Test 1: Employé peut créer une demande
    print("\n1️⃣ Test: Employé peut créer une demande")
    token = get_token(client, 'employe1', 'password123')
    if token:
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        
        permission_data = {
            'type_permission': 'leave',
            'date_sortie': (datetime.now() + timedelta(days=1)).isoformat(),
            'date_retour': (datetime.now() + timedelta(days=3)).isoformat(),
            'motif': 'Vacances familiales'
        }
        
        response = client.post(base_url, 
                              data=json.dumps(permission_data),
                              content_type='application/json',
                              **headers)
        
        if response.status_code == 201:
            print("✅ Employé peut créer une demande")
            permission_id = response.json()['id']
            print(f"   ID de la demande: {permission_id}")
        else:
            print(f"❌ Erreur: {response.status_code} - {response.json()}")
    else:
        print("❌ Impossible d'obtenir le token pour l'employé")
    
    # Test 2: RH ne peut PAS créer de demande
    print("\n2️⃣ Test: RH ne peut PAS créer une demande")
    rh_token = get_token(client, 'rh1', 'password123')
    if rh_token:
        headers = {'HTTP_AUTHORIZATION': f'Bearer {rh_token}'}
        
        response = client.post(base_url,
                              data=json.dumps(permission_data),
                              content_type='application/json',
                              **headers)
        
        if response.status_code == 403:
            print("✅ RH ne peut pas créer de demande (permission refusée)")
        else:
            print(f"❌ Erreur: RH ne devrait pas pouvoir créer - {response.status_code}")
    
    # Test 3: Admin ne peut PAS créer de demande
    print("\n3️⃣ Test: Admin ne peut PAS créer une demande")
    admin_token = get_token(client, 'admin1', 'password123')
    if admin_token:
        headers = {'HTTP_AUTHORIZATION': f'Bearer {admin_token}'}
        
        response = client.post(base_url,
                              data=json.dumps(permission_data),
                              content_type='application/json',
                              **headers)
        
        if response.status_code == 403:
            print("✅ Admin ne peut pas créer de demande (permission refusée)")
        else:
            print(f"❌ Erreur: Admin ne devrait pas pouvoir créer - {response.status_code}")
    
    # Test 4: RH peut voir les demandes en attente
    print("\n4️⃣ Test: RH peut voir les demandes en attente")
    if rh_token:
        headers = {'HTTP_AUTHORIZATION': f'Bearer {rh_token}'}
        response = client.get(base_url + 'pending/', **headers)
        
        if response.status_code == 200:
            print("✅ RH peut voir les demandes en attente")
            requests_data = response.json()
            if requests_data:
                print(f"   Nombre de demandes en attente: {len(requests_data)}")
                permission_id = requests_data[0]['id']
                
                # Test 5: RH peut approuver une demande
                print("\n5️⃣ Test: RH peut approuver une demande")
                approve_data = {'commentaire_rh': 'Approuvé par RH'}
                response = client.patch(f"{base_url}{permission_id}/approve/",
                                      data=json.dumps(approve_data),
                                      content_type='application/json',
                                      **headers)
                
                if response.status_code == 200:
                    print("✅ RH peut approuver une demande")
                else:
                    print(f"❌ Erreur approbation: {response.status_code}")
        else:
            print(f"❌ RH ne peut pas voir les demandes: {response.status_code}")
    
    # Test 6: Employé ne peut PAS approuver de demande
    print("\n6️⃣ Test: Employé ne peut PAS approuver une demande")
    if token and 'permission_id' in locals():
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        response = client.patch(f"{base_url}{permission_id}/approve/",
                              data=json.dumps({'commentaire_rh': 'test'}),
                              content_type='application/json',
                              **headers)
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas approuver (permission refusée)")
        else:
            print(f"❌ Erreur: Employé ne devrait pas pouvoir approuver - {response.status_code}")

if __name__ == '__main__':
    print("🚀 Configuration du test...")
    create_test_users()
    test_permissions()
    print("\n✨ Tests terminés!")

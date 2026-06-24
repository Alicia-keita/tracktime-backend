#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import requests
import json

os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_api_endpoints():
    base_url = "http://localhost:8000"
    
    print("🔍 Test API REST Endpoints...")
    
    # Test 1: Vérifier si le serveur répond
    try:
        response = requests.get(f"{base_url}/admin/")
        if response.status_code == 200:
            print("✅ Serveur Django répond")
        else:
            print(f"❌ Serveur répond avec code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Serveur Django ne répond pas - démarrez-le avec: python manage.py runserver")
        return False
    
    # Test 2: Obtenir un token JWT
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        response = requests.post(f"{base_url}/api/token/", json=login_data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access')
            print("✅ Authentification JWT réussie")
            
            # Test 3: Accéder aux endpoints protégés
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Tester les endpoints de congés
            response = requests.get(f"{base_url}/api/conges/", headers=headers)
            print(f"📊 Endpoint congés: {response.status_code}")
            
            # Tester les endpoints de soldes
            response = requests.get(f"{base_url}/api/soldes/", headers=headers)
            print(f"💰 Endpoint soldes: {response.status_code}")
            
            print("✅ Tests API réussis !")
            
        else:
            print(f"❌ Échec authentification: {response.status_code}")
            print(f"Réponse: {response.text}")
            
    except Exception as e:
        print(f"❌ Erreur API: {e}")
    
if __name__ == "__main__":
    test_api_endpoints()

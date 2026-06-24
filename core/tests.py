"""
Module de tests pour le système core
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
import json
from decimal import Decimal


class CoreSystemTester:
    """Classe de test pour le système core"""
    
    def __init__(self):
        self.client = Client()
        self.base_url = '/api'
    
    def test_all_modules(self):
        """Tester tous les modules du système core"""
        print("🧪 TEST COMPLET DU SYSTÈME CORE")
        print("=" * 50)
        
        # Test authentification
        self.test_auth()
        
        # Test permissions
        self.test_permissions()
        
        # Test bulletins
        self.test_bulletins()
        
        # Test gestion utilisateurs
        self.test_user_management()
        
        print("\n✨ Tests terminés !")
    
    def test_auth(self):
        """Tester le module d'authentification"""
        print("\n🔐 Test Authentification...")
        
        # Test login
        response = self.client.post(f'{self.base_url}/login/', 
                                  data=json.dumps({'username': 'rh1', 'password': 'password123'}),
                                  content_type='application/json')
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login réussi")
            print(f"   👤 Utilisateur: {token_data.get('username')}")
            print(f"   🎭 Rôle: {token_data.get('role')}")
            return token_data.get('access')
        else:
            print("❌ Login échoué")
            return None
    
    def test_permissions(self):
        """Tester le module des permissions"""
        print("\n📋 Test Permissions...")
        
        # Login employé
        response = self.client.post(f'{self.base_url}/login/', 
                                  data=json.dumps({'username': 'employe1', 'password': 'password123'}),
                                  content_type='application/json')
        
        if response.status_code == 200:
            token = response.json()['access']
            
            # Créer une demande
            permission_data = {
                'type_permission': 'leave',
                'date_sortie': '2026-04-10T09:00:00Z',
                'date_retour': '2026-04-12T17:00:00Z',
                'motif': 'Test permissions'
            }
            
            response = self.client.post(f'{self.base_url}/permissions/',
                                      data=json.dumps(permission_data),
                                      content_type='application/json',
                                      HTTP_AUTHORIZATION=f'Bearer {token}')
            
            if response.status_code == 201:
                print("✅ Permission créée avec succès")
                return True
            else:
                print(f"❌ Erreur création permission: {response.status_code}")
                return False
        else:
            print("❌ Login employé échoué")
            return False
    
    def test_bulletins(self):
        """Tester le module des bulletins"""
        print("\n💰 Test Bulletins...")
        
        # Login RH
        response = self.client.post(f'{self.base_url}/login/', 
                                  data=json.dumps({'username': 'rh1', 'password': 'password123'}),
                                  content_type='application/json')
        
        if response.status_code == 200:
            token = response.json()['access']
            
            # Générer un bulletin
            bulletin_data = {
                'employee': 18,
                'periode_debut': '2026-04-01',
                'periode_fin': '2026-04-30'
            }
            
            response = self.client.post(f'{self.base_url}/bulletins/generate/',
                                      data=json.dumps(bulletin_data),
                                      content_type='application/json',
                                      HTTP_AUTHORIZATION=f'Bearer {token}')
            
            if response.status_code == 201:
                result = response.json()
                print("✅ Bulletin généré avec succès")
                print(f"   📋 ID: {result['bulletin']['id']}")
                print(f"   💰 Salaire net: {result['bulletin']['salaire_net']} €")
                return True
            else:
                print(f"❌ Erreur génération bulletin: {response.status_code}")
                return False
        else:
            print("❌ Login RH échoué")
            return False
    
    def test_user_management(self):
        """Tester le module de gestion des utilisateurs"""
        print("\n👥 Test Gestion Utilisateurs...")
        
        # Login admin
        response = self.client.post(f'{self.base_url}/login/', 
                                  data=json.dumps({'username': 'admin1', 'password': 'password123'}),
                                  content_type='application/json')
        
        if response.status_code == 200:
            token = response.json()['access']
            
            # Lister les utilisateurs
            response = self.client.get(f'{self.base_url}/users/',
                                     HTTP_AUTHORIZATION=f'Bearer {token}')
            
            if response.status_code == 200:
                users = response.json()
                print(f"✅ {len(users)} utilisateur(s) trouvé(s)")
                return True
            else:
                print(f"❌ Erreur liste utilisateurs: {response.status_code}")
                return False
        else:
            print("❌ Login admin échoué")
            return False


if __name__ == '__main__':
    tester = CoreSystemTester()
    tester.test_all_modules()

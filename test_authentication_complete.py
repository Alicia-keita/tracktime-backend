#!/usr/bin/env python
import os, sys, django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from users.models import User

User = get_user_model()

class AuthenticationTester:
    """Tests complets du système d'authentification"""
    
    def __init__(self):
        self.client = Client()
        self.test_user = None
    
    def run_all_tests(self):
        """Exécuter tous les tests d'authentification"""
        print("🔐 TESTS COMPLETS - SYSTÈME D'AUTHENTIFICATION")
        print("=" * 60)
        
        self.test_registration()
        self.test_login()
        self.test_profile_management()
        self.test_password_operations()
        self.test_permissions_check()
        self.test_logout()
        self.test_token_refresh()
        
        print("\n✨ Tests d'authentification terminés !")
    
    def test_registration(self):
        """Tester l'inscription"""
        print("\n📝 1. TEST INSCRIPTION")
        print("-" * 30)
        
        # Test 1: Inscription valide
        user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'Password123!',
            'password_confirm': 'Password123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': 'employe',
            'service': 'IT'
        }
        
        response = self.client.post('/api/auth/register/',
                                  data=json.dumps(user_data),
                                  content_type='application/json')
        
        if response.status_code == 201:
            self.test_user = response.json()['user']
            print("✅ Inscription réussie")
            print(f"   👤 Utilisateur: {self.test_user['username']}")
            print(f"   🎭 Rôle: {self.test_user['role']}")
            print(f"   📧 Email: {self.test_user['email']}")
        else:
            print(f"❌ Erreur inscription: {response.status_code}")
            print(f"   Erreur: {response.json()}")
        
        # Test 2: Mot de passe non correspondant
        invalid_data = user_data.copy()
        invalid_data['username'] = 'testuser2'
        invalid_data['password_confirm'] = 'DifferentPassword'
        
        response = self.client.post('/api/auth/register/',
                                  data=json.dumps(invalid_data),
                                  content_type='application/json')
        
        if response.status_code == 400:
            print("✅ Validation mot de passe fonctionnelle")
        else:
            print(f"❌ Validation mot de passe échouée: {response.status_code}")
        
        # Test 3: Email déjà existant
        duplicate_data = user_data.copy()
        duplicate_data['username'] = 'testuser3'
        
        response = self.client.post('/api/auth/register/',
                                  data=json.dumps(duplicate_data),
                                  content_type='application/json')
        
        if response.status_code == 400:
            print("✅ Validation email unique fonctionnelle")
        else:
            print(f"❌ Validation email unique échouée: {response.status_code}")
    
    def test_login(self):
        """Tester la connexion"""
        print("\n🔑 2. TEST CONNEXION")
        print("-" * 30)
        
        # Test 1: Connexion valide
        login_data = {
            'username': 'testuser',
            'password': 'Password123!'
        }
        
        response = self.client.post('/api/auth/login/',
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        
        if response.status_code == 200:
            login_result = response.json()
            self.access_token = login_result['access']
            self.refresh_token = login_result['refresh']
            print("✅ Connexion réussie")
            print(f"   🔑 Access token reçu")
            print(f"   🔄 Refresh token reçu")
            print(f"   👤 Utilisateur: {login_result['user']['username']}")
        else:
            print(f"❌ Erreur connexion: {response.status_code}")
            print(f"   Erreur: {response.json()}")
        
        # Test 2: Connexion invalide
        invalid_login = {
            'username': 'testuser',
            'password': 'WrongPassword'
        }
        
        response = self.client.post('/api/auth/login/',
                                  data=json.dumps(invalid_login),
                                  content_type='application/json')
        
        if response.status_code == 400:
            print("✅ Connexion invalide rejetée")
        else:
            print(f"❌ Connexion invalide acceptée: {response.status_code}")
        
        # Test 3: Connexion avec utilisateur inexistant
        unknown_login = {
            'username': 'unknownuser',
            'password': 'Password123!'
        }
        
        response = self.client.post('/api/auth/login/',
                                  data=json.dumps(unknown_login),
                                  content_type='application/json')
        
        if response.status_code == 400:
            print("✅ Utilisateur inexistant rejeté")
        else:
            print(f"❌ Utilisateur inexistant accepté: {response.status_code}")
    
    def test_profile_management(self):
        """Tester la gestion du profil"""
        print("\n👤 3. TEST GESTION PROFIL")
        print("-" * 30)
        
        if not hasattr(self, 'access_token'):
            print("❌ Token non disponible - test ignoré")
            return
        
        # Test 1: Obtenir le profil
        response = self.client.get('/api/auth/profile/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        if response.status_code == 200:
            profile = response.json()
            print("✅ Profil obtenu avec succès")
            print(f"   👤 Nom: {profile['first_name']} {profile['last_name']}")
            print(f"   🎭 Rôle: {profile['role']}")
            print(f"   🏢 Service: {profile['service']}")
        else:
            print(f"❌ Erreur obtention profil: {response.status_code}")
        
        # Test 2: Mettre à jour le profil
        update_data = {
            'first_name': 'Test Updated',
            'last_name': 'User Updated',
            'service': 'Development'
        }
        
        response = self.client.patch('/api/auth/profile/update/',
                                   data=json.dumps(update_data),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        if response.status_code == 200:
            updated_profile = response.json()
            print("✅ Profil mis à jour avec succès")
            print(f"   👤 Nouveau nom: {updated_profile['first_name']} {updated_profile['last_name']}")
            print(f"   🏢 Nouveau service: {updated_profile['service']}")
        else:
            print(f"❌ Erreur mise à jour profil: {response.status_code}")
        
        # Test 3: Accès au profil sans token
        response = self.client.get('/api/auth/profile/')
        
        if response.status_code == 401:
            print("✅ Accès non authentifié rejeté")
        else:
            print(f"❌ Accès non authentifié accepté: {response.status_code}")
    
    def test_password_operations(self):
        """Tester les opérations de mot de passe"""
        print("\n🔒 4. TEST OPÉRATIONS MOT DE PASSE")
        print("-" * 30)
        
        if not hasattr(self, 'access_token'):
            print("❌ Token non disponible - test ignoré")
            return
        
        # Test 1: Changer le mot de passe
        password_data = {
            'old_password': 'Password123!',
            'new_password': 'NewPassword456!',
            'new_password_confirm': 'NewPassword456!'
        }
        
        response = self.client.post('/api/auth/password/change/',
                                   data=json.dumps(password_data),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        if response.status_code == 200:
            print("✅ Mot de passe changé avec succès")
            
            # Tester la connexion avec le nouveau mot de passe
            login_data = {
                'username': 'testuser',
                'password': 'NewPassword456!'
            }
            
            response = self.client.post('/api/auth/login/',
                                      data=json.dumps(login_data),
                                      content_type='application/json')
            
            if response.status_code == 200:
                self.access_token = response.json()['access']
                print("✅ Connexion avec nouveau mot de passe réussie")
            else:
                print("❌ Connexion avec nouveau mot de passe échouée")
        else:
            print(f"❌ Erreur changement mot de passe: {response.status_code}")
        
        # Test 2: Ancien mot de passe incorrect
        wrong_password_data = {
            'old_password': 'WrongPassword',
            'new_password': 'NewPassword789!',
            'new_password_confirm': 'NewPassword789!'
        }
        
        response = self.client.post('/api/auth/password/change/',
                                   data=json.dumps(wrong_password_data),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        if response.status_code == 400:
            print("✅ Ancien mot de passe incorrect rejeté")
        else:
            print(f"❌ Ancien mot de passe incorrect accepté: {response.status_code}")
        
        # Test 3: Nouveaux mots de passe non correspondants
        mismatch_data = {
            'old_password': 'NewPassword456!',
            'new_password': 'NewPassword789!',
            'new_password_confirm': 'DifferentPassword'
        }
        
        response = self.client.post('/api/auth/password/change/',
                                   data=json.dumps(mismatch_data),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        if response.status_code == 400:
            print("✅ Mots de passe non correspondants rejetés")
        else:
            print(f"❌ Mots de passe non correspondants acceptés: {response.status_code}")
        
        # Test 4: Réinitialisation de mot de passe
        reset_data = {
            'email': 'test@example.com'
        }
        
        response = self.client.post('/api/auth/password/reset/',
                                   data=json.dumps(reset_data),
                                   content_type='application/json')
        
        if response.status_code == 200:
            print("✅ Demande de réinitialisation envoyée")
        else:
            print(f"❌ Erreur réinitialisation: {response.status_code}")
    
    def test_permissions_check(self):
        """Tester la vérification des permissions"""
        print("\n🔍 5. TEST VÉRIFICATION PERMISSIONS")
        print("-" * 30)
        
        if not hasattr(self, 'access_token'):
            print("❌ Token non disponible - test ignoré")
            return
        
        # Test 1: Obtenir les permissions de l'utilisateur
        response = self.client.get('/api/auth/permissions/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        if response.status_code == 200:
            permissions = response.json()
            print("✅ Permissions obtenues avec succès")
            print(f"   🎭 Rôle: {permissions['role']}")
            print(f"   👁️  Peut créer permission: {permissions['can_create_permission']}")
            print(f"   ✅ Peut approuver permission: {permissions['can_approve_permission']}")
            print(f"   💰 Peut générer bulletin: {permissions['can_generate_bulletin']}")
            print(f"   🗑️  Peut supprimer bulletin: {permissions['can_delete_bulletin']}")
            print(f"   👥 Peut gérer utilisateurs: {permissions['can_manage_users']}")
        else:
            print(f"❌ Erreur obtention permissions: {response.status_code}")
        
        # Test 2: Accès aux permissions sans token
        response = self.client.get('/api/auth/permissions/')
        
        if response.status_code == 401:
            print("✅ Accès non authentifié rejeté")
        else:
            print(f"❌ Accès non authentifié accepté: {response.status_code}")
    
    def test_logout(self):
        """Tester la déconnexion"""
        print("\n🚪 6. TEST DÉCONNEXION")
        print("-" * 30)
        
        if not hasattr(self, 'refresh_token'):
            print("❌ Refresh token non disponible - test ignoré")
            return
        
        # Test 1: Déconnexion réussie
        logout_data = {
            'refresh': self.refresh_token
        }
        
        response = self.client.post('/api/auth/logout/',
                                   data=json.dumps(logout_data),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        if response.status_code == 200:
            print("✅ Déconnexion réussie")
        else:
            print(f"❌ Erreur déconnexion: {response.status_code}")
        
        # Test 2: Utiliser le token après déconnexion
        response = self.client.get('/api/auth/profile/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Le token devrait toujours fonctionner (déconnexion blacklist)
        if response.status_code == 200:
            print("✅ Token toujours valide après déconnexion normale")
        else:
            print("⚠️  Token invalidé après déconnexion")
    
    def test_token_refresh(self):
        """Tester le rafraîchissement du token"""
        print("\n🔄 7. TEST RAFRAÎCHISSEMENT TOKEN")
        print("-" * 30)
        
        if not hasattr(self, 'refresh_token'):
            print("❌ Refresh token non disponible - test ignoré")
            return
        
        # Test 1: Rafraîchissement réussi
        refresh_data = {
            'refresh': self.refresh_token
        }
        
        response = self.client.post('/api/auth/refresh/',
                                   data=json.dumps(refresh_data),
                                   content_type='application/json')
        
        if response.status_code == 200:
            new_token = response.json()['access']
            print("✅ Token rafraîchi avec succès")
            
            # Tester le nouveau token
            response = self.client.get('/api/auth/profile/',
                                     HTTP_AUTHORIZATION=f'Bearer {new_token}')
            
            if response.status_code == 200:
                print("✅ Nouveau token fonctionnel")
            else:
                print("❌ Nouveau token non fonctionnel")
        else:
            print(f"❌ Erreur rafraîchissement: {response.status_code}")
        
        # Test 2: Rafraîchissement avec token invalide
        invalid_refresh = {
            'refresh': 'invalid_token'
        }
        
        response = self.client.post('/api/auth/refresh/',
                                   data=json.dumps(invalid_refresh),
                                   content_type='application/json')
        
        if response.status_code == 400:
            print("✅ Token invalide rejeté")
        else:
            print(f"❌ Token invalide accepté: {response.status_code}")


if __name__ == '__main__':
    tester = AuthenticationTester()
    tester.run_all_tests()

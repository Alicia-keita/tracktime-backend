#!/usr/bin/env python
import os, sys, django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.permissions import PermissionRequest

User = get_user_model()

class PermissionsTester:
    """Tests spécialisés pour les permissions"""
    
    def __init__(self):
        self.client = Client()
        self.tokens = {}
    
    def run_all_tests(self):
        """Exécuter tous les tests de permissions"""
        print("📋 TESTS SPÉCIFIQUES - PERMISSIONS")
        print("=" * 50)
        
        self.setup_tokens()
        self.test_create_permission()
        self.test_approve_reject()
        self.test_list_permissions()
        self.test_permissions_by_role()
        self.test_validations()
        
        print("\n✨ Tests permissions terminés !")
    
    def setup_tokens(self):
        """Obtenir les tokens pour tous les rôles"""
        print("\n🔐 Configuration tokens:")
        roles = {
            'admin': 'admin1',
            'rh': 'rh1', 
            'employe': 'employe1'
        }
        
        for role_name, username in roles.items():
            response = self.client.post('/api/login/', 
                                      data=json.dumps({
                                          'username': username, 
                                          'password': 'password123'
                                      }),
                                      content_type='application/json')
            
            if response.status_code == 200:
                self.tokens[role_name] = response.json()['access']
                print(f"✅ {role_name}: Token obtenu")
    
    def test_create_permission(self):
        """Tester la création de permissions"""
        print("\n📝 Test création permissions:")
        
        # Test 1: Employé peut créer
        response = self.client.post('/api/permissions/',
                                  data=json.dumps({
                                      'type_permission': 'leave',
                                      'date_sortie': '2026-04-20T09:00:00Z',
                                      'date_retour': '2026-04-22T17:00:00Z',
                                      'motif': 'Test création'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 201:
            print("✅ Employé peut créer une demande")
            permission_id = response.json()['id']
        else:
            print(f"❌ Erreur création employé: {response.status_code}")
            return
        
        # Test 2: RH ne peut pas créer (normalement)
        response = self.client.post('/api/permissions/',
                                  data=json.dumps({
                                      'type_permission': 'leave',
                                      'date_sortie': '2026-04-25T09:00:00Z',
                                      'date_retour': '2026-04-26T17:00:00Z',
                                      'motif': 'Test RH création'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 403:
            print("✅ RH ne peut pas créer (correct)")
        else:
            print(f"⚠️  RH peut créer (statut: {response.status_code})")
        
        return permission_id
    
    def test_approve_reject(self):
        """Tester l'approbation et le rejet"""
        print("\n👍 Test approbation/rejet:")
        
        # Créer une demande pour les tests
        response = self.client.post('/api/permissions/',
                                  data=json.dumps({
                                      'type_permission': 'sick_leave',
                                      'date_sortie': '2026-04-23T09:00:00Z',
                                      'date_retour': '2026-04-24T17:00:00Z',
                                      'motif': 'Test approbation'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code != 201:
            print("❌ Impossible de créer une demande pour le test")
            return
        
        permission_id = response.json()['id']
        
        # Test 1: RH peut approuver
        response = self.client.patch(f'/api/permissions/{permission_id}/approve/',
                                   data=json.dumps({}),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            print("✅ RH peut approuver")
        else:
            print(f"❌ RH ne peut pas approuver: {response.status_code}")
        
        # Créer une autre demande pour le rejet
        response = self.client.post('/api/permissions/',
                                  data=json.dumps({
                                      'type_permission': 'unpaid',
                                      'date_sortie': '2026-04-27T09:00:00Z',
                                      'date_retour': '2026-04-28T17:00:00Z',
                                      'motif': 'Test rejet'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 201:
            permission_id_2 = response.json()['id']
            
            # Test 2: RH peut rejeter
            response = self.client.patch(f'/api/permissions/{permission_id_2}/reject/',
                                       data=json.dumps({
                                           'commentaire_rh': 'Motif de rejet'
                                       }),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
            
            if response.status_code == 200:
                print("✅ RH peut rejeter")
            else:
                print(f"❌ RH ne peut pas rejeter: {response.status_code}")
        
        # Test 3: Employé ne peut pas approuver
        response = self.client.patch(f'/api/permissions/{permission_id}/approve/',
                                   data=json.dumps({}),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas approuver (correct)")
        else:
            print(f"❌ Employé peut approuver (erreur): {response.status_code}")
    
    def test_list_permissions(self):
        """Tester la consultation des permissions"""
        print("\n👀 Test consultation permissions:")
        
        # Test 1: Admin voit toutes les permissions
        response = self.client.get('/api/permissions/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 200:
            all_permissions = response.json()
            print(f"✅ Admin voit {len(all_permissions)} permissions")
        else:
            print(f"❌ Admin ne peut pas voir: {response.status_code}")
        
        # Test 2: RH voit toutes les permissions
        response = self.client.get('/api/permissions/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            rh_permissions = response.json()
            print(f"✅ RH voit {len(rh_permissions)} permissions")
        else:
            print(f"❌ RH ne peut pas voir: {response.status_code}")
        
        # Test 3: Employé voit seulement ses permissions
        response = self.client.get('/api/permissions/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 200:
            emp_permissions = response.json()
            print(f"✅ Employé voit {len(emp_permissions)} permissions")
            
            # Vérifier que ce sont bien les siennes
            all_mine = all(p['employee_name'] == 'employe1' for p in emp_permissions)
            if all_mine:
                print("✅ Employé ne voit que ses permissions")
            else:
                print("❌ Employé voit des permissions qui ne sont pas les siennes")
        else:
            print(f"❌ Employé ne peut pas voir: {response.status_code}")
        
        # Test 4: Voir les demandes en attente
        response = self.client.get('/api/permissions/pending/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            pending = response.json()
            print(f"✅ RH voit {len(pending)} demandes en attente")
        else:
            print(f"❌ RH ne peut pas voir les demandes en attente: {response.status_code}")
    
    def test_permissions_by_role(self):
        """Tester les permissions spécifiques par rôle"""
        print("\n🔒 Test permissions par rôle:")
        
        # Test 1: Employé ne peut pas approuver
        response = self.client.get('/api/permissions/pending/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas voir les demandes en attente")
        else:
            print(f"❌ Employé peut voir les demandes en attente: {response.status_code}")
        
        # Test 2: Admin peut tout faire
        response = self.client.post('/api/permissions/',
                                  data=json.dumps({
                                      'type_permission': 'maternity',
                                      'date_sortie': '2026-05-01T09:00:00Z',
                                      'date_retour': '2026-05-15T17:00:00Z',
                                      'motif': 'Test admin'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code in [201, 403]:  # 403 serait normal si admin ne peut pas créer
            if response.status_code == 403:
                print("✅ Admin ne peut pas créer (normal)")
            else:
                print("✅ Admin peut créer")
        else:
            print(f"⚠️  Réponse inattendue admin: {response.status_code}")
    
    def test_validations(self):
        """Tester les validations"""
        print("\n⚠️  Test validations:")
        
        # Test 1: Date de retour avant date de sortie
        response = self.client.post('/api/permissions/',
                                  data=json.dumps({
                                      'type_permission': 'leave',
                                      'date_sortie': '2026-05-10T09:00:00Z',
                                      'date_retour': '2026-05-08T17:00:00Z',  # Avant !
                                      'motif': 'Test date invalide'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 400:
            print("✅ Validation date invalide fonctionnelle")
        else:
            print(f"❌ Validation date invalide échouée: {response.status_code}")
        
        # Test 2: Champs manquants
        response = self.client.post('/api/permissions/',
                                  data=json.dumps({
                                      'type_permission': 'leave',
                                      # date_sortie manquante
                                      'date_retour': '2026-05-12T17:00:00Z',
                                      'motif': 'Test champ manquant'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 400:
            print("✅ Validation champs manquants fonctionnelle")
        else:
            print(f"❌ Validation champs manquants échouée: {response.status_code}")


if __name__ == '__main__':
    tester = PermissionsTester()
    tester.run_all_tests()

#!/usr/bin/env python
import os, sys, django
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.permissions import PermissionRequest
from core.bulletin import Bulletin

User = get_user_model()

class PayrollAndPermissionsTester:
    """Classe de test complète pour bulletins et permissions"""
    
    def __init__(self):
        self.client = Client()
        self.tokens = {}
        self.test_results = {}
    
    def run_all_tests(self):
        """Exécuter tous les tests"""
        print("🧪 TESTS COMPLETS - BULLETINS & PERMISSIONS")
        print("=" * 60)
        
        # 1. Tests d'authentification
        self.test_authentication()
        
        # 2. Tests des permissions
        self.test_permissions_workflow()
        
        # 3. Tests des bulletins
        self.test_bulletins_workflow()
        
        # 4. Tests des permissions d'accès
        self.test_access_permissions()
        
        # 5. Tests de validation
        self.test_validations()
        
        # 6. Afficher les résultats
        self.display_results()
    
    def test_authentication(self):
        """Tester l'authentification pour tous les rôles"""
        print("\n🔐 1. TESTS D'AUTHENTIFICATION")
        print("-" * 30)
        
        roles = ['admin1', 'rh1', 'employe1']
        
        for role in roles:
            response = self.client.post('/api/login/', 
                                      data=json.dumps({
                                          'username': role, 
                                          'password': 'password123'
                                      }),
                                      content_type='application/json')
            
            if response.status_code == 200:
                token_data = response.json()
                self.tokens[role] = token_data['access']
                print(f"✅ {role}: Login réussi (Rôle: {token_data.get('role')})")
                self.test_results[f'auth_{role}'] = True
            else:
                print(f"❌ {role}: Login échoué ({response.status_code})")
                self.test_results[f'auth_{role}'] = False
    
    def test_permissions_workflow(self):
        """Tester le workflow complet des permissions"""
        print("\n📋 2. WORKFLOW PERMISSIONS")
        print("-" * 30)
        
        # 2.1 Employé crée une demande
        print("\n2.1 Employé crée une demande:")
        response = self.client.post('/api/permissions/',
                                  data=json.dumps({
                                      'type_permission': 'leave',
                                      'date_sortie': '2026-04-15T09:00:00Z',
                                      'date_retour': '2026-04-17T17:00:00Z',
                                      'motif': 'Vacances printemps'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens.get("employe1")}')
        
        if response.status_code == 201:
            permission_data = response.json()
            permission_id = permission_data['id']
            print(f"✅ Demande créée (ID: {permission_id})")
            self.test_results['permission_create'] = True
        else:
            print(f"❌ Erreur création: {response.status_code}")
            self.test_results['permission_create'] = False
            return
        
        # 2.2 RH approuve la demande
        print("\n2.2 RH approuve la demande:")
        response = self.client.patch(f'/api/permissions/{permission_id}/approve/',
                                   data=json.dumps({}),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens.get("rh1")}')
        
        if response.status_code == 200:
            print("✅ Demande approuvée")
            self.test_results['permission_approve'] = True
        else:
            print(f"❌ Erreur approbation: {response.status_code}")
            self.test_results['permission_approve'] = False
        
        # 2.3 Vérifier le statut
        print("\n2.3 Vérifier le statut:")
        response = self.client.get('/api/permissions/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens.get("employe1")}')
        
        if response.status_code == 200:
            permissions = response.json()
            approved_count = sum(1 for p in permissions if p['status'] == 'approved')
            print(f"✅ {approved_count} demande(s) approuvée(s)")
            self.test_results['permission_status_check'] = True
        else:
            print(f"❌ Erreur vérification: {response.status_code}")
            self.test_results['permission_status_check'] = False
    
    def test_bulletins_workflow(self):
        """Tester le workflow complet des bulletins"""
        print("\n💰 3. WORKFLOW BULLETINS")
        print("-" * 30)
        
        # 3.1 RH génère un bulletin
        print("\n3.1 RH génère un bulletin:")
        response = self.client.post('/api/bulletins/generate/',
                                  data=json.dumps({
                                      'employee': 18,  # employe1
                                      'periode_debut': '2026-04-01',
                                      'periode_fin': '2026-04-30'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens.get("rh1")}')
        
        if response.status_code == 201:
            bulletin_data = response.json()['bulletin']
            bulletin_id = bulletin_data['id']
            print(f"✅ Bulletin généré (ID: {bulletin_id})")
            print(f"   💰 Salaire net: {bulletin_data['salaire_net']} €")
            print(f"   📊 Absences: {bulletin_data['nb_absences']}")
            print(f"   ⏰ Heures sup: {bulletin_data['heures_supplementaires']}")
            self.test_results['bulletin_generate'] = True
        else:
            print(f"❌ Erreur génération: {response.status_code}")
            self.test_results['bulletin_generate'] = False
            return
        
        # 3.2 Employé consulte ses bulletins
        print("\n3.2 Employé consulte ses bulletins:")
        response = self.client.get('/api/bulletins/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens.get("employe1")}')
        
        if response.status_code == 200:
            bulletins = response.json()
            print(f"✅ {len(bulletins)} bulletin(s) trouvé(s)")
            self.test_results['bulletin_view_employee'] = True
        else:
            print(f"❌ Erreur consultation: {response.status_code}")
            self.test_results['bulletin_view_employee'] = False
        
        # 3.3 Admin tente de supprimer
        print("\n3.3 Admin supprime le bulletin:")
        response = self.client.delete(f'/api/bulletins/{bulletin_id}/',
                                     HTTP_AUTHORIZATION=f'Bearer {self.tokens.get("admin1")}')
        
        if response.status_code in [204, 200]:
            print("✅ Bulletin supprimé par admin")
            self.test_results['bulletin_delete_admin'] = True
        else:
            print(f"❌ Erreur suppression: {response.status_code}")
            self.test_results['bulletin_delete_admin'] = False
    
    def test_access_permissions(self):
        """Tester les permissions d'accès par rôle"""
        print("\n🔒 4. TESTS PERMISSIONS D'ACCÈS")
        print("-" * 30)
        
        # 4.1 Employé ne peut pas générer de bulletin
        print("\n4.1 Employé tente de générer un bulletin:")
        response = self.client.post('/api/bulletins/generate/',
                                  data=json.dumps({
                                      'employee': 18,
                                      'periode_debut': '2026-05-01',
                                      'periode_fin': '2026-05-31'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens.get("employe1")}')
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas générer (403)")
            self.test_results['access_employee_generate'] = True
        else:
            print(f"❌ Erreur: devrait être 403, got {response.status_code}")
            self.test_results['access_employee_generate'] = False
        
        # 4.2 RH ne peut pas supprimer de bulletin
        print("\n4.2 RH tente de supprimer un bulletin:")
        # D'abord créer un bulletin
        response = self.client.post('/api/bulletins/generate/',
                                  data=json.dumps({
                                      'employee': 18,
                                      'periode_debut': '2026-06-01',
                                      'periode_fin': '2026-06-30'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens.get("rh1")}')
        
        if response.status_code == 201:
            bulletin_id = response.json()['bulletin']['id']
            
            # Puis tenter de supprimer
            response = self.client.delete(f'/api/bulletins/{bulletin_id}/',
                                         HTTP_AUTHORIZATION=f'Bearer {self.tokens.get("rh1")}')
            
            if response.status_code == 403:
                print("✅ RH ne peut pas supprimer (403)")
                self.test_results['access_rh_delete'] = True
            else:
                print(f"❌ Erreur: devrait être 403, got {response.status_code}")
                self.test_results['access_rh_delete'] = False
        else:
            print("❌ Impossible de créer un bulletin pour le test")
            self.test_results['access_rh_delete'] = False
    
    def test_validations(self):
        """Tester les validations et cas d'erreur"""
        print("\n⚠️ 5. TESTS DE VALIDATION")
        print("-" * 30)
        
        # 5.1 Date de retour avant date de sortie
        print("\n5.1 Date invalide (retour < sortie):")
        response = self.client.post('/api/permissions/',
                                  data=json.dumps({
                                      'type_permission': 'leave',
                                      'date_sortie': '2026-04-20T09:00:00Z',
                                      'date_retour': '2026-04-18T17:00:00Z',  # Avant !
                                      'motif': 'Test date invalide'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens.get("employe1")}')
        
        if response.status_code == 400:
            print("✅ Validation date invalide (400)")
            self.test_results['validation_date'] = True
        else:
            print(f"❌ Erreur: devrait être 400, got {response.status_code}")
            self.test_results['validation_date'] = False
        
        # 5.2 Bulletin en double
        print("\n5.2 Tentative de bulletin en double:")
        response = self.client.post('/api/bulletins/generate/',
                                  data=json.dumps({
                                      'employee': 18,
                                      'periode_debut': '2026-04-01',
                                      'periode_fin': '2026-04-30'  # Même période
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens.get("rh1")}')
        
        if response.status_code == 400:
            print("✅ Bulletin en double rejeté (400)")
            self.test_results['validation_duplicate'] = True
        else:
            print(f"❌ Erreur: devrait être 400, got {response.status_code}")
            self.test_results['validation_duplicate'] = False
    
    def display_results(self):
        """Afficher les résultats finaux"""
        print("\n📊 RÉSULTATS FINAUX")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"✅ Tests réussis: {passed_tests}/{total_tests}")
        print(f"❌ Tests échoués: {failed_tests}/{total_tests}")
        
        if failed_tests > 0:
            print("\n❌ Tests échoués:")
            for test_name, result in self.test_results.items():
                if not result:
                    print(f"   - {test_name}")
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"\n📈 Taux de réussite: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("🎉 EXCELLENT ! Le système fonctionne très bien !")
        elif success_rate >= 70:
            print("👍 BIEN ! Le système fonctionne correctement.")
        else:
            print("⚠️  ATTENTION ! Des problèmes doivent être résolus.")


if __name__ == '__main__':
    tester = PayrollAndPermissionsTester()
    tester.run_all_tests()

#!/usr/bin/env python
import os, sys, django
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.bulletin import Bulletin

User = get_user_model()

class BulletinsTester:
    """Tests spécialisés pour les bulletins de salaire"""
    
    def __init__(self):
        self.client = Client()
        self.tokens = {}
    
    def run_all_tests(self):
        """Exécuter tous les tests de bulletins"""
        print("💰 TESTS SPÉCIFIQUES - BULLETINS DE SALAIRE")
        print("=" * 50)
        
        self.setup_tokens()
        self.test_generate_bulletin()
        self.test_bulletin_calculations()
        self.test_list_bulletins()
        self.test_bulletin_permissions()
        self.test_bulletin_validations()
        self.test_delete_bulletin()
        
        print("\n✨ Tests bulletins terminés !")
    
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
    
    def test_generate_bulletin(self):
        """Tester la génération de bulletins"""
        print("\n📈 Test génération bulletins:")
        
        # Test 1: RH peut générer
        response = self.client.post('/api/bulletins/generate/',
                                  data=json.dumps({
                                      'employee': 18,  # employe1
                                      'periode_debut': '2026-05-01',
                                      'periode_fin': '2026-05-31'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 201:
            bulletin = response.json()['bulletin']
            print("✅ RH peut générer un bulletin")
            print(f"   📋 ID: {bulletin['id']}")
            print(f"   💰 Salaire net: {bulletin['salaire_net']} €")
            print(f"   👤 Employé: {bulletin['employee_name']}")
            return bulletin['id']
        else:
            print(f"❌ RH ne peut pas générer: {response.status_code}")
            print(f"   Erreur: {response.json()}")
            return None
        
        # Test 2: Admin peut générer
        response = self.client.post('/api/bulletins/generate/',
                                  data=json.dumps({
                                      'employee': 18,
                                      'periode_debut': '2026-06-01',
                                      'periode_fin': '2026-06-30'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 201:
            print("✅ Admin peut générer un bulletin")
        else:
            print(f"❌ Admin ne peut pas générer: {response.status_code}")
    
    def test_bulletin_calculations(self):
        """Tester les calculs des bulletins"""
        print("\n🧮 Test calculs bulletins:")
        
        # Générer un bulletin pour les tests
        response = self.client.post('/api/bulletins/generate/',
                                  data=json.dumps({
                                      'employee': 18,
                                      'periode_debut': '2026-07-01',
                                      'periode_fin': '2026-07-31'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code != 201:
            print("❌ Impossible de générer un bulletin pour les tests")
            return
        
        bulletin = response.json()['bulletin']
        
        # Vérifier les calculs
        salaire_base = Decimal(str(bulletin['salaire_base']))
        salaire_net = Decimal(str(bulletin['salaire_net']))
        cnss = Decimal(str(bulletin['cnss']))
        impot = Decimal(str(bulletin['impot']))
        
        # Salaire net doit être = salaire brut - cnss - impot
        salaire_brut = salaire_base + Decimal(str(bulletin['prime_heures_sup'])) - Decimal(str(bulletin['deduction_absences']))
        calculated_net = salaire_brut - cnss - impot
        
        print(f"   💰 Salaire base: {salaire_base} €")
        print(f"   📈 Salaire brut: {salaire_brut} €")
        print(f"   🏥 CNSS: {cnss} €")
        print(f"   💸 Impôt: {impot} €")
        print(f"   💰 Salaire net: {salaire_net} €")
        print(f"   🧮 Net calculé: {calculated_net} €")
        
        if abs(salaire_net - calculated_net) < Decimal('0.01'):
            print("✅ Calculs du bulletin corrects")
        else:
            print("❌ Calculs du bulletin incorrects")
        
        # Vérifier les taux
        cnss_rate = cnss / salaire_brut * 100
        print(f"   📊 Taux CNSS: {cnss_rate:.2f}%")
        
        if abs(cnss_rate - Decimal('4.3')) < Decimal('0.1'):
            print("✅ Taux CNSS correct (4.3%)")
        else:
            print("❌ Taux CNSS incorrect")
    
    def test_list_bulletins(self):
        """Tester la consultation des bulletins"""
        print("\n👀 Test consultation bulletins:")
        
        # Test 1: Admin voit tous les bulletins
        response = self.client.get('/api/bulletins/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 200:
            all_bulletins = response.json()
            print(f"✅ Admin voit {len(all_bulletins)} bulletins")
        else:
            print(f"❌ Admin ne peut pas voir: {response.status_code}")
        
        # Test 2: RH voit tous les bulletins
        response = self.client.get('/api/bulletins/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            rh_bulletins = response.json()
            print(f"✅ RH voit {len(rh_bulletins)} bulletins")
        else:
            print(f"❌ RH ne peut pas voir: {response.status_code}")
        
        # Test 3: Employé voit seulement ses bulletins
        response = self.client.get('/api/bulletins/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 200:
            emp_bulletins = response.json()
            print(f"✅ Employé voit {len(emp_bulletins)} bulletins")
            
            # Vérifier que ce sont bien les siens
            all_mine = all(b['employee_name'] == 'employe1' for b in emp_bulletins)
            if all_mine:
                print("✅ Employé ne voit que ses bulletins")
            else:
                print("❌ Employé voit des bulletins qui ne sont pas les siens")
        else:
            print(f"❌ Employé ne peut pas voir: {response.status_code}")
    
    def test_bulletin_permissions(self):
        """Tester les permissions d'accès aux bulletins"""
        print("\n🔒 Test permissions bulletins:")
        
        # Test 1: Employé ne peut pas générer
        response = self.client.post('/api/bulletins/generate/',
                                  data=json.dumps({
                                      'employee': 18,
                                      'periode_debut': '2026-08-01',
                                      'periode_fin': '2026-08-31'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas générer de bulletin")
        else:
            print(f"❌ Employé peut générer (erreur): {response.status_code}")
        
        # Test 2: Créer un bulletin pour tester la suppression
        response = self.client.post('/api/bulletins/generate/',
                                  data=json.dumps({
                                      'employee': 18,
                                      'periode_debut': '2026-09-01',
                                      'periode_fin': '2026-09-30'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 201:
            bulletin_id = response.json()['bulletin']['id']
            
            # Test 3: RH ne peut pas supprimer
            response = self.client.delete(f'/api/bulletins/{bulletin_id}/',
                                         HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
            
            if response.status_code == 403:
                print("✅ RH ne peut pas supprimer de bulletin")
            else:
                print(f"❌ RH peut supprimer (erreur): {response.status_code}")
            
            # Test 4: Admin peut supprimer
            response = self.client.delete(f'/api/bulletins/{bulletin_id}/',
                                         HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
            
            if response.status_code in [204, 200]:
                print("✅ Admin peut supprimer un bulletin")
            else:
                print(f"❌ Admin ne peut pas supprimer: {response.status_code}")
    
    def test_bulletin_validations(self):
        """Tester les validations des bulletins"""
        print("\n⚠️  Test validations bulletins:")
        
        # Test 1: Bulletin en double
        response = self.client.post('/api/bulletins/generate/',
                                  data=json.dumps({
                                      'employee': 18,
                                      'periode_debut': '2026-05-01',  # Déjà utilisé
                                      'periode_fin': '2026-05-31'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 400:
            print("✅ Bulletin en double rejeté")
        else:
            print(f"❌ Bulletin en double accepté: {response.status_code}")
        
        # Test 2: Date invalide
        response = self.client.post('/api/bulletins/generate/',
                                  data=json.dumps({
                                      'employee': 18,
                                      'periode_debut': '2026-10-15',
                                      'periode_fin': '2026-10-01'  # Avant !
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 400:
            print("✅ Date invalide rejetée")
        else:
            print(f"❌ Date invalide acceptée: {response.status_code}")
        
        # Test 3: Employé inexistant
        response = self.client.post('/api/bulletins/generate/',
                                  data=json.dumps({
                                      'employee': 9999,  # N'existe pas
                                      'periode_debut': '2026-11-01',
                                      'periode_fin': '2026-11-30'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 404:
            print("✅ Employé inexistant rejeté")
        else:
            print(f"❌ Employé inexistant accepté: {response.status_code}")
    
    def test_delete_bulletin(self):
        """Tester la suppression de bulletins"""
        print("\n🗑️  Test suppression bulletins:")
        
        # Créer un bulletin spécifique pour la suppression
        response = self.client.post('/api/bulletins/generate/',
                                  data=json.dumps({
                                      'employee': 18,
                                      'periode_debut': '2026-12-01',
                                      'periode_fin': '2026-12-31'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code != 201:
            print("❌ Impossible de créer un bulletin pour le test de suppression")
            return
        
        bulletin_id = response.json()['bulletin']['id']
        print(f"📋 Bulletin créé (ID: {bulletin_id}) pour le test de suppression")
        
        # Test 1: Employé ne peut pas supprimer
        response = self.client.delete(f'/api/bulletins/{bulletin_id}/',
                                     HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas supprimer")
        else:
            print(f"❌ Employé peut supprimer (erreur): {response.status_code}")
        
        # Test 2: RH ne peut pas supprimer
        response = self.client.delete(f'/api/bulletins/{bulletin_id}/',
                                     HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 403:
            print("✅ RH ne peut pas supprimer")
        else:
            print(f"❌ RH peut supprimer (erreur): {response.status_code}")
        
        # Test 3: Admin peut supprimer
        response = self.client.delete(f'/api/bulletins/{bulletin_id}/',
                                     HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code in [204, 200]:
            print("✅ Admin peut supprimer")
            
            # Vérifier que le bulletin est bien supprimé
            response = self.client.get(f'/api/bulletins/{bulletin_id}/',
                                     HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
            
            if response.status_code == 404:
                print("✅ Bulletin bien supprimé")
            else:
                print("❌ Bulletin pas vraiment supprimé")
        else:
            print(f"❌ Admin ne peut pas supprimer: {response.status_code}")


if __name__ == '__main__':
    tester = BulletinsTester()
    tester.run_all_tests()

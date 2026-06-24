#!/usr/bin/env python
import os, sys, django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.solde import Solde

User = get_user_model()

class SoldesTester:
    """Tests complets du système de gestion des soldes"""
    
    def __init__(self):
        self.client = Client()
        self.tokens = {}
        self.test_solde = None
    
    def run_all_tests(self):
        """Exécuter tous les tests de soldes"""
        print("💰 TESTS COMPLETS - SYSTÈME DE GESTION DES SOLDES")
        print("=" * 65)
        
        self.setup_tokens()
        self.test_create_solde()
        self.test_solde_workflow()
        self.test_solde_permissions()
        self.test_solde_actions()
        self.test_solde_statistics()
        
        print("\n✨ Tests de soldes terminés !")
    
    def setup_tokens(self):
        """Obtenir les tokens pour tous les rôles"""
        print("\n🔐 Configuration tokens:")
        roles = {
            'admin': 'admin1',
            'rh': 'rh1', 
            'employe': 'employe1'
        }
        
        for role_name, username in roles.items():
            response = self.client.post('/api/auth/login/', 
                                      data=json.dumps({
                                          'username': username, 
                                          'password': 'password123'
                                      }),
                                      content_type='application/json')
            
            if response.status_code == 200:
                self.tokens[role_name] = response.json()['access']
                print(f"✅ {role_name}: Token obtenu")
    
    def test_create_solde(self):
        """Tester la création de soldes"""
        print("\n📝 1. TEST CRÉATION SOLD")
        print("-" * 40)
        
        # Test 1: Admin peut créer un solde
        solde_data = {
            'employe': 18,  # employe1
            'solde_annuel': 30.0,
            'conges_pris': 5.0,
            'annee_reference': 2026
        }
        
        response = self.client.post('/api/soldes/',
                                  data=json.dumps(solde_data),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 201:
            self.test_solde = response.json()
            print("✅ Admin peut créer un solde")
            print(f"   👤 Employé: {self.test_solde['nom_complet']}")
            print(f"   📊 Solde annuel: {self.test_solde['solde_annuel']} jours")
            print(f"   🏖️ Congés pris: {self.test_solde['conges_pris']} jours")
            print(f"   💰 Congés restants: {self.test_solde['conges_restant']} jours")
            print(f"   📅 Année: {self.test_solde['annee_reference']}")
        else:
            print(f"❌ Erreur création admin: {response.status_code}")
            print(f"   Erreur: {response.json()}")
        
        # Test 2: RH peut créer un solde
        solde_rh_data = {
            'employe': 2,  # rh1
            'solde_annuel': 28.0,
            'conges_pris': 3.0,
            'annee_reference': 2026
        }
        
        response = self.client.post('/api/soldes/',
                                  data=json.dumps(solde_rh_data),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 201:
            print("✅ RH peut créer un solde")
        else:
            print(f"❌ RH ne peut pas créer: {response.status_code}")
        
        # Test 3: Employé ne peut pas créer
        response = self.client.post('/api/soldes/',
                                  data=json.dumps({
                                      'employe': 18,
                                      'solde_annuel': 25.0,
                                      'conges_pris': 0.0,
                                      'annee_reference': 2026
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas créer de solde")
        else:
            print(f"❌ Employé peut créer (erreur): {response.status_code}")
        
        # Test 4: Solde en double (même employé, même année)
        response = self.client.post('/api/soldes/',
                                  data=json.dumps({
                                      'employe': 18,
                                      'solde_annuel': 25.0,
                                      'conges_pris': 2.0,
                                      'annee_reference': 2026  # Même année et employé
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 400:
            print("✅ Validation solde en double fonctionnelle")
        else:
            print(f"❌ Solde en double accepté: {response.status_code}")
    
    def test_solde_workflow(self):
        """Tester le workflow des soldes"""
        print("\n🔄 2. TEST WORKFLOW SOLD")
        print("-" * 40)
        
        if not self.test_solde:
            print("❌ Pas de solde de test disponible")
            return
        
        solde_id = self.test_solde['id']
        
        # Test 1: Admin peut mettre à jour
        update_data = {
            'solde_annuel': 35.0,
            'conges_pris': 8.0,
            'annee_reference': 2026
        }
        
        response = self.client.patch(f'/api/soldes/{solde_id}/',
                                   data=json.dumps(update_data),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 200:
            updated_solde = response.json()
            print("✅ Admin peut mettre à jour un solde")
            print(f"   📊 Nouveau solde annuel: {updated_solde['solde_annuel']} jours")
            print(f"   🏖️ Nouveaux congés pris: {updated_solde['conges_pris']} jours")
            print(f"   💰 Nouveaux congés restants: {updated_solde['conges_restant']} jours")
        else:
            print(f"❌ Admin ne peut pas mettre à jour: {response.status_code}")
        
        # Test 2: RH peut mettre à jour
        response = self.client.patch(f'/api/soldes/{solde_id}/',
                                   data=json.dumps({
                                       'conges_pris': 10.0
                                   }),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            print("✅ RH peut mettre à jour un solde")
        else:
            print(f"❌ RH ne peut pas mettre à jour: {response.status_code}")
        
        # Test 3: Employé ne peut pas mettre à jour
        response = self.client.patch(f'/api/soldes/{solde_id}/',
                                   data=json.dumps({
                                       'conges_pris': 12.0
                                   }),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas mettre à jour de solde")
        else:
            print(f"❌ Employé peut mettre à jour (erreur): {response.status_code}")
    
    def test_solde_permissions(self):
        """Tester les permissions d'accès aux soldes"""
        print("\n🔒 3. TEST PERMISSIONS ACCÈS SOLD")
        print("-" * 40)
        
        # Test 1: Admin voit tous les soldes
        response = self.client.get('/api/soldes/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 200:
            all_soldes = response.json()
            print(f"✅ Admin voit {len(all_soldes)} solde(s)")
        else:
            print(f"❌ Admin ne peut pas voir: {response.status_code}")
        
        # Test 2: RH voit tous les soldes
        response = self.client.get('/api/soldes/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            rh_soldes = response.json()
            print(f"✅ RH voit {len(rh_soldes)} solde(s)")
        else:
            print(f"❌ RH ne peut pas voir: {response.status_code}")
        
        # Test 3: Employé voit seulement son solde
        response = self.client.get('/api/soldes/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 200:
            emp_soldes = response.json()
            print(f"✅ Employé voit {len(emp_soldes)} solde(s)")
            
            # Vérifier que c'est bien le sien
            all_mine = all(s['username'] == 'employe1' for s in emp_soldes)
            if all_mine:
                print("✅ Employé ne voit que son solde")
            else:
                print("❌ Employé voit des soldes qui ne sont pas les siens")
        else:
            print(f"❌ Employé ne peut pas voir: {response.status_code}")
    
    def test_solde_actions(self):
        """Tester les actions spéciales sur les soldes"""
        print("\n🎯 4. TEST ACTIONS SPÉCIALES")
        print("-" * 40)
        
        if not self.test_solde:
            print("❌ Pas de solde de test disponible")
            return
        
        solde_id = self.test_solde['id']
        
        # Test 1: Voir son propre solde
        print("\n4.1 Employé consulte son solde:")
        response = self.client.get('/api/soldes/mon_solde/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 200:
            mon_solde = response.json()
            print("✅ Employé peut voir son solde")
            print(f"   👤 Nom: {mon_solde['nom_complet']}")
            print(f"   🏢 Service: {mon_solde['service']}")
            print(f"   📊 Solde annuel: {mon_solde['solde_annuel']} jours")
            print(f"   🏖️ Congés pris: {mon_solde['conges_pris']} jours")
            print(f"   💰 Congés restants: {mon_solde['conges_restant']} jours")
        else:
            print(f"❌ Erreur consultation solde: {response.status_code}")
        
        # Test 2: Réinitialiser le solde (Admin)
        print("\n4.2 Admin réinitialise le solde:")
        response = self.client.post(f'/api/soldes/{solde_id}/reinitialiser/',
                                   data=json.dumps({
                                       'solde_annuel': 40.0
                                   }),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Admin peut réinitialiser le solde")
            print(f"   📊 Nouveau solde: {result['solde']['solde_annuel']} jours")
        else:
            print(f"❌ Admin ne peut pas réinitialiser: {response.status_code}")
        
        # Test 3: Ajouter des congés pris (RH)
        print("\n4.3 RH ajoute des congés pris:")
        response = self.client.post(f'/api/soldes/{solde_id}/ajouter_conges/',
                                   data=json.dumps({
                                       'jours': 2.0
                                   }),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RH peut ajouter des congés pris")
            print(f"   🏖️ Jours ajoutés: 2.0")
            print(f"   💰 Nouveau solde restant: {result['solde']['conges_restant']} jours")
        else:
            print(f"❌ RH ne peut pas ajouter des congés: {response.status_code}")
        
        # Test 4: Employé ne peut pas réinitialiser
        response = self.client.post(f'/api/soldes/{solde_id}/reinitialiser/',
                                   data=json.dumps({
                                       'solde_annuel': 50.0
                                   }),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas réinitialiser le solde")
        else:
            print(f"❌ Employé peut réinitialiser (erreur): {response.status_code}")
    
    def test_solde_statistics(self):
        """Tester les statistiques des soldes"""
        print("\n📊 5. TEST STATISTIQUES")
        print("-" * 40)
        
        # Test 1: Admin peut voir les statistiques
        response = self.client.get('/api/soldes/statistiques/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Admin peut voir les statistiques")
            print(f"   👥 Total employés: {stats['total_employes']}")
            print(f"   🏖️ Total congés pris: {stats['total_conges_pris']} jours")
            print(f"   💰 Total congés restants: {stats['total_conges_restants']} jours")
            print(f"   📊 Moyenne par employé: {stats['moyenne_conges_par_employe']:.1f} jours")
            
            if stats['stats_par_service']:
                print("   📈 Stats par service:")
                for service_stat in stats['stats_par_service']:
                    print(f"      🏢 {service_stat['employe__service']}: {service_stat['total_pris']:.1f} jours pris")
        else:
            print(f"❌ Admin ne peut pas voir les statistiques: {response.status_code}")
        
        # Test 2: RH peut voir les statistiques
        response = self.client.get('/api/soldes/statistiques/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            print("✅ RH peut voir les statistiques")
        else:
            print(f"❌ RH ne peut pas voir les statistiques: {response.status_code}")
        
        # Test 3: Employé ne peut pas voir les statistiques
        response = self.client.get('/api/soldes/statistiques/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas voir les statistiques")
        else:
            print(f"❌ Employé peut voir les statistiques (erreur): {response.status_code}")


if __name__ == '__main__':
    tester = SoldesTester()
    tester.run_all_tests()

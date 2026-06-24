#!/usr/bin/env python
import os, sys, django
import json
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.conges import Conge

User = get_user_model()

class CongesTester:
    """Tests complets du système de gestion des congés"""
    
    def __init__(self):
        self.client = Client()
        self.tokens = {}
        self.test_conge = None
    
    def run_all_tests(self):
        """Exécuter tous les tests de congés"""
        print("🏖️ TESTS COMPLETS - SYSTÈME DE GESTION DES CONGÉS")
        print("=" * 60)
        
        self.setup_tokens()
        self.test_create_conge()
        self.test_conge_workflow()
        self.test_conge_permissions()
        self.test_conge_validations()
        self.test_conge_actions()
        self.test_solde_conges()
        
        print("\n✨ Tests de congés terminés !")
    
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
    
    def test_create_conge(self):
        """Tester la création de demandes de congé"""
        print("\n📝 1. TEST CRÉATION DEMANDES DE CONGÉ")
        print("-" * 40)
        
        # Test 1: Employé peut créer une demande
        conge_data = {
            'type_conge': 'annuel',
            'date_debut': '2026-05-10T09:00:00Z',
            'date_fin': '2026-05-15T17:00:00Z',
            'duree_jours': 5,
            'motif': 'Vacances détente'
        }
        
        response = self.client.post('/api/conges/',
                                  data=json.dumps(conge_data),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 201:
            self.test_conge = response.json()
            print("✅ Employé peut créer une demande de congé")
            print(f"   🏖️ Type: {self.test_conge['type_conge_display']}")
            print(f"   📅 Début: {self.test_conge['date_debut']}")
            print(f"   📅 Fin: {self.test_conge['date_fin']}")
            print(f"   ⏱️ Durée: {self.test_conge['duree_jours']} jours")
            print(f"   📋 Statut: {self.test_conge['statut_display']}")
        else:
            print(f"❌ Erreur création: {response.status_code}")
            print(f"   Erreur: {response.json()}")
        
        # Test 2: RH peut créer une demande
        conge_rh_data = {
            'type_conge': 'formation',
            'date_debut': '2026-06-01T09:00:00Z',
            'date_fin': '2026-06-03T17:00:00Z',
            'duree_jours': 3,
            'motif': 'Formation Django avancé'
        }
        
        response = self.client.post('/api/conges/',
                                  data=json.dumps(conge_rh_data),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 201:
            print("✅ RH peut créer une demande de congé")
        else:
            print(f"❌ RH ne peut pas créer: {response.status_code}")
        
        # Test 3: Date invalide
        invalid_conge = {
            'type_conge': 'annuel',
            'date_debut': '2026-07-10T09:00:00Z',
            'date_fin': '2026-07-05T17:00:00Z',  # Avant le début !
            'duree_jours': 5,
            'motif': 'Test date invalide'
        }
        
        response = self.client.post('/api/conges/',
                                  data=json.dumps(invalid_conge),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 400:
            print("✅ Validation date invalide fonctionnelle")
        else:
            print(f"❌ Validation date invalide échouée: {response.status_code}")
    
    def test_conge_workflow(self):
        """Tester le workflow complet des congés"""
        print("\n🔄 2. TEST WORKFLOW CONGÉS")
        print("-" * 40)
        
        if not self.test_conge:
            print("❌ Pas de congé de test disponible")
            return
        
        conge_id = self.test_conge['id']
        
        # Test 1: RH peut approuver
        print("\n2.1 RH approuve la demande:")
        response = self.client.patch(f'/api/conges/{conge_id}/approve/',
                                   data=json.dumps({}),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            result = response.json()
            print("✅ RH peut approuver une demande")
            print(f"   📋 Statut: {result['conge']['statut_display']}")
            print(f"   👤 Validé par: {result['conge']['valide_par']}")
        else:
            print(f"❌ RH ne peut pas approuver: {response.status_code}")
        
        # Créer une autre demande pour le rejet
        conge_rejet_data = {
            'type_conge': 'exceptionnel',
            'date_debut': '2026-08-01T09:00:00Z',
            'date_fin': '2026-08-02T17:00:00Z',
            'duree_jours': 2,
            'motif': 'Test rejet'
        }
        
        response = self.client.post('/api/conges/',
                                  data=json.dumps(conge_rejet_data),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 201:
            conge_rejet_id = response.json()['id']
            
            # Test 2: RH peut rejeter
            print("\n2.2 RH rejette la demande:")
            response = self.client.patch(f'/api/conges/{conge_rejet_id}/reject/',
                                       data=json.dumps({
                                           'commentaire_rh': 'Motif non valable'
                                       }),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
            
            if response.status_code == 200:
                result = response.json()
                print("✅ RH peut rejeter une demande")
                print(f"   📋 Statut: {result['conge']['statut_display']}")
                print(f"   💬 Commentaire: {result['conge']['commentaire_rh']}")
            else:
                print(f"❌ RH ne peut pas rejeter: {response.status_code}")
    
    def test_conge_permissions(self):
        """Tester les permissions d'accès aux congés"""
        print("\n🔒 3. TEST PERMISSIONS ACCÈS CONGÉS")
        print("-" * 40)
        
        # Test 1: Admin voit tous les congés
        response = self.client.get('/api/conges/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 200:
            all_conges = response.json()
            print(f"✅ Admin voit {len(all_conges)} congés")
        else:
            print(f"❌ Admin ne peut pas voir: {response.status_code}")
        
        # Test 2: RH voit tous les congés
        response = self.client.get('/api/conges/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            rh_conges = response.json()
            print(f"✅ RH voit {len(rh_conges)} congés")
        else:
            print(f"❌ RH ne peut pas voir: {response.status_code}")
        
        # Test 3: Employé voit seulement ses congés
        response = self.client.get('/api/conges/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 200:
            emp_conges = response.json()
            print(f"✅ Employé voit {len(emp_conges)} congés")
            
            # Vérifier que ce sont bien les siens
            all_mine = all(c['employe_name'] == 'employe1' for c in emp_conges)
            if all_mine:
                print("✅ Employé ne voit que ses congés")
            else:
                print("❌ Employé voit des congés qui ne sont pas les siens")
        else:
            print(f"❌ Employé ne peut pas voir: {response.status_code}")
        
        # Test 4: Voir les demandes en attente
        response = self.client.get('/api/conges/pending/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            pending = response.json()
            print(f"✅ RH voit {len(pending)} demandes en attente")
        else:
            print(f"❌ RH ne peut pas voir les demandes en attente: {response.status_code}")
    
    def test_conge_validations(self):
        """Tester les validations des congés"""
        print("\n⚠️ 4. TEST VALIDATIONS CONGÉS")
        print("-" * 40)
        
        # Test 1: Durée négative
        invalid_duree = {
            'type_conge': 'annuel',
            'date_debut': '2026-09-01T09:00:00Z',
            'date_fin': '2026-09-05T17:00:00Z',
            'duree_jours': -5,  # Négatif !
            'motif': 'Test durée invalide'
        }
        
        response = self.client.post('/api/conges/',
                                  data=json.dumps(invalid_duree),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 400:
            print("✅ Validation durée négative fonctionnelle")
        else:
            print(f"❌ Validation durée négative échouée: {response.status_code}")
        
        # Test 2: Conflit de dates
        # D'abord créer un congé
        base_conge = {
            'type_conge': 'annuel',
            'date_debut': '2026-10-10T09:00:00Z',
            'date_fin': '2026-10-15T17:00:00Z',
            'duree_jours': 5,
            'motif': 'Congé de base'
        }
        
        response = self.client.post('/api/conges/',
                                  data=json.dumps(base_conge),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        # Puis essayer d'en créer un qui chevauche
        conflit_conge = {
            'type_conge': 'exceptionnel',
            'date_debut': '2026-10-12T09:00:00Z',  # Chevauche !
            'date_fin': '2026-10-13T17:00:00Z',
            'duree_jours': 2,
            'motif': 'Test conflit'
        }
        
        response = self.client.post('/api/conges/',
                                  data=json.dumps(conflit_conge),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 400:
            print("✅ Validation conflit de dates fonctionnelle")
        else:
            print(f"❌ Validation conflit de dates échouée: {response.status_code}")
    
    def test_conge_actions(self):
        """Tester les actions spéciales sur les congés"""
        print("\n🎯 5. TEST ACTIONS SPÉCIALES")
        print("-" * 40)
        
        # Créer un congé pour les tests d'actions
        action_conge = {
            'type_conge': 'maladie',
            'date_debut': '2026-11-01T09:00:00Z',
            'date_fin': '2026-11-02T17:00:00Z',
            'duree_jours': 2,
            'motif': 'Test actions'
        }
        
        response = self.client.post('/api/conges/',
                                  data=json.dumps(action_conge),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 201:
            conge_id = response.json()['id']
            
            # Test 1: Employé peut annuler sa demande
            print("\n5.1 Employé annule sa demande:")
            response = self.client.patch(f'/api/conges/{conge_id}/cancel/',
                                       data=json.dumps({}),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Employé peut annuler sa demande")
                print(f"   📋 Statut: {result['conge']['statut_display']}")
            else:
                print(f"❌ Employé ne peut pas annuler: {response.status_code}")
            
            # Test 2: Voir ses congés
            print("\n5.2 Employé consulte ses congés:")
            response = self.client.get('/api/conges/mes_conges/',
                                     HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
            
            if response.status_code == 200:
                mes_conges = response.json()
                print(f"✅ Employé voit {len(mes_conges)} congés")
            else:
                print(f"❌ Erreur consultation: {response.status_code}")
        
        # Test 3: RH ne peut pas approuver un congé déjà traité
        if self.test_conge:
            response = self.client.patch(f'/api/conges/{self.test_conge["id"]}/approve/',
                                       data=json.dumps({}),
                                       content_type='application/json',
                                       HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
            
            if response.status_code == 400:
                print("✅ RH ne peut pas approuver un congé déjà traité")
            else:
                print(f"❌ RH peut approuver un congé déjà traité: {response.status_code}")
    
    def test_solde_conges(self):
        """Tester le calcul des soldes de congés"""
        print("\n💰 6. TEST SOLDE CONGÉS")
        print("-" * 40)
        
        # Test 1: Voir le solde de congés
        response = self.client.get('/api/conges/solde/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 200:
            solde = response.json()
            print("✅ Solde de congés obtenu")
            print(f"   📊 Solde annuel: {solde['solde_annuel']} jours")
            print(f"   🏖️ Congés pris: {solde['conges_pris']} jours")
            print(f"   💰 Solde restant: {solde['solde_restant']} jours")
            print(f"   👤 Employé: {solde['employe']}")
        else:
            print(f"❌ Erreur solde: {response.status_code}")
        
        # Test 2: Solde pour RH
        response = self.client.get('/api/conges/solde/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            solde_rh = response.json()
            print(f"✅ Solde RH obtenu: {solde_rh['solde_restant']} jours")
        else:
            print(f"❌ Erreur solde RH: {response.status_code}")
        
        # Test 3: Solde pour Admin
        response = self.client.get('/api/conges/solde/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 200:
            solde_admin = response.json()
            print(f"✅ Solde Admin obtenu: {solde_admin['solde_restant']} jours")
        else:
            print(f"❌ Erreur solde Admin: {response.status_code}")


if __name__ == '__main__':
    tester = CongesTester()
    tester.run_all_tests()

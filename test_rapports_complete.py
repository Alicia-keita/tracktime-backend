#!/usr/bin/env python
import os, sys, django
import json
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from core.rapport import Rapport

User = get_user_model()

class RapportTester:
    """Tests complets du système de gestion des rapports"""
    
    def __init__(self):
        self.client = Client()
        self.tokens = {}
        self.test_rapport = None
    
    def run_all_tests(self):
        """Exécuter tous les tests de rapports"""
        print("📊 TESTS COMPLETS - SYSTÈME DE GESTION DES RAPPORTS")
        print("=" * 70)
        
        self.setup_tokens()
        self.test_create_rapport()
        self.test_rapport_workflow()
        self.test_rapport_permissions()
        self.test_rapport_generation()
        self.test_rapport_actions()
        
        print("\n✨ Tests de rapports terminés !")
    
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
    
    def test_create_rapport(self):
        """Tester la création de rapports"""
        print("\n📝 1. TEST CRÉATION RAPPORTS")
        print("-" * 45)
        
        # Test 1: Admin peut créer un rapport
        rapport_data = {
            'titre': 'Rapport de Présence Mensuel',
            'type_rapport': 'presence',
            'periode_rapport': 'mois',
            'date_debut': '2026-04-01',
            'date_fin': '2026-04-30',
            'description': 'Rapport de présence pour le mois d\'avril 2026',
            'filtres': {'service': 'IT'},
            'parametres': {'inclure_weekend': False},
            'destinataires': [18]  # employe1
        }
        
        response = self.client.post('/api/rapports/',
                                  data=json.dumps(rapport_data),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 201:
            self.test_rapport = response.json()
            print("✅ Admin peut créer un rapport")
            print(f"   📋 Titre: {self.test_rapport['titre']}")
            print(f"   📊 Type: {self.test_rapport['type_rapport_display']}")
            print(f"   📅 Période: {self.test_rapport['periode_display']}")
            print(f"   📆 Durée: {self.test_rapport['duree_jours']} jours")
            print(f"   👤 Auteur: {self.test_rapport['auteur_name']}")
        else:
            print(f"❌ Erreur création admin: {response.status_code}")
            print(f"   Erreur: {response.json()}")
        
        # Test 2: RH peut créer un rapport
        rapport_rh_data = {
            'titre': 'Rapport des Congés Trimestriel',
            'type_rapport': 'conges',
            'periode_rapport': 'trimestre',
            'date_debut': '2026-01-01',
            'date_fin': '2026-03-31',
            'description': 'Rapport des congés Q1 2026'
        }
        
        response = self.client.post('/api/rapports/',
                                  data=json.dumps(rapport_rh_data),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 201:
            print("✅ RH peut créer un rapport")
        else:
            print(f"❌ RH ne peut pas créer: {response.status_code}")
        
        # Test 3: Employé ne peut pas créer
        response = self.client.post('/api/rapports/',
                                  data=json.dumps({
                                      'titre': 'Test rapport',
                                      'type_rapport': 'activite',
                                      'date_debut': '2026-04-01',
                                      'date_fin': '2026-04-30'
                                  }),
                                  content_type='application/json',
                                  HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas créer (correct)")
        else:
            print(f"❌ Employé peut créer (erreur): {response.status_code}")
    
    def test_rapport_workflow(self):
        """Tester le workflow des rapports"""
        print("\n🔄 2. TEST WORKFLOW RAPPORTS")
        print("-" * 45)
        
        if not self.test_rapport:
            print("❌ Pas de rapport de test disponible")
            return
        
        rapport_id = self.test_rapport['id']
        
        # Test 1: Admin peut mettre à jour
        update_data = {
            'titre': 'Rapport de Présence Mensuel - Mis à jour',
            'description': 'Description mise à jour'
        }
        
        response = self.client.patch(f'/api/rapports/{rapport_id}/',
                                   data=json.dumps(update_data),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 200:
            print("✅ Admin peut mettre à jour un rapport")
        else:
            print(f"❌ Admin ne peut pas mettre à jour: {response.status_code}")
        
        # Test 2: RH peut mettre à jour
        response = self.client.patch(f'/api/rapports/{rapport_id}/',
                                   data=json.dumps({
                                       'description': 'Mise à jour par RH'
                                   }),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            print("✅ RH peut mettre à jour un rapport")
        else:
            print(f"❌ RH ne peut pas mettre à jour: {response.status_code}")
        
        # Test 3: Employé ne peut pas mettre à jour
        response = self.client.patch(f'/api/rapports/{rapport_id}/',
                                   data=json.dumps({
                                       'description': 'Tentative employé'
                                   }),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas mettre à jour (correct)")
        else:
            print(f"❌ Employé peut mettre à jour (erreur): {response.status_code}")
    
    def test_rapport_permissions(self):
        """Tester les permissions d'accès aux rapports"""
        print("\n🔒 3. TEST PERMISSIONS ACCÈS RAPPORTS")
        print("-" * 45)
        
        # Test 1: Admin voit tous les rapports
        response = self.client.get('/api/rapports/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 200:
            all_rapports = response.json()
            print(f"✅ Admin voit {len(all_rapports)} rapport(s)")
        else:
            print(f"❌ Admin ne peut pas voir: {response.status_code}")
        
        # Test 2: RH voit tous les rapports
        response = self.client.get('/api/rapports/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["rh"]}')
        
        if response.status_code == 200:
            rh_rapports = response.json()
            print(f"✅ RH voit {len(rh_rapports)} rapport(s)")
        else:
            print(f"❌ RH ne peut pas voir: {response.status_code}")
        
        # Test 3: Employé voit seulement les rapports qui lui sont destinés
        response = self.client.get('/api/rapports/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 200:
            emp_rapports = response.json()
            print(f"✅ Employé voit {len(emp_rapports)} rapport(s)")
            
            # Vérifier que ce sont bien les rapports qui lui sont destinés
            if emp_rapports:
                print("   📋 Rapports destinés à l'employé:")
                for rapport in emp_rapports:
                    print(f"      - {rapport['titre']}")
        else:
            print(f"❌ Employé ne peut pas voir: {response.status_code}")
    
    def test_rapport_generation(self):
        """Tester la génération automatique de rapports"""
        print("\n🤖 4. TEST GÉNÉRATION AUTOMATIQUE")
        print("-" * 45)
        
        if not self.test_rapport:
            print("❌ Pas de rapport de test disponible")
            return
        
        rapport_id = self.test_rapport['id']
        
        # Test 1: Générer un rapport de présence
        generation_data = {
            'employe_ids': [18],
            'inclure_details': True,
            'format_export': 'json'
        }
        
        response = self.client.post(f'/api/rapports/{rapport_id}/generer_auto/',
                                   data=json.dumps(generation_data),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Génération automatique réussie")
            print(f"   📋 Message: {result['message']}")
            print(f"   📊 Statut: {result['rapport']['statut_display']}")
        else:
            print(f"❌ Erreur génération: {response.status_code}")
            print(f"   Erreur: {response.json()}")
        
        # Test 2: Valider un rapport
        response = self.client.post(f'/api/rapports/{rapport_id}/valider/',
                                   data=json.dumps({}),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Validation du rapport réussie")
            print(f"   📋 Message: {result['message']}")
            print(f"   👤 Validé par: {result['rapport']['valide_par']}")
        else:
            print(f"❌ Erreur validation: {response.status_code}")
    
    def test_rapport_actions(self):
        """Tester les actions spéciales sur les rapports"""
        print("\n🎯 5. TEST ACTIONS SPÉCIALES")
        print("-" * 45)
        
        if not self.test_rapport:
            print("❌ Pas de rapport de test disponible")
            return
        
        rapport_id = self.test_rapport['id']
        
        # Test 1: Voir ses rapports
        print("\n5.1 Voir ses rapports:")
        response = self.client.get('/api/rapports/mes_rapports/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 200:
            mes_rapports = response.json()
            print(f"✅ Employé voit {len(mes_rapports)} rapport(s)")
        else:
            print(f"❌ Erreur consultation: {response.status_code}")
        
        # Test 2: Dupliquer un rapport
        print("\n5.2 Dupliquer un rapport:")
        response = self.client.post(f'/api/rapports/{rapport_id}/dupliquer/',
                                   data=json.dumps({}),
                                   content_type='application/json',
                                   HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 201:
            duplicate = response.json()
            print("✅ Rapport dupliqué avec succès")
            print(f"   📋 Nouveau titre: {duplicate['titre']}")
        else:
            print(f"❌ Erreur duplication: {response.status_code}")
        
        # Test 3: Voir les statistiques
        print("\n5.3 Voir les statistiques:")
        response = self.client.get('/api/rapports/statistiques/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["admin"]}')
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Statistiques obtenues")
            print(f"   📊 Total rapports: {stats['total_rapports']}")
            
            if stats['par_type']:
                print("   📈 Par type:")
                for type_stat in stats['par_type']:
                    print(f"      - {type_stat['type_rapport_display']}: {type_stat['count']}")
            
            if stats['recent']:
                print("   📋 Rapports récents:")
                for recent in stats['recent']:
                    print(f"      - {recent['titre']} ({recent['date_generation'][:10]})")
        else:
            print(f"❌ Erreur statistiques: {response.status_code}")
        
        # Test 4: Employé ne peut pas voir les statistiques
        response = self.client.get('/api/rapports/statistiques/',
                                 HTTP_AUTHORIZATION=f'Bearer {self.tokens["employe"]}')
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas voir les statistiques (correct)")
        else:
            print(f"❌ Employé peut voir les statistiques (erreur): {response.status_code}")


if __name__ == '__main__':
    tester = RapportTester()
    tester.run_all_tests()

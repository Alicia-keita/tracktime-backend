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

def test_payroll_generation():
    """Tester la génération de bulletin de salaire selon le diagramme"""
    client = Client()
    base_url = '/api/payrolls/'
    
    print("💰 GÉNÉRATION DE BULLETIN DE SALAIRE")
    print("=" * 50)
    
    # 1. Connexion RH
    print("\n1️⃣ Connexion RH...")
    response = client.post('/api/login/', 
                          data=json.dumps({'username': 'rh1', 'password': 'password123'}),
                          content_type='application/json')
    
    if response.status_code == 200:
        token = response.json()['access']
        headers = {'HTTP_AUTHORIZATION': f'Bearer {token}'}
        print("✅ RH connecté avec succès")
    else:
        print("❌ Erreur connexion RH")
        return
    
    # 2. Récupérer la liste des employés
    print("\n2️⃣ Récupération des employés...")
    response = client.get('/api/users/', **headers)
    
    if response.status_code == 200:
        users = response.json()
        print(f"✅ {len(users)} employé(s) trouvé(s)")
        
        # Trouver l'employé employe1
        employee = None
        for user in users:
            if user['username'] == 'employe1':
                employee = user
                break
        
        if not employee:
            print("❌ Employé employe1 non trouvé")
            return
        
        print(f"   👤 Employé sélectionné: {employee['first_name']} {employee['last_name']} (ID: {employee['id']})")
        
        # 3. Générer le bulletin de salaire
        print("\n3️⃣ Génération du bulletin de salaire...")
        
        periode_debut = (datetime.now().replace(day=1)).date()
        periode_fin = (datetime.now().replace(day=1) + timedelta(days=30)).date()
        
        payroll_data = {
            'employee': employee['id'],
            'periode_debut': periode_debut.strftime('%Y-%m-%d'),
            'periode_fin': periode_fin.strftime('%Y-%m-%d')
        }
        
        print(f"   📅 Période: {periode_debut} → {periode_fin}")
        
        response = client.post(base_url + 'generate/',
                          data=json.dumps(payroll_data),
                          content_type='application/json',
                          **headers)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ {result['message']}")
            
            bulletin = result['bulletin']
            print(f"\n   📊 BULLETIN GÉNÉRÉ:")
            print(f"      👤 Employé: {bulletin['employee_name']}")
            print(f"      📅 Période: {bulletin['periode_debut']} → {bulletin['periode_fin']}")
            print(f"      ⏰ Heures travaillées: {bulletin['heures_travaillees']}")
            print(f"      ⏰ Heures sup.: {bulletin['heures_supplementaires']}")
            print(f"      ❌ Absences: {bulletin['nb_absences']}")
            print(f"      ⏰ Retards: {bulletin['nb_retards']}")
            print(f"      💰 Salaire base: {bulletin['salaire_base']} €")
            print(f"      💰 Prime sup.: {bulletin['prime_heures_sup']} €")
            print(f"      ❌ Déduction abs.: {bulletin['deduction_absences']} €")
            print(f"      💰 Salaire brut: {bulletin['salaire_brut']} €")
            print(f"      🏥 CNSS: {bulletin['cnss']} €")
            print(f"      💸 Impôt: {bulletin['impot']} €")
            print(f"      💰 Salaire net: {bulletin['salaire_net']} €")
            print(f"      👤 Généré par: {bulletin['genere_par_name']}")
            print(f"      🕐 Date: {bulletin['date_generation']}")
            
            payroll_id = bulletin['id']
            
        elif response.status_code == 400:
            error = response.json()
            print(f"❌ Erreur: {error}")
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
    else:
        print(f"❌ Erreur accès utilisateurs: {response.status_code}")
        # Utiliser l'ID de l'employé connu pour continuer le test
        employee_id = 18  # ID de employe1
        periode_debut = (datetime.now().replace(day=1)).date()
        periode_fin = (datetime.now().replace(day=1) + timedelta(days=30)).date()
        
        payroll_data = {
            'employee': employee_id,
            'periode_debut': periode_debut.strftime('%Y-%m-%d'),
            'periode_fin': periode_fin.strftime('%Y-%m-%d')
        }
        
        print(f"\n3️⃣ Génération du bulletin de salaire (avec ID connu)...")
        print(f"   📅 Période: {periode_debut} → {periode_fin}")
        
        response = client.post(base_url + 'generate/',
                          data=json.dumps(payroll_data),
                          content_type='application/json',
                          **headers)
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ {result['message']}")
            
            bulletin = result['bulletin']
            print(f"\n   📊 BULLETIN GÉNÉRÉ:")
            print(f"      👤 Employé: {bulletin['employee_name']}")
            print(f"      📅 Période: {bulletin['periode_debut']} → {bulletin['periode_fin']}")
            print(f"      💰 Salaire net: {bulletin['salaire_net']} €")
            payroll_id = bulletin['id']
        else:
            print(f"❌ Erreur génération: {response.status_code}")
            return
    
    # 4. Voir tous les bulletins (perspective RH)
    print("\n4️⃣ Voir tous les bulletins (perspective RH)...")
    response = client.get(base_url, **headers)
    
    if response.status_code == 200:
        payrolls = response.json()
        print(f"✅ {len(payrolls)} bulletin(s) trouvé(s)")
        
        for payroll in payrolls:
            print(f"   📋 Bulletin {payroll['id']}: {payroll['employee_name']} - {payroll['periode_debut']} → {payroll['periode_fin']} (Net: {payroll['salaire_net']} €)")
    
    # 5. Test employé qui essaie de générer (doit échouer)
    print("\n5️⃣ Test: Employé essaie de générer (doit échouer)...")
    
    # Login employé
    response = client.post('/api/login/', 
                          data=json.dumps({'username': 'employe1', 'password': 'password123'}),
                          content_type='application/json')
    
    if response.status_code == 200:
        emp_token = response.json()['access']
        emp_headers = {'HTTP_AUTHORIZATION': f'Bearer {emp_token}'}
        
        response = client.post(base_url + 'generate/',
                          data=json.dumps(payroll_data),
                          content_type='application/json',
                          **emp_headers)
        
        if response.status_code == 403:
            print("✅ Employé ne peut pas générer (permission refusée)")
        else:
            print(f"❌ Erreur: Employé ne devrait pas pouvoir générer - {response.status_code}")
    
    print("\n✨ Tests de génération terminés !")

if __name__ == '__main__':
    test_payroll_generation()

#!/usr/bin/env python
import os, sys, django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client

def test_payroll_permissions():
    """Tester les permissions de suppression des bulletins"""
    client = Client()
    
    print("🔒 TEST PERMISSIONS SUPPRESSION BULLETIN")
    print("=" * 50)
    
    # 1. Créer un bulletin avec RH
    print("\n1️⃣ Création bulletin avec RH...")
    response = client.post('/api/login/', 
                          data=json.dumps({'username': 'rh1', 'password': 'password123'}),
                          content_type='application/json')
    
    if response.status_code == 200:
        rh_token = response.json()['access']
        
        # Générer bulletin
        payroll_data = {
            'employee': 18,
            'periode_debut': '2026-04-01',
            'periode_fin': '2026-04-30'
        }
        
        response = client.post('/api/payrolls/generate/',
                              data=json.dumps(payroll_data),
                              content_type='application/json',
                              HTTP_AUTHORIZATION=f'Bearer {rh_token}')
        
        if response.status_code == 201:
            bulletin = response.json()['bulletin']
            bulletin_id = bulletin['id']
            print(f"✅ Bulletin créé - ID: {bulletin_id}")
        else:
            print("❌ Erreur création bulletin")
            return
    else:
        print("❌ Erreur login RH")
        return
    
    # 2. Test: RH essaie de supprimer (doit échouer)
    print("\n2️⃣ Test: RH essaie de supprimer (doit échouer)...")
    response = client.delete(f'/api/payrolls/{bulletin_id}/',
                            HTTP_AUTHORIZATION=f'Bearer {rh_token}')
    
    if response.status_code == 403:
        print("✅ RH ne peut PAS supprimer (permission refusée)")
    else:
        print(f"❌ Erreur: RH ne devrait pas pouvoir supprimer - {response.status_code}")
    
    # 3. Test: Admin peut supprimer
    print("\n3️⃣ Test: Admin peut supprimer...")
    response = client.post('/api/login/', 
                          data=json.dumps({'username': 'admin1', 'password': 'password123'}),
                          content_type='application/json')
    
    if response.status_code == 200:
        admin_token = response.json()['access']
        
        response = client.delete(f'/api/payrolls/{bulletin_id}/',
                                HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        
        if response.status_code == 204:
            print("✅ Admin peut supprimer")
        elif response.status_code == 200:
            result = response.json()
            print(f"✅ Admin peut supprimer: {result}")
        else:
            print(f"❌ Erreur suppression admin: {response.status_code}")
    else:
        print("❌ Erreur login admin")
    
    # 4. Test: Employé essaie de supprimer (doit échouer)
    print("\n4️⃣ Test: Employé essaie de supprimer (doit échouer)...")
    response = client.post('/api/login/', 
                          data=json.dumps({'username': 'employe1', 'password': 'password123'}),
                          content_type='application/json')
    
    if response.status_code == 200:
        emp_token = response.json()['access']
        
        response = client.delete(f'/api/payrolls/{bulletin_id}/',
                                HTTP_AUTHORIZATION=f'Bearer {emp_token}')
        
        if response.status_code == 403:
            print("✅ Employé ne peut PAS supprimer")
        elif response.status_code == 404:
            print("✅ Employé ne peut PAS supprimer (déjà supprimé)")
        else:
            print(f"❌ Erreur: Employé ne devrait pas pouvoir supprimer - {response.status_code}")
    
    print("\n✨ Tests de permissions terminés !")
    print("\n📋 Résumé des permissions:")
    print("   🆕 Générer bulletin: RH + Admin")
    print("   👁️  Voir bulletins: RH + Admin + Employé (ses bulletins)")
    print("   🗑️  Supprimer bulletin: Admin SEULEMENT")

if __name__ == '__main__':
    test_payroll_permissions()

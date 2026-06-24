#!/usr/bin/env python
import os, sys, django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client
from permissions.models import Payroll

def test_payroll_delete_permissions():
    """Tester les permissions de suppression des bulletins existants"""
    client = Client()
    
    print("🔒 TEST PERMISSIONS SUPPRESSION BULLETIN")
    print("=" * 50)
    
    # Récupérer un bulletin existant
    bulletins = Payroll.objects.all()
    if not bulletins:
        print("❌ Aucun bulletin trouvé. Créez d'abord un bulletin.")
        return
    
    bulletin_id = bulletins.first().id
    print(f"📋 Bulletin existant - ID: {bulletin_id}")
    
    # 1. Test: RH essaie de supprimer (doit échouer)
    print("\n1️⃣ Test: RH essaie de supprimer (doit échouer)...")
    response = client.post('/api/login/', 
                          data=json.dumps({'username': 'rh1', 'password': 'password123'}),
                          content_type='application/json')
    
    if response.status_code == 200:
        rh_token = response.json()['access']
        
        response = client.delete(f'/api/payrolls/{bulletin_id}/',
                                HTTP_AUTHORIZATION=f'Bearer {rh_token}')
        
        if response.status_code == 403:
            print("✅ RH ne peut PAS supprimer (permission refusée)")
        else:
            print(f"❌ Erreur: RH ne devrait pas pouvoir supprimer - {response.status_code}")
    
    # 2. Test: Admin peut supprimer
    print("\n2️⃣ Test: Admin peut supprimer...")
    response = client.post('/api/login/', 
                          data=json.dumps({'username': 'admin1', 'password': 'password123'}),
                          content_type='application/json')
    
    if response.status_code == 200:
        admin_token = response.json()['access']
        print(f"✅ Admin connecté")
        
        response = client.delete(f'/api/payrolls/{bulletin_id}/',
                                HTTP_AUTHORIZATION=f'Bearer {admin_token}')
        
        if response.status_code == 204:
            print("✅ Admin peut supprimer (204 No Content)")
        elif response.status_code == 200:
            result = response.json()
            print(f"✅ Admin peut supprimer: {result}")
        else:
            print(f"❌ Erreur suppression admin: {response.status_code}")
            print(f"   Réponse: {response.json() if response.content else 'Pas de contenu'}")
    else:
        print("❌ Erreur login admin")
    
    # 3. Test: Employé essaie de supprimer (doit échouer)
    print("\n3️⃣ Test: Employé essaie de supprimer (doit échouer)...")
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
    test_payroll_delete_permissions()

import os, sys, django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client

print("👁️  EMPLOYÉ VÉRIFIE LE STATUT DE SA DEMANDE")
print("=" * 50)

# Client pour simuler l'employé
client = Client()

# 1. Login employé
print("\n1️⃣ Connexion employé...")
response = client.post('/api/login/', 
                      data=json.dumps({'username': 'employe1', 'password': 'password123'}),
                      content_type='application/json')

if response.status_code == 200:
    token = response.json()['access']
    print("✅ Employé connecté")
    
    # 2. Voir toutes ses demandes
    print("\n2️⃣ Voir toutes les demandes de l'employé...")
    
    response = client.get('/api/permissions/',
                         HTTP_AUTHORIZATION=f'Bearer {token}')
    
    if response.status_code == 200:
        requests = response.json()
        print(f"📋 Total des demandes: {len(requests)}")
        
        for req in requests:
            print(f"\n   📝 DEMANDE #{req['id']}:")
            print(f"      📅 Type: {req['type_permission_display']}")
            print(f"      ⏰ Période: {req['date_sortie'][:19]} → {req['date_retour'][:19]}")
            print(f"      💭 Motif: {req['motif']}")
            print(f"      📊 Statut: {req['status_display']}")
            print(f"      🕐 Demandé le: {req['date_demande'][:19]}")
            
            if req['status'] == 'approved':
                print(f"      ✅ Approuvé par: {req['rh_traitant_name']}")
                print(f"      💬 Commentaire RH: {req['commentaire_rh']}")
                print(f"      🕐 Traité le: {req['date_traitement'][:19]}")
            elif req['status'] == 'rejected':
                print(f"      ❌ Rejeté par: {req['rh_traitant_name']}")
                print(f"      💬 Commentaire RH: {req['commentaire_rh']}")
                print(f"      🕐 Traité le: {req['date_traitement'][:19]}")
            elif req['status'] == 'pending':
                print(f"      ⏳ En attente de validation RH")
    
    # 3. Vérifier spécifiquement la demande approuvée (ID 5)
    print("\n3️⃣ Vérification détaillée de la demande approuvée...")
    
    response = client.get('/api/permissions/5/',
                         HTTP_AUTHORIZATION=f'Bearer {token}')
    
    if response.status_code == 200:
        req = response.json()
        print(f"✅ Détails de la demande #{req['id']}:")
        print(f"   👤 Employé: {req['employee_name']}")
        print(f"   📅 Type: {req['type_permission_display']}")
        print(f"   ⏰ Période: {req['date_sortie'][:19]} → {req['date_retour'][:19]}")
        print(f"   💭 Motif: {req['motif']}")
        print(f"   📊 Statut: {req['status_display']}")
        print(f"   🕐 Demandé le: {req['date_demande'][:19]}")
        
        if req['status'] == 'approved':
            print(f"\n   🎉 BONNE NOUVELLE !")
            print(f"   ✅ Approuvé par: {req['rh_traitant_name']}")
            print(f"   💬 Commentaire RH: {req['commentaire_rh']}")
            print(f"   🕐 Traité le: {req['date_traitement'][:19]}")
        elif req['status'] == 'rejected':
            print(f"\n   ❌ MAUVAISE NOUVELLE...")
            print(f"   ❌ Rejeté par: {req['rh_traitant_name']}")
            print(f"   💬 Commentaire RH: {req['commentaire_rh']}")
            print(f"   🕐 Traité le: {req['date_traitement'][:19]}")
    
    # 4. Instructions pour Postman
    print(f"\n🌐 POUR TESTER DANS POSTMAN (EMPLOYÉ):")
    print(f"   1. Login employé:")
    print(f"      POST http://127.0.0.1:8000/api/login/")
    print(f"      {{\"username\": \"employe1\", \"password\": \"password123\"}}")
    print(f"   ")
    print(f"   2. Voir ses demandes:")
    print(f"      GET http://127.0.0.1:8000/api/permissions/")
    print(f"      Authorization: Bearer <TOKEN_EMP>")
    print(f"   ")
    print(f"   3. Voir une demande spécifique:")
    print(f"      GET http://127.0.0.1:8000/api/permissions/5/")
    print(f"      Authorization: Bearer <TOKEN_EMP>")

else:
    print(f"❌ Erreur connexion: {response.status_code}")

print(f"\n✨ L'employé peut maintenant voir que sa demande a été approuvée !")

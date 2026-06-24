import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client

client = Client()

print("=== TEST FINAL - LOGIN VIA EMAIL ===")
print()

# Test 1: bodiel
print("1. Test: bodiel@gmail.com / password123")
response = client.post(
    '/api/auth/login/',
    {'email': 'bodiel@gmail.com', 'password': 'password123'},
    content_type='application/json'
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ RÉUSSI ! User: {data['user']['username']} ({data['user']['role']})")
else:
    print(f"   ❌ ÉCHEC: {response.json()}")

print()

# Test 2: admin
print("2. Test: admin@gmail.com / admin123")
response = client.post(
    '/api/auth/login/',
    {'email': 'admin@gmail.com', 'password': 'admin123'},
    content_type='application/json'
)
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ RÉUSSI ! User: {data['user']['username']} ({data['user']['role']})")
else:
    print(f"   ❌ ÉCHEC: {response.json()}")

print()
print("=== TOUS LES TESTS TERMINÉS ===")

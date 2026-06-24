import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client

client = Client()

print("=== TESTING EMAIL LOGIN ===")

print("\nTesting with email 'bodiel@gmail.com' and password 'password123'")
response = client.post(
    '/api/auth/login/',
    {'email': 'bodiel@gmail.com', 'password': 'password123'},
    content_type='application/json'
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

print("\nTesting with email 'admin@gmail.com' and password 'admin123'")
response = client.post(
    '/api/auth/login/',
    {'email': 'admin@gmail.com', 'password': 'admin123'},
    content_type='application/json'
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

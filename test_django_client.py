import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.test import Client

client = Client()

print("=== TESTING DJANGO CLIENT ===")

# Test login with username
print("\n1. Testing with username 'bodiel' and password 'password123'")
response = client.post(
    '/api/auth/login/',
    {'username': 'bodiel', 'password': 'password123'},
    content_type='application/json'
)
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Let's also look at what's happening in the serializer directly
print("\n2. Testing serializer directly")
from core.auth_complete import CustomTokenObtainPairSerializer

data = {'username': 'bodiel', 'password': 'password123'}
serializer = CustomTokenObtainPairSerializer(data=data)
print(f"Serializer is valid: {serializer.is_valid()}")
if not serializer.is_valid():
    print(f"Errors: {serializer.errors}")

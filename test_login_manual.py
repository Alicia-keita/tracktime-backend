import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from users.models import User
from django.contrib.auth import authenticate

print("=== Testing authentication manually ===")

# Test bodiel user
print("\n1. Testing bodiel user:")
user = User.objects.get(username='bodiel')
print(f"   Username: {user.username}")
print(f"   Email: {user.email}")
print(f"   Role: {user.role}")
print(f"   Is active: {user.is_active}")
print(f"   Checking password 'password123': {user.check_password('password123')}")

# Try authenticate function
print("\n2. Testing Django authenticate:")
auth_user = authenticate(username='bodiel', password='password123')
print(f"   Result with username: {auth_user}")

auth_user2 = authenticate(username='bodiel@gmail.com', password='password123')
print(f"   Result with email as username: {auth_user2}")

# Test admin user
print("\n3. Testing admin user:")
try:
    admin = User.objects.get(username='admin')
    print(f"   Username: {admin.username}")
    print(f"   Checking password 'admin123': {admin.check_password('admin123')}")
except User.DoesNotExist:
    print("   Admin user not found")

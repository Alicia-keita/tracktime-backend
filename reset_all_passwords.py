import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from users.models import User
from django.contrib.auth import authenticate

print("=== Resetting ALL passwords to known values ===\n")

users = User.objects.all()
print(f"Found {len(users)} users:\n")

for user in users:
    # Set password same as username, or use default
    if user.username == 'admin':
        pwd = 'admin123'
    elif user.username == 'bodiel':
        pwd = 'password123'
    elif user.username == 'rh' or user.username == 'HawaDemba':
        pwd = 'rh123'
    else:
        pwd = 'password123'
        
    user.set_password(pwd)
    user.save()
    print(f"✓ {user.username} ({user.email}) - password set to '{pwd}'")

    # Verify it works
    test_auth = authenticate(username=user.username, password=pwd)
    print(f"  ✓ Authentification: {'OK' if test_auth else 'FAILED'}\n")

print("\n=== ALL PASSWORDS RESET! ===")

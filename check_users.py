import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=== Liste des utilisateurs ===")
for user in User.objects.all():
    print(f"Email: {user.email}")
    print(f"Username: {user.username}")
    print(f"Role: {user.role}")
    print(f"Badge RFID: {user.badge_rfid}")
    print(f"Is active: {user.is_active}")
    print(f"Is staff: {user.is_staff}")
    print(f"Is superuser: {user.is_superuser}")
    print("---")

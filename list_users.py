import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from users.models import User

print("=== UTILISATEURS DANS LA BASE DE DONNEES ===")
for user in User.objects.all():
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Role: {user.role}")
    print("-" * 40)

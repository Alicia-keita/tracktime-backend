import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from users.models import User

print("=== UTILISATEURS DANS LA BASE MYSQL ===")
for user in User.objects.all():
    print(f"ID: {user.id}")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Password hash: {user.password[:50]}...")
    print(f"  Role: {user.role}")
    print("-" * 50)

print(f"\nTotal: {User.objects.count()} utilisateurs")

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from users.models import User

u = User.objects.get(username='bodiel')
print('Username:', u.username)
print('Email:', u.email)

# Try setting a known password to test
print("Setting test password to 'password123'...")
u.set_password('password123')
u.save()
print("Password set! Now check:", u.check_password('password123'))

# Also check another user
try:
    admin = User.objects.get(username='admin')
    print("\nAdmin user found!")
    admin.set_password('admin123')
    admin.save()
    print("Admin password set to admin123")
except Exception as e:
    print("Admin not found:", e)

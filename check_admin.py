import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from users.models import User

u = User.objects.filter(username='admin').first()
if u:
    print(f"✅ Admin existe: username={u.username}, role={u.role}, is_superuser={u.is_superuser}")
else:
    print("❌ Admin n'existe pas")
    # Create admin
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123',
        role='ADMIN'
    )
    print("✅ Admin créé: admin / admin123")

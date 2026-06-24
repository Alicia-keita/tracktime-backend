import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Créer un superutilisateur
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print("✅ Superutilisateur créé: admin / admin123")
else:
    print("ℹ️ Superutilisateur admin existe déjà")

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Réinitialiser le mot de passe de l'admin
user = User.objects.get(username='Amadou')
user.set_password('admin123')
user.save()

print(f"Mot de passe réinitialisé pour {user.username}: admin123")

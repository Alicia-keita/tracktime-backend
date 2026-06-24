import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Mettre à jour l'email de l'admin
user = User.objects.get(username='Amadou')
user.email = 'amadou@bac.com'
user.save()

print(f"Email mis à jour pour {user.username}: {user.email}")

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from users.models import User

# Créer un utilisateur
user = User.objects.create_user(
    username='employe1',
    email='employe1@example.com',
    password='password123',
    first_name='Jean',
    last_name='Dupont',
    role='EMPLOYE',
    service='Informatique'
)
print(f"✅ Utilisateur créé: {user.username} / password123")

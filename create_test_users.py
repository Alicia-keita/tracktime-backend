
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from users.models import User

# Créer des utilisateurs de test
test_users = [
    {
        'username': 'Admin',
        'password': 'Admin123',
        'role': 'admin',
        'email': 'admin@tracktime.com',
        'first_name': 'Admin',
        'last_name': 'System',
        'is_staff': True,
        'is_superuser': True
    },
    {
        'username': 'rh1',
        'password': 'password123',
        'role': 'rh',
        'email': 'rh1@tracktime.com',
        'first_name': 'RH',
        'last_name': 'User'
    },
    {
        'username': 'employe1',
        'password': 'password123',
        'role': 'employe',
        'email': 'employe1@tracktime.com',
        'first_name': 'Employé',
        'last_name': 'Test'
    }
]

for user_data in test_users:
    username = user_data.pop('username')
    password = user_data.pop('password')
    
    try:
        user, created = User.objects.get_or_create(username=username, defaults=user_data)
        if created:
            user.set_password(password)
            user.save()
            print(f"[OK] Utilisateur cree: {username} / {password}")
        else:
            user.set_password(password)
            for key, value in user_data.items():
                setattr(user, key, value)
            user.save()
            print(f"[UPDATE] Utilisateur mis a jour: {username} / {password}")
    except Exception as e:
        print(f"[ERROR] Erreur avec {username}: {e}")

print("\nTous les utilisateurs:")
for u in User.objects.all():
    print(f"- {u.username} ({u.role}) - {u.email}")


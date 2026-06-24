import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from users.models import User

# Mettre à jour l'utilisateur admin pour qu'il soit staff
try:
    admin = User.objects.get(username='Admin')
    admin.is_staff = True
    admin.is_superuser = True
    admin.save()
    print(f"Utilisateur Admin mis à jour avec succès: {admin.username} (is_staff={admin.is_staff}, is_superuser={admin.is_superuser})")
except User.DoesNotExist:
    print("Utilisateur Admin non trouvé, création en cours...")
    admin = User.objects.create_superuser(
        username='Admin',
        password='Admin123',
        role='admin',
        email='admin@tracktime.com'
    )
    print(f"Utilisateur Admin créé avec succès: {admin.username}")
except Exception as e:
    print(f"Erreur: {e}")

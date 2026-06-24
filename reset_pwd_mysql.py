import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from users.models import User
from django.contrib.auth import authenticate

users_config = [
    {'username': 'admin', 'email': 'admin@gmail.com', 'password': 'admin123'},
    {'username': 'bodiel', 'email': 'bodiel@gmail.com', 'password': 'password123'},
    {'username': 'rh', 'email': 'rh@gmail.com', 'password': 'rh123'},
    {'username': 'HawaDemba', 'email': '', 'password': 'rh123'},
    {'username': 'employe', 'email': 'employer@gmail.com', 'password': 'password123'},
    {'username': 'Hourayeseck', 'email': 'keitahawa09@gmail.com', 'password': 'password123'},
    {'username': 'Eva-Dieng', 'email': 'keitahawa415@gmail.com', 'password': 'password123'},
    {'username': 'hawak9969', 'email': 'hawak9969@gmail.com', 'password': 'password123'},
    {'username': 'evadieng75', 'email': 'evadieng75@gmail.com', 'password': 'password123'},
    {'username': 'Coumba-Sow', 'email': 'coumbasow@gmail.com', 'password': 'password123'},
    {'username': 'Abou', 'email': 'sow22@gmail.com', 'password': 'password123'},
    {'username': 'Ndeye', 'email': 'dieng@gmail.com', 'password': 'password123'},
]

print("=== RÉINITIALISATION DES MOTS DE PASSE DANS MYSQL ===")
for config in users_config:
    try:
        user = User.objects.get(username=config['username'])
        user.set_password(config['password'])
        user.save()
        print(f"✅ {config['username']} ({config['email']}) - Mot de passe: {config['password']}")
        
        # Verify the password
        test_auth = authenticate(username=config['username'], password=config['password'])
        print(f"   ↳ Test d'authentification: {'SUCCÈS' if test_auth else 'ÉCHEC'}")
        
    except Exception as e:
        print(f"❌ Erreur avec {config['username']}: {e}")

print("\n=== TERMINÉ ===")

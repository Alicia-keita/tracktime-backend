import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth import authenticate, get_user_model
User = get_user_model()

test_passwords = ['admin123', 'admin', 'password123', 'password', '123456', 'rh123', 'employe123']

emails_to_test = [
    'keitahawa415@gmail.com',
    'rh@gmail.com',
    'admin@gmail.com',
]

for email in emails_to_test:
    try:
        user = User.objects.get(email=email)
        print(f"\nUser: {user.username} | Email: {email} | Role: {user.role}")
        found = False
        for pwd in test_passwords:
            result = authenticate(username=user.username, password=pwd)
            if result:
                print(f"  => MOT DE PASSE TROUVE: [{pwd}]")
                found = True
                break
        if not found:
            print(f"  => Aucun mot de passe connu ne fonctionne")
    except User.DoesNotExist:
        print(f"\nEmail {email} introuvable en base")

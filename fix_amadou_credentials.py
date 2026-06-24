import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Remettre l'email original et définir le mot de passe
user = User.objects.get(username='Amadou')
user.email = 'amadou04@gmail.com'
user.set_password('Sow@1213')
user.save()

print(f"Email remis à: {user.email}")
print(f"Mot de passe défini à: Sow@1213")

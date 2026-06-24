import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

print("=== VÉRIFICATION DE LA BASE DE DONNÉES ===")
print(f"Engine: {connection.settings_dict['ENGINE']}")
print(f"Name: {connection.settings_dict['NAME']}")
print(f"User: {connection.settings_dict['USER']}")
print(f"Host: {connection.settings_dict['HOST']}")
print()

print("=== TEST DE CONNEXION ===")
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("[OK] Connexion réussie !")
except Exception as e:
    print(f"[ERROR] Échec de la connexion : {e}")

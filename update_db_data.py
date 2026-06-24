import os
import django

# Configuration de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from core.pointage import Pointage

User = get_user_model()

print("--- Demarrage de la mise a jour de la base de donnees ---")

# 1. Mise à jour de Hawa Keita
try:
    hawa = User.objects.get(username='hawa')
    hawa.badge_rfid = '891667220'
    hawa.save()
    print(f"Hawa Keita mise a jour avec badge RFID : {hawa.badge_rfid}")
except User.DoesNotExist:
    print("Utilisateur 'hawa' introuvable dans la base de donnees.")

# 2. Mise à jour de Fatou Diaw
try:
    fatou = User.objects.get(username='fatou')
    fatou.badge_rfid = '1992385737'
    fatou.save()
    print(f"Fatou Diaw mise a jour avec badge RFID : {fatou.badge_rfid}")
except User.DoesNotExist:
    print("Utilisateur 'fatou' introuvable dans la base de donnees.")

# 3. Création / Mise à jour de Abdou Fall
abdou_username = 'abdou'
abdou_email = 'abdou25@gmail.com'
abdou_pwd = 'Fall@1213'
abdou_badge = '2312423937'

try:
    abdou = User.objects.get(username=abdou_username)
    print(f"L'utilisateur '{abdou_username}' existe deja. Mise a jour...")
    abdou.email = abdou_email
    abdou.first_name = 'Abdou'
    abdou.last_name = 'Fall'
    abdou.role = 'employe'
    abdou.badge_rfid = abdou_badge
    abdou.set_password(abdou_pwd)
    abdou.save()
    print(f"Employe Abdou Fall mis a jour.")
except User.DoesNotExist:
    print(f"Creation de l'employe Abdou Fall...")
    abdou = User.objects.create_user(
        username=abdou_username,
        email=abdou_email,
        password=abdou_pwd,
        first_name='Abdou',
        last_name='Fall',
        role='employe',
        badge_rfid=abdou_badge
    )
    print(f"Employe Abdou Fall cree.")

# 4. Recalcul des statuts des pointages existants
print("\nRecalcul des statuts des pointages existants...")
pointages = Pointage.objects.all()
count = 0
for p in pointages:
    old_statut = p.statut
    # recalculer
    p.save()
    if old_statut != p.statut:
        print(f"  - Pointage de {p.employee.username} le {p.date} : {old_statut} -> {p.statut}")
    count += 1

print(f"Recalcul termine pour {count} pointages.")
print("--- Mise a jour terminee ---")

#!/usr/bin/env python
"""
Script pour tester l'endpoint pointages
"""
import os
import sys
import django
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'attendance_system.settings')
django.setup()

from core.pointage import Pointage
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

client = APIClient()

# Créer un token pour un utilisateur test
user = User.objects.first()
print(f"Utilisateur test: {user.username}")

# Générer un token JWT
refresh = RefreshToken.for_user(user)
access_token = str(refresh.access_token)
print(f"Token: {access_token[:50]}...")

# Simuler une requête GET sur /api/pointages/ avec authentification
client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
response = client.get('/api/pointages/')
print(f"Status code: {response.status_code}")
print(f"Données reçues: {response.data}")

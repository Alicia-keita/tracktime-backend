#!/bin/bash

# Script de test manuel pour l'API de demande de permission
# Usage: ./test_api.sh

BASE_URL="http://localhost:8000/api"

echo "🧪 TEST MANUEL - API DEMANDE DE PERMISSION"
echo "=========================================="

# 1. Obtenir un token pour l'employé
echo -e "\n1️⃣ Connexion employé..."
TOKEN_EMP=$(curl -s -X POST "$BASE_URL/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "employe1", "password": "password123"}' | \
  python -c "import sys, json; print(json.load(sys.stdin)['access'])")

if [ -n "$TOKEN_EMP" ]; then
    echo "✅ Token employé obtenu: ${TOKEN_EMP:0:20}..."
else
    echo "❌ Erreur connexion employé"
    exit 1
fi

# 2. Créer une demande de permission (employé)
echo -e "\n2️⃣ Création demande (employé)..."
RESPONSE=$(curl -s -X POST "$BASE_URL/permissions/" \
  -H "Authorization: Bearer $TOKEN_EMP" \
  -H "Content-Type: application/json" \
  -d '{
    "type_permission": "leave",
    "date_sortie": "2026-04-10T09:00:00Z",
    "date_retour": "2026-04-12T17:00:00Z",
    "motif": "Vacances printemps"
  }')

echo "$RESPONSE" | python -m json.tool

# 3. Obtenir un token pour RH
echo -e "\n3️⃣ Connexion RH..."
TOKEN_RH=$(curl -s -X POST "$BASE_URL/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "rh1", "password": "password123"}' | \
  python -c "import sys, json; print(json.load(sys.stdin)['access'])")

# 4. Voir les demandes en attente (RH)
echo -e "\n4️⃣ Voir demandes en attente (RH)..."
curl -s -X GET "$BASE_URL/permissions/pending/" \
  -H "Authorization: Bearer $TOKEN_RH" | \
  python -m json.tool

# 5. Tentative de création par RH (doit échouer)
echo -e "\n5️⃣ Tentative création par RH (doit échouer)..."
curl -s -X POST "$BASE_URL/permissions/" \
  -H "Authorization: Bearer $TOKEN_RH" \
  -H "Content-Type: application/json" \
  -d '{
    "type_permission": "leave",
    "date_sortie": "2026-04-15T09:00:00Z",
    "date_retour": "2026-04-16T17:00:00Z",
    "motif": "Test RH"
  }' | python -m json.tool

echo -e "\n✨ Tests manuels terminés!"
echo -e "\n💡 Pour tester en continu, lancez: python manage.py runserver"

# 🧪 GUIDE POSTMAN - BULLETIN DE SALAIRE

## ÉTAPE 1: Configuration de base

### 1.1 Créer une nouvelle collection
- Nom : "Système de Paie"
- Créer 3 requêtes principales

### 1.2 Variables d'environnement
Créer ces variables dans la collection :
```
{{base_url}} = http://127.0.0.1:8000/api
{{token_rh}} = (sera rempli après login)
{{token_emp}} = (sera rempli après login)
{{employee_id}} = 18
```

---

## ÉTAPE 2: Login RH

### Requête 1: Login RH
```
Method: POST
URL: {{base_url}}/login/
Headers: Content-Type: application/json
Body (raw JSON):
{
  "username": "rh1",
  "password": "password123"
}
```

**Réponse attendue :**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Action :** Copier la valeur de "access" et la mettre dans la variable `{{token_rh}}`

---

## ÉTAPE 3: Générer Bulletin de Salaire

### Requête 2: Générer Bulletin
```
Method: POST
URL: {{base_url}}/payrolls/generate/
Headers: 
  Content-Type: application/json
  Authorization: Bearer {{token_rh}}
Body (raw JSON):
{
  "employee": {{employee_id}},
  "periode_debut": "2026-04-01",
  "periode_fin": "2026-04-30"
}
```

**Réponse attendue :**
```json
{
  "message": "Bulletin généré avec succès.",
  "bulletin": {
    "id": 2,
    "employee_name": "employe1",
    "employee_first_name": "Jean",
    "employee_last_name": "Dupont",
    "periode_debut": "2026-04-01",
    "periode_fin": "2026-04-30",
    "heures_travaillees": "160.00",
    "heures_supplementaires": "5.50",
    "nb_absences": 3,
    "nb_retards": 2,
    "salaire_base": "2000.00",
    "prime_heures_sup": "79.55",
    "deduction_absences": "200.00",
    "salaire_brut": "1879.55",
    "cnss": "80.82",
    "impot": "187.96",
    "autres_deductions": "0.00",
    "salaire_net": "1610.77",
    "date_generation": "2026-04-01T15:45:00.123456Z",
    "genere_par_name": "rh1"
  }
}
```

---

## ÉTAPE 4: Voir les Bulletins

### Requête 3: Lister Bulletins (RH)
```
Method: GET
URL: {{base_url}}/payrolls/
Headers: Authorization: Bearer {{token_rh}}
Body: (none)
```

**Réponse attendue :**
```json
[
  {
    "id": 2,
    "employee_name": "employe1",
    "periode_debut": "2026-04-01",
    "periode_fin": "2026-04-30",
    "salaire_net": "1610.77",
    "date_generation": "2026-04-01T15:45:00.123456Z",
    "genere_par_name": "rh1"
  }
]
```

---

## ÉTAPE 5: Test Employé (optionnel)

### 5.1 Login Employé
```
Method: POST
URL: {{base_url}}/login/
Headers: Content-Type: application/json
Body:
{
  "username": "employe1",
  "password": "password123"
}
```

**Action :** Copier le token dans `{{token_emp}}`

### 5.2 Voir ses bulletins
```
Method: GET
URL: {{base_url}}/payrolls/
Headers: Authorization: Bearer {{token_emp}}
```

---

## ÉTAPE 6: Tests d'erreur

### 6.1 Employé essaie de générer (doit échouer)
```
Method: POST
URL: {{base_url}}/payrolls/generate/
Headers: 
  Content-Type: application/json
  Authorization: Bearer {{token_emp}}
Body:
{
  "employee": {{employee_id}},
  "periode_debut": "2026-04-01",
  "periode_fin": "2026-04-30"
}
```

**Réponse attendue :**
```json
{
  "detail": "Vous n'avez pas la permission d'effectuer cette action."
}
```

### 6.2 Période invalide
```
Method: POST
URL: {{base_url}}/payrolls/generate/
Headers: 
  Content-Type: application/json
  Authorization: Bearer {{token_rh}}
Body:
{
  "employee": {{employee_id}},
  "periode_debut": "2026-04-30",
  "periode_fin": "2026-04-01"
}
```

**Réponse attendue :**
```json
{
  "periode_fin": ["La date de début doit être antérieure à la date de fin."]
}
```

---

## 🎯 QUICK TEST - Copier/Coller

### Test rapide avec curl (si Postman ne fonctionne pas)

1. **Login RH :**
```bash
curl -X POST "http://127.0.0.1:8000/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "rh1", "password": "password123"}'
```

2. **Générer bulletin :**
```bash
curl -X POST "http://127.0.0.1:8000/api/payrolls/generate/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer VOTRE_TOKEN_RH" \
  -d '{"employee": 18, "periode_debut": "2026-04-01", "periode_fin": "2026-04-30"}'
```

---

## 📋 Checklist Postman

- [ ] Serveur Django lancé : `python manage.py runserver`
- [ ] Login RH fonctionnel
- [ ] Token RH copié dans variable
- [ ] Génération bulletin réussie
- [ ] Vérification des calculs
- [ ] Test permissions employé
- [ ] Tests d'erreur

---

## 🔧 Dépannage

### "Token not valid"
- Vérifier que le token est bien copié (sans espaces)
- Regénérer un nouveau token si nécessaire

### "403 Forbidden"
- Vérifier que vous utilisez le bon compte (rh1 pour générer)
- Vérifier l'URL : `/api/payrolls/generate/` (avec / à la fin)

### "400 Bad Request"
- Vérifier le format JSON
- Vérifier les dates (YYYY-MM-DD)
- Vérifier que l'employee_id existe (18 pour employe1)

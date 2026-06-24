# 💰 API BULLETIN DE SALAIRE

## 📋 Vue d'ensemble

Le système de bulletin de salaire permet au RH de générer des bulletins de paie en suivant le diagramme de séquence :

1. **RH** demande la génération → **Système**
2. **Système** récupère données de pointage → **Base de données**
3. **Système** vérifie heures + absences
4. **Système** effectue calcul du salaire
5. **Système** enregistre bulletin → **Base de données**
6. **Système** retourne bulletin généré → **RH**

## 🌐 Endpoints

### 1. **Générer un bulletin** (RH uniquement)
```http
POST /api/payrolls/generate/
Authorization: Bearer <TOKEN_RH>
Content-Type: application/json

{
  "employee": 18,
  "periode_debut": "2026-04-01",
  "periode_fin": "2026-04-30"
}
```

**Réponse :**
```json
{
  "message": "Bulletin généré avec succès.",
  "bulletin": {
    "id": 1,
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
    "date_generation": "2026-04-01T15:30:00.123456Z",
    "genere_par_name": "rh1"
  }
}
```

### 2. **Voir tous les bulletins** (RH/Admin)
```http
GET /api/payrolls/
Authorization: Bearer <TOKEN_RH>
```

### 3. **Voir ses bulletins** (Employé)
```http
GET /api/payrolls/
Authorization: Bearer <TOKEN_EMP>
```

### 4. **Voir un bulletin spécifique**
```http
GET /api/payrolls/{id}/
Authorization: Bearer <TOKEN>
```

## 📊 Champs du Bulletin

### 📋 Informations générales
- `employee_name`: Nom de l'employé
- `periode_debut/fin`: Période de paie
- `date_generation`: Date de génération
- `genere_par_name`: RH qui a généré

### ⏰ Données de pointage
- `heures_travaillees`: Heures normales travaillées
- `heures_supplementaires`: Heures supplémentaires
- `nb_absences`: Nombre d'absences (calculé depuis permissions)
- `nb_retards`: Nombre de retards

### 💰 Calculs salariaux
- `salaire_base`: Salaire de base mensuel (2000€)
- `prime_heures_sup`: Prime pour heures sup. (125% du taux horaire)
- `deduction_absences`: Déduction pour absences
- `salaire_brut`: Salaire avant déductions

### 🏥 Déductions
- `cnss`: Cotisation CNSS (4.3%)
- `impot`: Impôt sur le revenu (10-20% selon tranche)
- `autres_deductions`: Autres déductions
- `salaire_net`: Salaire final

## 🔐 Permissions

| Rôle | Générer | Voir tous | Voir ses bulletins | Supprimer |
|-------|----------|------------|-------------------|-----------|
| RH | ✅ | ✅ | ✅ | ❌ |
| Admin | ✅ | ✅ | ✅ | ✅ |
| Employé | ❌ | ❌ | ✅ | ❌ |

**Règles importantes :**
- Seul l'admin peut supprimer des bulletins de salaire
- RH peut générer et voir tous les bulletins mais pas supprimer
- Employé ne voit que ses propres bulletins

## 🧪 Tests

### Générer un bulletin complet
```bash
# 1. Login RH
curl -X POST "http://127.0.0.1:8000/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "rh1", "password": "password123"}'

# 2. Générer bulletin
curl -X POST "http://127.0.0.1:8000/api/payrolls/generate/" \
  -H "Authorization: Bearer <TOKEN_RH>" \
  -H "Content-Type: application/json" \
  -d '{
    "employee": 18,
    "periode_debut": "2026-04-01",
    "periode_fin": "2026-04-30"
  }'
```

### Voir ses bulletins (employé)
```bash
# 1. Login employé
curl -X POST "http://127.0.0.1:8000/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "employe1", "password": "password123"}'

# 2. Voir ses bulletins
curl -X GET "http://127.0.0.1:8000/api/payrolls/" \
  -H "Authorization: Bearer <TOKEN_EMP>"
```

### Supprimer un bulletin (admin uniquement)
```bash
# 1. Login admin
curl -X POST "http://127.0.0.1:8000/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin1", "password": "password123"}'

# 2. Supprimer un bulletin
curl -X DELETE "http://127.0.0.1:8000/api/payrolls/{id}/" \
  -H "Authorization: Bearer <TOKEN_ADMIN>"
```

## ⚡ Fonctionnalités avancées

### 🔄 Calcul automatique des absences
Le système calcule automatiquement le nombre d'absences depuis les permissions approuvées dans la période.

### ⚠️ Alertes
Si le nombre d'absences > 10, une alerte est générée.

### 🚫 Doublons
Impossible de générer deux bulletins pour la même période et le même employé.

## 📈 Exemple de calcul

Pour un employé avec :
- Salaire base: 2000€
- Heures sup: 5.5h
- Absences: 3 jours

**Calcul :**
- Taux horaire: 2000€ / 173.33h = 11.54€/h
- Prime sup: 5.5h × 11.54€ × 1.25 = 79.55€
- Déduction absences: 3 × (2000€ / 30) = 200€
- Salaire brut: 2000 + 79.55 - 200 = 1879.55€
- CNSS: 1879.55 × 4.3% = 80.82€
- Impôt: 1879.55 × 10% = 187.96€
- Salaire net: 1879.55 - 80.82 - 187.96 = 1610.77€

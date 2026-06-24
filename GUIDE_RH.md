# 📋 GUIDE RH - RÉCEPTION ET TRAITEMENT DES DEMANDES

## 🔍 ÉTAPE 1: Vérifier si le RH a reçu des demandes

### Méthode 1: Voir toutes les demandes en attente
```bash
# Login RH d'abord
POST /api/login/
{
  "username": "rh1", 
  "password": "password123"
}

# Puis vérifier les demandes en attente
GET /api/permissions/pending/
Authorization: Bearer <TOKEN_RH>
```

### Méthode 2: Voir toutes les demandes (avec filtre)
```bash
GET /api/permissions/
Authorization: Bearer <TOKEN_RH>

# Dans la réponse, chercher "status": "pending"
```

## 📊 Réponse Attendue - Demandes en Attente

```json
[
  {
    "id": 3,
    "employee_name": "employe1",
    "employee_first_name": "Jean",
    "employee_last_name": "Dupont",
    "type_permission_display": "Congé",
    "date_sortie": "2026-04-10T09:00:00Z",
    "date_retour": "2026-04-12T17:00:00Z",
    "motif": "Test",
    "status_display": "En attente",
    "date_demande": "2026-04-01T14:38:15.987777Z"
  }
]
```

## ✅ ÉTAPE 2: Approuver une Demande

```bash
PATCH /api/permissions/3/approve/
Authorization: Bearer <TOKEN_RH>
Content-Type: application/json

{
  "commentaire_rh": "Approuvé - Bonnes vacances !"
}
```

### Réponse d'Approbation
```json
{
  "message": "Demande approuvée avec succès.",
  "permission_request": {
    "id": 3,
    "status": "approved",
    "status_display": "Approuvé",
    "rh_traitant_name": "rh1",
    "commentaire_rh": "Approuvé - Bonnes vacances !",
    "date_traitement": "2026-04-01T14:46:33.621188Z"
  }
}
```

## ❌ ÉTAPE 3: Rejeter une Demande

```bash
PATCH /api/permissions/3/reject/
Authorization: Bearer <TOKEN_RH>
Content-Type: application/json

{
  "commentaire_rh": "Rejeté - Période critique"
}
```

### Réponse de Rejet
```json
{
  "message": "Demande rejetée avec succès.",
  "permission_request": {
    "id": 3,
    "status": "rejected",
    "status_display": "Rejeté",
    "rh_traitant_name": "rh1",
    "commentaire_rh": "Rejeté - Période critique",
    "date_traitement": "2026-04-01T14:48:15.123456Z"
  }
}
```

## 🔄 Workflow Complet RH

1. **Se connecter** avec les identifiants RH
2. **Vérifier** les demandes en attente: `GET /api/permissions/pending/`
3. **Examiner** les détails de chaque demande
4. **Décider**: Approuver ou Rejeter
5. **Traiter**: Utiliser les endpoints appropriés
6. **Vérifier** que la demande n'est plus en attente

## 💡 Conseils RH

- **Vérifiez régulièrement** `/api/permissions/pending/`
- **Ajoutez toujours des commentaires** pour transparence
- **Vérifiez les conflits de dates** avant d'approuver
- **Communiquez** avec les employés si besoin

## 🧪 Test Rapide

```bash
# 1. Login RH
curl -X POST "http://127.0.0.1:8000/api/login/" \
  -H "Content-Type: application/json" \
  -d '{"username": "rh1", "password": "password123"}'

# 2. Voir demandes en attente (remplacer TOKEN)
curl -X GET "http://127.0.0.1:8000/api/permissions/pending/" \
  -H "Authorization: Bearer TOKEN_RH"

# 3. Approuver (remplacer ID et TOKEN)
curl -X PATCH "http://127.0.0.1:8000/api/permissions/3/approve/" \
  -H "Authorization: Bearer TOKEN_RH" \
  -H "Content-Type: application/json" \
  -d '{"commentaire_rh": "Approuvé !"}'
```

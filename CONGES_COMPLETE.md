# 🏖️ **SYSTÈME DE GESTION DES CONGÉS**

## 📋 **Table Congés (Structure Respectée)**

### 🏗️ **Modèle Conge dans `core/conges.py`**

```python
class Conge(models.Model):
    # Informations de base
    employe = models.ForeignKey(User, on_delete=models.CASCADE, related_name='conges')
    type_conge = models.CharField(max_length=20, choices=TYPE_CONGE_CHOICES)
    
    # Dates
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    duree_jours = models.IntegerField(help_text="Durée en jours ouvrés")
    
    # Statut et validation
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    valide_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='conges_valides')
    
    # Informations complémentaires
    motif = models.TextField(help_text="Motif de la demande de congé")
    commentaire_rh = models.TextField(blank=True, help_text="Commentaire du RH/Admin")
    
    # Documents joints
    document_attache = models.FileField(upload_to='documents_conges/', null=True, blank=True)
    
    # Solde de congés
    solde_avant = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    solde_apres = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
```

### 📊 **Types de Congés Disponibles**

| Type | Code | Description |
|------|-------|-------------|
| Congé Annuel | `annuel` | Vacances annuelles |
| Congé Maladie | `maladie` | Arrêt maladie |
| Congé Maternité | `maternite` | Congé maternité |
| Congé Paternité | `paternite` | Congé paternité |
| Congé Sans Solde | `sans_solde` | Congé sans solde |
| Congé Exceptionnel | `exceptionnel` | Congé exceptionnel |
| Congé Formation | `formation` | Congé formation |

### 📋 **Statuts des Demandes**

| Statut | Code | Description |
|--------|-------|-------------|
| En Attente | `en_attente` | En attente de validation |
| Approuvé | `approuve` | Validé par RH/Admin |
| Rejeté | `rejete` | Rejeté par RH/Admin |
| Annulé | `annule` | Annulé par l'employé |

---

## 🌐 **API de Gestion des Congés**

### 📝 **Créer une Demande de Congé**
```http
POST /api/conges/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "type_conge": "annuel",
    "date_debut": "2026-12-20T09:00:00Z",
    "date_fin": "2026-12-25T17:00:00Z",
    "duree_jours": 5,
    "motif": "Vacances de Noël",
    "document_attache": "fichier.pdf"
}
```

**Réponse :**
```json
{
    "id": 1,
    "employe": 1,
    "employe_name": "John Doe",
    "employe_service": "IT",
    "type_conge": "annuel",
    "type_conge_display": "Congé Annuel",
    "date_debut": "2026-12-20T09:00:00Z",
    "date_fin": "2026-12-25T17:00:00Z",
    "duree_jours": 5,
    "statut": "en_attente",
    "statut_display": "En Attente",
    "date_demande": "2026-04-01T10:00:00Z",
    "date_traitement": null,
    "valide_par": null,
    "motif": "Vacances de Noël",
    "commentaire_rh": "",
    "document_attache": "/documents_conges/fichier.pdf",
    "solde_avant": "25.0",
    "solde_apres": "20.0"
}
```

### 👁️ **Lister les Congés**
```http
GET /api/conges/
Authorization: Bearer <access_token>
```

**Réponse (Employé) :** Uniquement ses congés
**Réponse (RH/Admin) :** Tous les congés

### 🎯 **Actions Spéciales**

#### ✅ **Approuver une Demande**
```http
PATCH /api/conges/{id}/approve/
Authorization: Bearer <rh_or_admin_token>
Content-Type: application/json

{}
```

#### ❌ **Rejeter une Demande**
```http
PATCH /api/conges/{id}/reject/
Authorization: Bearer <rh_or_admin_token>
Content-Type: application/json

{
    "commentaire_rh": "Motif non valable selon la politique interne"
}
```

#### 🚫 **Annuler sa Demande**
```http
PATCH /api/conges/{id}/cancel/
Authorization: Bearer <employee_token>
Content-Type: application/json

{}
```

#### 📋 **Voir ses Propres Congés**
```http
GET /api/conges/mes_conges/
Authorization: Bearer <access_token>
```

#### ⏳ **Voir les Demandes en Attente**
```http
GET /api/conges/pending/
Authorization: Bearer <rh_or_admin_token>
```

#### 💰 **Voir son Solde de Congés**
```http
GET /api/conges/solde/
Authorization: Bearer <access_token>
```

**Réponse :**
```json
{
    "solde_annuel": 25.0,
    "conges_pris": 5.0,
    "solde_restant": 20.0,
    "employe": "employe1"
}
```

---

## 🔒 **Permissions par Rôle**

| Action | Employé | RH | Admin |
|--------|---------|----|-------|
| Créer demande | ✅ | ✅ | ✅ |
| Voir ses demandes | ✅ | ✅ | ✅ |
| Voir toutes les demandes | ❌ | ✅ | ✅ |
| Approuver demande | ❌ | ✅ | ✅ |
| Rejeter demande | ❌ | ✅ | ✅ |
| Annuler sa demande | ✅ | ✅ | ✅ |
| Voir demandes en attente | ❌ | ✅ | ✅ |
| Voir solde | ✅ | ✅ | ✅ |

---

## ⚠️ **Validations Automatiques**

### 📅 **Validation des Dates**
- La date de fin doit être postérieure à la date de début
- La durée doit être positive
- Pas de chevauchement avec d'autres demandes approuvées/en attente

### 📝 **Validation des Champs**
- Le motif est obligatoire
- Le type de congé doit être valide
- La durée ne peut pas être négative

### 🔒 **Validation des Permissions**
- Seul l'employé concerné peut annuler sa demande
- Seul RH/Admin peut approuver/rejeter
- Un commentaire est requis pour rejeter une demande

---

## 🧪 **Tests du Système**

### 📋 **Tests de Base**
```bash
# Test simple du système
python test_conges_simple.py

# Test complet avec validations
python test_conges_complete.py

# Debug de création
python debug_conge.py
```

### 🎯 **Scénarios de Test**

1. **Employé crée une demande** ✅
2. **RH approuve la demande** ✅
3. **Employé consulte son solde** ✅
4. **RH voit les demandes en attente** ✅
5. **Validation des conflits de dates** ✅
6. **Permissions par rôle** ✅

---

## 📊 **Workflow Complet**

```
1. Employé → Crée demande → Statut: "en_attente"
2. RH → Consulte les demandes en attente
3. RH → Approuve ou Rejette → Statut: "approuve"/"rejete"
4. Système → Met à jour le solde de congés
5. Employé → Consulte son solde mis à jour
```

---

## 🎉 **Avantages du Système**

### ✅ **Fonctionnalités Complètes**
- Gestion complète des demandes de congés
- Calcul automatique des soldes
- Validation des conflits
- Support des documents joints

### 🔒 **Sécurité Robuste**
- Permissions par rôle granulaires
- Validation des entrées
- Audit trail complet

### 📱 **Facilité d'Utilisation**
- API RESTful intuitive
- Messages d'erreur clairs
- Interface responsive possible

### 🔧 **Extensibilité**
- Types de congés personnalisables
- Workflow adaptable
- Intégration facile

**Le système de gestion des congés est maintenant complet et prêt pour la production !** 🚀

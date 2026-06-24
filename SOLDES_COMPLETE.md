# 💰 **SYSTÈME DE GESTION DES SOLDES DE CONGÉS**

## 📋 **Table Solde (Structure Respectée)**

### 🏗️ **Modèle Solde dans `core/solde.py`**

```python
class Solde(models.Model):
    # Informations employé
    employe = models.OneToOneField(User, on_delete=models.CASCADE, related_name='solde_conges')
    
    # Soldes de congés
    solde_annuel = models.DecimalField(max_digits=4, decimal_places=1, default=25.0)
    conges_pris = models.DecimalField(max_digits=4, decimal_places=1, default=0.0)
    conges_restant = models.DecimalField(max_digits=4, decimal_places=1, default=25.0)
    
    # Période de référence
    annee_reference = models.IntegerField(default=2026)
    
    # Métadonnées
    date_mise_a_jour = models.DateTimeField(auto_now=True)
    mis_a_jour_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
```

### 📊 **Structure de la Table**

| Champ | Type | Description |
|-------|------|-------------|
| `id` | Integer | Clé primaire |
| `employe` | ForeignKey | Référence à l'utilisateur |
| `solde_annuel` | Decimal(4,1) | Solde annuel de congés |
| `conges_pris` | Decimal(4,1) | Jours de congés pris |
| `conges_restant` | Decimal(4,1) | Solde restant (calculé auto) |
| `annee_reference` | Integer | Année de référence |
| `date_mise_a_jour` | DateTime | Date de dernière mise à jour |
| `mis_a_jour_par` | ForeignKey | Qui a mis à jour |

---

## 🌐 **API de Gestion des Soldes**

### 📝 **Créer un Solde (Admin/RH uniquement)**
```http
POST /api/soldes/
Authorization: Bearer <admin_or_rh_token>
Content-Type: application/json

{
    "employe": 18,
    "solde_annuel": 30.0,
    "conges_pris": 5.0,
    "annee_reference": 2026
}
```

**Réponse :**
```json
{
    "id": 1,
    "employe": 18,
    "nom_complet": "Jean Dupont",
    "username": "employe1",
    "service": "IT",
    "solde_annuel": "30.0",
    "conges_pris": "5.0",
    "conges_restant": "25.0",
    "annee_reference": 2026,
    "date_mise_a_jour": "2026-04-01T10:00:00Z",
    "mis_a_jour_par": 1
}
```

### 👁️ **Lister les Soldes**
```http
GET /api/soldes/
Authorization: Bearer <access_token>
```

**Réponse (Employé) :** Uniquement son solde
**Réponse (Admin/RH) :** Tous les soldes

### 🔄 **Mettre à Jour un Solde (Admin/RH uniquement)**
```http
PATCH /api/soldes/{id}/
Authorization: Bearer <admin_or_rh_token>
Content-Type: application/json

{
    "conges_pris": 8.0
}
```

### 🎯 **Actions Spéciales**

#### 👤 **Voir son Propre Solde**
```http
GET /api/soldes/mon_solde/
Authorization: Bearer <access_token>
```

#### 🔄 **Réinitialiser le Solde Annuel (Admin/RH uniquement)**
```http
POST /api/soldes/{id}/reinitialiser/
Authorization: Bearer <admin_or_rh_token>
Content-Type: application/json

{
    "solde_annuel": 40.0
}
```

#### ➕ **Ajouter des Congés Pris (Admin/RH uniquement)**
```http
POST /api/soldes/{id}/ajouter_conges/
Authorization: Bearer <admin_or_rh_token>
Content-Type: application/json

{
    "jours": 2.0
}
```

#### 📊 **Voir les Statistiques (Admin/RH uniquement)**
```http
GET /api/soldes/statistiques/
Authorization: Bearer <admin_or_rh_token>
```

**Réponse :**
```json
{
    "total_employes": 10,
    "total_conges_pris": 45.5,
    "total_conges_restants": 204.5,
    "moyenne_conges_par_employe": 4.55,
    "stats_par_service": [
        {
            "employe__service": "IT",
            "nb_employes": 4,
            "total_pris": 18.0,
            "total_restant": 82.0
        },
        {
            "employe__service": "RH",
            "nb_employes": 2,
            "total_pris": 9.0,
            "total_restant": 41.0
        }
    ]
}
```

---

## 🔒 **Permissions par Rôle**

| Action | Employé | RH | Admin |
|--------|---------|----|-------|
| Créer solde | ❌ | ✅ | ✅ |
| Voir tous les soldes | ❌ | ✅ | ✅ |
| Voir son solde | ✅ | ✅ | ✅ |
| Mettre à jour solde | ❌ | ✅ | ✅ |
| Supprimer solde | ❌ | ✅ | ✅ |
| Réinitialiser solde | ❌ | ✅ | ✅ |
| Ajouter congés pris | ❌ | ✅ | ✅ |
| Voir statistiques | ❌ | ✅ | ✅ |

---

## ⚠️ **Validations Automatiques**

### 🔢 **Validation des Nombres**
- Le solde annuel doit être positif
- Les congés pris ne peuvent pas être négatifs
- Le solde restant est calculé automatiquement

### 🆔 **Validation d'Unicité**
- Un seul solde par employé et par année
- Empêche les doublons automatiquement

### 📅 **Calcul Automatique**
- `conges_restant = solde_annuel - conges_pris`
- Mis à jour automatiquement à chaque modification

---

## 🧪 **Tests du Système**

### 📋 **Tests de Base**
```bash
# Test complet du système
python test_soldes_complete.py
```

### 🎯 **Scénarios de Test Validés**

1. **Admin crée un solde** ✅
2. **RH met à jour un solde** ✅
3. **Employé consulte son solde** ✅
4. **Admin réinitialise un solde** ✅
5. **RH ajoute des congés pris** ✅
6. **Admin voit les statistiques** ✅
7. **Permissions par rôle respectées** ✅

---

## 📊 **Workflow Complet**

```
1. Admin/RH → Crée le solde initial de l'employé
2. Système → Calcule automatiquement le solde restant
3. Employé → Consulte son solde à tout moment
4. RH/Admin → Met à jour le solde si nécessaire
5. Système → Maintient l'historique des mises à jour
6. Admin/RH → Consulte les statistiques globales
```

---

## 🎉 **Avantages du Système**

### ✅ **Fonctionnalités Complètes**
- Gestion complète des soldes de congés
- Calculs automatiques et fiables
- Historique des modifications
- Statistiques détaillées

### 🔒 **Sécurité Robuste**
- Permissions granulaires par rôle
- CRUD réservé à Admin/RH
- Validation des données
- Audit trail complet

### 📱 **Facilité d'Utilisation**
- API RESTful intuitive
- Messages d'erreur clairs
- Interface responsive possible
- Actions spécialisées

### 🔧 **Extensibilité**
- Support multi-années
- Adaptation aux règles métier
- Intégration facile avec les congés
- Évolution possible

---

## 📈 **Intégration avec le Système de Congés**

La table `solde` s'intègre parfaitement avec la table `conges` :

1. **Création de congé** → Mise à jour automatique du solde
2. **Validation de demande** → Vérification du solde disponible
3. **Approbation** → Déduction automatique des jours
4. **Consultation** → Vue unifiée du solde et des congés

**Le système de gestion des soldes est maintenant complet et prêt pour la production !** 🚀

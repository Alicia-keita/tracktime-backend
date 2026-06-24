# 📁 ORGANISATION DU CODE - SYSTÈME DE PAIE

## 🏗️ **Structure des Applications**

### 📋 **Permissions** (`permissions/`)
- **Rôle** : Gestion des demandes de permission
- **Fichiers** :
  - `models.py` : `PermissionRequest`
  - `serializers.py` : `PermissionRequestSerializer`, `PermissionRequestUpdateSerializer`
  - `views.py` : `PermissionRequestViewSet`, permissions `IsEmployeeOrReadOnly`, `IsRHOrAdmin`
  - `urls.py` : Routes `/api/permissions/`

### 💰 **Payrolls** (`payrolls/`) - NOUVELLE APPLICATION
- **Rôle** : Gestion des bulletins de salaire
- **Fichiers** :
  - `models.py` : `Payroll`
  - `serializers.py` : `PayrollSerializer`, `PayrollGenerateSerializer`
  - `views.py` : `PayrollViewSet`, permissions `IsAdminOnly`, `IsRHOrAdmin`
  - `urls.py` : Routes `/api/payrolls/`

### 👥 **Users** (`users/`)
- **Rôle** : Gestion des utilisateurs
- **Fichiers** :
  - `models.py` : `User` (modèle personnalisé)
  - `serializers.py` : `UserSerializer`
  - `views.py` : `UserViewSet`, permission `IsAdminOnly`
  - `urls.py` : Routes `/api/users/`

---

## 🔗 **Dépendances entre Applications**

```
payrolls/ → permissions/ (pour calculer les absences)
payrolls/ → users/ (pour les informations employés)
permissions/ → users/ (pour les employés)
```

---

## 🌐 **Points d'accès API**

### Permissions (demandes de permission)
- `GET /api/permissions/` - Voir les permissions
- `POST /api/permissions/` - Créer une demande (employé uniquement)
- `PATCH /api/permissions/{id}/approve/` - Approuver (RH/Admin)
- `PATCH /api/permissions/{id}/reject/` - Rejeter (RH/Admin)

### Payrolls (bulletins de salaire)
- `GET /api/payrolls/` - Voir les bulletins
- `POST /api/payrolls/generate/` - Générer un bulletin (RH/Admin)
- `DELETE /api/payrolls/{id}/` - Supprimer un bulletin (Admin uniquement)

### Users (utilisateurs)
- `GET /api/users/` - Voir les utilisateurs (Admin uniquement)
- `POST /api/users/` - Créer un utilisateur (Admin uniquement)

---

## 🔐 **Matrice des Permissions**

| Action | Employé | RH | Admin |
|--------|---------|----|-------|
| Créer demande permission | ✅ | ❌ | ❌ |
| Voir ses permissions | ✅ | ✅ | ✅ |
| Approuver permission | ❌ | ✅ | ✅ |
| Générer bulletin | ❌ | ✅ | ✅ |
| Voir ses bulletins | ✅ | ✅ | ✅ |
| Voir tous les bulletins | ❌ | ✅ | ✅ |
| Supprimer bulletin | ❌ | ❌ | ✅ |
| Gérer utilisateurs | ❌ | ❌ | ✅ |

---

## 🎯 **Avantages de cette Organisation**

### 📦 **Séparation des responsabilités**
- Chaque application a un rôle clair et défini
- Pas de mélange de logique métier

### 🔧 **Maintenance facile**
- Modifications des permissions sans toucher aux bulletins
- Évolution indépendante de chaque module

### 🚀 **Extensibilité**
- Ajout facile de nouvelles fonctionnalités
- Intégration possible avec d'autres systèmes

### 🧪 **Tests unitaires**
- Tests par application
- Isolation des fonctionnalités

---

## 📊 **Flux de données**

```
1. Employé → permissions/ → Crée demande
2. RH → permissions/ → Approuve demande
3. RH → payrolls/ → Génère bulletin (utilise les permissions approuvées)
4. Admin → payrolls/ → Supprime bulletin si nécessaire
```

Le code est maintenant **proprement organisé** et **facile à maintenir** ! 🎉

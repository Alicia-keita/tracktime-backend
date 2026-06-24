# 📁 NOUVELLE STRUCTURE - SYSTÈME CORE

## 🏗️ **Organisation par Fichiers Individuels**

### 📦 **Structure du dossier `core/`**

```
core/
├── __init__.py          # Import principal des modules
├── apps.py             # Configuration de l'application
├── urls.py             # Routes principales du système
├── permissions.py      # Module des permissions de demande
├── bulletin.py         # Module des bulletins de salaire
├── user_management.py  # Module de gestion des utilisateurs
├── auth.py             # Module d'authentification JWT
├── tests.py            # Tests du système complet
```

---

## 📋 **Fichiers et Responsabilités**

### 🔐 **`permissions.py`**
- **Modèle** : `PermissionRequest`
- **Serializer** : `PermissionRequestSerializer`, `PermissionRequestUpdateSerializer`
- **ViewSet** : `PermissionRequestViewSet`
- **Permissions** : `IsEmployeeOrReadOnly`, `IsRHOrAdmin`
- **Actions** : `approve`, `reject`, `pending`

### 💰 **`bulletin.py`**
- **Modèle** : `Bulletin` (anciennement `Payroll`)
- **Serializer** : `BulletinSerializer`, `BulletinGenerateSerializer`
- **ViewSet** : `BulletinViewSet`
- **Permissions** : `IsAdminOnly`, `IsRHOrAdmin`
- **Actions** : `generate`

### 👥 **`user_management.py`**
- **Serializer** : `UserSerializer`
- **ViewSet** : `UserViewSet`
- **Permissions** : `IsAdminOnly`
- **Actions** : CRUD complet des utilisateurs

### 🔑 **`auth.py`**
- **Serializer** : `CustomTokenObtainPairSerializer`
- **Vue** : `UserProfileView`
- **Classe** : `AuthSystem`
- **Fonctions** : Login, refresh, profil, permissions

---

## 🌐 **Nouveaux Endpoints**

### Permissions
- `GET /api/permissions/` - Lister les permissions
- `POST /api/permissions/` - Créer une demande
- `PATCH /api/permissions/{id}/approve/` - Approuver
- `PATCH /api/permissions/{id}/reject/` - Rejeter
- `GET /api/permissions/pending/` - Demandes en attente

### Bulletins
- `GET /api/bulletins/` - Lister les bulletins
- `POST /api/bulletins/generate/` - Générer un bulletin
- `DELETE /api/bulletins/{id}/` - Supprimer (admin uniquement)

### Utilisateurs
- `GET /api/users/` - Lister les utilisateurs (admin)
- `POST /api/users/` - Créer un utilisateur (admin)

### Authentification
- `POST /api/login/` - Login JWT
- `POST /api/refresh/` - Rafraîchir token
- `GET /api/profile/` - Profil utilisateur

---

## 🎯 **Avantages de cette Structure**

### ✅ **Pas de conflits**
- Chaque module dans son propre fichier
- Imports clairs et définis
- Pas de mélange de code

### 🔧 **Maintenance facile**
- Trouver rapidement le code à modifier
- Modifications isolées
- Tests par module

### 📦 **Réutilisabilité**
- Modules indépendants
- Facile à déplacer dans d'autres projets
- Import sélectif possible

### 🧪 **Tests modulaires**
- Tests par fichier
- Isolation des fonctionnalités
- Débogage simplifié

---

## 🔄 **Comment utiliser**

```python
# Importer tous les modules
from core import PermissionRequest, Bulletin, UserManagement, AuthSystem

# Importer un module spécifique
from core.permissions import PermissionRequestViewSet
from core.bulletin import BulletinViewSet
from core.auth import AuthSystem
```

---

## 📊 **Flux de travail**

```
1. Utilisateur → auth.py → Login JWT
2. Employé → permissions.py → Crée demande
3. RH → permissions.py → Approuve demande
4. RH → bulletin.py → Génère bulletin
5. Admin → bulletin.py → Supprime bulletin si besoin
```

Le code est maintenant **parfaitement organisé** avec **zéro conflit** ! 🚀

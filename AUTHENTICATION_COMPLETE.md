# 🔐 **SYSTÈME D'AUTHENTIFICATION COMPLET**

## 📋 **Table User (Structure Respectée)**

### 🏗️ **Modèle User dans `users/models.py`**
```python
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('rh', 'RH'),
        ('employe', 'Employé'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    service = models.CharField(max_length=100)
    badge_rfid = models.CharField(max_length=100, unique=True, null=True, blank=True)
    face_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
```

### 📊 **Champs de la Table**
| Champ | Type | Description |
|-------|------|-------------|
| `id` | Integer | Clé primaire |
| `username` | VARCHAR(150) | Nom d'utilisateur unique |
| `email` | VARCHAR(254) | Email unique |
| `first_name` | VARCHAR(150) | Prénom |
| `last_name` | VARCHAR(150) | Nom |
| `role` | VARCHAR(20) | Rôle (admin/rh/employe) |
| `service` | VARCHAR(100) | Service/Département |
| `badge_rfid` | VARCHAR(100) | Badge RFID (unique) |
| `face_id` | VARCHAR(100) | Face ID (unique) |
| `password` | VARCHAR(128) | Mot de passe hashé |
| `is_active` | Boolean | Compte actif |
| `is_staff` | Boolean | Accès admin |
| `is_superuser` | Boolean | Super admin |
| `date_joined` | DateTime | Date d'inscription |
| `last_login` | DateTime | Dernière connexion |

---

## 🌐 **API d'Authentification**

### 📝 **Inscription**
```http
POST /api/auth/register/
Content-Type: application/json

{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "Password123!",
    "password_confirm": "Password123!",
    "first_name": "John",
    "last_name": "Doe",
    "role": "employe",
    "service": "IT",
    "badge_rfid": "RFID123456",
    "face_id": "FACE789012"
}
```

**Réponse :**
```json
{
    "message": "Utilisateur créé avec succès",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "employe",
        "service": "IT",
        "badge_rfid": "RFID123456",
        "face_id": "FACE789012"
    }
}
```

### 🔑 **Connexion**
```http
POST /api/auth/login/
Content-Type: application/json

{
    "username": "johndoe",
    "password": "Password123!"
}
```

**Réponse :**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "employe",
        "service": "IT",
        "is_staff": false,
        "is_superuser": false,
        "date_joined": "2026-04-01T12:00:00Z",
        "last_login": "2026-04-01T14:30:00Z"
    }
}
```

### 👤 **Profil Utilisateur**
```http
GET /api/auth/profile/
Authorization: Bearer <access_token>
```

**Réponse :**
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "employe",
    "service": "IT",
    "badge_rfid": "RFID123456",
    "face_id": "FACE789012",
    "is_staff": false,
    "is_superuser": false,
    "date_joined": "2026-04-01T12:00:00Z",
    "last_login": "2026-04-01T14:30:00Z"
}
```

### 🔒 **Permissions Utilisateur**
```http
GET /api/auth/permissions/
Authorization: Bearer <access_token>
```

**Réponse :**
```json
{
    "can_create_permission": true,
    "can_approve_permission": false,
    "can_generate_bulletin": false,
    "can_delete_bulletin": false,
    "can_manage_users": false,
    "can_view_all_permissions": false,
    "can_view_all_bulletins": false,
    "role": "employe",
    "is_admin": false
}
```

---

## 🔄 **Opérations de Mot de Passe**

### 🔐 **Changer le Mot de Passe**
```http
POST /api/auth/password/change/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "old_password": "Password123!",
    "new_password": "NewPassword456!",
    "new_password_confirm": "NewPassword456!"
}
```

### 📧 **Réinitialiser le Mot de Passe**
```http
POST /api/auth/password/reset/
Content-Type: application/json

{
    "email": "john@example.com"
}
```

---

## 🔄 **Gestion des Tokens**

### 🔄 **Rafraîchir le Token**
```http
POST /api/auth/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Réponse :**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 🚪 **Déconnexion**
```http
POST /api/auth/logout/
Authorization: Bearer <access_token>
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

---

## 🎯 **Matrix des Permissions par Rôle**

| Permission | Employé | RH | Admin |
|------------|----------|----|-------|
| `can_create_permission` | ✅ | ✅ | ✅ |
| `can_approve_permission` | ❌ | ✅ | ✅ |
| `can_generate_bulletin` | ❌ | ✅ | ✅ |
| `can_delete_bulletin` | ❌ | ❌ | ✅ |
| `can_manage_users` | ❌ | ❌ | ✅ |
| `can_view_all_permissions` | ❌ | ✅ | ✅ |
| `can_view_all_bulletins` | ❌ | ✅ | ✅ |

---

## 🧪 **Tests Complets**

### 📋 **Tests d'Authentification**
```bash
python test_authentication_complete.py
```

**Résultats attendus :**
- ✅ Inscription valide
- ✅ Connexion réussie
- ✅ Gestion du profil
- ✅ Changement de mot de passe
- ✅ Vérification des permissions
- ✅ Déconnexion
- ✅ Rafraîchissement du token

---

## 🔧 **Configuration Django**

### 📦 **Applications Requises**
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'rest_framework',
    'rest_framework_simplejwt',
    'core',
    'users',
]
```

### 🔐 **Configuration JWT**
```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

---

## 🎉 **Avantages du Système**

### ✅ **Sécurité**
- Tokens JWT avec expiration
- Mot de passe hashé
- Permissions par rôle
- Validation des entrées

### 🔧 **Facilité d'Utilisation**
- API RESTful complète
- Messages d'erreur clairs
- Documentation détaillée
- Tests automatisés

### 📱 **Flexibilité**
- Support multi-rôles
- Authentification par badge/face_id
- Personnalisation des permissions
- Extensibilité facile

**Le système d'authentification est maintenant complet et prêt pour la production !** 🚀

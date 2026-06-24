
# PLAN DE MIGRATION VERS POSTGRESQL

## ÉTAPES:

### 1. Créer l'utilisateur PostgreSQL
```sql
-- Exécuter dans pgAdmin en tant que postgres
CREATE USER pointage_user WITH PASSWORD 'pointage123';
GRANT ALL PRIVILEGES ON DATABASE pointage TO pointage_user;
```

### 2. Créer les tables
```sql
-- Exécuter create_postgresql_tables.sql dans la base pointage
```

### 3. Mettre à jour settings.py
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pointage',
        'USER': 'pointage_user',
        'PASSWORD': 'pointage123',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 4. Tester la connexion
```bash
python manage.py migrate
python manage.py runserver
```

### 5. Importer les données (optionnel)
```bash
python migrate_data.py
```

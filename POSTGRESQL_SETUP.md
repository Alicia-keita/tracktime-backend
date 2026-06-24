
# GUIDE D'INSTALLATION POSTGRESQL

## 1. Installation

### Windows
1. Télécharger PostgreSQL depuis : https://www.postgresql.org/download/windows/
2. Exécuter l'installateur
3. Noter le mot de passe de l'utilisateur 'postgres'
4. Cocher l'installation de pgAdmin

### Linux (Ubuntu/Debian)
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

### macOS
brew install postgresql
brew services start postgresql

## 2. Configuration

### Changer le mot de passe postgres
sudo -u postgres psql
\password postgres
# Entrer le nouveau mot de passe deux fois

### Créer la base de données
CREATE DATABASE pointage;

### Créer un utilisateur dédié (optionnel)
CREATE USER pointage_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE pointage TO pointage_user;

## 3. Configuration Django

Mettre à jour settings.py avec vos identifiants :

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'pointage',
        'USER': 'postgres',  # ou 'pointage_user'
        'PASSWORD': 'votre_mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

## 4. Migration

python manage.py makemigrations
python manage.py migrate

## 5. Test de connexion

python manage.py dbshell
# Si ça fonctionne, PostgreSQL est bien configuré

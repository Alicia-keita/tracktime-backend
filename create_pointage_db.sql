
-- Commands SQL pour créer la base de données pointage
-- Exécuter ces commandes dans pgAdmin ou psql

-- 1. Créer la base de données
CREATE DATABASE pointage;

-- 2. Vérifier que la base est créée
\l

-- 3. Se connecter à la nouvelle base
\c pointage

-- 4. Vérifier que nous sommes dans la bonne base
SELECT current_database();

-- 5. (Optionnel) Créer un utilisateur dédié
CREATE USER pointage_user WITH PASSWORD 'pointage123';
GRANT ALL PRIVILEGES ON DATABASE pointage TO pointage_user;

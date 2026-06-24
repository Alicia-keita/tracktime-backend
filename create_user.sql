
-- Créer un utilisateur dédié pour le projet
CREATE USER pointage_user WITH PASSWORD 'pointage123';

-- Donner les permissions sur la base de données
GRANT ALL PRIVILEGES ON DATABASE pointage TO pointage_user;

-- Donner les permissions sur le schéma public
GRANT ALL ON SCHEMA public TO pointage_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO pointage_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO pointage_user;

-- Donner les permissions par défaut pour les futures tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO pointage_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO pointage_user;

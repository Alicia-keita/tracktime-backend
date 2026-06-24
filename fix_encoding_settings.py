# Script pour modifier la configuration d'encodage PostgreSQL
# À exécuter dans pgAdmin Query Tool

-- Modifier l'encodage du client PostgreSQL
SET client_encoding TO 'UTF8';

-- Vérifier l'encodage actuel
SHOW client_encoding;

-- Tester la connexion
SELECT 'Encodage UTF8 configuré' AS message, version() AS postgres_version;

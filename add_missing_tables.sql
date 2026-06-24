-- Ajouter les tables manquantes
-- Exécutez ce code dans pgAdmin Query Tool

-- Table core_employe (pour la gestion des employés)
CREATE TABLE IF NOT EXISTS core_employe (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    matricule VARCHAR(20) NOT NULL UNIQUE,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    telephone VARCHAR(20),
    date_embauche DATE NOT NULL,
    salaire_base DECIMAL(10,2) NOT NULL,
    departement VARCHAR(50),
    poste VARCHAR(50),
    statut VARCHAR(20) NOT NULL,
    actif BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Table core_pointage (pour les pointages)
CREATE TABLE IF NOT EXISTS core_pointage (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    employe_id BIGINT NOT NULL,
    date_pointage DATE NOT NULL,
    heure_entree TIMESTAMP,
    heure_sortie TIMESTAMP,
    type_pointage VARCHAR(20) NOT NULL,
    statut VARCHAR(20) NOT NULL,
    retard_minutes INTEGER DEFAULT 0,
    commentaire TEXT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Table core_soldeconge (solde de congés spécifique)
CREATE TABLE IF NOT EXISTS core_soldeconge (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    employe_id BIGINT NOT NULL,
    annee INTEGER NOT NULL,
    solde_annuel DECIMAL(5,2) NOT NULL,
    solde_pris DECIMAL(5,2) NOT NULL,
    solde_restant DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Tables système Django manquantes
CREATE TABLE IF NOT EXISTS django_content_type (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS auth_permission (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL,
    content_type_id BIGINT NOT NULL,
    codename VARCHAR(100) NOT NULL
);

-- Créer l'utilisateur admin
INSERT INTO users_user (
    password,
    is_superuser,
    username,
    first_name,
    last_name,
    email,
    is_staff,
    is_active,
    date_joined,
    role,
    service
) VALUES (
    'pbkdf2_sha256$600000$admin$hashed_admin_password_2024',
    true,
    'admin',
    'Admin',
    'User',
    'admin@example.com',
    true,
    true,
    NOW(),
    'admin',
    'Administration'
) ON CONFLICT (username) DO NOTHING;

-- Message de confirmation
SELECT 'Tables manquantes créées et admin ajouté avec succès!' AS message;

-- Vérifier toutes les tables
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

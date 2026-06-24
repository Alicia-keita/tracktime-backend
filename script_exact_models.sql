-- Script SQL EXACT basé sur vos modèles Django
-- À exécuter dans la base de données "Pointage"

-- Table users_user (modèle User dans users/models.py)
CREATE TABLE users_user (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP,
    is_superuser BOOLEAN NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    date_joined TIMESTAMP NOT NULL,
    role VARCHAR(20) NOT NULL,
    service VARCHAR(100) NOT NULL,
    badge_rfid VARCHAR(100) UNIQUE,
    face_id VARCHAR(100) UNIQUE
);

-- Table core_conge (modèle Conge dans core/conges.py)
CREATE TABLE core_conge (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    employe_id BIGINT NOT NULL,
    type_conge VARCHAR(20) NOT NULL,
    date_debut TIMESTAMP NOT NULL,
    date_fin TIMESTAMP NOT NULL,
    duree_jours INTEGER NOT NULL,
    statut VARCHAR(20) NOT NULL DEFAULT 'en_attente',
    date_demande TIMESTAMP NOT NULL,
    date_traitement TIMESTAMP,
    valide_par_id BIGINT,
    motif TEXT NOT NULL,
    commentaire_rh TEXT NOT NULL,
    document_attache VARCHAR(100),
    solde_avant DECIMAL(4,1) NOT NULL DEFAULT 0.0,
    solde_apres DECIMAL(4,1) NOT NULL DEFAULT 0.0,
    FOREIGN KEY (employe_id) REFERENCES users_user(id),
    FOREIGN KEY (valide_par_id) REFERENCES users_user(id)
);

-- Table core_solde (modèle Solde dans core/solde.py)
CREATE TABLE core_solde (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    employe_id BIGINT NOT NULL,
    solde_annuel DECIMAL(4,1) NOT NULL DEFAULT 25.0,
    conges_pris DECIMAL(4,1) NOT NULL DEFAULT 0.0,
    conges_restant DECIMAL(4,1) NOT NULL DEFAULT 25.0,
    annee_reference INTEGER NOT NULL DEFAULT 2026,
    date_mise_a_jour TIMESTAMP NOT NULL,
    mis_a_jour_par_id BIGINT,
    FOREIGN KEY (employe_id) REFERENCES users_user(id),
    FOREIGN KEY (mis_a_jour_par_id) REFERENCES users_user(id),
    UNIQUE (employe_id, annee_reference)
);

-- Table core_permissionrequest (modèle PermissionRequest dans core/permissions.py)
CREATE TABLE core_permissionrequest (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    employee_id BIGINT NOT NULL,
    type_permission VARCHAR(20) NOT NULL,
    date_sortie TIMESTAMP NOT NULL,
    date_retour TIMESTAMP NOT NULL,
    motif TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    date_demande TIMESTAMP NOT NULL,
    date_traitement TIMESTAMP,
    commentaire_rh TEXT NOT NULL,
    rh_traitant_id BIGINT,
    FOREIGN KEY (employee_id) REFERENCES users_user(id),
    FOREIGN KEY (rh_traitant_id) REFERENCES users_user(id)
);

-- Table core_bulletin (modèle Bulletin dans core/bulletin.py)
CREATE TABLE core_bulletin (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    heures_travaillees DECIMAL NOT NULL,
    heures_supplementaires DECIMAL NOT NULL,
    nb_absences INTEGER NOT NULL,
    nb_retards INTEGER NOT NULL,
    salaire_base DECIMAL NOT NULL,
    prime_heures_sup DECIMAL NOT NULL,
    deduction_absences DECIMAL NOT NULL,
    salaire_brut DECIMAL NOT NULL,
    cnss DECIMAL NOT NULL,
    impot DECIMAL NOT NULL,
    autres_deductions DECIMAL NOT NULL,
    salaire_net DECIMAL NOT NULL,
    date_generation TIMESTAMP NOT NULL,
    employee_id BIGINT NOT NULL,
    genere_par_id BIGINT,
    FOREIGN KEY (employee_id) REFERENCES users_user(id),
    FOREIGN KEY (genere_par_id) REFERENCES users_user(id)
);

-- Table core_rapport (modèle Rapport dans core/rapport.py)
CREATE TABLE core_rapport (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    titre VARCHAR(200) NOT NULL,
    type_rapport VARCHAR(20) NOT NULL,
    periode_rapport VARCHAR(20) NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    fichier_pdf VARCHAR(255),
    date_generation TIMESTAMP NOT NULL,
    genere_par_id BIGINT NOT NULL,
    FOREIGN KEY (genere_par_id) REFERENCES users_user(id)
);

-- Tables système Django
CREATE TABLE django_migrations (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP NOT NULL
);

CREATE TABLE django_content_type (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL
);

CREATE TABLE auth_permission (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL,
    content_type_id BIGINT NOT NULL,
    codename VARCHAR(100) NOT NULL,
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id)
);

-- Tables JWT token blacklist
CREATE TABLE outstanding_token (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    token TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    user_id BIGINT,
    jti VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE blacklisted_token (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    token_id BIGINT NOT NULL UNIQUE,
    blacklisted_at TIMESTAMP NOT NULL,
    FOREIGN KEY (token_id) REFERENCES outstanding_token(id)
);

-- Index pour optimiser les performances
CREATE INDEX idx_core_conge_employe ON core_conge(employe_id);
CREATE INDEX idx_core_conge_statut ON core_conge(statut);
CREATE INDEX idx_core_solde_employe ON core_solde(employe_id);
CREATE INDEX idx_core_permissionrequest_employee ON core_permissionrequest(employee_id);
CREATE INDEX idx_core_bulletin_employee ON core_bulletin(employee_id);
CREATE INDEX idx_core_rapport_genere_par ON core_rapport(genere_par_id);
CREATE INDEX idx_users_user_username ON users_user(username);
CREATE INDEX idx_users_user_role ON users_user(role);

SELECT 'Toutes les tables Django ont été créées avec succès!' AS message;

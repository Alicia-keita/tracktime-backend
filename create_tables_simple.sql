-- Script SQL simplifie pour creer les tables essentielles
-- Copiez ce code et executez-le dans pgAdmin

-- Table des utilisateurs Django
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
    telephone VARCHAR(20),
    adresse TEXT,
    date_embauche DATE,
    salaire_base DECIMAL(10,2),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Table des employes
CREATE TABLE core_employe (
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

-- Table des pointages
CREATE TABLE core_pointage (
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
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (employe_id) REFERENCES core_employe(id)
);

-- Table des conges
CREATE TABLE core_conge (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    employe_id BIGINT NOT NULL,
    type_conge VARCHAR(20) NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    duree_jours INTEGER NOT NULL,
    statut VARCHAR(20) NOT NULL,
    date_demande DATE NOT NULL,
    date_traitement DATE,
    motif TEXT NOT NULL,
    commentaire_rh TEXT,
    solde_avant DECIMAL(5,2) NOT NULL,
    solde_apres DECIMAL(5,2) NOT NULL,
    valide_par_id BIGINT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (employe_id) REFERENCES core_employe(id),
    FOREIGN KEY (valide_par_id) REFERENCES users_user(id)
);

-- Table des soldes de conges
CREATE TABLE core_soldeconge (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    employe_id BIGINT NOT NULL,
    annee INTEGER NOT NULL,
    solde_annuel DECIMAL(5,2) NOT NULL,
    solde_pris DECIMAL(5,2) NOT NULL,
    solde_restant DECIMAL(5,2) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (employe_id) REFERENCES core_employe(id)
);

-- Table des bulletins de paie
CREATE TABLE core_bulletin (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    employe_id BIGINT NOT NULL,
    periode_debut DATE NOT NULL,
    periode_fin DATE NOT NULL,
    heures_travaillees DECIMAL(8,2) NOT NULL,
    heures_supplementaires DECIMAL(8,2) NOT NULL,
    nb_absences INTEGER NOT NULL,
    nb_retards INTEGER NOT NULL,
    salaire_base DECIMAL(10,2) NOT NULL,
    prime_heures_sup DECIMAL(10,2) NOT NULL,
    deduction_absences DECIMAL(10,2) NOT NULL,
    salaire_brut DECIMAL(10,2) NOT NULL,
    cnss DECIMAL(10,2) NOT NULL,
    impot DECIMAL(10,2) NOT NULL,
    autres_deductions DECIMAL(10,2) NOT NULL,
    salaire_net DECIMAL(10,2) NOT NULL,
    date_generation TIMESTAMP NOT NULL,
    genere_par_id BIGINT,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (employe_id) REFERENCES core_employe(id),
    FOREIGN KEY (genere_par_id) REFERENCES users_user(id)
);

-- Table des rapports
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
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    FOREIGN KEY (genere_par_id) REFERENCES users_user(id)
);

-- Tables Django systeme
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

-- Index pour optimiser les performances
CREATE INDEX idx_core_pointage_employe ON core_pointage(employe_id);
CREATE INDEX idx_core_pointage_date ON core_pointage(date_pointage);
CREATE INDEX idx_core_conge_employe ON core_conge(employe_id);
CREATE INDEX idx_core_soldeconge_employe ON core_soldeconge(employe_id);
CREATE INDEX idx_core_bulletin_employe ON core_bulletin(employe_id);
CREATE INDEX idx_users_user_username ON users_user(username);
CREATE INDEX idx_core_employe_matricule ON core_employe(matricule);

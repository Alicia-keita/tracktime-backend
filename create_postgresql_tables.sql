-- Création des tables pour PostgreSQL

-- Table: auth_group
CREATE TABLE auth_group (
    id INTEGER PRIMARY KEY,
    name VARCHAR(150) NOT NULL);

-- Table: auth_group_permissions
CREATE TABLE auth_group_permissions (
    id INTEGER PRIMARY KEY,
    group_id INTEGER NOT NULL,
    permission_id INTEGER NOT NULL,
    -- Foreign Keys
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id),
    FOREIGN KEY (group_id) REFERENCES auth_group(id)
);

-- Table: auth_permission
CREATE TABLE auth_permission (
    id INTEGER PRIMARY KEY,
    content_type_id INTEGER NOT NULL,
    codename VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    -- Foreign Keys
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id)
);

-- Table: core_bulletin
CREATE TABLE core_bulletin (
    id INTEGER PRIMARY KEY,
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
    -- Foreign Keys
    FOREIGN KEY (genere_par_id) REFERENCES users_user(id),
    FOREIGN KEY (employee_id) REFERENCES users_user(id)
);

-- Table: core_conge
CREATE TABLE core_conge (
    id INTEGER PRIMARY KEY,
    type_conge VARCHAR(20) NOT NULL,
    date_debut TIMESTAMP NOT NULL,
    date_fin TIMESTAMP NOT NULL,
    duree_jours INTEGER NOT NULL,
    statut VARCHAR(20) NOT NULL,
    date_demande TIMESTAMP NOT NULL,
    date_traitement TIMESTAMP,
    motif TEXT NOT NULL,
    commentaire_rh TEXT NOT NULL,
    document_attache VARCHAR(100),
    solde_avant DECIMAL NOT NULL,
    solde_apres DECIMAL NOT NULL,
    employe_id BIGINT NOT NULL,
    valide_par_id BIGINT,
    -- Foreign Keys
    FOREIGN KEY (valide_par_id) REFERENCES users_user(id),
    FOREIGN KEY (employe_id) REFERENCES users_user(id)
);

-- Table: core_permissionrequest
CREATE TABLE core_permissionrequest (
    id INTEGER PRIMARY KEY,
    type_permission VARCHAR(20) NOT NULL,
    date_sortie TIMESTAMP NOT NULL,
    date_retour TIMESTAMP NOT NULL,
    motif TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    date_demande TIMESTAMP NOT NULL,
    date_traitement TIMESTAMP,
    commentaire_rh TEXT NOT NULL,
    employee_id BIGINT NOT NULL,
    rh_traitant_id BIGINT,
    -- Foreign Keys
    FOREIGN KEY (rh_traitant_id) REFERENCES users_user(id),
    FOREIGN KEY (employee_id) REFERENCES users_user(id)
);

-- Table: core_rapport
CREATE TABLE core_rapport (
    id INTEGER PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    type_rapport VARCHAR(20) NOT NULL,
    periode_rapport VARCHAR(20) NOT NULL,
    date_debut DATE NOT NULL,
    date_fin DATE NOT NULL,
    date_generation TIMESTAMP NOT NULL,
    date_modification TIMESTAMP NOT NULL,
    description TEXT NOT NULL,
    contenu TEXT NOT NULL,
    fichier_attache VARCHAR(100),
    statut VARCHAR(20) NOT NULL,
    filtres TEXT NOT NULL,
    parametres TEXT NOT NULL,
    total_enregistrements INTEGER NOT NULL,
    total_heures DECIMAL NOT NULL,
    pourcentage_presence DECIMAL,
    auteur_id BIGINT NOT NULL,
    valide_par_id BIGINT,
    -- Foreign Keys
    FOREIGN KEY (valide_par_id) REFERENCES users_user(id),
    FOREIGN KEY (auteur_id) REFERENCES users_user(id)
);

-- Table: core_rapport_destinataires
CREATE TABLE core_rapport_destinataires (
    id INTEGER PRIMARY KEY,
    rapport_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users_user(id),
    FOREIGN KEY (rapport_id) REFERENCES core_rapport(id)
);

-- Table: core_solde
CREATE TABLE core_solde (
    id INTEGER PRIMARY KEY,
    solde_annuel DECIMAL NOT NULL,
    conges_pris DECIMAL NOT NULL,
    conges_restant DECIMAL NOT NULL,
    annee_reference INTEGER NOT NULL,
    date_mise_a_jour TIMESTAMP NOT NULL,
    employe_id BIGINT NOT NULL,
    mis_a_jour_par_id BIGINT,
    -- Foreign Keys
    FOREIGN KEY (mis_a_jour_par_id) REFERENCES users_user(id),
    FOREIGN KEY (employe_id) REFERENCES users_user(id)
);

-- Table: django_admin_log
CREATE TABLE django_admin_log (
    id INTEGER PRIMARY KEY,
    object_id TEXT,
    object_repr VARCHAR(200) NOT NULL,
    action_flag TEXT NOT NULL,
    change_message TEXT NOT NULL,
    content_type_id INTEGER,
    user_id BIGINT NOT NULL,
    action_time TIMESTAMP NOT NULL,
    -- Foreign Keys
    FOREIGN KEY (user_id) REFERENCES users_user(id),
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id)
);

-- Table: django_content_type
CREATE TABLE django_content_type (
    id INTEGER PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL);

-- Table: django_migrations
CREATE TABLE django_migrations (
    id INTEGER PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied TIMESTAMP NOT NULL);

-- Table: django_session
CREATE TABLE django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP NOT NULL);

-- Table: payrolls_payroll
CREATE TABLE payrolls_payroll (
    id INTEGER PRIMARY KEY,
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
    -- Foreign Keys
    FOREIGN KEY (genere_par_id) REFERENCES users_user(id),
    FOREIGN KEY (employee_id) REFERENCES users_user(id)
);

-- Table: permissions_payroll
CREATE TABLE permissions_payroll (
    id INTEGER PRIMARY KEY,
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
    -- Foreign Keys
    FOREIGN KEY (genere_par_id) REFERENCES users_user(id),
    FOREIGN KEY (employee_id) REFERENCES users_user(id)
);

-- Table: permissions_permissionrequest
CREATE TABLE permissions_permissionrequest (
    id INTEGER PRIMARY KEY,
    type_permission VARCHAR(20) NOT NULL,
    date_sortie TIMESTAMP NOT NULL,
    date_retour TIMESTAMP NOT NULL,
    motif TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    date_demande TIMESTAMP NOT NULL,
    date_traitement TIMESTAMP,
    commentaire_rh TEXT NOT NULL,
    employee_id BIGINT NOT NULL,
    rh_traitant_id BIGINT,
    -- Foreign Keys
    FOREIGN KEY (rh_traitant_id) REFERENCES users_user(id),
    FOREIGN KEY (employee_id) REFERENCES users_user(id)
);

-- Table: users_user
CREATE TABLE users_user (
    id INTEGER PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login TIMESTAMP,
    is_superuser TEXT NOT NULL,
    username VARCHAR(150) NOT NULL,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff TEXT NOT NULL,
    is_active TEXT NOT NULL,
    date_joined TIMESTAMP NOT NULL,
    role VARCHAR(20) NOT NULL,
    service VARCHAR(100) NOT NULL,
    badge_rfid VARCHAR(100),
    face_id VARCHAR(100));

-- Table: users_user_groups
CREATE TABLE users_user_groups (
    id INTEGER PRIMARY KEY,
    user_id BIGINT NOT NULL,
    group_id INTEGER NOT NULL,
    -- Foreign Keys
    FOREIGN KEY (group_id) REFERENCES auth_group(id),
    FOREIGN KEY (user_id) REFERENCES users_user(id)
);

-- Table: users_user_user_permissions
CREATE TABLE users_user_user_permissions (
    id INTEGER PRIMARY KEY,
    user_id BIGINT NOT NULL,
    permission_id INTEGER NOT NULL,
    -- Foreign Keys
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id),
    FOREIGN KEY (user_id) REFERENCES users_user(id)
);

-- Index pour auth_group

-- Index pour auth_group_permissions
CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON auth_group_permissions (permission_id);
CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON auth_group_permissions (group_id);
CREATE UNIQUE INDEX auth_group_permissions_group_id_permission_id_0cd325b0_uniq ON auth_group_permissions (group_id, permission_id);

-- Index pour auth_permission
CREATE INDEX auth_permission_content_type_id_2f476e4b ON auth_permission (content_type_id);
CREATE UNIQUE INDEX auth_permission_content_type_id_codename_01ab375a_uniq ON auth_permission (content_type_id, codename);

-- Index pour core_bulletin
CREATE INDEX core_bulletin_genere_par_id_9d0ec44c ON core_bulletin (genere_par_id);
CREATE INDEX core_bulletin_employee_id_07221626 ON core_bulletin (employee_id);
CREATE UNIQUE INDEX core_bulletin_employee_id_periode_debut_periode_fin_70ba5414_uniq ON core_bulletin (employee_id, periode_debut, periode_fin);

-- Index pour core_conge
CREATE INDEX core_conge_valide_par_id_201fddee ON core_conge (valide_par_id);
CREATE INDEX core_conge_employe_id_5d54b84e ON core_conge (employe_id);

-- Index pour core_permissionrequest
CREATE INDEX core_permissionrequest_rh_traitant_id_bccc951c ON core_permissionrequest (rh_traitant_id);
CREATE INDEX core_permissionrequest_employee_id_cc5b3647 ON core_permissionrequest (employee_id);

-- Index pour core_rapport
CREATE INDEX core_rappor_date_ge_162c13_idx ON core_rapport (date_generation);
CREATE INDEX core_rappor_auteur__95d81d_idx ON core_rapport (auteur_id, statut);
CREATE INDEX core_rappor_type_ra_a24f38_idx ON core_rapport (type_rapport, date_debut);
CREATE INDEX core_rapport_valide_par_id_3dd12c86 ON core_rapport (valide_par_id);
CREATE INDEX core_rapport_auteur_id_7e9ee422 ON core_rapport (auteur_id);

-- Index pour core_rapport_destinataires
CREATE INDEX core_rapport_destinataires_user_id_9690ec4a ON core_rapport_destinataires (user_id);
CREATE INDEX core_rapport_destinataires_rapport_id_9dc1cc1e ON core_rapport_destinataires (rapport_id);
CREATE UNIQUE INDEX core_rapport_destinataires_rapport_id_user_id_9170dafc_uniq ON core_rapport_destinataires (rapport_id, user_id);

-- Index pour core_solde
CREATE INDEX core_solde_mis_a_jour_par_id_8b6301d5 ON core_solde (mis_a_jour_par_id);
CREATE UNIQUE INDEX core_solde_employe_id_annee_reference_fc893d04_uniq ON core_solde (employe_id, annee_reference);

-- Index pour django_admin_log
CREATE INDEX django_admin_log_user_id_c564eba6 ON django_admin_log (user_id);
CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON django_admin_log (content_type_id);

-- Index pour django_content_type
CREATE UNIQUE INDEX django_content_type_app_label_model_76bd3d3b_uniq ON django_content_type (app_label, model);

-- Index pour django_session
CREATE INDEX django_session_expire_date_a5c62663 ON django_session (expire_date);

-- Index pour payrolls_payroll
CREATE INDEX payrolls_payroll_genere_par_id_1241b3e2 ON payrolls_payroll (genere_par_id);
CREATE INDEX payrolls_payroll_employee_id_f921e184 ON payrolls_payroll (employee_id);
CREATE UNIQUE INDEX payrolls_payroll_employee_id_periode_debut_periode_fin_13e3a7cf_uniq ON payrolls_payroll (employee_id, periode_debut, periode_fin);

-- Index pour permissions_payroll
CREATE INDEX permissions_payroll_genere_par_id_f96c1ba6 ON permissions_payroll (genere_par_id);
CREATE INDEX permissions_payroll_employee_id_67301275 ON permissions_payroll (employee_id);
CREATE UNIQUE INDEX permissions_payroll_employee_id_periode_debut_periode_fin_55f0857b_uniq ON permissions_payroll (employee_id, periode_debut, periode_fin);

-- Index pour permissions_permissionrequest
CREATE INDEX permissions_permissionrequest_rh_traitant_id_c848a92e ON permissions_permissionrequest (rh_traitant_id);
CREATE INDEX permissions_permissionrequest_employee_id_a1fe85c7 ON permissions_permissionrequest (employee_id);

-- Index pour users_user

-- Index pour users_user_groups
CREATE INDEX users_user_groups_group_id_9afc8d0e ON users_user_groups (group_id);
CREATE INDEX users_user_groups_user_id_5f6f5a90 ON users_user_groups (user_id);
CREATE UNIQUE INDEX users_user_groups_user_id_group_id_b88eab82_uniq ON users_user_groups (user_id, group_id);

-- Index pour users_user_user_permissions
CREATE INDEX users_user_user_permissions_permission_id_0b93982e ON users_user_user_permissions (permission_id);
CREATE INDEX users_user_user_permissions_user_id_20aca447 ON users_user_user_permissions (user_id);
CREATE UNIQUE INDEX users_user_user_permissions_user_id_permission_id_43338c45_uniq ON users_user_user_permissions (user_id, permission_id);


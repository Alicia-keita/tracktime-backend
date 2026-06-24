-- Vérification complète de la base de données PostgreSQL
-- Exécutez ce code dans pgAdmin Query Tool

-- 1. Vérifier la connexion et la version
SELECT 
    'Connexion réussie!' AS status,
    version() AS postgres_version,
    current_database() AS database_name,
    current_user AS connected_user;

-- 2. Lister toutes les tables avec leurs colonnes
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'public' 
ORDER BY table_name, ordinal_position;

-- 3. Vérifier les tables créées
SELECT 
    table_name,
    COUNT(*) as column_count
FROM information_schema.columns 
WHERE table_schema = 'public' 
GROUP BY table_name 
ORDER BY table_name;

-- 4. Vérifier si l'utilisateur admin existe
SELECT 
    id,
    username,
    email,
    role,
    is_superuser,
    is_staff,
    date_joined
FROM users_user 
WHERE username = 'admin';

-- 5. Compter les enregistrements dans chaque table
SELECT 
    'users_user' as table_name, 
    COUNT(*) as record_count 
FROM users_user
UNION ALL
SELECT 
    'core_conge' as table_name, 
    COUNT(*) as record_count 
FROM core_conge
UNION ALL
SELECT 
    'core_solde' as table_name, 
    COUNT(*) as record_count 
FROM core_solde
UNION ALL
SELECT 
    'core_employe' as table_name, 
    COUNT(*) as record_count 
FROM core_employe
UNION ALL
SELECT 
    'core_pointage' as table_name, 
    COUNT(*) as record_count 
FROM core_pointage;

-- 6. Test d'insertion/lecture
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
    'test_password_hash',
    false,
    'test_verification',
    'Test',
    'Verification',
    'test@verify.com',
    false,
    true,
    NOW(),
    'employe',
    'Test Service'
);

-- Vérifier l'insertion
SELECT 'Test insertion réussie!' AS result, username, email 
FROM users_user 
WHERE username = 'test_verification';

-- Nettoyer le test
DELETE FROM users_user WHERE username = 'test_verification';

SELECT 'Test complet terminé - PostgreSQL fonctionne parfaitement!' AS final_message;

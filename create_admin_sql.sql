-- Créer un utilisateur admin directement dans PostgreSQL
-- Exécutez ce code dans pgAdmin Query Tool

-- Insérer un utilisateur admin dans la table users_user
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
    service,
    badge_rfid,
    face_id
) VALUES (
    'pbkdf2_sha256$600000$admin123$hashed_password_here', -- sera hashé automatiquement
    true,
    'admin',
    'Admin',
    'User',
    'admin@example.com',
    true,
    true,
    NOW(),
    'admin',
    'Administration',
    NULL,
    NULL
);

-- Message de confirmation
SELECT 'Utilisateur admin créé avec succès !' AS message;

-- Vérifier que l'utilisateur a été créé
SELECT id, username, email, role, is_superuser, is_staff 
FROM users_user 
WHERE username = 'admin';

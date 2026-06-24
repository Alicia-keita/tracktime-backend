-- Script SQL pour assigner les badge_rfid aux utilisateurs
-- Exécuter ce script dans phpMyAdmin sur la base de données 'pointage'

UPDATE users_user SET badge_rfid = '217013220' WHERE username = 'Amadou';
UPDATE users_user SET badge_rfid = '1992385737' WHERE username = 'fatou';

-- Vérification
SELECT username, email, badge_rfid, role FROM users_user;

# Script PowerShell pour configurer l'encodage et tester Django avec PostgreSQL
# Copiez et exécutez ces commandes dans PowerShell

# 1. Configurer l'encodage UTF-8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PGCLIENTENCODING = "UTF8"
$env:LC_ALL = "en_US.UTF-8"
$env:LANG = "en_US.UTF-8"

# 2. Activer l'environnement virtuel
.venv\Scripts\Activate.ps1

# 3. Tester la connexion
Write-Host "Test de connexion PostgreSQL..." -ForegroundColor Green
python test_postgres_fix.py

# 4. Si le test réussit, démarrer Django
if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Connexion réussie! Démarrage de Django..." -ForegroundColor Green
    python manage.py runserver
} else {
    Write-Host "❌ Erreur de connexion" -ForegroundColor Red
}

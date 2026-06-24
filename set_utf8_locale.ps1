# Script pour activer UTF-8 sur Windows 10/11
# Nécessite un redémarrage après exécution

Write-Host "Activation de l'UTF-8 sur Windows..." -ForegroundColor Green

# Méthode 1: Via les paramètres régionaux
Write-Host "1. Configuration des paramètres régionaux..."
Set-WinSystemLocale -SystemLocale "fr-FR"

# Méthode 2: Via le registre (Beta: Use Unicode UTF-8 for worldwide language support)
Write-Host "2. Activation de l'UTF-8 Beta via le registre..."
$registryPath = "HKLM:\SYSTEM\CurrentControlSet\Control\Nls\CodePage"
Set-ItemProperty -Path $registryPath -Name "ACP" -Value "65001"
Set-ItemProperty -Path $registryPath -Name "OEMCP" -Value "65001"
Set-ItemProperty -Path $registryPath -Name "MACCP" -Value "65001"

# Méthode 3: Variables d'environnement système
Write-Host "3. Configuration des variables d'environnement..."
[Environment]::SetEnvironmentVariable("PYTHONIOENCODING", "utf-8", "Machine")
[Environment]::SetEnvironmentVariable("PGCLIENTENCODING", "utf-8", "Machine")

Write-Host "`n✅ Configuration UTF-8 terminée!" -ForegroundColor Green
Write-Host "`n⚠️  REDEMARRAGE REQUIS pour appliquer les changements" -ForegroundColor Yellow
Write-Host "`nAprès le redémarrage:"
Write-Host "   1. Relancez PowerShell en tant qu'administrateur"
Write-Host "   2. Exécutez: cd '$PSScriptRoot'"
Write-Host "   3. Exécutez: python manage.py migrate"
Write-Host ""

$restart = Read-Host "Voulez-vous redémarrer maintenant? (O/N)"
if ($restart -eq "O" -or $restart -eq "o") {
    Restart-Computer
} else {
    Write-Host "`nN'oubliez pas de redémarrer manuellement plus tard!" -ForegroundColor Red
}

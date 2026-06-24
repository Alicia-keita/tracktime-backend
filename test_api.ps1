# Script de test PowerShell pour l'API de demande de permission
$BASE_URL = "http://localhost:8000/api"

Write-Host "🧪 TEST MANUEL - API DEMANDE DE PERMISSION" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Obtenir un token pour l'employé
Write-Host "`n1️⃣ Connexion employé..." -ForegroundColor Yellow
try {
    $loginResponse = Invoke-RestMethod -Uri "$BASE_URL/login/" -Method POST -ContentType "application/json" -Body @{
        username = "employe1"
        password = "password123"
    }
    $TOKEN_EMP = $loginResponse.access
    Write-Host "✅ Token employé obtenu" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur connexion employé: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 2. Créer une demande de permission (employé)
Write-Host "`n2️⃣ Création demande (employé)..." -ForegroundColor Yellow
try {
    $permissionData = @{
        type_permission = "leave"
        date_sortie = "2026-04-10T09:00:00Z"
        date_retour = "2026-04-12T17:00:00Z"
        motif = "Vacances printemps"
    }
    
    $createResponse = Invoke-RestMethod -Uri "$BASE_URL/permissions/" -Method POST -ContentType "application/json" -Headers @{
        Authorization = "Bearer $TOKEN_EMP"
    } -Body ($permissionData | ConvertTo-Json)
    
    Write-Host "✅ Demande créée avec ID: $($createResponse.id)" -ForegroundColor Green
    $PERMISSION_ID = $createResponse.id
} catch {
    Write-Host "❌ Erreur création demande: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. Obtenir un token pour RH
Write-Host "`n3️⃣ Connexion RH..." -ForegroundColor Yellow
try {
    $rhLoginResponse = Invoke-RestMethod -Uri "$BASE_URL/login/" -Method POST -ContentType "application/json" -Body @{
        username = "rh1"
        password = "password123"
    }
    $TOKEN_RH = $rhLoginResponse.access
    Write-Host "✅ Token RH obtenu" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur connexion RH: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Voir les demandes en attente (RH)
Write-Host "`n4️⃣ Voir demandes en attente (RH)..." -ForegroundColor Yellow
try {
    $pendingResponse = Invoke-RestMethod -Uri "$BASE_URL/permissions/pending/" -Method GET -Headers @{
        Authorization = "Bearer $TOKEN_RH"
    }
    Write-Host "✅ Demandes en attente: $($pendingResponse.Count)" -ForegroundColor Green
    $pendingResponse | ForEach-Object { Write-Host "   - ID: $($_.id), Employé: $($_.employee_name), Statut: $($_.status_display)" }
} catch {
    Write-Host "❌ Erreur récupération demandes: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Approuver une demande (RH)
if ($PERMISSION_ID) {
    Write-Host "`n5️⃣ Approuver demande (RH)..." -ForegroundColor Yellow
    try {
        $approveResponse = Invoke-RestMethod -Uri "$BASE_URL/permissions/$PERMISSION_ID/approve/" -Method PATCH -ContentType "application/json" -Headers @{
            Authorization = "Bearer $TOKEN_RH"
        } -Body @{
            commentaire_rh = "Approuvé par RH - Bonnes vacances!"
        }
        Write-Host "✅ Demande approuvée: $($approveResponse.message)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Erreur approbation: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 6. Tentative de création par RH (doit échouer)
Write-Host "`n6️⃣ Tentative création par RH (doit échouer)..." -ForegroundColor Yellow
try {
    $rhPermissionData = @{
        type_permission = "leave"
        date_sortie = "2026-04-15T09:00:00Z"
        date_retour = "2026-04-16T17:00:00Z"
        motif = "Test RH"
    }
    
    $rhCreateResponse = Invoke-RestMethod -Uri "$BASE_URL/permissions/" -Method POST -ContentType "application/json" -Headers @{
        Authorization = "Bearer $TOKEN_RH"
    } -Body ($rhPermissionData | ConvertTo-Json)
    
    Write-Host "❌ ERREUR: RH ne devrait pas pouvoir créer! Réponse: $rhCreateResponse" -ForegroundColor Red
} catch {
    Write-Host "✅ RH ne peut pas créer (comme attendu)" -ForegroundColor Green
}

Write-Host "`n✨ Tests manuels terminés!" -ForegroundColor Cyan
Write-Host "`n💡 Serveur doit être lancé avec: python manage.py runserver" -ForegroundColor Gray

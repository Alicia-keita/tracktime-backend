@echo off
echo ========================================================
echo        DEPLOIEMENT DU BACKEND (TRACKTIME) SUR HEROKU
echo ========================================================
echo.
echo ETAPE 1: Connexion a Heroku
echo ---------------------------
echo Une fenetre de navigateur va s'ouvrir. Connectez-vous, puis revenez ici.
call heroku login
echo.
echo ETAPE 2: Creation de l'application sur Heroku
echo ---------------------------------------------
call heroku create
echo.
echo ETAPE 3: Envoi du code (Deploiement)
echo ------------------------------------
git init
git add .
git commit -m "Deploiement automatique"
git branch -M main
git push heroku main -f
echo.
echo ========================================================
echo DEPLOIEMENT TERMINE ! 
echo ========================================================
pause

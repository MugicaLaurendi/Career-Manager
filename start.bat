@echo off
title Lancement de la Carte Interactive
echo Verification de l'environnement...
pushd "%~dp0"
if not exist requirements.txt (
    echo Fichier requirements.txt introuvable.
    pause
    exit /b 1
)

:: Installation des dépendances depuis requirements.txt
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Erreur lors de l'installation des dépendances.
    pause
    exit /b %errorlevel%
)

echo Lancement de l'application...
streamlit run "%~dp0app.py"
popd
pause
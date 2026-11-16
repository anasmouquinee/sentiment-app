@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul
title Sentiment App 1.0.0 - Installateur Windows (Roue Python)

echo =====================================================================
echo           SENTIMENT APP 1.0.0 - INSTALLATEUR WINDOWS
echo           Installation locale a partir de la roue (.whl)
echo =====================================================================
echo.

:: 1. Localiser la roue (.whl)
set "ROUE="
if exist "%~dp0sentiment_app-1.0.0-py3-none-any.whl" (
    set "ROUE=%~dp0sentiment_app-1.0.0-py3-none-any.whl"
) else if exist "%~dp0..\dist\sentiment_app-1.0.0-py3-none-any.whl" (
    set "ROUE=%~dp0..\dist\sentiment_app-1.0.0-py3-none-any.whl"
)

if "%ROUE%"=="" (
    echo [ERREUR] La roue sentiment_app-1.0.0-py3-none-any.whl est introuvable.
    echo Veuillez d'abord construire la roue avec 'python -m build'.
    echo.
    pause
    exit /b 1
)

echo [OK] Roue detectee : %ROUE%
echo.

:: 2. Verifier Python
echo [*] Verification de l'interpreteur Python...
set "PYTHON_CMD="
where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON_CMD=py -3.11"
    py -3.11 --version >nul 2>nul || set "PYTHON_CMD=py"
) else (
    where python >nul 2>nul
    if %errorlevel%==0 (
        set "PYTHON_CMD=python"
    )
)

if "%PYTHON_CMD%"=="" (
    echo [ERREUR] Python 3.11 n'a pas ete detecte sur ce systeme.
    echo Veuillez installer Python depuis https://www.python.org/downloads/
    echo en cochant la case 'Add Python to PATH'.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('%PYTHON_CMD% --version 2^>^&1') do echo [OK] %%v detecte

:: 3. Definir le repertoire d'installation
set "INSTALL_DIR=%LOCALAPPDATA%\SentimentApp"
echo.
echo [*] Repertoire d'installation : %INSTALL_DIR%

if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\bin" mkdir "%INSTALL_DIR%\bin"

:: 4. Creer l'environnement virtuel isole
echo [*] Creation de l'environnement virtuel isole...
if not exist "%INSTALL_DIR%\env\Scripts\python.exe" (
    %PYTHON_CMD% -m venv "%INSTALL_DIR%\env"
    if %errorlevel% neq 0 (
        echo [ERREUR] Echec lors de la creation du venv.
        pause
        exit /b 1
    )
)
echo [OK] Environnement pret.

:: 5. Installer la roue (.whl)
echo.
echo [*] Installation de la roue sentiment_app-1.0.0-py3-none-any.whl...
"%INSTALL_DIR%\env\Scripts\python.exe" -m pip install --upgrade pip -q
"%INSTALL_DIR%\env\Scripts\python.exe" -m pip install --force-reinstall -q "%ROUE%"
if %errorlevel% neq 0 (
    echo [ERREUR] Echec de l'installation de la roue via pip.
    pause
    exit /b 1
)
echo [OK] Roue et dependances installees avec succes.

:: 6. Creer le script lanceur sentiment.bat
(
    echo @echo off
    echo "%INSTALL_DIR%\env\Scripts\sentiment.exe" %%*
) > "%INSTALL_DIR%\bin\sentiment.bat"

:: 7. Creer le lanceur interactif
(
    echo @echo off
    echo chcp 65001 ^>nul
    echo title Sentiment App - Console d'analyse
    echo ==============================================================
    echo    SENTIMENT APP 1.0.0 - ANALYSE DE SENTIMENT D'AVIS CLIENTS
    echo ==============================================================
    echo.
    echo Tapez un texte d'avis a analyser ou 'exit' pour quitter.
    echo.
    echo :boucle
    echo set "texte="
    echo set /p texte="Avis client ^> "
    echo if not defined texte goto boucle
    echo if /i "%%texte%%"=="exit" goto fin
    echo if /i "%%texte%%"=="quit" goto fin
    echo.
    echo Resultat :
    echo "%INSTALL_DIR%\bin\sentiment.bat" "%%texte%%"
    echo.
    echo --------------------------------------------------------------
    echo goto boucle
    echo :fin
) > "%INSTALL_DIR%\SentimentApp-Console.bat"

:: 8. Creer le raccourci sur le Bureau
set "DESKTOP_DIR=%USERPROFILE%\Desktop"
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP_DIR%\Sentiment App.lnk'); $s.TargetPath = '%INSTALL_DIR%\SentimentApp-Console.bat'; $s.Description = 'Lancer Sentiment App'; $s.Save()" >nul 2>nul
echo [OK] Raccourci cree sur le Bureau : Sentiment App.lnk

:: 9. Creer le script de desinstallation
(
    echo @echo off
    echo title Desinstallation de Sentiment App
    echo echo Desinstallation en cours...
    echo if exist "%USERPROFILE%\Desktop\Sentiment App.lnk" del "%USERPROFILE%\Desktop\Sentiment App.lnk"
    echo rmdir /s /q "%INSTALL_DIR%"
    echo echo [OK] Sentiment App a ete completement supprime.
    echo pause
) > "%INSTALL_DIR%\uninstall.bat"

:: 10. Test de verification immediate
echo.
echo =====================================================================
echo                TEST DE L'APPLICATION INSTALLEE
echo =====================================================================
echo Commande executee : sentiment --json "Livraison rapide, produit conforme, tres satisfait"
"%INSTALL_DIR%\bin\sentiment.bat" --json "Livraison rapide, produit conforme, tres satisfait"
echo.
echo =====================================================================
echo [SUCCES] L'installation de Sentiment App 1.0.0 est terminee !
echo.
echo Pour analyser un avis :
echo   - Double-cliquez sur le raccourci 'Sentiment App' sur votre Bureau
echo   - Ou lancez directement : "%INSTALL_DIR%\bin\sentiment.bat" "votre texte"
echo =====================================================================
echo.
pause

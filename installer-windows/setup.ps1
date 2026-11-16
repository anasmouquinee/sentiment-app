<#
.SYNOPSIS
    Installateur Windows PowerShell pour Sentiment App 1.0.0 utilisant la roue Python (.whl).
.DESCRIPTION
    Déploie la roue 'sentiment_app-1.0.0-py3-none-any.whl' dans un environnement local isolé,
    configure les lanceurs Windows, le raccourci Bureau et valide le bon fonctionnement du modèle.
#>
[CmdletBinding()]
param(
    [string]$InstallPath = "$env:LOCALAPPDATA\SentimentApp",
    [switch]$NoShortcut,
    [switch]$AddToUserPath
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "          SENTIMENT APP 1.0.0 - INSTALLATEUR WINDOWS (POWERSHELL)    " -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Localisation de la roue
$roue = $null
$candidats = @(
    (Join-Path $PSScriptRoot "sentiment_app-1.0.0-py3-none-any.whl"),
    (Join-Path (Join-Path $PSScriptRoot "..") "dist\sentiment_app-1.0.0-py3-none-any.whl")
)

foreach ($c in $candidats) {
    if (Test-Path $c) {
        $roue = (Resolve-Path $c).Path
        break
    }
}

if (-not $roue) {
    Write-Error "La roue 'sentiment_app-1.0.0-py3-none-any.whl' est introuvable."
    exit 1
}
Write-Host "[OK] Roue trouvée : $roue" -ForegroundColor Green

# 2. Vérification de Python
Write-Host "[*] Recherche de l'interpréteur Python..." -ForegroundColor Yellow
$pythonExe = $null

$pythonCommands = @("py -3.11", "py", "python")
foreach ($cmd in $pythonCommands) {
    try {
        $res = & ([string]$cmd.Split()[0]) ($cmd.Split()[1..($cmd.Split().Length-1)]) --version 2>&1
        if ($LASTEXITCODE -eq 0 -and $res -match "Python 3\.") {
            $pythonCmd = $cmd
            Write-Host "[OK] $res détecté ($cmd)" -ForegroundColor Green
            break
        }
    } catch {}
}

if (-not $pythonCmd) {
    Write-Error "Python 3.11+ n'a pas été détecté sur votre machine. Veuillez l'installer depuis python.org."
    exit 1
}

# 3. Préparation des répertoires
Write-Host "[*] Répertoire cible : $InstallPath" -ForegroundColor Yellow
New-Item -ItemType Directory -Path "$InstallPath\bin" -Force | Out-Null
$envPath = Join-Path $InstallPath "env"

# 4. Création de l'environnement virtuel
if (-not (Test-Path "$envPath\Scripts\python.exe")) {
    Write-Host "[*] Création de l'environnement virtuel isolé..." -ForegroundColor Yellow
    $argsList = @("-m", "venv", $envPath)
    if ($pythonCmd -match " ") {
        $pyParts = $pythonCmd.Split()
        & $pyParts[0] $pyParts[1..($pyParts.Length-1)] @argsList
    } else {
        & $pythonCmd @argsList
    }
}
$vpy = Join-Path $envPath "Scripts\python.exe"

# 5. Installation de la roue
Write-Host "[*] Installation de la roue via pip..." -ForegroundColor Yellow
& $vpy -m pip install --upgrade pip -q
& $vpy -m pip install --force-reinstall -q $roue
Write-Host "[OK] Paquet installé dans l'environnement avec succès." -ForegroundColor Green

# 6. Lanceur sentiment.bat
$launcherBat = Join-Path $InstallPath "bin\sentiment.bat"
Set-Content -Path $launcherBat -Value "@echo off`n`"$envPath\Scripts\sentiment.exe`" %*" -Encoding ASCII

# 7. Lanceur interactif Console
$consoleBat = Join-Path $InstallPath "SentimentApp-Console.bat"
$consoleContent = @"
@echo off
chcp 65001 >nul
title Sentiment App 1.0.0
echo ==============================================================
echo    SENTIMENT APP 1.0.0 - ANALYSE DE SENTIMENT D'AVIS CLIENTS
echo ==============================================================
echo.
echo Tapez un texte d'avis ou 'exit' pour quitter.
echo.
:boucle
set "texte="
set /p texte="Avis client > "
if not defined texte goto boucle
if /i "%texte%"=="exit" goto fin
if /i "%texte%"=="quit" goto fin
echo.
echo Resultat :
call "%~dp0bin\sentiment.bat" "%texte%"
echo.
echo --------------------------------------------------------------
goto boucle
:fin
"@
Set-Content -Path $consoleBat -Value $consoleContent -Encoding UTF8

# 8. Raccourci Bureau
if (-not $NoShortcut) {
    $desktop = [System.Environment]::GetFolderPath("Desktop")
    $shortcutPath = Join-Path $desktop "Sentiment App.lnk"
    $wsh = New-Object -ComObject WScript.Shell
    $s = $wsh.CreateShortcut($shortcutPath)
    $s.TargetPath = $consoleBat
    $s.WorkingDirectory = $InstallPath
    $s.Description = "Classifieur de sentiment d'avis clients"
    $s.Save()
    Write-Host "[OK] Raccourci créé sur le Bureau : $shortcutPath" -ForegroundColor Green
}

# 9. Ajout au PATH si demandé
if ($AddToUserPath) {
    $binDir = Join-Path $InstallPath "bin"
    $userPath = [System.Environment]::GetEnvironmentVariable("Path", "User")
    if ($userPath -notmatch [regex]::Escape($binDir)) {
        [System.Environment]::SetEnvironmentVariable("Path", "$userPath;$binDir", "User")
        Write-Host "[OK] Commande 'sentiment' ajoutée au PATH utilisateur." -ForegroundColor Green
    }
}

# 10. Désinstalleur
$uninstallBat = Join-Path $InstallPath "uninstall.bat"
$unContent = @"
@echo off
title Desinstallation de Sentiment App
echo Desinstallation en cours...
if exist "%USERPROFILE%\Desktop\Sentiment App.lnk" del "%USERPROFILE%\Desktop\Sentiment App.lnk"
rmdir /s /q "$InstallPath"
echo [OK] Sentiment App a ete completement supprime.
pause
"@
Set-Content -Path $uninstallBat -Value $unContent -Encoding ASCII

# 11. Test immédiat
Write-Host ""
Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host "               TEST DE FONCTIONNEMENT DU MODÈLE                     " -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan
$testText = "Livraison rapide, emballage soigné, très satisfait !"
Write-Host "Texte testé : '$testText'" -ForegroundColor Gray
$jsonRes = & (Join-Path $envPath "Scripts\sentiment.exe") --json $testText
Write-Host "Réponse de l'application :" -ForegroundColor Yellow
Write-Host $jsonRes -ForegroundColor Cyan
Write-Host ""
Write-Host "[SUCCÈS] Installation terminée avec succès !" -ForegroundColor Green

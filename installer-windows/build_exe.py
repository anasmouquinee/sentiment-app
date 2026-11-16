"""Compile l'assistant graphique en un fichier exécutable autonome Setup-SentimentApp-Windows.exe."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
INSTALLER_DIR = RACINE / "installer-windows"
ROUE = RACINE / "dist" / "sentiment_app-1.0.0-py3-none-any.whl"

if not ROUE.exists():
    print(f"Erreur : La roue {ROUE} n'existe pas. Lancez d'abord python -m build.")
    sys.exit(1)

# Copier également la roue dans installer-windows pour distribution zip
shutil.copy2(ROUE, INSTALLER_DIR / ROUE.name)
print(f"[OK] Roue copiée dans {INSTALLER_DIR / ROUE.name}")

# Lancer PyInstaller
cmd = [
    sys.executable,
    "-m",
    "PyInstaller",
    "--onefile",
    "--windowed",
    "--name",
    "Setup-SentimentApp-Windows",
    f"--add-data={ROUE};dist",
    f"--distpath={INSTALLER_DIR}",
    f"--workpath={INSTALLER_DIR / 'build'}",
    "--specpath",
    str(INSTALLER_DIR),
    "--clean",
    "-y",
    str(INSTALLER_DIR / "installer_gui.py"),
]

print("Construction de Setup-SentimentApp-Windows.exe via PyInstaller...")
res = subprocess.run(cmd, cwd=RACINE, check=False)
if res.returncode == 0:
    print("\n[SUCCÈS] Exécutable créé avec succès dans :")
    print(f"  {INSTALLER_DIR / 'Setup-SentimentApp-Windows.exe'}")
    # Nettoyage des dossiers de build temporaires de PyInstaller
    if (INSTALLER_DIR / "build").exists():
        shutil.rmtree(INSTALLER_DIR / "build", ignore_errors=True)
    if (INSTALLER_DIR / "Setup-SentimentApp-Windows.spec").exists():
        (INSTALLER_DIR / "Setup-SentimentApp-Windows.spec").unlink(missing_ok=True)
else:
    print(f"[ERREUR] Échec de la compilation (code {res.returncode})")
    sys.exit(res.returncode)

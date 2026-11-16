"""Assistant d'installation graphique Windows pour Sentiment App 1.0.0.

Installe la roue sentiment_app-1.0.0-py3-none-any.whl dans un environnement
local isolé, configure les raccourcis Bureau et valide le modèle.
Fonctionne directement avec Python ou compilé en Setup-SentimentApp.exe.
"""
import json
import os
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

NOM_ROUE = "sentiment_app-1.0.0-py3-none-any.whl"


def trouver_roue() -> Path | None:
    """Localise le fichier .whl, soit embarqué (PyInstaller), soit à côté, soit dans dist/."""
    candidats = []
    # Si exécutable PyInstaller
    if hasattr(sys, "_MEIPASS"):
        candidats.append(Path(sys._MEIPASS) / "dist" / NOM_ROUE)
        candidats.append(Path(sys._MEIPASS) / NOM_ROUE)

    base = Path(__file__).resolve().parent
    candidats.extend([
        base / NOM_ROUE,
        base.parent / "dist" / NOM_ROUE,
        base / "dist" / NOM_ROUE,
    ])
    for c in candidats:
        if c.exists():
            return c
    return None


def trouver_python() -> str | None:
    """Trouve un interpréteur Python 3.11+ valide sur le système."""
    commandes = ["py -3.11", "py", "python", sys.executable]
    for cmd in commandes:
        try:
            p = subprocess.run(
                cmd.split() + ["--version"],
                capture_output=True,
                text=True,
                check=False,
            )
            if p.returncode == 0 and "Python 3." in (p.stdout + p.stderr):
                return cmd
        except Exception:
            continue
    return None


class AssistantInstallation(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Assistant d'installation - Sentiment App 1.0.0")
        self.geometry("640x520")
        self.minsize(580, 480)
        self.configure(bg="#F3F4F6")

        # Variables
        default_dir = os.path.join(
            os.environ.get("LOCALAPPDATA", os.path.expanduser("~")),
            "SentimentApp",
        )
        self.dossier_install = tk.StringVar(value=default_dir)
        self.opt_raccourci = tk.BooleanVar(value=True)
        self.opt_path = tk.BooleanVar(value=True)
        self.opt_test = tk.BooleanVar(value=True)

        self.roue_path = trouver_roue()
        self.python_cmd = trouver_python()

        self._creer_widgets()

    def _creer_widgets(self):
        # En-tête
        header = tk.Frame(self, bg="#1E3A8A", height=70)
        header.pack(fill="x")
        header.pack_propagate(False)

        titre = tk.Label(
            header,
            text="Sentiment App 1.0.0",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#1E3A8A",
        )
        titre.pack(anchor="w", padx=20, pady=(12, 0))

        sous_titre = tk.Label(
            header,
            text="Installation Windows à partir de la roue officielle (.whl)",
            font=("Segoe UI", 9),
            fg="#93C5FD",
            bg="#1E3A8A",
        )
        sous_titre.pack(anchor="w", padx=20)

        # Corps
        body = tk.Frame(self, bg="#F3F4F6", padx=20, pady=15)
        body.pack(fill="both", expand=True)

        # Cadre informations détection
        info_frame = tk.LabelFrame(
            body,
            text=" Environnement détecté ",
            font=("Segoe UI", 9, "bold"),
            bg="#F3F4F6",
            padx=10,
            pady=8,
        )
        info_frame.pack(fill="x", pady=(0, 10))

        lbl_roue = tk.Label(
            info_frame,
            text=f"Roue (.whl) : {'✓ ' + self.roue_path.name if self.roue_path else '✗ Introuvable'}",
            fg="#047857" if self.roue_path else "#DC2626",
            bg="#F3F4F6",
            font=("Segoe UI", 9),
        )
        lbl_roue.pack(anchor="w")

        lbl_py = tk.Label(
            info_frame,
            text=f"Python : {'✓ ' + self.python_cmd if self.python_cmd else '✗ Python non détecté'}",
            fg="#047857" if self.python_cmd else "#DC2626",
            bg="#F3F4F6",
            font=("Segoe UI", 9),
        )
        lbl_py.pack(anchor="w")

        # Cadre Destination
        dest_frame = tk.LabelFrame(
            body,
            text=" Dossier d'installation ",
            font=("Segoe UI", 9, "bold"),
            bg="#F3F4F6",
            padx=10,
            pady=8,
        )
        dest_frame.pack(fill="x", pady=(0, 10))

        entry_frame = tk.Frame(dest_frame, bg="#F3F4F6")
        entry_frame.pack(fill="x")

        entry = tk.Entry(
            entry_frame,
            textvariable=self.dossier_install,
            font=("Segoe UI", 9),
        )
        entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        btn_browse = tk.Button(
            entry_frame,
            text="Parcourir...",
            command=self._parcourir,
            font=("Segoe UI", 8),
        )
        btn_browse.pack(side="right")

        # Options
        opt_frame = tk.LabelFrame(
            body,
            text=" Options ",
            font=("Segoe UI", 9, "bold"),
            bg="#F3F4F6",
            padx=10,
            pady=6,
        )
        opt_frame.pack(fill="x", pady=(0, 10))

        tk.Checkbutton(
            opt_frame,
            text="Créer un raccourci interactif sur le Bureau",
            variable=self.opt_raccourci,
            bg="#F3F4F6",
            font=("Segoe UI", 9),
        ).pack(anchor="w")
        tk.Checkbutton(
            opt_frame,
            text="Ajouter la commande 'sentiment' au PATH de l'utilisateur",
            variable=self.opt_path,
            bg="#F3F4F6",
            font=("Segoe UI", 9),
        ).pack(anchor="w")
        tk.Checkbutton(
            opt_frame,
            text="Exécuter un test de validation du modèle après installation",
            variable=self.opt_test,
            bg="#F3F4F6",
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        # Barre de progression et journal
        self.progress = ttk.Progressbar(body, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 6))

        self.log_text = tk.Text(body, height=6, font=("Consolas", 8), bg="#FFFFFF")
        self.log_text.pack(fill="both", expand=True, pady=(0, 10))
        self.log_text.insert(
            "end", "Prêt. Cliquez sur 'Installer' pour démarrer.\n"
        )
        self.log_text.config(state="disabled")

        # Pied de page (boutons)
        footer = tk.Frame(self, bg="#E5E7EB", height=50)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        self.btn_install = tk.Button(
            footer,
            text="Installer",
            bg="#2563EB",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            padx=18,
            pady=4,
            command=self._demarrer_installation,
        )
        self.btn_install.pack(side="right", padx=15, pady=8)

        self.btn_quitter = tk.Button(
            footer,
            text="Quitter",
            font=("Segoe UI", 9),
            padx=12,
            pady=4,
            command=self.destroy,
        )
        self.btn_quitter.pack(side="right", pady=8)

    def _parcourir(self):
        d = filedialog.askdirectory(initialdir=self.dossier_install.get())
        if d:
            self.dossier_install.set(d)

    def _log(self, message: str):
        self.log_text.config(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _demarrer_installation(self):
        if not self.roue_path or not self.roue_path.exists():
            messagebox.showerror(
                "Erreur",
                "Le fichier roue sentiment_app-1.0.0-py3-none-any.whl est introuvable.",
            )
            return
        if not self.python_cmd:
            messagebox.showerror(
                "Erreur", "Python 3.11+ n'a pas été détecté sur votre ordinateur."
            )
            return

        self.btn_install.config(state="disabled")
        self.progress.start(10)
        threading.Thread(target=self._installer, daemon=True).start()

    def _installer(self):
        try:
            target = Path(self.dossier_install.get())
            bin_dir = target / "bin"
            env_dir = target / "env"
            bin_dir.mkdir(parents=True, exist_ok=True)

            self._log(f"[*] Dossier cible : {target}")

            # 1. venv
            py_venv = env_dir / "Scripts" / "python.exe"
            if not py_venv.exists():
                self._log("[*] Création de l'environnement virtuel...")
                cmd_parts = self.python_cmd.split() + ["-m", "venv", str(env_dir)]
                subprocess.run(cmd_parts, check=True, capture_output=True)
                self._log("[OK] Environnement créé.")
            else:
                self._log("[OK] Environnement virtuel existant réutilisé.")

            # 2. pip install wheel
            self._log(f"[*] Installation de la roue : {self.roue_path.name}...")
            r = subprocess.run(
                [
                    str(py_venv),
                    "-m",
                    "pip",
                    "install",
                    "--force-reinstall",
                    "-q",
                    str(self.roue_path),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            if r.returncode != 0:
                raise RuntimeError(
                    f"Échec de l'installation pip : {r.stderr.strip()}"
                )
            self._log("[OK] Roue et dépendances installées avec succès.")

            # 3. Lanceur sentiment.bat
            launcher_bat = bin_dir / "sentiment.bat"
            sentiment_exe = env_dir / "Scripts" / "sentiment.exe"
            launcher_bat.write_text(
                f'@echo off\n"{sentiment_exe}" %*\n', encoding="ascii"
            )

            # 4. Lanceur interactif console
            console_bat = target / "SentimentApp-Console.bat"
            console_bat.write_text(
                f"""@echo off
chcp 65001 >nul
title Sentiment App 1.0.0
echo ==============================================================
echo    SENTIMENT APP 1.0.0 - ANALYSE DE SENTIMENT D'AVIS CLIENTS
echo ==============================================================
echo.
echo Tapez un texte d'avis a analyser ou 'exit' pour quitter.
echo.
:boucle
set "texte="
set /p texte="Avis client > "
if not defined texte goto boucle
if /i "%texte%"=="exit" goto fin
if /i "%texte%"=="quit" goto fin
echo.
echo Resultat :
call "{launcher_bat}" "%texte%"
echo.
echo --------------------------------------------------------------
goto boucle
:fin
""",
                encoding="utf-8",
            )
            self._log("[OK] Lanceurs Windows configurés.")

            # 5. Raccourci Bureau
            if self.opt_raccourci.get():
                desktop = Path(os.environ["USERPROFILE"]) / "Desktop"
                shortcut = desktop / "Sentiment App.lnk"
                ps_script = (
                    f"$ws = New-Object -ComObject WScript.Shell; "
                    f"$s = $ws.CreateShortcut('{shortcut}'); "
                    f"$s.TargetPath = '{console_bat}'; "
                    f"$s.WorkingDirectory = '{target}'; "
                    f"$s.Description = 'Sentiment App 1.0.0'; $s.Save()"
                )
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_script],
                    check=False,
                )
                self._log(f"[OK] Raccourci créé sur le Bureau : {shortcut.name}")

            # 6. PATH utilisateur
            if self.opt_path.get():
                try:
                    import winreg

                    key = winreg.OpenKey(
                        winreg.HKEY_CURRENT_USER,
                        r"Environment",
                        0,
                        winreg.KEY_ALL_ACCESS,
                    )
                    curr_path, _ = winreg.QueryValueEx(key, "Path")
                    if str(bin_dir) not in curr_path:
                        new_path = f"{curr_path};{bin_dir}"
                        winreg.SetValueEx(
                            key, "Path", 0, winreg.REG_EXPAND_SZ, new_path
                        )
                        self._log("[OK] 'sentiment' ajouté au PATH utilisateur.")
                    winreg.CloseKey(key)
                except Exception as e:
                    self._log(f"[!] Info PATH : {e}")

            # 7. Test de validation
            if self.opt_test.get():
                self._log("[*] Exécution du test de validation du modèle...")
                r_test = subprocess.run(
                    [
                        str(sentiment_exe),
                        "--json",
                        "Livraison express et produit de grande qualité",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if r_test.returncode == 0:
                    try:
                        donnees = json.loads(r_test.stdout.strip())
                        self._log(
                            f"[OK] Test réussi : label={donnees.get('label')} "
                            f"(score={donnees.get('score'):.1%})"
                        )
                    except Exception:
                        self._log(f"[OK] Réponse : {r_test.stdout.strip()}")
                else:
                    self._log(f"[!] Remarque test : {r_test.stderr.strip()}")

            self._log(
                "\n======================================================="
            )
            self._log("[SUCCÈS] Installation terminée avec succès !")
            self._log(
                "Vous pouvez utiliser 'sentiment' en ligne de commande ou le raccourci Bureau."
            )

            self.progress.stop()
            self.progress.config(value=100)
            messagebox.showinfo(
                "Succès",
                "Sentiment App 1.0.0 a été installé avec succès sur votre machine !",
            )

        except Exception as e:
            self._log(f"\n[ERREUR] {e}")
            self.progress.stop()
            messagebox.showerror(
                "Échec de l'installation", f"Une erreur est survenue :\n{e}"
            )
        finally:
            self.btn_install.config(state="normal")


def main():
    app = AssistantInstallation()
    app.mainloop()


if __name__ == "__main__":
    main()

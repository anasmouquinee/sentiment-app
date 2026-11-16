# Sentiment App 1.0.0 - Installateurs Windows (Roue Python)

Ce dossier fournit des solutions d'installation prêtes à l'emploi pour Windows, utilisant la roue officielle **`sentiment_app-1.0.0-py3-none-any.whl`**.

---

## 🚀 Options d'installation sous Windows

### Option 1 : L'installateur graphique autonome (.exe) — **Recommandé**
Double-cliquez simplement sur :
👉 **`Setup-SentimentApp-Windows.exe`**

* Assistant graphique avec sélection du répertoire d'installation.
* Déploie la roue embarquée dans un environnement virtuel isolé (`%LOCALAPPDATA%\SentimentApp`).
* Crée un raccourci interactif sur le Bureau : **`Sentiment App`**.
* Ajoute la commande `sentiment` au PATH utilisateur Windows.
* Effectue un test de validation immédiat du modèle d'analyse de sentiment.

---

### Option 2 : L'installateur en 1 clic (Script Batch .bat)
Faites un clic droit sur **`setup.bat`** $\rightarrow$ **Exécuter**.

* Détecte automatiquement l'interpréteur Python 3.11+.
* Installe la roue locale `sentiment_app-1.0.0-py3-none-any.whl`.
* Configure les lanceurs et le raccourci Bureau.
* Affiche le résultat du test dans la console avant de terminer.

---

### Option 3 : L'installateur PowerShell
Ouvrez PowerShell dans ce dossier et exécutez :
```powershell
.\setup.ps1 -AddToUserPath
```

---

## 💡 Utilisation après installation

Une fois installé, vous pouvez interroger le classifieur de trois façons :

1. **Par le raccourci Bureau** : Double-cliquez sur l'icône `Sentiment App` pour ouvrir la console d'analyse interactive.
2. **En ligne de commande classique (CMD / PowerShell)** :
   ```cmd
   sentiment "Livraison rapide, article parfait, je recommande !"
   ```
   Sortie :
   ```text
   positive (confiance 91%)
   ```
3. **Avec sortie JSON** :
   ```cmd
   sentiment --json "Produit cassé et service injoignable"
   ```
   Sortie :
   ```json
   {"label": "negative", "score": 0.7465}
   ```

---

## 🗑️ Désinstallation
Pour supprimer complètement l'application et ses raccourcis :
* Lancez le fichier `%LOCALAPPDATA%\SentimentApp\uninstall.bat`.

# Semaine 4 — TP4 : Tests approfondis et qualité

## 1. Mesures de départ

### Couverture
Couverture initiale mesurée avant les corrections TP4 :
- **TOTAL : 91 %**
- Lignes manquantes dans `api/main.py` : 503 (modèle non chargé), 500 (modèle en panne), bloc `__main__`

### ruff
11 remarques initiales :
- `B904` deux fois dans `main.py`
- `I001`, `F401` dans `model.py`
- `F401`, `B905` deux fois dans `evaluate.py`
- `I001` dans `test_api.py`
- `E741` trois fois dans deux tests du TP1

### mypy
Résultat initial : `Success: no issues found in 4 source files`

---

## 2. Étape B — Contrat d'entrée (T22, T23)

`api/schemas.py` corrigé avec `field_validator` qui refuse les textes blancs.  
`tests/test_limites.py` : 8 cas paramétrés + 2 propriétés Hypothesis → **10 passed**, trois fois de suite.

---

## 3. Étape C — Abstention et jeu d'or (T24, T25)

Seuil d'abstention : **SEUIL_ABSTENTION = 0.60** dans `api/model.py`.

Textes de mots inventés → **INDETERMINE** (score ≈ 0,5162, sous le seuil).

### Bilan du jeu d'or (20 avis)

| Catégorie | Nombre |
|---|---|
| Avis analysés | 20 |
| Réponses justes | 7 |
| Abstentions (INDETERMINE) | 9 |
| Erreurs franches connues | 4 |
| Erreurs inattendues | 0 |

---

## 4. Étape D — API telle qu'elle tourne (T26)

`tests/test_integration.py` couvre :
- Démarrage réel avec TestClient
- Refus sans modèle (FileNotFoundError)
- 503 quand le modèle est retiré de app.state
- 500 sans message interne (RuntimeError)
- Rejet d'un modèle aux étiquettes inconnues

Couverture finale : **≥ 95 %** (`pytest --cov=api --cov-fail-under=95`)

---

## 5. Étape E — Qualité statique, crochet et CI (T27)

### ruff
`ruff check . --fix` règle l'essentiel. Corrections manuelles restantes : `strict=True` dans `zip()` d'`evaluate.py`, `from None` sur le `raise` du 500, renommage `l → ligne` dans les tests TP1.

### mypy
`TypedDict ResultatPredict` avec `Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]` — mypy muet.

### Pre-commit
`pre-commit install` installé. Teste le rejet d'un commit fautif (`ruff` → Failed, commit annulé).

### CI
`.github/workflows/ci.yml` mis à jour avec les quatre étapes TP4 : `ruff`, `mypy`, tests + couverture 95 %.

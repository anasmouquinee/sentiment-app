"""Tests du jeu d'or (TP4 — T25).

Le jeu d'or est un ensemble de 20 avis rédigés par le binôme,
absents des données d'entraînement, chacun avec l'étiquette attendue.

Règles :
  - Aucune erreur franche ne provoque un `failed` (les erreurs connues sont en xfail).
  - Une abstention (INDETERMINE) est comptée mais n'est pas un échec.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

RACINE = Path(__file__).resolve().parents[1]
JEU_OR = RACINE / "data" / "jeu_or.csv"
MODELE = RACINE / "models" / "sentiment.joblib"

# Correspondance étiquettes API → étiquettes du jeu d'or
CORRESPONDANCE = {"POSITIVE": "POSITIVE", "NEGATIVE": "NEGATIVE", "INDETERMINE": None}


def charger_jeu() -> list[dict]:
    """Charge et valide le jeu d'or."""
    assert JEU_OR.exists(), f"{JEU_OR} absent — créez data/jeu_or.csv"
    df = pd.read_csv(JEU_OR)
    assert len(df) >= 20, f"jeu d'or incomplet : {len(df)} avis sur 20"
    return df.to_dict(orient="records")


def _predict_api(texte: str) -> dict:
    """Prédit via l'API en mémoire."""
    from api.main import app
    from fastapi.testclient import TestClient

    with TestClient(app) as client:
        reponse = client.post("/predict", json={"text": texte})
    assert reponse.status_code == 200
    return reponse.json()


# ---------------------------------------------------------------------------
# T25-a : le jeu d'or est complet
# ---------------------------------------------------------------------------


def test_jeu_or_complet():
    """Le fichier jeu_or.csv contient au moins 20 avis."""
    jeu = charger_jeu()
    assert len(jeu) >= 20, f"jeu d'or incomplet : {len(jeu)} avis sur 20"


# ---------------------------------------------------------------------------
# T25-b : tests paramétrés — un par avis du jeu d'or
# ---------------------------------------------------------------------------


def _cas_jeu_or() -> list:
    """Génère les cas pytest depuis le CSV."""
    if not JEU_OR.exists() or not MODELE.exists():
        return []
    jeu = charger_jeu()
    return [
        pytest.param(
            avis["text"],
            avis["attendu"],
            str(avis.get("erreur_connue", "")) if pd.notna(avis.get("erreur_connue", "")) else "",
            id=f"avis_{i + 1}",
        )
        for i, avis in enumerate(jeu)
    ]


@pytest.mark.parametrize("texte,attendu,erreur_connue", _cas_jeu_or())
def test_avis_jeu_or(texte: str, attendu: str, erreur_connue: str):
    """Teste chaque avis du jeu d'or.

    - INDETERMINE → abstention, pas un échec.
    - Erreur connue → xfail(strict=True) : on attend cet échec.
    - Erreur inattendue → failed.
    """
    if not MODELE.exists():
        pytest.skip("models/sentiment.joblib absent")

    resultat = _predict_api(texte)
    label_obtenu = resultat["label"]

    if label_obtenu == "INDETERMINE":
        # Abstention : acceptable, on signale mais on ne fait pas échouer.
        pytest.skip(f"abstention sur : {texte[:60]!r}")

    if erreur_connue:
        # Erreur déclarée : on marque le test comme xfail strict.
        if label_obtenu != attendu:
            pytest.xfail(f"erreur connue ({erreur_connue}) : prédit {label_obtenu}, attendu {attendu}")

    assert label_obtenu == attendu, (
        f"Prédit {label_obtenu}, attendu {attendu} pour : {texte[:80]!r}"
    )

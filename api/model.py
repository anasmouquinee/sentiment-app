"""Raccord entre l'API et le modèle entraîné au TP2.

L'API n'entraîne rien et ne connaît pas scikit-learn : elle appelle la fonction
predict() du paquet (sentiment_app/predict.py), qui charge le modèle une seule fois.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any, TypedDict

import joblib

from api.schemas import Label
from sentiment_app import predict as _pred
from sentiment_app.predict import charger_modele as _charger_modele
from sentiment_app.predict import predict as _predict

# Compatibilité et localisation
RACINE = Path(__file__).resolve().parents[1]
MODELE = _pred.chemin_modele()

# Choisi sur la courbe du seuil (python src/courbe_seuil.py) : voir docs/semaine4.md, partie 3
SEUIL_ABSTENTION = 0.60
# Étiquettes du modèle -> étiquettes du contrat : une correspondance explicite, vérifiée au démarrage
CORRESPONDANCE: dict[str, Label] = {"positive": "POSITIVE", "negative": "NEGATIVE"}


class Prediction(TypedDict):
    """Type de retour pour l'API et la CLI."""

    label: Label
    score: float
    text: str


ResultatPredict = Prediction


@lru_cache(maxsize=1)
def charger_modele():
    """Charge le pipeline scikit-learn via sentiment_app.predict ou MODELE.

    Lève FileNotFoundError si le modèle n'existe pas.
    Lève RuntimeError si les étiquettes du modèle sont inconnues.
    """
    if MODELE != _pred.chemin_modele():
        if not MODELE.exists():
            raise FileNotFoundError(
                f"Modèle absent : {MODELE} — lancez python src/train.py"
            )
        pipeline = joblib.load(MODELE)
    else:
        pipeline = _charger_modele()

    etiquettes_modele = frozenset(str(c) for c in pipeline.classes_)
    if not etiquettes_modele <= set(CORRESPONDANCE):
        raise RuntimeError(
            f"Étiquettes inconnues dans le modèle : {etiquettes_modele - set(CORRESPONDANCE)}"
        )
    return pipeline


class SentimentClassifier:
    """Enveloppe du modèle TP2 avec l'interface attendue par l'API."""

    model_name = "tfidf-logreg (TP2, models/sentiment.joblib)"

    def __init__(self, pipeline: Any = None) -> None:
        modele = pipeline if pipeline is not None else charger_modele()
        inconnues = {str(c) for c in modele.classes_} - set(CORRESPONDANCE)
        if inconnues:
            raise RuntimeError(f"classes inconnues du contrat : {sorted(inconnues)}")
        self._pipeline = modele

    def predict(self, text: str) -> Prediction:
        """Renvoie l'étiquette du contrat, ou INDETERMINE quand le modèle hésite."""
        r = _predict(text)
        label: Label = (
            "INDETERMINE"
            if r["score"] < SEUIL_ABSTENTION
            else CORRESPONDANCE[r["label"]]
        )
        return {"label": label, "score": r["score"], "text": text}


def load_model() -> SentimentClassifier:
    """Construit le classifier (le cache de chargement est dans sentiment_app/predict.py)."""
    return SentimentClassifier()


def predict_texte(texte: str) -> Prediction:
    """Fonction de commodité : charge le modèle et prédit en une seule ligne."""
    return load_model().predict(texte)

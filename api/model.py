"""Chargement et inférence du modèle de sentiment.

TP3 : chargement paresseux via lru_cache, prédiction binaire.
TP4 : seuil d'abstention (SEUIL_ABSTENTION) → label INDETERMINE.
       TypedDict annoté pour mypy.
"""
from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path
from typing import Literal, TypedDict

import joblib

# Chemin résolu depuis la racine du dépôt, indépendant du répertoire de lancement.
RACINE = Path(__file__).resolve().parents[1]
MODELE = RACINE / "models" / "sentiment.joblib"

# Seuil en dessous duquel le modèle s'abstient.
SEUIL_ABSTENTION: float = 0.60

# Étiquettes reconnues par le modèle entraîné (src/train.py).
ETIQUETTES_CONNUES: frozenset[str] = frozenset({"negative", "positive"})


class ResultatPredict(TypedDict):
    """Type de retour de SentimentClassifier.predict() et de predict_texte()."""

    label: Literal["POSITIVE", "NEGATIVE", "INDETERMINE"]
    score: float


@lru_cache(maxsize=1)
def charger_modele():
    """Charge le pipeline scikit-learn une seule fois par processus.

    Lève FileNotFoundError si le modèle n'existe pas (contrôle T20).
    Lève RuntimeError si les étiquettes du modèle sont inconnues.
    """
    if not MODELE.exists():
        raise FileNotFoundError(
            f"Modèle absent : {MODELE} — lancez python src/train.py"
        )
    pipeline = joblib.load(MODELE)
    # Vérification au démarrage : les étiquettes doivent être connues.
    etiquettes_modele = frozenset(pipeline.classes_)
    if not etiquettes_modele <= ETIQUETTES_CONNUES:
        raise RuntimeError(
            f"Étiquettes inconnues dans le modèle : {etiquettes_modele - ETIQUETTES_CONNUES}"
        )
    return pipeline


class SentimentClassifier:
    """Encapsule le pipeline scikit-learn et applique le seuil d'abstention."""

    # Correspondance des étiquettes internes (minuscules) vers l'API (majuscules).
    _CORRESPONDANCE: dict[str, Literal["POSITIVE", "NEGATIVE"]] = {
        "positive": "POSITIVE",
        "negative": "NEGATIVE",
    }

    def __init__(self, pipeline) -> None:
        self._pipeline = pipeline

    def predict(self, texte: str) -> ResultatPredict:
        """Prédit le sentiment d'un texte.

        Returns:
            ResultatPredict avec label POSITIVE, NEGATIVE ou INDETERMINE et score.
        """
        probas = self._pipeline.predict_proba([texte])[0]
        score = float(probas.max())
        etiquette_brute: str = self._pipeline.predict([texte])[0]

        if score < SEUIL_ABSTENTION:
            label: Literal["POSITIVE", "NEGATIVE", "INDETERMINE"] = "INDETERMINE"
        else:
            label = self._correspondance_label(etiquette_brute)

        return ResultatPredict(label=label, score=round(score, 4))

    def _correspondance_label(
        self, etiquette: str
    ) -> Literal["POSITIVE", "NEGATIVE"]:
        """Convertit l'étiquette interne en étiquette API majuscule."""
        if etiquette not in self._CORRESPONDANCE:
            raise RuntimeError(f"Étiquette inattendue du modèle : {etiquette!r}")
        return self._CORRESPONDANCE[etiquette]


def predict_texte(texte: str) -> ResultatPredict:
    """Fonction de commodité : charge le modèle et prédit en une seule ligne."""
    pipeline = charger_modele()
    return SentimentClassifier(pipeline).predict(texte)


# Permet de tester le module en ligne de commande :
#   python api/model.py "Livraison rapide, très satisfait"
if __name__ == "__main__":  # pragma: no cover
    if len(sys.argv) < 2:
        print("Usage : python api/model.py \"texte à analyser\"")
        sys.exit(2)
    texte = " ".join(sys.argv[1:])
    resultat = predict_texte(texte)
    print(f"{resultat['label']} ({resultat['score']:.0%})")

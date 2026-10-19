from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, Field, field_validator


class RequetePredict(BaseModel):
    """Corps de la requête POST /predict."""

    text: Annotated[str, Field(max_length=2000)]

    @field_validator("text")
    @classmethod
    def texte_non_vide(cls, valeur: str) -> str:
        # Refuser un texte vide ou composé uniquement d'espaces/sauts de ligne.
        # Même règle que predict() en src/predict.py.
        if not valeur.strip():
            raise ValueError("texte vide ou composé uniquement de blancs")
        return valeur


class ReponsePredict(BaseModel):
    """Corps de la réponse de POST /predict."""

    label: str   # POSITIVE | NEGATIVE | INDETERMINE
    score: float
    text: str


class ReponseHealth(BaseModel):
    """Corps de la réponse de GET /health."""

    status: str
    model: str

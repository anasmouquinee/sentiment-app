"""Application FastAPI de l'API de sentiment.

TP3 : routes GET /  GET /health  POST /predict
TP4 : gestion des pannes (503 modèle absent, 500 erreur interne)
       couverture de test ≥ 95 %

Usage :
  uvicorn api.main:app --reload
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from api.model import SentimentClassifier, charger_modele
from api.schemas import ReponseHealth, ReponsePredict, RequetePredict


# ---------------------------------------------------------------------------
# Cycle de vie : charge le modèle au démarrage (T20 : FileNotFoundError → crash)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(application: FastAPI):
    """Démarre l'application en pré-chargeant le modèle (fail-fast)."""
    pipeline = charger_modele()           # lève FileNotFoundError si absent
    application.state.classifier = SentimentClassifier(pipeline)
    yield
    # Rien à libérer ici.


app = FastAPI(
    title="API de sentiment",
    description="Classifie des avis clients en POSITIVE, NEGATIVE ou INDETERMINE.",
    version="0.4.0",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# Gestionnaire d'erreur global : convertit les RuntimeError en 500 propres
# sans exposer le message interne (T26).
# ---------------------------------------------------------------------------
@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError) -> JSONResponse:
    return JSONResponse(status_code=500, content={"detail": "Erreur interne du serveur"})


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.get("/", summary="Accueil")
def racine() -> dict[str, Any]:
    """Point d'entrée : redirige vers la documentation."""
    return {"message": "API de sentiment — documentation : /docs"}


@app.get("/health", response_model=ReponseHealth, summary="Santé de l'API")
def health(request: Request) -> ReponseHealth:
    """Vérifie que l'API et le modèle sont opérationnels."""
    if not hasattr(request.app.state, "classifier"):
        raise HTTPException(status_code=503, detail="Modèle non chargé")
    return ReponseHealth(
        status="OK",
        model="tfidf-logreg (TP2, models/sentiment.joblib)",
    )


@app.post("/predict", response_model=ReponsePredict, summary="Prédiction de sentiment")
def predict(requete: RequetePredict, request: Request) -> ReponsePredict:
    """Analyse le sentiment d'un avis client.

    - **text** : texte à analyser (1 à 2000 caractères, non vide après suppression des blancs)
    - Renvoie **label** (POSITIVE | NEGATIVE | INDETERMINE), **score** et le texte reçu.
    """
    if not hasattr(request.app.state, "classifier"):
        raise HTTPException(status_code=503, detail="Modèle non chargé")

    classifier: SentimentClassifier = request.app.state.classifier
    resultat = classifier.predict(requete.text)

    return ReponsePredict(
        label=resultat["label"],
        score=resultat["score"],
        text=requete.text,
    )

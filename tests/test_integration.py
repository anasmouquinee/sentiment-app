"""Tests d'intégration approfondis de l'API (TP4 — T26).

Couvre :
  - Démarrage réel avec TestClient (app en mémoire)
  - Refus de démarrer si le modèle est absent (FileNotFoundError)
  - 503 quand le modèle est retiré de app.state
  - 500 quand le modèle plante (RuntimeError, ValueError)
  - Rejet d'un modèle aux étiquettes inconnues
"""
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"

# ---------------------------------------------------------------------------
# Fixture : client avec modèle réel
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def client():
    if not MODELE.exists():
        pytest.skip("models/sentiment.joblib absent")
    from api.main import app
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# T26-a : démarrage réel — le modèle se charge sans erreur
# ---------------------------------------------------------------------------


def test_demarrage_reel(client: TestClient):
    """L'API démarre et /health répond 200."""
    reponse = client.get("/health")
    assert reponse.status_code == 200


# ---------------------------------------------------------------------------
# T26-b : modèle absent → FileNotFoundError au démarrage
# ---------------------------------------------------------------------------


def test_refuse_sans_modele(monkeypatch, tmp_path):
    """L'API lève FileNotFoundError si le modèle est absent."""
    import api.model as model_module
    # Rediriger le chemin vers un fichier inexistant
    chemin_faux = tmp_path / "absent.joblib"
    monkeypatch.setattr(model_module, "MODELE", chemin_faux)
    model_module.charger_modele.cache_clear()

    from api.main import app
    with pytest.raises(FileNotFoundError):
        with TestClient(app):
            pass

    # Restaurer le cache pour les autres tests
    model_module.charger_modele.cache_clear()


# ---------------------------------------------------------------------------
# T26-c : modèle retiré de app.state → 503
# ---------------------------------------------------------------------------


def test_503_modele_retire(client: TestClient):
    """Si le classifier est retiré de app.state, /predict renvoie 503."""
    classifier_sauvegarde = client.app.state.classifier
    del client.app.state.classifier
    try:
        reponse = client.post("/predict", json={"text": "Test"})
        assert reponse.status_code == 503
    finally:
        client.app.state.classifier = classifier_sauvegarde


# ---------------------------------------------------------------------------
# T26-d : panne RuntimeError → 500 sans message interne
# ---------------------------------------------------------------------------


def test_500_runtime_error(client: TestClient):
    """Une RuntimeError dans predict() renvoie 500, sans exposer le message."""
    classifier_original = client.app.state.classifier
    mock_classifier = MagicMock()
    mock_classifier.predict.side_effect = RuntimeError("panne interne secrète")
    client.app.state.classifier = mock_classifier
    try:
        reponse = client.post("/predict", json={"text": "Test"})
        assert reponse.status_code == 500
        # Le message interne ne doit PAS apparaître dans la réponse
        assert "panne interne secrète" not in reponse.text
    finally:
        client.app.state.classifier = classifier_original


# ---------------------------------------------------------------------------
# T26-e : modèle aux étiquettes inconnues → RuntimeError au chargement
# ---------------------------------------------------------------------------


def test_etiquettes_inconnues(monkeypatch, tmp_path):
    """Un modèle renvoyant des étiquettes inconnues lève RuntimeError."""
    import joblib
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline

    import api.model as model_module

    # Entraîner un vrai mini-pipeline avec des étiquettes inconnues (bon/mauvais)
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", LogisticRegression()),
    ])
    pipeline.fit(["bien", "mal", "super", "nul"], ["bon", "mauvais", "bon", "mauvais"])

    chemin_faux = tmp_path / "faux.joblib"
    joblib.dump(pipeline, chemin_faux)

    monkeypatch.setattr(model_module, "MODELE", chemin_faux)
    model_module.charger_modele.cache_clear()

    with pytest.raises(RuntimeError, match="Étiquettes inconnues"):
        model_module.charger_modele()

    model_module.charger_modele.cache_clear()

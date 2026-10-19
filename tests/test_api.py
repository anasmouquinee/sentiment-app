"""Tests de l'API REST (TP3).

Six tests couvrant les routes GET / GET /health POST /predict.
Utilisent TestClient (pas de serveur réel : rapide, fiable en CI).
Les tests sont sautés si le modèle est absent sur le poste ; la CI
entraîne le modèle avant de les lancer.
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"


@pytest.fixture(scope="module")
def client():
    """Lance l'application en mémoire pour tous les tests du module."""
    if not MODELE.exists():
        pytest.skip("models/sentiment.joblib absent (normal en CI avant entraînement)")
    from api.main import app
    with TestClient(app) as c:
        yield c


def test_root(client: TestClient):
    """GET / renvoie 200 et mentionne /docs."""
    reponse = client.get("/")
    assert reponse.status_code == 200
    assert "/docs" in reponse.text


def test_health(client: TestClient):
    """GET /health : status vaut OK et le modèle est identifié."""
    reponse = client.get("/health")
    assert reponse.status_code == 200
    data = reponse.json()
    assert data["status"] == "OK"
    assert "tfidf-logreg" in data["model"]


def test_predict_positif(client: TestClient):
    """Un avis évident reçoit POSITIVE (ou INDETERMINE si le score est bas) avec score > 0,5."""
    reponse = client.post("/predict", json={"text": "Livraison rapide, produit conforme, très satisfait"})
    assert reponse.status_code == 200
    data = reponse.json()
    assert data["label"] in {"POSITIVE", "INDETERMINE"}
    assert data["score"] > 0.5


def test_predict_negatif(client: TestClient):
    """Un avis évident reçoit NEGATIVE."""
    reponse = client.post("/predict", json={"text": "Produit cassé et service client injoignable, à fuir"})
    assert reponse.status_code == 200
    assert reponse.json()["label"] == "NEGATIVE"


def test_predict_texte_vide_422(client: TestClient):
    """Texte vide et texte de blancs reçoivent 422."""
    assert client.post("/predict", json={"text": ""}).status_code == 422
    assert client.post("/predict", json={"text": "   "}).status_code == 422


def test_predict_champ_manquant_422(client: TestClient):
    """Corps vide et type incorrect reçoivent 422."""
    assert client.post("/predict", json={}).status_code == 422
    assert client.post("/predict", json={"text": 42}).status_code == 422

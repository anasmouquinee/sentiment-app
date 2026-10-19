"""Tests aux limites du contrat d'entrée de l'API (TP4 — T22, T23).

Contenu :
  1. test_limites_parametres : 8 cas aux frontières → 422 attendu, forme vérifiée.
  2. test_propriete_texte_non_blanc : hypothesis — tout texte non blanc 1..2000 car → 200.
  3. test_propriete_texte_blanc : hypothesis — tout texte de blancs → 422.
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from hypothesis import given, settings
from hypothesis import strategies as st

MODELE = Path(__file__).resolve().parents[1] / "models" / "sentiment.joblib"


@pytest.fixture(scope="module")
def client():
    if not MODELE.exists():
        pytest.skip("models/sentiment.joblib absent")
    from api.main import app
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# Cas paramétrés : 8 situations aux frontières du contrat
# ---------------------------------------------------------------------------
CAS_422 = [
    # (description, corps_json)
    ("texte_vide", {"text": ""}),
    ("espaces_seuls", {"text": "   "}),
    ("saut_de_ligne_seul", {"text": "\n"}),
    ("un_caractere_blanc", {"text": "\x85"}),          # str.strip() retire \x85
    ("champ_absent", {}),
    ("type_entier", {"text": 42}),
    ("corps_non_json", None),                           # corps vide → 422
    ("trop_long_2001", {"text": "a" * 2001}),
]


@pytest.mark.parametrize("description,corps", CAS_422)
def test_limites_parametres(client: TestClient, description: str, corps):
    """Chaque cas aux limites doit renvoyer 422 avec detail en liste."""
    if corps is None:
        reponse = client.post("/predict", content=b"", headers={"Content-Type": "application/json"})
    else:
        reponse = client.post("/predict", json=corps)

    assert reponse.status_code == 422, f"{description} : attendu 422, reçu {reponse.status_code}"
    # TP4 : detail doit être une liste (validé par field_validator)
    data = reponse.json()
    assert isinstance(data["detail"], list), (
        f"{description} : detail doit être une liste, reçu {type(data['detail'])}"
    )


# ---------------------------------------------------------------------------
# Propriétés Hypothesis
# ---------------------------------------------------------------------------
ETIQUETTES_VALIDES = {"POSITIVE", "NEGATIVE", "INDETERMINE"}


@settings(max_examples=50)
@given(texte=st.text(min_size=1, max_size=2000).filter(lambda t: t.strip()))
def test_propriete_texte_non_blanc(texte: str):
    """Tout texte non blanc de 1 à 2000 caractères → 200, étiquette valide, score ∈ [0, 1]."""
    if not MODELE.exists():
        pytest.skip("modèle absent")
    from api.main import app
    with TestClient(app) as client:
        reponse = client.post("/predict", json={"text": texte})
    assert reponse.status_code == 200
    data = reponse.json()
    assert data["label"] in ETIQUETTES_VALIDES
    assert 0.0 <= data["score"] <= 1.0


BLANCS = " \t\n\r\x0b\x0c\x85\xa0"  # tous les caractères que str.strip() retire


@settings(max_examples=50)
@given(texte=st.text(alphabet=st.sampled_from(BLANCS), min_size=1))
def test_propriete_texte_blanc(texte: str):
    """Tout texte constitué uniquement de blancs → 422."""
    if not MODELE.exists():
        pytest.skip("modèle absent")
    from api.main import app
    with TestClient(app) as client:
        reponse = client.post("/predict", json={"text": texte})
    assert reponse.status_code == 422

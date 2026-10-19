#!/usr/bin/env python
"""Bilan du jeu d'or : réponses justes, abstentions, erreurs franches déclarées.

Usage :
  python src/bilan_jeu_or.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
from fastapi.testclient import TestClient

RACINE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RACINE))
JEU_OR = RACINE / "data" / "jeu_or.csv"
SORTIE = RACINE / "docs" / "semaine4.md"
MODELE = RACINE / "models" / "sentiment.joblib"


def charger_jeu() -> pd.DataFrame:
    if not JEU_OR.exists():
        raise SystemExit(f"{JEU_OR} absent — créez data/jeu_or.csv")
    df = pd.read_csv(JEU_OR)
    if len(df) < 20:
        raise SystemExit(f"Jeu d'or incomplet : {len(df)} avis sur 20 attendus")
    return df


def predire_tous(df: pd.DataFrame) -> pd.DataFrame:
    if not MODELE.exists():
        raise SystemExit("Modèle absent : lancez d'abord python src/train.py")

    from api.main import app

    resultats = []
    with TestClient(app) as client:
        for _, row in df.iterrows():
            reponse = client.post("/predict", json={"text": row["text"]})
            data = reponse.json()
            resultats.append({
                "text": row["text"],
                "attendu": row["attendu"],
                "obtenu": data["label"],
                "score": data["score"],
                "difficulte": row.get("difficulte", ""),
                "erreur_connue": row.get("erreur_connue", ""),
            })
    return pd.DataFrame(resultats)


def afficher_bilan(df: pd.DataFrame) -> None:
    n = len(df)
    abstentions = (df["obtenu"] == "INDETERMINE").sum()
    erreurs_connues = df[df["erreur_connue"].notna() & (df["erreur_connue"] != "")]
    repondus = df[df["obtenu"] != "INDETERMINE"]
    justes = (repondus["obtenu"] == repondus["attendu"]).sum()
    erreurs_franches = (repondus["obtenu"] != repondus["attendu"]).sum()
    erreurs_inattendues = repondus[
        (repondus["obtenu"] != repondus["attendu"])
        & (repondus["erreur_connue"].isna() | (repondus["erreur_connue"] == ""))
    ]

    print(f"\n{'=' * 60}")
    print(f"  Bilan du jeu d'or ({n} avis)")
    print(f"{'=' * 60}")
    print(f"  Réponses  : {len(repondus)} / {n}")
    print(f"  Juste     : {justes}")
    print(f"  Abstention: {abstentions}")
    print(f"  Erreurs   : {erreurs_franches} total")
    print(f"    dont connues  : {len(erreurs_connues)}")
    print(f"    dont inattendu: {len(erreurs_inattendues)}")
    if len(erreurs_inattendues) > 0:
        print("\n  Erreurs inattendues :")
        for _, row in erreurs_inattendues.iterrows():
            print(f"    attendu={row['attendu']} obtenu={row['obtenu']} | {row['text'][:70]}")
    print()


def main() -> int:
    df = charger_jeu()
    resultats = predire_tous(df)
    afficher_bilan(resultats)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

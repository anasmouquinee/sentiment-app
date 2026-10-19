#!/usr/bin/env python
"""Mesure le compromis précision / renvoi vers humain selon le seuil d'abstention.

Usage :
  python src/courbe_seuil.py
"""
import sys
from pathlib import Path

import joblib
from sklearn.model_selection import train_test_split

sys.path.insert(0, str(Path(__file__).resolve().parent))
from train import GRAINE, MODELE, charger


def main() -> int:
    if not MODELE.exists():
        raise SystemExit("Modèle absent : lancez d'abord python src/train.py")

    pipeline = joblib.load(MODELE)
    df, _ = charger(allocine=False)
    _, X_test, _, y_test = train_test_split(
        df["review"], df["label"], test_size=0.2, random_state=GRAINE, stratify=df["label"]
    )
    probas = pipeline.predict_proba(X_test)
    scores_max = probas.max(axis=1)
    predictions = pipeline.predict(X_test)
    n = len(y_test)

    print(f"{'seuil':>6}  {'répond à':>9}  {'part':>6}  {'exactitude':>10}  {'erreurs':>8}  {'vers un humain':>14}")
    for seuil_int in range(50, 96, 5):
        seuil = seuil_int / 100
        masque = scores_max >= seuil
        repond = masque.sum()
        if repond == 0:
            continue
        exact = (predictions[masque] == list(y_test[masque])).mean()
        erreurs = (predictions[masque] != list(y_test[masque])).sum()
        vers_humain = n - repond
        part = repond / n
        print(
            f"{seuil:>6.2f}  {repond:>9}  {part:>6.0%}  {exact:>10.3f}  {erreurs:>8}  {vers_humain:>14}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

# Semaine 5 : l'interface, notes du binôme

> Trois questions, quelques phrases chacune. Répondez avec ce que vous avez observé.

## 1. Pourquoi l'interface n'importe-t-elle jamais `predict()` ni le fichier `.joblib` ?

L'interface est un client HTTP découplé de la couche d'inférence. En communiquant exclusivement avec l'API FastAPI (`/health` et `/predict`) via `ui.client`, un réentraînement du modèle, une modification de son algorithme interne ou le déploiement de l'API sur un serveur distant ne demandent aucune modification de la page Streamlit. Cela respecte la troisième règle d'architecture du projet : les clients consomment le service sans toucher aux artefacts du modèle.

## 2. Que montre l'interface quand le modèle hésite, et pourquoi est-ce mieux qu'un verdict forcé ?

Quand la confiance est inférieure au seuil d'abstention (0.60), comme pour le texte de test `xqzvb wlkptr grombu` (52 %), l'interface affiche le verdict `Je ne sais pas : à faire vérifier par un humain` accompagné d'un message informatif indiquant que la confiance est insuffisante. C'est nettement préférable à une décision binaire forcée, car cela évite de propager une prédiction fausse ou hasardeuse auprès des équipes métier et déclenche l'arbitrage par un opérateur humain sur les cas ambigus.

## 3. Que voit l'utilisateur quand l'API tombe ? Et le fichier `data/avis_exemple.csv` : combien d'avis partent vers un humain ?

Si l'API est arrêtée ou indisponible, `ui.client` intercepte l'exception réseau (`httpx.TransportError`) et la page affiche un message d'erreur clair en haut : `API injoignable : lancez d'abord uvicorn api.main:app` au lieu d'une trace d'erreur Python brute.
Dans le fichier `data/avis_exemple.csv` (6 avis au total, dont 3 positifs, 2 négatifs et 1 indéterminé), exactement **1 avis sur 6** (soit environ 17 %) part vers une vérification humaine.

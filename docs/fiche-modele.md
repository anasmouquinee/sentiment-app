# Fiche modèle : sentiment-app

## Identité du modèle

Modèle `tfidf-logreg` du paquet sentiment_app, version 0.6.0. Pipeline scikit-learn 1.5 : une
vectorisation TF-IDF (mots seuls et paires de mots, 316 termes), puis une régression logistique.
Entraîné sur le jeu de démonstration, avec la graine 42.

## Usage prévu

Trier les avis clients rédigés en français pour l'équipe de relation client, afin de repérer en
priorité les avis négatifs. Le modèle propose un verdict et une confiance ; l'API répond INDETERMINE
quand il hésite.

## Usages exclus

Décider seul d'un remboursement, d'une sanction ou d'une réponse envoyée au client ; analyser des
textes d'un autre domaine (critiques de films, messages internes) ou d'une autre langue ; évaluer une
personne, client ou salarié.

## Données d'entraînement

Jeu de démonstration de 290 avis synthétiques sur des produits (145 positifs, 145 négatifs), dont 100
avis mitigés et 30 neutres : 232 avis d'entraînement et 58 de test. Les tournures sont répétitives ;
l'ironie, l'argot et les fautes d'orthographe ne sont pas couverts.

## Performances mesurées

Sur les 58 avis de test : F1 macro 0.879, exactitude 0.879, rappel des négatifs 0.931 (lus dans
models/metrics.json). Avec le seuil d'abstention de l'API, 0.60, le modèle répond à 42 avis sur 58
(72 %) avec 2 erreurs au lieu de 7 ; les 16 autres vont à un humain.

## Limites connues

Le modèle ne voit pas l'ordre des mots : les avis qui se retournent (« Taille trop petite et retour
payant au déballage, sauf que ensuite produit conforme ») sont mal classés, et les 7 erreurs du jeu de
test sont toutes de ce type. Un texte sans mot connu reçoit toujours la même confiance, 0.5162. Le jeu
d'or garde une erreur franche déclarée : « Service client réactif et aimable, merci », classé négatif.

## Biais mesurés

Selon python src/biais.py, les avis avec un retournement (17 sur 58) n'ont que 0.588 d'exactitude,
contre 1.000 pour les avis directs, et 15 d'entre eux partent vers un humain. Les avis longs semblent
moins bien servis (0.741), mais c'est un effet du retournement : les 10 avis longs sans retournement
sont tous bien classés.

## Explicabilité

Selon python src/expliquer.py, des mots-outils (« je », « en », « au ») figurent parmi les termes les
plus influents : le modèle a appris des tournures du jeu de démonstration, pas seulement des mots porteurs
de sentiment. Sur l'avis mitigé, les termes présents se compensent presque (-1.006 contre +0.918) :
le modèle hésite (0.5335), et le terme le plus négatif, « déballage sauf », chevauche le retournement.

## Conditions d'usage

Un humain lit tout avis INDETERMINE, et tout avis négatif avant qu'une réponse parte au client. Le
modèle ne sert que pour des avis de produits rédigés en français ; aucune décision visant une personne
n'est prise sur sa seule sortie.

## Maintenance

Réentraîner dès que de nouveaux avis étiquetés sont disponibles, ou si le rappel des négatifs passe
sous 0.90 ; garder scikit-learn 1.5 pour l'entraînement et le paquet, car un modèle ne se relit
qu'avec la version qui l'a produit ; indiquer le modèle au paquet installé avec la variable
SENTIMENT_MODELE.

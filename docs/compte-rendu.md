# Compte rendu global des TP1 à TP3

**Binôme :** Anas Mouqine ([@anasmouqine](https://github.com/anasmouqine)) et Assia Nouaoury ([@nouaoury](https://github.com/nouaoury))  
**Dépôt :** https://github.com/anasmouquinee/sentiment-app  
**Date :** 12/10/2026  

---

## 1. Le besoin et son cadrage

### 1.1 Le problème métier
Une direction de la relation client opérant sur une plateforme de commerce en ligne reçoit quotidiennement des milliers d'avis d'acheteurs. Historiquement, ces messages étaient traités de façon linéaire, par ordre chronologique d'arrivée dans la boîte de réception générale. Cette absence de priorisation créait un risque opérationnel majeur : un client très mécontent exprimant une réclamation grave (produit défectueux, non-livraison, litige financier) pouvait patienter plusieurs jours avant qu'un conseiller n'ouvre son dossier, transformant une insatisfaction ponctuelle en résiliation ou en crise sur les réseaux sociaux. L'objectif fonctionnel consiste donc à intercepter les flux entrants, à détecter automatiquement les avis négatifs pour les placer en tête de file de traitement prioritaire, tout en isolant les cas ambigus pour une revue humaine.

### 1.2 L'approche retenue pour le cas 3
Pour répondre à ce besoin, nous avons formellement retenu une approche par **Machine Learning supervisé classique** (représentation TF-IDF associée à une régression logistique binaire), en écartant à la fois les règles métier manuelles et les modèles génératifs de type LLM. Ce choix découle directement de l'application rigoureuse de la grille d'aide à la décision :

* **(a) Données étiquetées :** L'historique d'exploitation e-commerce fournit immédiatement des dizaines de milliers d'avis passés associés à des évaluations chiffrées (notes de 1 à 5 étoiles). Les notes 1 et 2 étoiles constituent des étiquettes négatives fiables, gratuites et immédiatement disponibles en grande masse sans nécessiter de campagne d'annotation manuelle coûteuse.
* **(c) Coût par requête et latence :** Face à des volumes de plusieurs dizaines de milliers de requêtes par jour, un classifieur linéaire s'exécute en moins de deux millisecondes par inférence sur un serveur standard et engendre un coût d'infrastructure quasi nul. En comparaison, solliciter une API de modèle génératif (LLM) introduirait une latence de 500 ms à 2 s par avis ainsi qu'une facture récurrente prohibitive et imprévisible.
* **(d) Conséquence d'une erreur :** La criticité d'une mauvaise classification reste très modérée dans ce cas d'usage. Si un avis négatif est accidentellement classé comme positif ou neutre, il n'est pas perdu ni détruit : il reste dans la file générale d'attente et sera traité par les agents dans le délai habituel. Le système améliore la réactivité moyenne sans jamais dégrader le service existant.
* **(b) Vérifiabilité et stabilité :** La frontière de décision d'une régression logistique couplée aux n-grammes de TF-IDF est entièrement inspectable, stable dans le temps et facilement auditable via ses poids lexicaux, contrairement aux dérives potentielles de modèles non déterministes.

---

## 2. L'architecture du dépôt

### 2.1 Organisation modulaire du projet
Le dépôt `sentiment-app` a été conçu de manière incrémentale selon les principes d'ingénierie logicielle propre (séparation stricte des responsabilités, modularité et reproductibilité) :
* `app/` : Emplacement réservé pour l'exposition de l'API de prédiction (microservice FastAPI pour les étapes ultérieures).
* `data/` : Répertoire hébergeant les données tabulaires locales (`sample_reviews.csv` et le jeu généré `demo_reviews.csv`).
* `docs/` : Documentation d'architecture, fiches de cadrage initiales (`docs/cadrage/`) et comptes rendus de suivi hebdomadaire (`semaine2.md`, `semaine3.md`, `compte-rendu.md`).
* `models/` : Répertoire de destination des artefacts d'entraînement (contenant `metrics.json` et le modèle compilé `sentiment.joblib`).
* `notebooks/` : Notebooks interactifs (variantes Colab pour l'expérimentation et les démonstrations en ligne).
* `scripts/` : Outils d'automatisation, d'installation (`setup.ps1`, `setup.sh`) et de diagnostic d'environnement (`check_setup.py`, `verif_clone.sh`).
* `src/` : Cœur algorithmique de l'application comprenant la génération de données de test (`make_demo.py`), l'entraînement du pipeline (`train.py`), l'évaluation détaillée (`evaluate.py`) et l'inférence unitaire (`predict.py`).
* `ui/` : Interface utilisateur Streamlit (`app.py`) et fonctions pures d'aide au classement (`helpers.py`).
* `tests/` : Suite complète de 45 tests unitaires et d'intégration automatisés avec `pytest`.

### 2.2 Gestion des artefacts : Ce qui est versionné et ce qui ne l'est pas
Un principe fondamental de MLOps régit le dépôt : **tout ce qui est déterministe et reconstructible en une commande ne doit jamais être versionné dans Git**.

* **Ce qui n'est pas versionné (exclu par `.gitignore`) :**
  1. L'environnement virtuel `.venv/` : volumineux (> 300 Mo), dépendant de l'OS et de l'architecture locale. Il se recrée via `python -m venv .venv` et `pip install -r requirements.txt`.
  2. Le modèle binaire `models/sentiment.joblib` : un fichier binaire lourd qui saturerait rapidement l'historique Git sans valeur ajoutée de diff textuel. Il est entièrement reproductible en relançant `python src/train.py`.
  3. Les données générées ou volumineuses `data/demo_reviews.csv` : produites instantanément par `python src/make_demo.py`.
* **Pourquoi `models/metrics.json` est-il versionné alors que `models/sentiment.joblib` ne l'est pas ?**  
  `metrics.json` est un fichier texte léger contenant l'évaluation objective de la qualité du modèle (F1 score, exactitude, date d'entraînement, volume de données). Versionner ce fichier dans Git permet :
  1. De suivre l'évolution des performances du modèle commit par commit (traçabilité et auditabilité).
  2. De permettre à l'intégration continue (GitHub Actions CI) d'exécuter l'intégralité des 45 tests sans avoir à télécharger ni recalculer le modèle de plusieurs mégaoctets sur les runners GitHub, garantissant une CI ultra-rapide et légère.

---

## 3. Le modèle

### 3.1 Données, découpage et pipeline
L'apprentissage repose sur un pipeline scikit-learn standardisé assurant l'absence totale de fuite de données (*data leakage*) :
* **Découpage strict avant vectorisation :** La fonction `train_test_split(..., test_size=0.20, random_state=42, stratify=df['label'])` est exécutée sur le texte brut. Le vocabulaire et les fréquences inverses de documents (TF-IDF) sont appris exclusivement sur le sous-ensemble d'entraînement (`X_train`), empêchant toute contamination des fréquences du jeu de test.
* **Pipeline scikit-learn unifié :** L'objet `Pipeline` encapsule le `TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)` et le classifieur `LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)`. Cela garantit que la transformation textuelle appliquée lors de la prédiction en production est strictement identique à celle de la phase d'apprentissage.
* **Reproductibilité :** L'utilisation de la graine pseudo-aléatoire `random_state=42` fige le découpage et la convergence de l'optimiseur L-BFGS.

### 3.2 Résultats comparatifs
Le pipeline a été entraîné et évalué sur deux jeux de données distincts : le jeu synthétique de démonstration (conçu pour tester les limites du modèle) et le jeu réel public Allociné (20 000 critiques de cinéma).

| Jeu de données | Volume total | Train / Test | Vocabulaire retenu | F1 macro | Exactitude (Accuracy) | Rappel négatif |
| --- | --- | --- | --- | --- | --- | --- |
| **Démonstration** | 290 avis | 232 / 58 | 316 termes | **0,879** | 0,879 | 0,931 (27/29) |
| **Allociné (public)** | 20 000 avis | 16 000 / 4 000 | 149 529 termes | **0,920** | 0,920 | 0,911 (1 860/2 041) |

*Les résultats sur Allociné dépassent largement le seuil minimal requis de 0,85 fixé dans `tests/test_model.py`.*

### 3.3 Matrice de confusion sur le jeu de démonstration
L'évaluation sur les 58 avis de test du jeu de démonstration produit la matrice de confusion suivante :

```text
                  Prédit : Négatif    Prédit : Positif
Vérité : Négatif         27                   2
Vérité : Positif          5                  24
```

* **Lecture de la ligne 1 (Avis réellement négatifs, 29 cas) :**
  * 27 avis négatifs sont correctement classés (Vrais Négatifs, 93,1 % de rappel).
  * 2 avis négatifs sont classés par erreur comme positifs (**Faux Positifs métier**). Ce sont les erreurs les plus préjudiciables : un client mécontent n'est pas priorisé et risque d'attendre dans la file générale.
* **Lecture de la ligne 2 (Avis réellement positifs, 29 cas) :**
  * 5 avis positifs sont prédits comme négatifs (**Faux Négatifs métier**). Ces clients satisfaits sont orientés par erreur vers la file prioritaire ; l'impact est bénin car l'agent constatera rapidement la satisfaction du client.
  * 24 avis positifs sont fidèlement reconnus (Vrais Positifs, 82,8 % de spécificité).

---

## 4. L'analyse des erreurs

### 4.1 Caractérisation et exemples réels
Sur les 58 avis du jeu de test de démonstration, exactement **7 erreurs** sont relevées. L'analyse qualitative de ces 7 cas révèle qu'ils appartiennent tous sans exception à la catégorie des **avis mitigés ou complexes** contenant une concession stylistique.

Exemples extraits directement de nos données d'évaluation :
1. **Vérité = Négatif, Prédit = Positif (erreur critique) :**  
   > *« Service impeccable et livraison en avance sur le papier, sauf que ensuite produit cassé à l'arrivée et aucun remboursement »*  
   Le client commence par un éloge appuyé du service pour souligner sa déception finale.
2. **Vérité = Positif, Prédit = Négatif (erreur tolérable) :**  
   > *« Taille trop petite et retour payant au déballage, sauf que ensuite produit conforme à la description et vendeur réactif »*  
   L'avis commence par une friction logistique avant de conclure sur une issue très favorable.

### 4.2 Le mécanisme sous-jacent : L'absence d'ordre du sac de mots
Le modèle linéaire s'appuie sur une représentation vectorielle de type *Bag of Words* (TF-IDF). Dans ce paradigme, une phrase est réduite à un comptage non ordonné de n-grammes :
* Le modèle additionne le poids des mots à polarité positive (*« impeccable »*, *« avance »*) et le poids des mots à polarité négative (*« cassé »*, *« aucun remboursement »*).
* Il est incapable de repérer les marqueurs de rupture syntaxique (*« sauf que »*, *« mais finalement »*, *« cependant »*) qui inversent le sens de la proposition précédente.
* L'étiquette humaine dépend systématiquement de la proposition conclusive finale. Le modèle sac-de-mots, ignorant la structure séquentielle et la syntaxe, se laisse submerger par la densité lexicale de la première partie du texte.

### 4.3 Ce qu'il faudrait pour corriger
Pour résoudre ce comportement, il ne suffit pas d'ajouter des règles heuristiques ou des bigrammes supplémentaires :
1. **Embeddings contextuels et transformers (vus en semaine 9) :** L'emploi de modèles de type BERT ou RoBERTa (ex. CamemBERT pour le français) intégrant des mécanismes d'attention bidirectionnelle permet de capturer les relations d'ordre, la portée des négations et la hiérarchie temporelle des propositions.
2. **Pourquoi ce n'était pas le sujet de ces premières séances :** L'objectif pédagogique des TP1 à TP3 est de poser un socle d'ingénierie logicielle robuste, reproductible et mesurable (gestion de versions, tests unitaires, pipeline CI, déploiement d'interface). Avant de chercher à améliorer un modèle complexe, il est impératif de disposer d'une base de référence (*baseline*) simple, rapide, dont on comprend exactement les mécanismes d'échec.

---

## 5. L'interface et le seuil d'incertitude

### 5.1 Choix et formalisation du seuil
Dans l'interface Streamlit ([ui/helpers.py](file:///c:/Users/anasm/Downloads/sentiment-app/sentiment-app/ui/helpers.py)), nous avons paramétré la constante `SEUIL_INCERTITUDE = 0.60`.
Lorsqu'un avis est soumis, la régression logistique calcule la probabilité $P(\text{classe} \mid \text{texte})$. Si cette confiance maximale est strictement inférieure à 60 % ($\max(P) < 0,60$), le système refuse de trancher arbitrairement et attribue le statut explicite **« à vérifier »**.

### 5.2 Effet chiffré sur les données de démonstration
Nous avons testé la sensibilité de la file de vérification humaine en faisant varier le seuil sur les 290 avis de démonstration :

| Seuil d'incertitude | Avis renvoyés à vérification (« à vérifier ») | Proportion du flux orientée vers l'humain |
| --- | --- | --- |
| **0,55** | 63 / 290 | 21,7 % |
| **0,60 (retenu)** | **117 / 290** | **40,3 %** |
| **0,65** | 152 / 290 | 52,4 % |
| **0,70** | 201 / 290 | 69,3 % |
| **0,75** | 234 / 290 | 80,7 % |

### 5.3 L'arbitrage métier relation client
Ce compromis à **0,60** constitue un équilibre optimal entre sécurité relationnelle et productivité :
* Un seuil trop bas (0,50 ou 0,55) forcerait le modèle à classer des avis mitigés sur un coup de dé probabiliste, laissant passer des clients furieux dans la file normale.
* Un seuil trop élevé (0,75) engorgerait le service client en lui renvoyant plus de 80 % des avis, anéantissant l'intérêt même de l'automatisation.
* À 0,60, l'application automatise environ 60 % des avis dont le ton ne fait aucun doute, tout en protégeant les 40 % d'avis nuancés en les déléguant au discernement d'un agent humain.

---

## 6. Ce qui a échoué

Conformément à la démarche d'ingénierie, plusieurs difficultés réelles ont été rencontrées et résolues au cours des séances :

1. **Tests initiaux en échec lors de la découverte du kit (TP1) :**  
   Au premier lancement de `pytest -q`, 3 tests ont échoué et 4 ont été ignorés. Ce comportement a d'abord suscité une inquiétude avant que la lecture de `TESTS.md` ne confirme qu'il s'agissait de l'état nominal attendu : les 3 échecs signalaient les fiches de cadrage vides et les tests ignorés attendaient l'initialisation du dépôt Git.
2. **Dépendance manquante `pyarrow` lors de l'entraînement Allociné (TP2) :**  
   Lors de l'exécution de `python src/train.py --allocine`, le chargement du fichier distant au format Parquet a levé une exception `ModuleNotFoundError: No module named 'pyarrow'`. La commande d'installation initiale du TP1 n'avait installé que le triplet minimal (`pandas scikit-learn pytest`). L'installation de `pyarrow` et `streamlit` dans le `.venv` a permis de rétablir immédiatement l'exécution.
3. **Contrainte PowerShell d'exécution de scripts sous Windows :**  
   L'activation de l'environnement virtuel via `.venv\Scripts\Activate.ps1` a initialement été bloquée par la politique de sécurité Windows (`ExecutionPolicy`). Ce blocage a été levé via la commande `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.
4. **Gestion de l'arborescence lors de l'application des kits :**  
   Les scripts `appliquer_tp2.py` et `appliquer_tp3.py` nécessitent impérativement d'être lancés depuis le dossier du kit extrait à côté du dépôt et non depuis l'intérieur de `sentiment-app`, sous peine d'altérer les chemins relatifs.

---

## 7. Ce que vous feriez autrement

Avec le recul de ces trois séances et les ressources d'une équipe en environnement de production :
1. **Modèle de langage contextuel léger :** Nous remplacerions le sac de mots TF-IDF par un petit modèle transformer pré-entraîné (tel que DistilCamemBERT ou ModernBERT) adapté au français, fine-tuné avec une tête de classification pour résoudre définitivement les retournements de sentiment tout en conservant une latence inférieure à 20 ms.
2. **Gestion fine du neutre et multi-classes :** Le cadrage binaire (positif vs négatif) est réducteur ; de nombreux avis clients posent une simple question logistique sans charge affective. Une classification à trois classes (Positif / Neutre / Négatif) avec détection d'intention explicite (réclamation, question, remerciement) offrirait une valeur ajoutée supérieure.
3. **Pipeline DVC complet :** Bien que les données synthétiques soient isolées de Git, l'intégration de DVC (*Data Version Control*) connectée à un stockage objet (S3/GCS) permettrait de versionner le jeu Allociné et les artefacts de validation de façon plus stricte dès le démarrage.

---

## 8. Répartition du travail

| Membre | Ce qu'il a pris en charge |
| --- | --- |
| **Anas Mouqine** ([@anasmouqine](https://github.com/anasmouqine)) | Initialisation du dépôt Git, configuration de l'environnement, cadrage des cas 1 et 3, pipeline d'entraînement TP2 (`make_demo.py`, `train.py`) et architecture globale. |
| **Assia Nouaoury** ([@nouaoury](https://github.com/nouaoury)) | Intégration Git distante, cadrage du cas 2, évaluation et analyse des matrices de confusion (`evaluate.py`), expérimentation du seuil d'incertitude Streamlit (`helpers.py`) et validation des 45 tests. |

---

## Outils d'aide à la rédaction

Ce compte rendu a été structuré et synthétisé en binôme avec l'appui de l'assistant de programmation Antigravity AI pour la mise en forme du Markdown et l'extraction des métriques réelles de `models/metrics.json`, dont l'intégralité des calculs, des tests et des analyses a été vérifiée par nos soins.

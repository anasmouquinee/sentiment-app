# Fiche de cadrage : Questions sur le règlement intérieur

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Fournir aux étudiants et au personnel des réponses fiables et directement sourcées aux questions posées sur le règlement intérieur de l'école.

## Utilisateur final (obligatoire)

Les étudiants, enseignants et membres du personnel administratif souhaitant clarifier une règle ou une procédure scolaire.

## Approche retenue (obligatoire)

Cocher une seule case :

- [ ] Règles métier
- [ ] Machine learning
- [x] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(b) Les réponses doivent impérativement citer les articles officiels du règlement intérieur afin d'assurer une vérifiabilité indiscutable. (a) Aucun jeu volumineux de questions-réponses préalablement étiquetées n'est requis car la connaissance est entièrement contenue dans les documents institutionnels existants. (c) Le coût par requête reste modéré grâce à l'indexation vectorielle d'un corpus documentaire stable.

## Données nécessaires et leur origine (obligatoire)

Documents PDF et textes officiels à jour du règlement intérieur, des chartes informatiques et des règlements des examens fournis par la scolarité.

## Métrique de succès et seuil d'acceptation (obligatoire)

Précision de récupération documentaire (recall@3) supérieure à 0,95 et exactitude factuelle des citations supérieure à 0,90 évaluée sur un jeu d'évaluation de 100 questions types.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

En cas d'ambiguïté ou de score de confiance faible, l'application renvoie vers le secrétariat pédagogique avec un lien direct vers l'article concerné du document officiel.

## Risques éthiques ou de confidentialité (obligatoire)

Risque d'interprétation erronée des règles disciplinaires ou des droits étudiants ; aucun enregistrement nominatif des requêtes pour préserver la vie privée des usagers.

## Approche écartée et pourquoi (facultatif)

Modèle génératif seul écarté car il risque d'inventer des règles ou des articles inexistants, et règles métier trop rigides face à la diversité des questions en langage naturel.

# Fiche de cadrage : Priorisation des avis négatifs

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Détecter et prioriser automatiquement les avis clients négatifs ou critiques pour permettre un traitement rapide par l'équipe support.

## Utilisateur final (obligatoire)

Les gestionnaires de la relation client et les agents du service après-vente chargés de désamorcer les insatisfactions des clients.

## Approche retenue (obligatoire)

Cocher une seule case :

- [ ] Règles métier
- [x] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(a) La plateforme dispose de dizaines de milliers d'avis clients historiques accompagnés de notes de 1 à 5 étoiles constituant des données étiquetées immédiatement exploitables. (c) Le volume quotidien de plusieurs milliers d'avis impose un coût par requête quasi nul qu'un classifieur supervisé (TF-IDF + régression logistique) garantit parfaitement par rapport à un LLM. (d) La conséquence d'une erreur de classement est faible car un avis mal classé reste visible dans la file générale d'attente.

## Données nécessaires et leur origine (obligatoire)

Historique anonymisé des avis textuels et des notes associées extrait de la base e-commerce, filtré de tout identifiant personnel (nom, numéro de commande).

## Métrique de succès et seuil d'acceptation (obligatoire)

Rappel supérieur à 0,90 sur la classe des avis négatifs avec un score F1 macro d'au moins 0,85 sur le jeu de test pour ne rater aucun client mécontent.

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Les avis identifiés comme négatifs sont priorisés dans la file d'attente d'un agent humain qui valide ou requalifie l'avis avant d'engager une action commerciale.

## Risques éthiques ou de confidentialité (obligatoire)

Risques de biais algorithmiques envers certains types de vocabulaire ou dialectes, et fuite de données personnelles si les adresses ou téléphones des clients ne sont pas masqués.

## Approche écartée et pourquoi (facultatif)

Modèle génératif seul écarté en raison d'un coût financier prohibitif à grande échelle et d'une latence inutile pour une tâche de classification binaire ou ternaire.

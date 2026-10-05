# Fiche de cadrage : Ordonnances incomplètes en pharmacie

> Remplir chaque rubrique en une à trois phrases. Les rubriques marquées (obligatoire) sont vérifiées par `pytest`.

## Besoin en une phrase (obligatoire)

Détecter automatiquement les mentions obligatoires manquantes sur les ordonnances scannées ou saisies avant la délivrance des médicaments.

## Utilisateur final (obligatoire)

Les pharmaciens et préparateurs en pharmacie au comptoir, qui reçoivent une alerte immédiate en cas d'incohérence ou d'omission.

## Approche retenue (obligatoire)

Cocher une seule case :

- [x] Règles métier
- [ ] Machine learning
- [ ] RAG
- [ ] Modèle génératif seul

## Justification (obligatoire, citer au moins deux critères de la grille : (a) données étiquetées, (b) vérifiabilité, (c) coût par requête, (d) conséquence d'une erreur)

(b) Les critères de validité d'une ordonnance sont strictement codifiés par la réglementation de santé, exigeant une vérifiabilité totale et déterministe. (d) La conséquence d'une erreur médicale étant critique pour la santé du patient et la responsabilité légale du pharmacien, aucune ambiguïté n'est permise. De plus, (c) le coût par requête est quasi nul et l'exécution instantanée en local sans dépendance externe.

## Données nécessaires et leur origine (obligatoire)

Structure des champs d'ordonnance issue du logiciel de gestion d'officine (date, identification du praticien, posologie, signature), sans export de données de santé hors de l'officine.

## Métrique de succès et seuil d'acceptation (obligatoire)

Taux d'exactitude de 100 % sur la détection des champs obligatoires manquants, avec zéro faux négatif (rappel de 1,0 sur les ordonnances non conformes).

## Conséquence d'une erreur et validation humaine prévue (obligatoire)

Le système agit uniquement comme un assistant de pré-contrôle ; le pharmacien diplômé conserve la validation finale humaine obligatoire avant toute délivrance.

## Risques éthiques ou de confidentialité (obligatoire)

Traitement de données de santé hautement sensibles protégées par le secret médical et la réglementation (RGPD / loi 09-08) ; le traitement doit s'effectuer en local sans fuite vers des tiers.

## Approche écartée et pourquoi (facultatif)

Modèle génératif ou LLM écarté en raison du risque d'hallucination inacceptable dans le domaine de la santé, du coût récurrent élevé et du manque d'explicabilité déterministe.

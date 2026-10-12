# Analyse des erreurs du modèle (Semaine 2)

Sur les 58 avis du jeu de test de démonstration, le modèle commet 7 erreurs (2 faux positifs et 5 faux négatifs), qui portent toutes sur des avis mitigés comportant un retournement de situation (ex. « sauf que ensuite... »).
Ces erreurs surviennent parce que l'approche par sac de mots (TF-IDF) ignore l'ordre temporel et la syntaxe des mots : le modèle fait un décompte global des termes positifs et négatifs sans percevoir que la conclusion de la phrase inverse le sentiment initial.
Pour corriger ces erreurs, il faudrait utiliser des représentations contextuelles et sémantiques plus avancées comme des embeddings de phrases ou des modèles de type transformeur qui prennent en compte l'ordre et le contexte complet du texte.

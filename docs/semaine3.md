# Analyse du seuil d'incertitude (Semaine 3)

Nous retenons un seuil d'incertitude de 0,60 dans l'interface, qui déclenche automatiquement le statut « à vérifier » dès que le score de probabilité de la classe dominante est inférieur à 60 %.
Sur notre jeu d'évaluation de démonstration comportant une forte proportion d'avis ambigus (290 avis au total), ce réglage renvoie 117 avis (soit 40,3 %) vers un agent humain pour validation manuelle.
Ce compromis paraît juste car il sécurise la relation client en interceptant la grande majorité des avis mitigés ou à retournement où le modèle sac-de-mots est faillible, tout en automatisant le traitement de près de 60 % des flux clairement tranchés sans surcharger l'équipe support.

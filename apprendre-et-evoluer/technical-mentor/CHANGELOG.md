# Changelog

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) · versions : [SemVer](https://semver.org/lang/fr/).

## [0.2.0] — 2026-11-06

Première version dans le dépôt. La 0.1.0 n'existait qu'en local.

### Ajouté
- Règles d'écriture de la fiche en français simple.
- Mode notion en sept étapes : la solution est expliquée en mots avant tout code.
- Sujets « outil » : où l'outil tourne, ce qu'il fait vraiment, bonnes pratiques, FAQ, test de sortie des 80 %.
- `verifier.py` contrôle le nombre d'étapes selon le mode, les phrases trop longues, les analogies interdites et les langages de coloration du code.

### Corrigé
- Les scripts trouvent le dossier des fiches à partir du dossier personnel, sans chemin Windows en dur.

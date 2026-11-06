# Changelog

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) · versions : [SemVer](https://semver.org/lang/fr/).

## [0.2.0] — 2026-11-06

### Ajouté
- Remplace **Roadmap projets** (0.1.0), avec le même rôle : savoir où en est un projet ou une organisation.
- Deux maps par demande : `par-volet` et `par-lot` pour un projet, `par-projet` et `lots-restants` pour une organisation.
- Scripts de collecte (`collecter_projet.py`, `collecter_orga.py`) et de rendu (`generer_maps.py`) : le script calcule les couleurs, les phases, l'avancement et le verdict.
- Chaque lot porte sa source : le script refuse un lot sans source.
- Comparaison entre le plan et l'application réelle.
- 36 tests automatiques (`scripts/test_generer_maps.py`).

### Retiré
- Gabarits HTML et exemple de réponse de Roadmap projets, qui contenaient des données réelles de projets.

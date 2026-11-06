# Changelog

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) · versions : [SemVer](https://semver.org/lang/fr/).

## [0.4.0] — 2026-11-06

### Ajouté
- Choix du nombre de colonnes : trois boutons 1, 2, 3 au-dessus des cartes, dans la conversation, sans régénérer. Les cartes gardent leur ordre de lecture.
- Option `--colonnes 1|2|3` : nombre de colonnes à l'ouverture, dans la conversation et dans le HTML.
- Test du choix des colonnes (38 tests).

### Corrigé
- La 0.3.0 forçait une seule colonne dans la conversation. La map s'ouvre maintenant en 2 colonnes.

## [0.3.0] — 2026-11-06

### Modifié
- Les maps sont dessinées directement dans la conversation avec `show_widget`, comme dans Roadmap projets. Plus besoin de Chrome ni d'Edge.
- `generer_maps.py` écrit un `<map>.widget.html` par map : fragment prêt pour `show_widget`, aux couleurs du thème de la conversation (clair et sombre).
- Le PNG devient optionnel : option `--png`. L'ancienne option `--sans-png` disparaît.

### Ajouté
- Test du fragment : pas de DOCTYPE, pas de commentaire, deux graisses, rien sous 11 px, aucune couleur en dur.

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

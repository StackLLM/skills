# Piloter les projets

> Suite de Skills StackLLM · usage interne, pas encore commercialisée

**Savoir où en est chaque projet, et le tenir au niveau d'une grande équipe.**

| Skill | Rôle | Version |
|---|---|---|
| `map-projet-reponse` | La map d'avancement d'un projet ou d'une organisation GitHub, **affichée dans la conversation** : volets, lots, phases, bloquants, verdict. Réglage 1, 2 ou 3 colonnes. Rien à installer. | 0.1.0 |
| `map-projet` | Les mêmes maps **en fichiers** : 2 PNG et 2 HTML, à garder, imprimer ou envoyer. Le PNG demande Chrome ou Edge. | 0.5.0 |
| `adviser-dev` | Le conseiller de développement. Projet existant : audit du socle, rapport de refactoring en lots, accompagnement lot par lot. Projet à créer : socle `frontend/` + `backend/` prêt pour la production (tests, CI, Docker, santé, limites, en-têtes, journaux, sauvegarde). Se lance seulement avec `/adviser-dev`. | 0.1.0 |

Les deux skills de map lisent le même `carte.json` : une carte faite pour l'une marche telle quelle dans l'autre.

## Installation

Depuis la racine du dépôt `skills` :

```bash
./install.sh map-projet-reponse map-projet adviser-dev
```

Ou comme plugins Claude Code (voir le README racine) :

```bash
/plugin install map-projet-reponse --marketplace StackLLM/skills
/plugin install map-projet --marketplace StackLLM/skills
/plugin install adviser-dev --marketplace StackLLM/skills
```

## Prérequis

- Python 3, bibliothèque standard seulement.
- `gh` authentifié pour une organisation GitHub (maps) ou un dépôt distant (`adviser-dev`).
- `map-projet` : Chrome ou Edge pour les PNG.
- `adviser-dev` : piles de l'équipe seulement (Vite + React + TypeScript + Tailwind, FastAPI, Node, SQLite, PostgreSQL).

## Limites connues

- Les deux maps se déclenchent sur des phrases proches. Pour la version fichiers, demander les fichiers ou le PNG.
- Les commandes des `SKILL.md` sont écrites `python` : sur macOS, c'est `python3`.

## Tests

```bash
cd map-projet-reponse/scripts && python3 test_generer_widget.py
cd map-projet/scripts && python3 test_generer_maps.py
```

## Licence

Propriétaire, tous droits réservés. Voir le [LICENSE](../LICENSE) du dépôt.

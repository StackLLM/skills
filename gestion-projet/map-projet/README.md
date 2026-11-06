# Map projet

> Skill StackLLM · v0.4.1 · usage interne, pas encore commercialisée

**« On est où ? » — deux maps et un verdict.**

Map projet montre où en est un projet ou toute une organisation GitHub. Les deux maps sont dessinées directement dans la conversation, avec une version HTML à télécharger. Aucun dossier n'est créé dans le projet.

Remplace **Roadmap projets** (0.1.0).

## Le problème

Quand on mène plusieurs projets, ou un gros projet à plusieurs volets, l'état réel se perd entre les plans, les suivis de lots, les README et l'historique Git. On ne sait plus ce qui est fait, ce qui reste et ce qui bloque.

## Ce que fait Map projet

| Demande | Map 1 | Map 2 |
|---|---|---|
| Un projet | `par-volet` : volets × phases, une carte par volet | `par-lot` : tous les lots de chaque volet, en détail |
| Une organisation | `par-projet` : projets × phases, une carte par projet | `lots-restants` : ce qui reste sur chaque projet |

Les phases : Cadrage, Construction, Pré-production, Bêta, Lancement.

- **Collecte** par script : où chercher dans le projet ou dans chaque dépôt.
- **Compare** le plan et l'application réelle.
- **Chaque lot porte sa source** : fichier, commit, ticket ou demande datée. Sans preuve, le lot passe « à confirmer ». Le script refuse un lot sans source.
- **Le script calcule** les couleurs, la phase, l'avancement et le verdict. Rien n'est estimé à la main.
- **1, 2 ou 3 colonnes** : trois boutons au-dessus des cartes, ou « en 3 colonnes » dans la demande.
- **Lecture seule** : rien n'est modifié, l'application n'est pas lancée, aucun `.env` n'est ouvert.

## Pour qui

Fondateurs, responsables de produit et développeurs qui pilotent plusieurs projets, ou qui reprennent un projet dont ils ont perdu le fil.

## Installation

Depuis la racine du dépôt `skills` :

```bash
./install.sh map-projet
```

Ou comme plugin Claude Code (accès GitHub requis, voir le README racine) :

```bash
/plugin marketplace add StackLLM/skills
/plugin install map-projet --marketplace StackLLM/skills
```

## Utilisation

Dans Claude Code :

- « fais-moi la map du projet », « où en est ce projet », « quels lots il me reste » : mode projet.
- « map de l'orga », « où en sont mes projets » : mode organisation.

## Prérequis

- Python 3.9 ou plus (`python3`), bibliothèque standard seulement.
- `gh` authentifié pour lire une organisation GitHub.
- Claude Code avec l'outil de visualisation en ligne (`show_widget`). Sans lui, les maps arrivent en fichiers HTML.
- Seulement pour une image PNG (option `--png`) : Chrome ou Edge. Autre chemin : variable `CHROME`.

## Limites connues

- Elle ne vaut que ce que valent les documents du projet : sans plan ni suivi de lots, beaucoup de lots restent « à confirmer ».
- Le découpage en volets d'un plan rangé par phases est fait par la Skill, pas par le plan.

## Tests

```bash
cd scripts && python3 test_generer_maps.py
```

38 tests : contrôle de la carte, calculs, rendu, fragment pour la conversation, colonnes.

## Contenu

| Chemin | Rôle |
|---|---|
| `SKILL.md` | règles, collecte, découpage, livraison |
| `references/format-carte.md` | format de `carte.json` |
| `scripts/collecter_projet.py` | inventaire d'un projet |
| `scripts/collecter_orga.py` | inventaire d'une organisation |
| `scripts/generer_maps.py` | contrôle de `carte.json`, rendu des deux maps pour la conversation et en HTML |
| `scripts/exemple-projet.json` | carte d'exemple |
| `scripts/test_generer_maps.py` | tests automatiques |

## Mise à jour

`git pull` à la racine du dépôt. Les changements sont dans `CHANGELOG.md`.

## Licence

Propriétaire, tous droits réservés. Voir le [LICENSE](../../LICENSE) du dépôt.

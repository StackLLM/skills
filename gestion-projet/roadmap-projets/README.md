# Roadmap projets

> Skill StackLLM · v0.1.0 · usage interne, pas encore commercialisée

**« On est où ? » — la réponse en une image, puis trois listes courtes.**

Roadmap projets affiche l'état d'avancement directement dans la conversation, avec un roadmap visuel, puis trois sections : ce qui avance, ce qui attend une action de votre part, les décalages à corriger.

## Le problème

Quand on mène plusieurs projets, ou un gros projet à plusieurs volets, l'état réel se perd entre les plans, les suivis de lots, les README et l'historique Git. Les documents se contredisent, et on ne sait plus ce qui attend sa propre validation.

## Ce que fait Roadmap projets

Deux modes, un même rendu.

- **Mode organisation** : tous les projets d'une organisation GitHub (ou d'un dossier de projets) sur cinq phases : Cadrage, Construction, Pré-production, Bêta, Lancement. Une carte par projet, avec barre de progression, ce qui manque et l'action humaine.
- **Mode projet** : un seul projet, découpé volet par volet (IA, front, backend, base de données, infra, sécurité…). Chaque carte de volet montre ses lots ou ses étapes sur une timeline, avec « vous êtes ici ».

Dans les deux cas :

- Lit d'abord vos documents : plans, contextes, suivis de lots, roadmaps, README. Confirme ensuite avec le code et l'historique Git.
- Distingue « livré, à valider » de « terminé ».
- Calcule chaque barre de progression : rien n'est estimé.
- Cite ses sources et dit quand elles sont périmées.
- Ne modifie rien : elle propose de corriger les décalages, sans le faire.

## Pour qui

Fondateurs, responsables de produit et développeurs qui pilotent plusieurs projets, ou qui reprennent un projet dont ils ont perdu le fil.

## Installation

Depuis la racine du dépôt `skills` :

```bash
./install.sh roadmap-projets
```

## Utilisation

Dans Claude Code :

- « on est où dans nos projets », « roadmap de l'organisation » : mode organisation.
- « je suis perdu dans ce projet », « fais le point sur X » : mode projet.

## Prérequis

- Claude Code avec l'outil de visualisation en ligne (sinon, tableaux Markdown de repli).
- `gh` authentifié pour lire une organisation GitHub.

## Limites connues

- Elle ne vaut que ce que valent les documents du projet : sans plan ni suivi de lots, l'état est déduit du code, et la réponse le dit.
- Le découpage en volets d'un plan rangé par phases est fait par la Skill, pas par le plan. Il est signalé comme tel.
- `references/exemple-reponse.md` et `references/gabarit-orga.html` contiennent des données réelles de projets StackLLM. À remplacer par des exemples génériques avant toute distribution.

## Contenu

| Chemin | Rôle |
|---|---|
| `SKILL.md` | règles, deux modes, ordre de la réponse |
| `references/collecte.md` | où chercher, commandes, repérage des décalages |
| `references/gabarit-orga.html` | roadmap du mode organisation |
| `references/gabarit-projet.html` | roadmap du mode projet : cartes de volet avec timeline |
| `references/exemple-reponse.md` | réponse complète à imiter |

## Mise à jour

`git pull` à la racine du dépôt. Les changements sont dans `CHANGELOG.md`.

## Licence

Propriétaire, tous droits réservés. Voir le [LICENSE](../../LICENSE) du dépôt.

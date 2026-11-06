# Technical Mentor

> Skill StackLLM · v0.2.0 · usage interne, pas encore commercialisée

**Savoir nommer une technologie ne suffit pas. Il faut savoir la faire et la défendre.**

Technical Mentor transforme une notion mal maîtrisée en compréhension d'ingénieur. Il produit une fiche HTML premium : le problème, le mécanisme, la solution en mots, la mise en œuvre réelle, les compromis et les questions d'un expert en entretien.

## Le problème

On peut dire « j'utiliserais du rate limiting ». On bloque à la question suivante : « à quel niveau tu le places, et comment tu comptes les requêtes avec trois instances ? » Les explications courantes restent en surface ou passent par des analogies qui ne tiennent pas devant un expert.

## Ce que fait Technical Mentor

- **Aucun terme technique avant sa définition.** Chaque mot est défini sur place.
- **Mode notion** (sept étapes) : problème, mécanisme, solution en mots, mise en œuvre réelle (code, config, commandes expliqués ligne par ligne), niveau ingénieur, face-à-face expert, contrôle.
- **Mode architecture** : part de la carte d'un système réel et de ses échanges, sans la partie « problème ».
- **Sujets « outil »** : où il tourne, ce qu'il fait vraiment, bonnes pratiques, FAQ.
- **Pas d'analogie de cuisine ou de voiture** : les exemples viennent de vrais projets informatiques.
- Couvre développement, architecture, systèmes, réseaux, Linux, DevOps, Cloud, IA et cybersécurité, y compris le hacking éthique en cadre autorisé.

## Pour qui

Développeurs qui préparent un entretien technique, ou qui veulent passer de « je connais le mot » à « je sais le mettre en place ».

## Installation

Depuis la racine du dépôt `skills` :

```bash
./install.sh technical-mentor
```

Ou comme plugin Claude Code (accès GitHub requis, voir le README racine) :

```bash
/plugin marketplace add StackLLM/skills
/plugin install technical-mentor --marketplace StackLLM/skills
```

## Utilisation

Dans Claude Code :

- « explique-moi X », « je ne maîtrise pas X », « comment ça marche vraiment » : mode notion.
- « prépare-moi à une question d'entretien sur X » : mode notion, accent sur le face-à-face expert.
- « explique-moi l'architecture de X », « de localhost à la prod » : mode architecture.

Les fiches sont écrites dans `~/Documents/REVISION-TECHNIQUE/Technical-words/`, avec un index.

## Prérequis

- Python 3, bibliothèque standard seulement.

## Limites connues

- Pas de tests automatiques des scripts. `verifier.py` contrôle les fiches, pas la Skill elle-même.
- Le contenu technique dépend de la recherche disponible dans la session. Sans recherche, la fiche le signale.

## Contenu

| Chemin | Rôle |
|---|---|
| `SKILL.md` | règles, étapes, modes, livrable, vérifications |
| `references/domaines.md` | ce qu'un expert attend, domaine par domaine |
| `references/parcours.md` | progression entre les fiches |
| `references/gabarit-html.md` | structure HTML d'une fiche |
| `references/mentor.css` | charte des fiches |
| `scripts/indexer.py` | injecte la charte, reconstruit l'index |
| `scripts/verifier.py` | contrôle mécanique de la checklist |

## Mise à jour

`git pull` à la racine du dépôt. Les changements sont dans `CHANGELOG.md`.

## Licence

Propriétaire, tous droits réservés. Voir le [LICENSE](../../LICENSE) du dépôt.

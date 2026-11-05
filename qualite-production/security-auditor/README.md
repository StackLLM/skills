# Security Auditor

> Skill StackLLM · v0.1.0 · usage interne, pas encore commercialisée

**Chercher comment une application peut être attaquée, pas cocher des cases.**

Security Auditor audite un projet local ou un ou plusieurs dépôts GitHub d'une même solution. Il comprend d'abord l'architecture réelle, puis cherche les chemins d'attaque. Il rend un rapport HTML premium, avec les valeurs sensibles masquées.

## Le problème

Beaucoup d'applications partent en production sans audit. Les checklists génériques produisent du bruit et ratent les vraies failles, propres à l'architecture du projet.

## Ce que fait Security Auditor

- Reconstruit l'architecture et les portes d'entrée du projet.
- Cherche les secrets exposés, y compris dans l'historique Git.
- Examine le contrôle des accès, l'authentification, les sessions, les API, les uploads, les injections, les dépendances, la configuration, les en-têtes, le chiffrement et le hachage.
- Pour chaque constat : criticité, niveau de confiance (confirmé, probable, à vérifier), scénario d'attaque, impact, étapes de correction.
- N'affiche jamais un secret en entier.

## Pour qui

Freelances, PME et startups qui livrent des applications sans équipe sécurité dédiée.

## Installation

Depuis la racine du dépôt `skills` :

```bash
./install.sh security-auditor
```

Ou comme plugin Claude Code, depuis le marketplace privé du dépôt (voir le README racine) :

```bash
/plugin marketplace add StackLLM/skills
/plugin install security-auditor --marketplace StackLLM/skills
```

Voir le [README du dépôt](../../README.md) pour l'installation complète.

## Utilisation

Dans Claude Code : « audit de sécurité », « est-ce que mon app est sécurisée », « revue sécurité avant production ».

Scripts utilisables seuls (Python 3, bibliothèque standard) :

```bash
python3 scripts/sonder_projet.py <projet> [--dependances]
python3 scripts/chercher_secrets.py <projet> [--historique]
python3 scripts/rapport.py scripts/constats.exemple.json --sortie rapport.html
```

## Prérequis

- Python 3.
- `gh` authentifié pour auditer des dépôts GitHub.

## Limites connues

- Ne remplace pas un test d'intrusion ni un audit certifié.
- Analyse statique du code et de la configuration : rien n'est attaqué en réel.
- Fait référence à des Skills complémentaires optionnelles (`atelier:*`) qui ne sont pas fournies.

## Contenu

| Chemin | Rôle |
|---|---|
| `SKILL.md` | règles et déroulé en six temps |
| `references/` | méthode d'attaque, contrôles, secrets, format du rapport |
| `scripts/` | sondage du projet, recherche de secrets, rendu du rapport, exemple de constats |

## Mise à jour

`git pull` à la racine du dépôt. Les liens installés suivent automatiquement. Les changements sont dans `CHANGELOG.md`.

## Licence

Propriétaire, tous droits réservés. Voir le [LICENSE](../../LICENSE) du dépôt.

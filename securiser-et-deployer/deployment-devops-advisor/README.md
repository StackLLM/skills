# Deployment Advisor

> Skill StackLLM · v0.1.0 · usage interne, pas encore commercialisée

**« Ça marche chez moi » : vérifier que ça marchera aussi en production.**

Deployment Advisor analyse un projet local ou un ou plusieurs dépôts GitHub. Il cherche ce qui va casser au passage en production, compare les architectures possibles avec leur coût, et rend un rapport HTML premium avec des checklists.

## Le problème

Une application qui tourne sur le poste du développeur échoue souvent une fois déployée : variable d'environnement absente, `localhost` en dur, stockage effacé au redémarrage, CORS, HTTPS. Ces pannes se découvrent tard, en production.

## Ce que fait Deployment Advisor

- Comprend ce que fait l'application et ce dont elle a besoin.
- Cherche les pièges : variables d'environnement, adresses et ports en dur, chemins Windows, build, migrations, stockage non persistant, CORS, proxy inverse, HTTPS, DNS, santé du service, journaux, sauvegarde, retour arrière.
- Compare les architectures de déploiement possibles, avec coût et complexité.
- Dimensionne une IA locale si le projet en utilise une.
- Rend un rapport avec trois checklists : avant, pendant et après le déploiement.
- Chaque constat porte son niveau de confiance. Aucun problème inventé.

## Pour qui

Développeurs et petites équipes qui ne sont pas spécialistes de l'infrastructure.

## Installation

Depuis la racine du dépôt `skills` :

```bash
./install.sh deployment-devops-advisor
```

Ou comme plugin Claude Code, depuis le marketplace privé du dépôt (voir le README racine) :

```bash
/plugin marketplace add StackLLM/skills
/plugin install deployment-devops-advisor --marketplace StackLLM/skills
```

Voir le [README du dépôt](../../README.md) pour l'installation complète.

## Utilisation

Dans Claude Code : « est-ce que je peux déployer », « ça marche en local mais pas en prod », « comment héberger ce projet ».

Scripts utilisables seuls (Python 3, bibliothèque standard) :

```bash
python3 scripts/verifier_prod.py <projet>
python3 scripts/rapport.py scripts/constats.exemple.json --sortie rapport.html
```

## Prérequis

- Python 3.
- `gh` authentifié pour analyser des dépôts GitHub.

## Limites connues

- Conseille et vérifie : ne déploie rien et ne modifie pas l'infrastructure.
- Les coûts d'hébergement sont des ordres de grandeur, à confirmer chez le fournisseur.
- Fait référence à des Skills complémentaires optionnelles (`atelier:*`) qui ne sont pas fournies.

## Contenu

| Chemin | Rôle |
|---|---|
| `SKILL.md` | règles et déroulé en six temps |
| `references/` | pièges local → prod, architectures, IA locale, parcours, format du rapport |
| `scripts/` | détection des pièges, rendu du rapport, exemple de constats |

## Mise à jour

`git pull` à la racine du dépôt. Les liens installés suivent automatiquement. Les changements sont dans `CHANGELOG.md`.

## Licence

Propriétaire, tous droits réservés. Voir le [LICENSE](../../LICENSE) du dépôt.

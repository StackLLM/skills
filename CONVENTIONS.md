# Conventions

Règles communes à toutes les Skills du dépôt.

## Rangement

- Une Skill = un dossier, dans une **catégorie** : `frontend/`, `qualite-production/`, `documentation/`, `carriere/`, `commun/`.
- Nom du dossier en minuscules avec tirets. Le nom déclaré (`name:` dans `SKILL.md`) est celui qu'on installe.
- Nouvelle catégorie seulement quand aucune ne convient. L'ajouter alors au README racine.

## Contenu d'une Skill

| Fichier ou dossier | Obligatoire | Rôle |
|---|---|---|
| `SKILL.md` | oui | instructions et règles d'exécution, avec `name` et `description` en en-tête |
| `README.md` | oui (ou README de catégorie pour une suite) | valeur, capacités vérifiées, installation, prérequis, limites |
| `CHANGELOG.md` | oui (ou celui de la catégorie pour une suite) | historique des versions |
| `references/` | si utile | méthode détaillée, lue à la demande |
| `scripts/` | si utile | outils exécutables |
| `tests/` ou `exemples/` | si disponible | preuve que la Skill marche |

Pas de fichier vide pour respecter la structure. La licence et le `.gitignore` sont à la racine, communs à tout le dépôt.

## Dépendances

- Une dépendance entre Skills est **déclarée** dans le README, jamais copiée.
- Les Skills qui dépendent l'une de l'autre restent dans la même catégorie, côte à côte (ex. CloneMe, UI Stealer et Animation Stealer).
- Scripts : bibliothèque standard de préférence. Toute dépendance externe est citée dans les prérequis.

## Versions

- SemVer par Skill : `0.x` tant qu'elle n'est pas commercialisée.
- Chaque changement visible va dans le `CHANGELOG.md` de la Skill. Le `CHANGELOG.md` racine résume les versions de la gamme.

## Règles partagées par toutes les Skills

- Aucune valeur inventée : ce qui n'est ni lu ni mesuré est marqué comme déduction.
- Chaque constat porte son niveau de confiance.
- Validation par mesure, test ou contrôle avant de livrer.
- Écriture selon `commun/explainer`.

## Avant chaque envoi

- Rechercher secrets, données personnelles et chemins locaux :

  ```bash
  python3 qualite-production/security-auditor/scripts/chercher_secrets.py .
  ```

- Après les tests de cv-ats, nettoyer les chemins absolus de `carriere/cv-ats/tests/resultats/*/_controle/rapport.json`.
- Aucune donnée client, aucune information interne d'un employeur ou d'un autre projet.

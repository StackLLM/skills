# Changelog

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) · versions : [SemVer](https://semver.org/lang/fr/).

## 2026-11-14 (4)

### Modifié
- `adviser-dev` 0.1.3 : le commit `livraison` se pose à la fin d'une phase pour la mettre en production. Rappelé seulement quand le dev dit la phase finie, comme dans `libelle-de-commit` 0.1.1.

## 2026-11-14 (3)

### Corrigé
- `adviser-dev` 0.1.2 : plus aucune mention d'un outil de prime interne. Le commit `livraison` borne la livraison ; les libellés suivent `libelle-de-commit`.

## 2026-11-14 (2)

### Corrigé
- `map-projet` 0.5.1, `map-projet-reponse` 0.1.1, `adviser-dev` 0.1.1 : commandes en `python3` avec le chemin de la skill (`python` n'existe pas sur macOS).
- Plus aucun nom de projet ou d'organisation d'un employeur : exemples en `StackLLM`, comptes de projets sans noms dans `adviser-dev/references/piles.md`.

## 2026-11-14

### Ajouté
- Suite **Piloter les projets**, qui remplace la catégorie `gestion-projet/`.
- `adviser-dev` 0.1.0 : conseiller de développement, audit et création de socle, modèles Node et Python.
- `map-projet-reponse` 0.1.0 : la map affichée dans la conversation, réglage 1, 2 ou 3 colonnes.

### Modifié
- `map-projet` 0.5.0 : retour à la version de l'auteur (maps en fichiers PNG et HTML). L'affichage dans la conversation passe à `map-projet-reponse`. Les versions 0.3.0 à 0.4.1 restent dans l'historique Git.

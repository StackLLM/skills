# Git, CI et livraison — de la branche de travail à main

## Sommaire

1. Les trois niveaux de branches
2. Le quotidien : une fonction, une branche
3. La CI : ce qu'elle vérifie
4. La livraison vers main
5. Régler GitHub (une seule fois)
6. Les cas difficiles
7. Commits et Pull Requests

---

## 1. Les trois niveaux de branches

```text
feature/<nom>   le travail d'une fonction ou d'une correction      courte : quelques jours
dev             la recette : ce qui est fini et attend la prod     permanente
main            la production : ce qui est en ligne                 permanente, protégée
```

- `main` ne reçoit **que** des commits déjà passés par `dev` et une CI verte.
- `dev` ne reçoit **que** des branches terminées, par Pull Request, CI verte.
- Personne ne travaille directement sur `main`. Personne ne force (`--force`) sur `dev` ou `main`.

Préfixes de branche : `feature/` (fonction nouvelle), `fix/` (correction),
`refactor/` (réorganisation sans changement visible), `docs/`, `chore/`
(outillage). Le nom dit ce que la branche apporte : `feature/reservation-en-ligne`.

Un projet existant avec une branche personnelle (`dev-oam`…) la garde comme
branche de recette, ou passe à `dev` : c'est réglé dans `.github/livraison.json`
(`brancheRecette`).

---

## 2. Le quotidien

```bash
git switch dev; git pull
git switch -c feature/reservation-en-ligne
# … travail, commits réguliers …
npm run verifier                       # la même chose que la CI, en local
git push -u origin feature/reservation-en-ligne
```

Puis sur GitHub : Pull Request `feature/reservation-en-ligne` → `dev`.

- La CI tourne sur la PR. Rouge = on corrige sur la branche, on repousse.
- Relecture par un autre dev quand c'est possible (au moins un « approuvé »).
- Fusion : **squash** (un commit propre par fonction sur `dev`) ou merge, au
  choix de l'équipe, mais le même partout.
- Branche supprimée après fusion.

Avant d'ouvrir la PR, si `dev` a avancé : `git merge origin/dev` dans la
branche, régler les conflits **chez soi**, relancer `npm run verifier`.

---

## 3. La CI

Fichier `.github/workflows/ci.yml`. Elle tourne à **chaque push** et sur chaque PR.

| Job | Quand | Ce qu'il vérifie |
|---|---|---|
| `verifier` | toujours | installation exacte (`npm ci`, `uv sync --frozen`), types, lint, tests, compilation |
| `pret-pour-main` | seulement sur un commit `livraison` poussé sur la branche de recette | la branche est bien la recette ; `main` peut avancer **sans conflit** (avance rapide) |

Règles de la CI :

- `permissions: contents: read` : la CI ne peut rien écrire dans le dépôt.
- `concurrency` : un nouveau push annule la CI précédente de la même branche.
- `timeout-minutes` sur chaque job : une CI bloquée ne consomme pas des heures.
- Versions des actions vérifiées et épinglées (majeure).
- Le job `image` (fichier `image.yml`) construit l'image Docker sur `main` et
  sur les tags `v*`, **après** une CI verte, et la publie sur GHCR (le registre
  d'images de GitHub). Avec des miroirs, seule l'organisation principale publie.

### Le job « prêt pour main », en clair

Quand le commit poussé s'appelle exactement `livraison` :

1. il vérifie que la branche est la branche de recette (`dev`, ou celle de `livraison.json`) ;
2. il récupère `main` et vérifie que `main` est **déjà contenu** dans la branche
   (`git merge-base --is-ancestor origin/main HEAD`). Si oui, `main` pourra
   avancer jusqu'à ce commit sans fusion, donc sans conflit possible ;
3. sinon il échoue avec la marche à suivre : `main` a reçu des commits qui ne
   sont pas dans la recette (un correctif urgent, par exemple) ; il faut d'abord
   fusionner `main` dans la recette.

Ce job ne pousse **rien**. Il dit seulement « tout est prêt ». GitHub envoie
le résultat par mail.

---

## 4. La livraison vers main

```bash
# sur la branche de recette, quand ce qui doit partir est fini et vérifié
git switch dev; git pull
git commit --allow-empty -m "livraison"
git push
# → la CI tourne ; le mail de GitHub arrive : vert ou rouge
```

CI verte : lancer `livrer.bat` (Windows) ou `sh livrer.sh` (Mac, Linux).
Le script `.github/livrer.mjs` vérifie, dans l'ordre :

1. on n'est pas sur `main` ;
2. le dernier commit s'appelle exactement `livraison` ;
3. rien n'est modifié sans être commité ;
4. ce commit est bien celui qui est sur GitHub (poussé, et la branche n'a pas bougé) ;
5. la CI de **ce commit précis** est terminée et verte (via `gh`) ;
6. il affiche les dépôts concernés et demande `OUI`.

Puis il pousse ce commit vers `main` dans chaque dépôt de `livraison.json`,
**sans force**. Si `main` a bougé à côté, Git refuse : rien n'est écrasé.

**Pourquoi à la main et pas automatique** : la livraison est une décision.
Le mail vert dit « c'est possible », le dev décide « on y va ». Un script peut
automatiser la poussée (job déclenché par la CI verte) ; l'équipe a choisi la
version manuelle, plus sûre tant qu'il n'y a pas de recette automatisée.

**Le commit `livraison`** est aussi la borne de la livraison dans l'historique :
seul le dev sait quand le cahier des charges est fini. Ni l'IA ni la skill ne
le créent ou ne le proposent.

---

## 5. Régler GitHub (une seule fois par dépôt)

### Protéger les branches (Settings → Rules → Rulesets)

| Branche | Règles |
|---|---|
| `main` | bloquer la suppression ; bloquer les poussées forcées ; (optionnel) restreindre les mises à jour aux responsables de livraison |
| `dev` | bloquer la suppression et la force ; exiger une Pull Request ; exiger le contrôle `CI / Types, tests et compilation` vert |

En ligne de commande (à adapter) :

```bash
gh api repos/<org>/<depot>/rulesets -X POST --input regles-main.json
```

### Recevoir les CI vertes par mail

Par défaut, GitHub n'envoie un mail que quand une CI **échoue**.
Pour la livraison, on veut aussi le vert :
GitHub → photo de profil → Settings → Notifications → **Actions** →
décocher « Only notify for failed workflows ».

### Secrets

- `GITHUB_TOKEN` suffit pour publier l'image sur GHCR (permission `packages: write` dans le job).
- Les autres secrets (clé d'hébergeur…) vont dans Settings → Secrets → Actions,
  jamais dans le code ni dans un fichier commité.

### Dependabot

`.github/dependabot.yml` : mises à jour hebdomadaires de npm, pip/uv, des
actions GitHub et de l'image Docker. Chaque PR de mise à jour passe par la CI.

---

## 6. Les cas difficiles

| Cas | Que faire |
|---|---|
| La CI de `livraison` est rouge | corriger sur une branche `fix/…` → PR vers `dev` → nouveau commit `livraison` |
| `pret-pour-main` dit que `main` a bougé | sur la recette : `git merge origin/main`, régler les conflits, `npm run verifier`, pousser, nouveau `livraison` |
| Correctif urgent en production | branche `fix/…` partie de `main` → PR vers `dev` → livraison normale. Si c'est vraiment urgent : PR vers `main` avec CI verte, **puis** fusionner `main` dans `dev` tout de suite |
| Revenir en arrière en production | redéployer l'image précédente (tag `sha-…` ou `v…`) ; côté site vitrine, republier la version précédente depuis le CMS. Puis corriger normalement |
| Deux dépôts (principal + miroir) | les deux dans `livraison.json` ; `livrer` pousse le même commit dans les deux ; aligner aussi la branche de recette du miroir |
| Une branche a divergé (historique réécrit) | ne jamais forcer sur `dev`/`main` ; créer une branche de sauvetage, comparer, fusionner |

---

## 7. Commits et Pull Requests

- Un commit = une intention. Libellé : `<préfixe>: <type de livraison> — <objectif>`
  (skill `libelle-de-commit`). Exemple : `feat: fonctionnalité — ajoute la réservation en ligne`.
- Commits petits et fréquents sur la branche de travail ; la PR raconte l'ensemble.
- **Description de PR** (modèle `.github/pull_request_template.md`) : ce qui
  change, pourquoi, comment c'est vérifié, ce qui reste. Captures d'écran pour
  un changement visible.
- Une PR se relit en moins de 30 minutes. Au-delà, la découper.
- Jamais de secret dans un commit. Si ça arrive : le secret est **changé**
  (le retirer de l'historique ne suffit pas, il a déjà pu être copié).

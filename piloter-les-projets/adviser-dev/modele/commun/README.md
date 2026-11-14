# {{NOM}}

<!-- En deux phrases : à quoi sert le projet, et pour qui. -->

## Lancer le projet (5 minutes)

Il faut : Node 24 ou plus{{PREREQUIS_PILE}}, Git, et GitHub CLI (`gh`) pour livrer.

```bash
npm install
```

{{INSTALLATION_PILE}}

```bash
cp backend/.env.example backend/.env
npm run dev:backend
npm run dev:frontend
```

## Les commandes

| Commande | Rôle |
|---|---|
| `npm run dev:frontend` / `npm run dev:backend` | développer |
| `npm run lint` | types et règles d'écriture |
| `npm test` | tous les tests |
| `npm run build` | compiler ce qui part en production |
| `npm run verifier` | lint + tests + build : exactement ce que fait la CI |

## Architecture

```text
frontend/   l'interface (Vite + React + TypeScript)
backend/    le serveur : API, santé, limites, journaux ({{PILE_LIBELLE}})
infra/      image Docker, lancement sur une machine, sauvegarde et restauration
docs/       le projet (docs/projet) et les décisions (docs/decisions)
.github/    CI, image Docker, livraison
```

Santé du service : `GET /sante/vivant` (le processus répond) et `GET /sante/pret` (il peut servir).

## Travailler et livrer

```text
feature/<nom>  ──PR + CI verte──▶  dev (recette)  ──« livraison » + CI verte──▶  main (production)
```

1. Une branche par fonction, partie de `dev` : `git switch -c feature/<nom>`.
2. Pull Request vers `dev`, CI verte, relecture.
3. Sur `dev`, quand tout est prêt : `git commit --allow-empty -m "livraison"`, puis `git push`.
   La CI vérifie tout, puis que `main` peut avancer sans conflit. GitHub envoie le résultat par mail.
4. CI verte : `livrer.bat` (Windows) ou `sh livrer.sh`. Le script revérifie la CI de ce commit, demande `OUI`, puis pousse vers `main`.

Pour recevoir aussi les CI vertes par mail : GitHub → Settings → Notifications → Actions,
décocher « Only notify for failed workflows ».

## Mettre en ligne

L'hébergement n'est pas fixé dans le code. Le service est livré en image Docker
(publiée sur GHCR depuis `main`) et respecte un contrat simple : configuration
par l'environnement, un port, un dossier de données, la santé, les journaux sur
la sortie standard. Sur une machine avec Docker : voir `infra/docker-compose.yml`.

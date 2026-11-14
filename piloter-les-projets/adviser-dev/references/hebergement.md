# Hébergement — le contrat, pas le fournisseur

L'hébergeur change : Netlify aujourd'hui, un VPS ou un autre service demain.
Le socle ne choisit pas l'hébergeur. Il garantit que le projet **peut partir
sur n'importe lequel** sans réécriture.

Pour choisir un hébergeur : skills `choix-hebergement` et
`deployment-devops-advisor`. Ici, seulement le contrat.

## Sommaire

1. Le contrat d'un service bien élevé
2. L'image Docker
3. Lancer sans hébergeur : docker compose
4. Les adaptateurs d'hébergeur
5. Avant de choisir un hébergeur

---

## 1. Le contrat

Un service du socle respecte ces sept points. N'importe quel hébergeur
sérieux sait alors le faire tourner.

| # | Le service… | Concrètement |
|---|---|---|
| 1 | se configure par l'environnement | aucune valeur d'hébergeur dans le code |
| 2 | écoute sur un port donné | `PORT` ou `<PREFIXE>_PORT`, `0.0.0.0` en conteneur |
| 3 | écrit ses données dans **un** dossier | `<PREFIXE>_DONNEES`, monté en volume ; le reste est jetable |
| 4 | dit s'il va bien | `/sante/vivant`, `/sante/pret` |
| 5 | journalise sur la sortie standard | pas de fichier de journal |
| 6 | s'arrête proprement | `SIGTERM` → fin des requêtes → sortie |
| 7 | est livré en image | même image en test et en production ; tag par commit et par version |

---

## 2. L'image Docker

Modèles : `modele/node/infra/docker/Dockerfile`, `modele/python/infra/docker/Dockerfile`.

- **Image de base précise et légère** : `node:24.x-bookworm-slim`, `python:3.x-slim`.
  Jamais `latest` : une image doit se reconstruire à l'identique dans six mois.
- **Les dépendances avant le code** : on copie d'abord les fichiers de
  dépendances, on installe, puis on copie le code. Une modification du code ne
  réinstalle pas tout.
- **Installation exacte** : `npm ci`, `uv sync --frozen --no-dev`.
- **Sans root** : `USER node` ou un utilisateur créé. Le service n'écrit que
  dans son dossier de données.
- **`HEALTHCHECK`** sur `/sante/vivant`.
- **`.dockerignore`** strict : `node_modules`, `.env*` (sauf `.env.example`),
  `.git`, données locales, journaux, docs. Un `.env` copié dans une image est
  un secret publié.
- Multi-étapes quand une compilation produit des fichiers : l'étape finale ne
  garde que le nécessaire.
- Ports : `EXPOSE` le port interne ; l'ouverture vers l'extérieur se décide au lancement.

---

## 3. Lancer sans hébergeur

`infra/docker-compose.yml` lance le service sur **n'importe quelle machine
avec Docker** (un VPS, un poste) :

- le service + un proxy HTTPS (Caddy prend le certificat tout seul) ;
- un volume nommé pour les données ;
- `restart: unless-stopped` ;
- le port du service n'est ouvert qu'au proxy (`expose`, pas `ports`).

Pour un poste de l'équipe (démo, recette interne), une variante sans proxy :
le port n'écoute que sur `127.0.0.1`, et un tunnel l'ouvre au monde le temps
qu'il faut (voir le projet La Fourchette : `infra/compose.poste.yml`).

Sauvegarde : `infra/sauvegarde.sh` (copie cohérente du volume, archive datée,
rotation) et `infra/restaurer.sh`. La restauration se teste.

---

## 4. Les adaptateurs d'hébergeur

Ce qui est propre à un hébergeur vit dans **un seul module**, isolé :

```text
backend/src/publication/netlify.ts      l'envoi du site vers Netlify
backend/src/publication/<autre>.ts      demain, un autre hébergeur
```

- Le reste du code appelle une interface (`envoyer(dossier)`), pas Netlify.
- Les réglages de l'hébergeur viennent de l'environnement
  (`CMS_NETLIFY_SITE`, `CMS_NETLIFY_JETON`) ; absents = l'adaptateur est inactif.
- Un fichier de l'hébergeur dans le dépôt (`netlify.toml`, `vercel.json`)
  porte un commentaire qui dit pourquoi il est là. Exemple réel : un
  `netlify.toml` qui empêche Netlify de publier le dépôt brut à chaque push.
- Changer d'hébergeur = écrire un adaptateur + une décision dans
  `docs/decisions/`. Le reste du code ne bouge pas.

---

## 5. Avant de choisir un hébergeur

Les questions à poser (et à écrire dans la décision) :

- Le projet a-t-il un serveur qui tourne en continu, ou seulement des fichiers statiques ?
- A-t-il un disque de données à garder ? Où vit-il, qui le sauvegarde ?
- Combien d'instances ? (une seule → SQLite possible ; plusieurs → PostgreSQL, limites partagées)
- Où sont les clients (latence, RGPD : données dans l'UE) ?
- Qui reçoit l'alerte la nuit ?
- Combien ça coûte par mois, et à 10 fois plus de trafic ?
- Comment on revient en arrière ?

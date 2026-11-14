# Architecture — la structure commune à tous les projets

## Sommaire

1. L'arborescence
2. La configuration
3. Adapter au type de projet
4. Le frontend
5. Le backend
6. La documentation
7. Les erreurs d'architecture les plus fréquentes

---

## 1. L'arborescence

```text
<projet>/
├── frontend/              l'interface (Vite + React + TypeScript)
│   ├── src/
│   ├── tests/
│   └── package.json
├── backend/               le serveur : API, base, tâches
│   ├── src/  (Node)   ou  app/  (Python)
│   ├── tests/
│   ├── scripts/           outils lancés à la main (comptes, migrations, imports)
│   ├── .env.example
│   └── package.json  ou  pyproject.toml
├── contenu/               (site vitrine seulement) le contenu du client : données + médias
├── infra/
│   ├── docker/Dockerfile
│   ├── docker-compose.yml  le lancement « serveur », sans dépendre d'un hébergeur
│   └── sauvegarde.sh, restaurer.sh
├── docs/
│   ├── projet/            plan, cahier des charges
│   └── decisions/         une décision = un fichier numéroté (ADR)
├── .github/
│   ├── workflows/ci.yml, image.yml
│   ├── livraison.json     les dépôts et la branche de recette
│   └── livrer.mjs
├── livrer.bat, livrer.sh  la livraison vers main
├── package.json           espaces de travail (workspaces) npm, scripts communs
├── .editorconfig, .gitattributes, .gitignore, .dockerignore
└── README.md
```

**Pourquoi un seul dépôt (monorepo)** : le frontend et le backend changent
souvent ensemble. Un seul dépôt = un seul commit, une seule CI, une seule
version livrée. On sépare en plusieurs dépôts seulement si deux équipes
différentes livrent à des rythmes différents.

**Toujours `frontend/` et `backend/`.** Jamais `client/`, `server/`, `web/`,
`api/` : tous les projets de l'équipe se lisent de la même façon.

**Les scripts communs à la racine** (`package.json`) :

| Script | Rôle |
|---|---|
| `npm run dev:frontend`, `npm run dev:backend` | développer |
| `npm run lint` | types et règles de style, partout |
| `npm test` | tous les tests |
| `npm run build` | compiler ce qui part en production |
| `npm run verifier` | lint + tests + build : exactement ce que fait la CI |

Avec un backend Python, `npm run verifier` appelle aussi `uv run` dans
`backend/` : une seule commande pour tout vérifier, quel que soit le langage.

---

## 2. La configuration

**Règle** : le code est le même partout ; seul l'environnement change
(principe 3 des *Twelve-Factor Apps*).

- Toute valeur qui change entre le poste et la production vient d'une
  **variable d'environnement** : port, adresse publique, chemins de données,
  clés, niveau de journal.
- Les variables sont lues **une seule fois**, au démarrage, dans un seul module
  (`config.ts` ou `config.py`). Le reste du code reçoit un objet `Config`.
- La configuration est **validée au démarrage**. Variable obligatoire absente
  en production = le serveur refuse de démarrer, avec un message clair.
  Mieux vaut un serveur qui ne démarre pas qu'un serveur qui démarre faux.
- `backend/.env.example` liste **toutes** les variables, avec un commentaire
  et une valeur d'exemple sans secret. Le vrai `.env` n'entre jamais dans Git.
- Préfixe commun par projet (`CMS_`, `APP_`…) : on voit tout de suite ce qui appartient au projet.
- Les mots de passe ne s'écrivent jamais en clair dans `.env` : seulement leur
  **empreinte** (argon2id), fabriquée par un script du projet.

Un même fichier `.env` doit être lisible par Node (`--env-file`), par Python
(`python-dotenv`) **et par Docker** (`env_file`). Donc : une ligne = `CLE=valeur`,
clé sans espace, commentaires sur leur propre ligne commençant par `#`.

---

## 3. Adapter au type de projet

| Bloc | Site vitrine | SaaS | Outil interne | API |
|---|---|---|---|---|
| Frontend | site statique pré-rendu (SEO), petit espace `/admin` | application complète | application complète | aucun, ou doc |
| Backend | CMS : contenu, publication, formulaires | métier, comptes, facturation | métier | métier |
| Contenu | **`contenu/` séparé du code** : le client le change sans livraison | dans la base | dans la base | dans la base |
| Comptes | un compte admin (empreinte dans `.env`) | inscription, rôles, réinitialisation, éventuellement équipes (multi-locataires) | via le portail de l'équipe (SSO) | clés d'API |
| Base | SQLite | PostgreSQL + migrations | SQLite ou PostgreSQL | PostgreSQL |
| Limites | connexion, formulaires | connexion, inscription, API par compte | connexion | par clé d'API |
| Santé | + contrôle du site publié (pages, poids, certificat) | + base, file de tâches, services externes | + base | + base |
| Données sensibles | peu | fortes : RGPD, export, suppression de compte | moyennes | selon le métier |

**Le cas du site vitrine** (le plus fréquent dans l'équipe) :

- Le site public est **statique** : il part sur un hébergeur de fichiers
  (Netlify ou autre). Rapide, presque impossible à faire tomber.
- Le CMS (`/admin` + API) est un **serveur à part**, qui compile le site et
  l'envoie à l'hébergeur à chaque publication.
- Le contenu du client vit dans `contenu/` (en local) puis sur le **disque de
  données** en production. Au premier lancement, le contenu livré avec le code
  sert de départ ; ensuite on n'y touche plus.
- Les publications sont **versionnées** : on peut revenir à la version d'avant.

---

## 4. Le frontend

```text
frontend/src/
├── <espace>/              un dossier par espace : site/, admin/, app/
│   ├── pages/             une page = une route
│   ├── composants/        composants réutilisables de cet espace
│   ├── hooks/             logique React réutilisable
│   ├── services/          appels au backend (un seul endroit fait fetch)
│   └── lib/               fonctions pures, sans React
└── commun/                ce qui sert à plusieurs espaces
```

- **TypeScript strict** (`"strict": true`, `noUnusedLocals`, `noUnusedParameters`).
- **Un seul client HTTP** (`services/api.ts`) : il gère l'adresse du backend,
  les erreurs, le délai max, la session. Aucun composant n'appelle `fetch` lui-même.
- **Les adresses viennent de l'environnement** (`VITE_…`), jamais écrites en dur.
- **Vitest + Testing Library** : on teste ce que voit l'utilisateur, pas le détail interne.
- **Accessibilité** : HTML sémantique, labels, contraste, navigation au clavier
  (voir `normes-code.md`, section HTML).
- **Code splitting** : l'espace admin ne se charge pas sur le site public.

---

## 5. Le backend

### Node + TypeScript

```text
backend/src/
├── index.ts               démarrage : config → base → application → écoute
├── config.ts              lecture et validation de l'environnement
├── http/                  application, routes, en-têtes, fichiers
├── sante/                 /sante/vivant, /sante/pret, contrôles réguliers
├── auth/                  comptes, sessions, limites d'essais
├── <domaine>/             un dossier par domaine métier
└── base.ts                ouverture de la base, migrations
```

Node 24 lit le TypeScript directement (suppression des types) : pas de
compilation pour lancer, `tsc --noEmit` pour vérifier.

### Python + FastAPI

```text
backend/app/
├── main.py                création de l'application (fonction creer_application)
├── config.py              Pydantic Settings : lecture et validation
├── sante.py               /sante/vivant, /sante/pret
├── limites.py             limites d'essais
├── journal.py             journaux structurés, identifiant de requête
├── <domaine>/
│   ├── routes.py          HTTP seulement : lire, valider, appeler, répondre
│   ├── service.py         le métier, sans HTTP
│   ├── modeles.py         schémas Pydantic (entrées / sorties)
│   └── depot.py           accès à la base
└── base.py
```

### Les couches, dans les deux langages

```text
route (HTTP)  →  service (métier)  →  dépôt (base)
```

- La **route** ne contient pas de métier : elle valide, appelle, répond.
- Le **service** ne connaît pas HTTP : il se teste sans serveur.
- Le **dépôt** est le seul à écrire du SQL.

Une règle métier dans une route, c'est une règle qu'on ne peut tester qu'en
lançant un serveur. On la descend dans le service.

---

## 6. La documentation

- **README** : à quoi sert le projet, comment le lancer en 5 minutes, les
  scripts, l'architecture en dix lignes, la livraison. Il est tenu à jour à
  chaque lot.
- **`docs/decisions/NNNN-titre.md`** (ADR) : le contexte, les options, la
  décision, ses conséquences. On n'efface pas une décision : on en écrit une
  nouvelle qui la remplace.
- **Le code se documente par ses noms et ses tests.** Un commentaire en tête
  de fichier dit à quoi sert le module et sa limite principale.

---

## 7. Les erreurs d'architecture les plus fréquentes

| Erreur | Ce qui arrive en prod | Correction |
|---|---|---|
| Adresse `localhost` écrite en dur | rien ne marche une fois en ligne | variable d'environnement |
| Contenu du client mélangé au code | une livraison écrase ses changements | dossier `contenu/` + disque de données |
| Données écrites dans le dossier du code | perdues à chaque nouvelle image | dossier de données configurable, monté en volume |
| Métier dans les routes | impossible à tester, dupliqué | couche service |
| Un `.env` différent par dev, sans `.env.example` | « chez moi ça marche » | `.env.example` complet et validé au démarrage |
| Pas de séparation espace public / admin | l'admin est chargé (et exposé) sur le site | espaces séparés, politique de sécurité plus stricte pour l'admin |
| Dépendance à un hébergeur dans le code | changer d'hébergeur = réécrire | un adaptateur isolé (voir `hebergement.md`) |

# Les piles de l'équipe — ce qu'on utilise, et rien d'autre

Cette liste vient des projets réels de l'équipe (relevé du 2026-11-10 sur
`Documents/Developer` : 33 projets React, 14 projets FastAPI, 9 Express…).
**On ne propose pas une technologie hors de cette liste.** Si un besoin ne
rentre pas dedans, c'est une décision : fiche, puis `docs/decisions/`.

Seule exception, sans décision : les **compléments de sécurité standard** des
frameworks déjà utilisés — `helmet`, `express-rate-limit`, `@fastify/helmet`,
`@fastify/rate-limit`, `flask-limiter`, `flask-talisman`, `argon2-cffi`. Ils
servent à remplir les blocs 9 et 10 du socle, pas à changer de pile.

## Sommaire

1. Choisir la pile d'un nouveau projet
2. Frontend
3. Backend Python
4. Backend Node
5. Bases de données
6. Documents, fichiers, scraping
7. IA
8. Ce qu'on rencontre dans les anciens projets
9. Noms de dossiers dans les projets existants

---

## 1. Choisir la pile d'un nouveau projet

| Projet | Frontend | Backend | Base |
|---|---|---|---|
| **SaaS, outil métier, traitement de documents** (le cas le plus fréquent) | Vite + React + TS + Tailwind | **FastAPI** | PostgreSQL (plusieurs utilisateurs) ou SQLite (petit) |
| **Site vitrine avec CMS** | Vite + React + TS, pages pré-rendues | **Node + TS sans framework** (`node:http`, modèle La Fourchette) | SQLite (`node:sqlite`) |
| **Outil interne JS, temps réel ou petite API** | Vite + React + TS + Tailwind | **Express + Prisma** ou **Fastify + better-sqlite3** | SQLite ou PostgreSQL |
| **Script ou outil à lancer à la main** | aucun | Python + Typer | fichiers |

Le modèle de la skill fournit FastAPI (`--pile python`) et Node sans framework
(`--pile node`). Express ou Fastify : partir du modèle Node et ajouter le
framework, avec les mêmes briques (santé, limites, journaux, en-têtes).

---

## 2. Frontend

| Besoin | Bibliothèque de l'équipe | Règle |
|---|---|---|
| Base | **Vite + React + TypeScript** | TypeScript strict (par défaut depuis TS 6, ne jamais le couper) |
| Styles | **Tailwind** (v4 : `@tailwindcss/vite` ; v3 : PostCSS + autoprefixer) | les couleurs et espaces dans le thème, pas de valeurs au hasard dans les classes |
| Composants de base | style shadcn : `@radix-ui/*`, `class-variance-authority`, `clsx`, `tailwind-merge` | une fonction `cn()` unique ; les variantes dans `cva`, pas dans des `if` |
| Icônes | `lucide-react` | importer icône par icône (le reste n'entre pas dans le bundle) |
| Navigation | `react-router-dom` | les routes dans un seul fichier ; pages chargées à la demande (`lazy`) |
| Données du serveur | `@tanstack/react-query` | un seul client HTTP dans `services/` ; react-query gère cache, chargement, erreur |
| Formulaires et validation | `zod` (+ `react-hook-form` si gros formulaire) | le même schéma valide le formulaire et la réponse du serveur |
| Animations | `framer-motion` ; `gsap` + `lenis` pour le défilement des sites vitrines | respecter `prefers-reduced-motion` |
| 3D | `three`, `@react-three/fiber`, `@react-three/drei` | chargée à la demande, jamais dans le premier écran |
| Graphiques | `recharts` | — |
| Polices | `@fontsource/*` (servies par le site) | pas de Google Fonts en lien : la politique de sécurité (CSP) reste à `'self'` |
| PDF dans le navigateur | `pdfjs-dist`, `jspdf` | le worker de pdfjs servi par le site |
| Excel dans le navigateur | `xlsx`, `xlsx-js-style` | lire les fichiers de l'utilisateur sans les envoyer si possible |
| Tests | **Vitest + Testing Library + jsdom** | tester ce que voit l'utilisateur |
| Lint | `eslint` + `typescript-eslint` + `eslint-plugin-react-hooks`, ou `oxlint` | lancé par `npm run lint` et par la CI |

État global : rarement utile. `zustand` si vraiment partagé partout ; sinon l'état local et react-query.

---

## 3. Backend Python

| Besoin | Bibliothèque de l'équipe | Règle |
|---|---|---|
| API | **FastAPI** + **uvicorn** | fabrique `creer_application(config)` ; routes minces, métier dans des services |
| Validation | **pydantic** | un modèle pour chaque entrée et chaque sortie |
| Configuration | **pydantic-settings** | validée au démarrage (modèle `app/config.py`) |
| Base | **SQLAlchemy** ou **SQLModel**, migrations **Alembic** | jamais de `create_all` en production : Alembic seulement |
| PostgreSQL | `psycopg` | pool de connexions, délai max |
| Limites d'essais | **slowapi** (déjà utilisé) ou le `Limiteur` du modèle | sur la connexion, les formulaires publics et chaque route chère (IA, OCR) |
| Mots de passe | `bcrypt` dans les projets existants ; **argon2** (`argon2-cffi`) pour les nouveaux | jamais en clair, ni en base ni dans `.env` |
| Jetons de session | `pyjwt` | durée courte, clé de 32 octets au moins, algorithme fixé (`HS256`), jamais `none` |
| Appels sortants | **httpx** (de préférence à `requests`) | délai max sur chaque appel |
| Envoi de fichiers | `python-multipart` | taille max, type vérifié par le contenu (Pillow, PyMuPDF), pas par l'extension |
| Tests | **pytest** + TestClient (`httpx2`) | base dans un dossier temporaire |
| Qualité | **ruff** + **mypy** | dans `npm run lint` et dans la CI |
| Outils en ligne de commande | `typer` | — |

**Flask** existe dans 4 anciens projets (`excel-to-dossier`, `melko-tfpb-automation`,
`melko_facture_ocr`…). On l'audite avec les mêmes douze blocs :
`flask-limiter` pour les limites, `flask-talisman` pour les en-têtes,
`flask-wtf` pour le CSRF, `gunicorn` en production (jamais `app.run()`).
Pas de nouveau projet en Flask : FastAPI.

**Streamlit** (2 projets) : outil interne seulement, jamais exposé sur Internet sans la passerelle de l'équipe.

---

## 4. Backend Node

| Besoin | Bibliothèque de l'équipe | Règle |
|---|---|---|
| Sans framework | `node:http` + TypeScript lu directement par Node 24 | modèle La Fourchette et `--pile node` |
| Express | **express** + `cors` | `helmet` pour les en-têtes, `express-rate-limit` pour les limites, `express.json({ limit: '16kb' })` |
| Fastify | **fastify** + `@fastify/cookie` | `@fastify/helmet`, `@fastify/rate-limit`, `bodyLimit` ; son journal (pino) intégré, activé |
| Base | **Prisma** (avec Express) ; **better-sqlite3** ou `node:sqlite` ; `drizzle-orm` + `pg` | migrations versionnées (`prisma migrate`, `drizzle-kit`) commitées |
| Validation | **zod** | à l'entrée de chaque route |
| Sessions | `jsonwebtoken` (existant), cookies `HttpOnly` | même règles que pyjwt |
| Mots de passe | `bcryptjs` (existant) ; argon2 pour les nouveaux | — |
| Configuration | `dotenv` ou `node --env-file` | validée au démarrage par zod |
| Tests | `node --test`, `vitest`, `supertest` | l'application démarre dans le test, sur un port libre |
| Lancement en dev | `node --watch` (préféré à `nodemon`), `tsx` si besoin | — |

---

## 5. Bases de données

| Base | Quand | Règles |
|---|---|---|
| **SQLite** (`node:sqlite`, `better-sqlite3`, `sqlite3`) | une seule instance, petit volume | mode WAL, `busy_timeout`, sauvegarde par `VACUUM INTO` |
| **sqlite-vec** | recherche par vecteurs dans SQLite (CEE_bot, CEE-CHECK) | même fichier, même sauvegarde |
| **PostgreSQL** (`psycopg`, `pg`, Prisma) | plusieurs utilisateurs ou instances, SaaS | migrations, sauvegarde `pg_dump` quotidienne, restauration testée |

---

## 6. Documents, fichiers, scraping

Le cœur de beaucoup de projets de l'équipe (CEE, factures, TFPB).

| Besoin | Bibliothèque | Règle de production |
|---|---|---|
| Excel | `openpyxl`, `pandas` | lire en `read_only=True` les gros fichiers ; limite de taille à l'envoi |
| PDF : lire | `pymupdf`, `pdfplumber` | délai max par fichier ; un PDF piégé ne doit pas bloquer le serveur |
| PDF : produire | `weasyprint`, `reportlab`, `fpdf2` | gabarits `jinja2` avec échappement automatique |
| Word | `docxtpl` | — |
| Images | `pillow`, `opencv-python` | rouvrir et réécrire l'image (efface les métadonnées, prouve que c'est une image) |
| OCR | `pdf2image` + moteur | traitement long → hors de la requête (tâche de fond), avec une limite d'essais |
| Scraping | `httpx` + `beautifulsoup4` / `lxml` ; `playwright` si la page a besoin du navigateur | respecter le site visé (délai entre requêtes, robots.txt), pas d'identifiants en dur |

---

## 7. IA

`anthropic`, `openai`, `ollama`, `sentence-transformers`, `tiktoken`.

- Clé d'API dans l'environnement, jamais dans le code ni dans le frontend.
- Délai max et nombre maximum de tentatives sur chaque appel.
- **Limite d'essais par utilisateur** sur toute route qui appelle un modèle : chaque appel coûte de l'argent.
- Journal du coût (jetons utilisés) par appel, sans le contenu des documents.
- Le modèle utilisé est un réglage (variable d'environnement), pas une chaîne dans le code.

---

## 8. Ce qu'on rencontre dans les anciens projets

| Rencontré | Où | Ce que fait la skill |
|---|---|---|
| **Next.js** | `Melko-dashboard`, `melko-constellation` | audit avec les douze blocs (le frontend est reconnu) ; pas proposé pour un nouveau projet |
| **Flask** | 4 projets Python | audit (section 3) ; migration vers FastAPI seulement sur décision |
| **Streamlit** | 2 outils | audit allégé : outil interne, jamais exposé |
| Go | `paperclip` (dépôt externe) | hors périmètre |

---

## 9. Noms de dossiers dans les projets existants

| Noms | Projets |
|---|---|
| `ui/` + `server/` | 15 projets (AskMe, CEE-CHECK, CEE_GUIDE, PROSPECTION, LuxuryOS, agenda_tasks, money_guru, school, boilerplate…) |
| `frontend/` + `backend/` | 8 projets (CEE_bot, TeamBot, melko-hub, Site-vitrine-restau, excel-to-dossier…) |
| `web/` + `api/` | Melko-webV3 |

Nouveau projet : **`frontend/` + `backend/`**, sans exception. Projet existant :
le script reconnaît `ui/`, `server/`, `web/`, `api/` à leur contenu ; le
renommage est une décision (fiche), faite dans une PR à part, jamais mélangée
avec un autre changement.

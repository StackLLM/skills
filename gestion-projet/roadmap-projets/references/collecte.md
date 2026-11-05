# Collecte — trouver où on en est

Ordre de lecture : **ce que l'utilisateur a écrit d'abord**, le code et Git
ensuite pour confirmer.

## 1. Les documents qui disent l'état

Chercher dans cet ordre, à la racine puis dans `docs/` :

| Fichier (ou proche) | Ce qu'on y prend |
|---|---|
| `Plan.md`, `PLAN.md`, `plan-*.md`, `docs/plan*.md` | objectifs, volets, lots prévus, section « état actuel » ou « avancement » |
| `CONTEXTE.md`, `contexte*.md`, `docs/produit.md` | pourquoi le projet existe, périmètre, décisions |
| `docs/lots.md`, `LOTS.md`, `suivi*.md` | tableau des lots : statut, date de validation, tests |
| `docs/roadmap.md`, `ROADMAP.md` | phases, « où on en est », la route |
| `docs/prod.md`, `deploiement*.md` | lots de mise en production (P0…P9 ou équivalent) |
| `TODO.md`, `Bloquage.md`, `BLOCAGES.md` | ce qui bloque, ce qui reste |
| `CLAUDE.md` | guide de reprise, priorités, renvois vers les autres documents |
| `CHANGELOG.md` | versions livrées |
| `README.md` | ligne « Statut », fonctionnalités annoncées |
| `docs/decisions/`, `ADR-*.md` | décisions qui changent le plan |

Repérer les marqueurs de statut usuels : `✅` `🟡` `⬜` `↪️` `❌` `⏳`,
`[x]` / `[ ]`, « clôturé », « livré, à valider », « reporté », « remplacé par ».

Les lire comme ceci :

| Marqueur | État dans le roadmap |
|---|---|
| ✅, `[x]`, clôturé, validé, fait | terminé |
| 🟡, livré à valider | à valider |
| ⏳, en cours, démarré | en cours |
| ⬜, `[ ]`, prévu, à venir | à venir |
| ❌, bloqué, reporté sans date | bloqué |
| ↪️, remplacé par | ne pas compter ; suivre le remplaçant |

## 2. Mode organisation — commandes

Organisation GitHub (par défaut `StackLLM`) :

```bash
gh repo list <org> --limit 100 --json name,description,visibility,isArchived,pushedAt
gh api repos/<org>/<repo>/contents -q '.[].name'
gh api "repos/<org>/<repo>/commits?per_page=5" -q '.[] | "\(.commit.author.date[:10]) \(.commit.message | split("\n")[0])"'
gh api "repos/<org>/<repo>/contents/<chemin>" -H "Accept: application/vnd.github.raw"
```

Pour chaque dépôt : lire le README, puis chaque document du § 1 qui existe.
Un document long : chercher d'abord ses titres (`grep -nE "^#{1,3} "`), puis
lire seulement la section d'état (« État actuel », « Où on en est », sommaire
des lots).

Lire aussi :
- le **profil public** de l'organisation (`.github/profile/README.md`) : liste
  des produits et statut annoncé ;
- les projets annoncés **sans dépôt** (profil, portfolio, dossiers locaux) :
  ils apparaissent dans le roadmap avec « pas de dépôt » ;
- les dépôts **archivés** : les mentionner seulement s'ils portent un projet
  encore vivant ailleurs, sinon une ligne dans la réponse suffit.

Dossier local de projets au lieu d'une organisation : mêmes lectures, avec
`git -C <dossier> log -5 --format='%ad %s' --date=short`.

## 3. Mode projet — commandes

```bash
ls ; ls docs 2>/dev/null
git log -15 --format='%ad %s' --date=short
git log --since="30 days ago" --name-only --format= | cut -d/ -f1-2 | sort | uniq -c | sort -rn | head
```

La deuxième commande montre **où** le travail récent a eu lieu : elle aide à
rattacher les commits aux volets (`ui/` → Front, `server/` → Backend,
`migrations/` → Base de données…).

Pour confirmer un lot « fait » : chercher ses fichiers ou son commit. Un lot
annoncé fait sans aucune trace dans le code est un décalage.

Pour trouver les volets quand le plan n'en a pas : la structure du dépôt
(`ui/`, `api/`, `server/`, `ml/`, `prisma/`, `docker/`, `infra/`) et le
contenu de chaque lot.

## 4. Repérer les décalages

| Décalage | Comment le voir |
|---|---|
| README périmé | sa ligne « Statut » contredit la roadmap ou le suivi des lots |
| Statut public faux | le profil de l'organisation annonce « en développement » un projet sans dépôt ni code |
| Document en retard sur le code | commits récents après la dernière mise à jour du suivi des lots |
| Lot fait sans trace | marqué terminé, aucun fichier ni commit correspondant |
| Lot remplacé non suivi | « remplacé par X », mais X n'existe nulle part |
| Deux documents qui se contredisent | même lot, deux statuts différents |
| Projet sans plan | aucun document du § 1 : l'état est déduit du code, le dire |

Chaque décalage cite les deux sources qui se contredisent.

## 5. Ce qui attend l'utilisateur

Ne garder que les actions qu'**une personne** doit faire :

- valider des lots livrés ;
- une tâche marquée « action humaine » (annoter, relire, tester en vrai) ;
- une décision ouverte (choix d'hébergeur, de nom, de prix) ;
- réunir des gens (comité, testeurs, juriste) ;
- un accès à fournir (compte, clé, domaine).

Ce que Claude peut faire seul ne va pas dans cette section.

# [Nom du chantier] — plan par phases et par lots

> [Le chantier en une phrase : ce qu'on construit et pour qui.]
> [Une ou deux lignes de contexte : où ça tourne, avec quoi, pour quelle équipe.]

- **Date** : AAAA-MM-JJ (version 1)
- **Auteur** : [prénom nom] (avec Claude)
- **Branche de travail** : `[branche]` → `[branche principale]` après validation
- **État** (AAAA-MM-JJ) : rien de commencé. [Plus tard : phases faites, ce qui reste, ce qui attend l'utilisateur.]

---

## Sommaire

- [Le problème et le but](#but)
- [Décisions prises](#decisions-prises)
- [Ce qu'on a trouvé](#constat)
- [Comment les morceaux s'emboîtent](#architecture)
- [Phase 0 — [nom]](#phase-0)
  - [Lot 0.1 — [nom]](#lot-0-1)
  - [Lot 0.2 — [nom]](#lot-0-2)
- [Phase 1 — [nom]](#phase-1)
  - [Lot 1.1 — [nom]](#lot-1-1)
  - [Lot 1.2 — [nom]](#lot-1-2)
  - [Test réel de la phase 1](#test-1)
- [Actions de [prénom]](#actions)
- [Points à confirmer en cours de route](#a-confirmer)
- [Décidé automatiquement](#decide)
- [Zone technique concernée](#zone-technique)

---

<a id="but"></a>
## Le problème et le but

**Aujourd'hui** : [ce qui ne va pas, en 2 ou 3 phrases concrètes. Pas de chemin de fichier.]

**Le but** : [ce que l'utilisateur aura à la fin, en une phrase.]

| Besoin | Où dans [le produit] |
|---|---|
| [besoin 1] | **[écran ou module]** (phase 1) |
| [besoin 2] | **[écran ou module]** (phase 2) |

[Une ligne sur ce qui est volontairement hors du chantier.]

---

<a id="decisions-prises"></a>
## Décisions prises

Décisions de [prénom], le AAAA-MM-JJ.

| # | Sujet | Choix | Conséquence dans le plan |
|---|---|---|---|
| 1 | [sujet] | **[choix]** | [Lot x.y : ce que ça change] |
| 2 | ~~[sujet d'une décision annulée]~~ (AAAA-MM-JJ, **annulée le …**) | ~~[ancien choix]~~ — [raison] | [Lot retiré ou modifié] |

---

<a id="constat"></a>
## Ce qu'on a trouvé

**Fait** — vérifié sur la machine et dans le code le AAAA-MM-JJ.

### [Sujet 1 : la machine, l'hébergement, l'existant…]
- [constat, avec sa mesure ou sa preuve]
- [constat]

### [Sujet 2 : l'application]
- **Déjà là** : [ce qu'on réutilise].
- **Manque** : [ce qu'il faut construire].

### [Sujet 3 : une application ou un service voisin]
- [ce qu'il expose, comment il identifie l'appelant, ses limites]

**À confirmer** : [ce qui n'a pas pu être vérifié, et pourquoi].

---

<a id="architecture"></a>
## Comment les morceaux s'emboîtent

```text
 [Source A] ─── [ce qu'elle donne] ───┐
                                      ▼
                              ┌────────────────┐
 [Source B] ─── [donnée] ───► │  [Le cœur]     │ ───► [Ce que voit l'utilisateur]
                              └────────────────┘
```

- **[Règle 1]** : [qui parle à qui, dans quel sens].
- **[Règle 2]** : [ce qui est en lecture seule, ce qui ne sort jamais].
- **[Règle 3]** : [ce qui se passe quand un morceau tombe].

---

<a id="phase-0"></a>
## Phase 0 — [nom court]

**Objectif** : [ce que la phase apporte, en une phrase].
**Résultat de phase** : [ce que l'utilisateur constate quand elle est finie].

<a id="lot-0-1"></a>
### Lot 0.1 — [nom court]

- **Objectif** : [une phrase].
- **Pourquoi** : [le constat qui rend ce lot nécessaire].
- **À faire**
  - [geste concret]
  - [geste concret]
  - **Toi** : [geste réservé à l'utilisateur, s'il y en a un].
- **Dépend de** : rien.
- **Résultat attendu** : [ce qu'on observe].

<a id="lot-0-2"></a>
### Lot 0.2 — [nom court]

- **Objectif** : [une phrase].
- **À faire**
  - [geste concret]
  - [geste concret]
- **Dépend de** : 0.1.
- **Résultat attendu** : [ce qu'on observe].
- **Décision nécessaire**
  - **Pourquoi la question se pose** : [constat].
  - **A — [option]** → conséquence : […]
  - **B — [option]** → conséquence : […]
  - **Avis technique** : [factuel, court].

---

<a id="phase-1"></a>
## Phase 1 — [nom court]

**Objectif** : [une phrase].
**Pourquoi** : [seulement si ce n'est pas évident].
**Résultat de phase** : [ce que l'utilisateur constate].

**Constat (AAAA-MM-JJ)** : [ce qui a été vu et qui explique la phase, s'il y a lieu].

<a id="lot-1-1"></a>
### Lot 1.1 — [nom court]

- **Objectif** : [une phrase].
- **À faire**
  - [geste concret]
  - [geste concret]
- **Dépend de** : 0.2.
- **Résultat attendu** : [ce qu'on observe].

<a id="lot-1-2"></a>
### Lot 1.2 — [nom court, lot d'interface]

- **Objectif** : [la question à laquelle l'écran répond].
- **À faire**
  - [données : route existante réutilisée, ou route à créer]
  - [écran : composition propre à la page, composants existants réutilisés]
  - États vide, chargement et erreur dessinés.
  - Vérifié dans le navigateur, largeur ordinateur et téléphone.
- **Dépend de** : 1.1.
- **Résultat attendu** : [ce que l'utilisateur voit et peut faire].

<a id="test-1"></a>
### Test réel de la phase 1

- **À faire** : [le parcours complet, sur l'instance réelle, avec de vraies données].
- **Résultat attendu** : [ce qui prouve que la phase marche pour de bon].

<!-- Quand un lot est fini, ajouter à ce lot :
- **Fait (AAAA-MM-JJ)** : [ce qui a été fait, ce qui diffère du prévu, la preuve].
Une phase ajoutée plus tard s'appelle « 1 bis », « 1C »… : on ne renumérote jamais. -->

---

<a id="actions"></a>
## Actions de [prénom]

Ce que Claude ne fait pas à ta place (réglages système, mots de passe, clés, comptes d'autres apps, commit, push).

| Quand | Action |
|---|---|
| Lot 0.1 | [action] |
| Lot 1.1 | [action] — **fait** (AAAA-MM-JJ) |

---

<a id="a-confirmer"></a>
## Points à confirmer en cours de route

| Point | Quand | Pourquoi |
|---|---|---|
| [point] | Lot x.y | [ce qui manque pour le savoir] |

---

<a id="decide"></a>
## Décidé automatiquement

| Sujet | Choix | Pourquoi |
|---|---|---|
| Ordre des phases | 0 → 1 → 2 ; [ce qui peut avancer en parallèle] | Chaque phase s'appuie sur la précédente |
| [sujet] | [choix] | [raison en une ligne] |

---

<a id="zone-technique"></a>
## Zone technique concernée

- **[Sujet 1]** : `[fichier]`, `[fichier]`
- **[Sujet 2]** : `[route]`, `[table]`, `[script]`
- **[Application voisine]** : `[dossier/fichier]`

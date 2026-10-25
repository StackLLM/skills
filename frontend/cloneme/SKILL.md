---
name: cloneme
description: >
  À utiliser quand l'utilisateur donne l'URL d'un site et veut le reproduire en
  entier dans un vrai projet frontend exécutable — « clone ce site », « CloneMe
  <url> », « reproduis <url> à l'identique », « refais tout le site de X »,
  « je veux une base de dev qui ressemble à <url> ». Aussi quand il a modifié
  design.md, palette.md ou animation.md d'un projet déjà cloné et veut que le
  code suive. Pour une seule section animée : animation-stealer. Pour une
  maquette en image : UI-Stealer. Projet en français.
---

# CloneMe · reproduire un site entier, pas une capture

## Principe

Entrée : **une URL**. Sortie : un **projet frontend qui se lance**, avec toutes
les pages accessibles, leurs composants, leurs états, leurs animations, et trois
fichiers de référence qui pilotent le code.

La règle qui commande tout :

```text
lire avant de deviner → tout le périmètre → les trois fichiers → le code qui les suit
```

Un clone dont seule la page d'accueil ressemble est un échec. Une valeur
devinée alors qu'elle pouvait être lue est un échec. Un bouton qui ne fait rien
est un échec.

## Deux modes

| Mode | Déclencheur | Ce qu'on fait |
|---|---|---|
| **Cloner** | une URL | les 9 étapes ci-dessous, de l'analyse au rapport |
| **Mettre à jour** | « j'ai modifié palette.md », « applique design.md » | `references/modifier-via-les-references.md` |

Un projet déjà cloné se reconnaît à son dossier `.cloneme/` à la racine.

---

## Les deux skills partenaires

CloneMe **orchestre**. Il ne recopie pas leurs méthodes : il les lit et les
applique, avec les exceptions ci-dessous.

### Les trouver

Dans cet ordre, s'arrêter au premier trouvé :

1. `../ui-stealer/` et `../animation-stealer/` (dossiers voisins de CloneMe,
   chemin relatif au dossier de CloneMe) ;
2. une recherche `**/ui-stealer/SKILL.md` et `**/animation-stealer/SKILL.md`
   dans `~/.claude/skills`, `~/.kimi/skills` — ou, si
   le dossier a été renommé, un `SKILL.md` dont le `name:` vaut
   `ui-stealer` (nom déclaré d'UI-Stealer) ou `animation-stealer` ;
3. introuvables : le dire au user en une ligne, et continuer avec les règles
   minimales recopiées dans `references/architecture-du-projet.md` et
   `references/analyser-le-site.md`.

Lire **en entier** leur `SKILL.md` et leurs `references/` avant l'étape 1.

### Ce qu'on prend, ce qu'on écarte

| Skill | On prend | On écarte, et pourquoi |
|---|---|---|
| **UI-Stealer** | la stack et l'arborescence maison, le contexte animations on/off, les scripts `.bat`, Docker, la validation par DOM + styles calculés + `tsc`/`vitest`/`build`, les pièges Windows | **la charte Forêt imposée** (ici la palette est celle du site source) · l'entrée par image `Template/` · le périmètre « accueil + conversation » · les recettes propres à la charte Forêt (rail en verre, mascotte, composeur) sauf si le site source a le même élément |
| **animation-stealer** | toute l'analyse : `outerHTML`, chunks JS, timeline, géométrie, minuteries, table GSAP → framer-motion, mode animations coupées, validation par mesures | sa règle « ne jamais copier leur charte » : dans un clone, **la charte du projet cible, c'est `palette.md`**, tirée de la source. Sa règle « réutiliser l'existant » s'applique à ce que CloneMe a déjà construit |

Les deux skills disent « ne pas reposer de questions ». CloneMe aussi, sauf les
trois cas de la section « Quand demander ».

---

## Les règles qui priment

### 1. Chaque valeur porte son origine

| Niveau | Sens | Exemple |
|---|---|---|
| **Relevé** | lu dans le HTML, le CSS ou le JS source | `transition: opacity .5s ease` dans `main.css` |
| **Mesuré** | lu dans les styles calculés ou la géométrie, à une largeur donnée | `h1 : 56 px / 1.1, à 1440 px` |
| **Déduit** | tiré d'une capture ou d'un raisonnement | « le menu glisse de la droite » |
| **Approximé** | invisible depuis l'URL, choix cohérent assumé | état d'erreur d'un formulaire jamais affiché |
| **Inaccessible** | protégé, derrière connexion, en erreur | page `/compte` |

Ce niveau est écrit dans les trois fichiers, à côté de chaque valeur. Un
« Déduit » écrit comme un « Relevé » est une faute.

### 2. Tout le périmètre accessible

Toutes les pages liées depuis le site, pas seulement l'accueil. Les pages qui
partagent un même gabarit (500 articles de blog) forment **un type de page** :
on reproduit le gabarit, plus deux ou trois exemples. Chaque page ou type de
page a une route qui marche.

Pour un type de page à beaucoup d'instances :

- la **liste** (page blog, catalogue) garde le même nombre de cartes que la
  source, avec titres et résumés repris dans `donneesDemo.ts` ;
- chaque carte mène à la route du gabarit (`/blog/:slug`) ;
- les 2 ou 3 exemples ont leur contenu complet ; les autres affichent le
  gabarit avec leur titre et un bandeau « article non cloné — contenu de
  démonstration ». Aucun lien ne tombe sur une 404.

### 3. Frontend seulement, et honnête

- Pas d'API métier inventée, pas de logique serveur.
- Les données dynamiques deviennent des **données de démonstration**, rangées
  dans un seul fichier et marquées comme telles dans l'interface du code.
- Chaque action qui appellerait un serveur passe par un **point d'intégration**
  unique, documenté, en mode démo par défaut.
- Un formulaire valide, affiche ses erreurs et son état « envoyé (démo) ». Il
  ne prétend jamais avoir envoyé quelque chose.

### 4. Aucun élément décoratif qui ment

Chaque lien mène quelque part. Chaque bouton fait quelque chose : ouvrir,
fermer, filtrer, valider, ou afficher « disponible après branchement du
backend ». Une route non reproduite affiche une page qui le dit, et elle est
listée dans le rapport.

### 5. Une seule maison pour chaque valeur

Couleurs, polices, tailles, rayons, ombres, espacements répétés : dans
`tokens.css`. Durées, courbes, ressorts, seuils : dans `animations.ts`. Les
composants n'écrivent **aucune** couleur ni durée en dur. C'est ce qui permet
de changer l'apparence en éditant `palette.md` seul.

### 6. Les droits

Repérer la licence ou les conditions du site (pied de page, `LICENSE`, page
mentions). Les ressources téléchargées restent dans le projet local et sont
listées avec leur source dans `.cloneme/ressources.json`. Le rapport rappelle
que publier un clone avec les textes, logos et images d'origine demande des
droits. Jamais de contournement : pas de connexion, pas de CAPTCHA, pas de
mur payant, pas de données personnelles collectées.

---

## Mode Cloner — les 9 étapes

Chaque étape a une **porte** : on ne passe pas à la suivante tant qu'elle n'est
pas franchie.

**Où créer le projet** — dès l'étape 1, car l'analyse y écrit déjà
(`.cloneme/`, ressources). Nom : `<site>-clone` (ex. `stellar-clone`). Lieu :
celui que le user donne ; sinon le dossier de travail de la session s'il est
vide ou dédié ; sinon le dossier parent habituel de ses projets, dit en une
ligne. Le dossier `ui/` n'est créé qu'à l'étape 4.

| # | Étape | Fiche | Porte |
|---|---|---|---|
| 1 | Analyser l'URL, crawler les pages, détecter la stack, relever licence et ressources | `references/analyser-le-site.md` §1–4 | `.cloneme/inventaire.json` liste chaque page, son type, son statut |
| 2 | Inventorier composants, états, comportements et animations, à 4 largeurs | `analyser-le-site.md` §5–9 + animation-stealer | chaque composant a un ID `C-xx`, chaque animation un ID `A-xx` |
| 3 | Écrire `design.md`, `palette.md`, `animation.md` | `references/fichiers-de-reference.md` | aucune ligne sans niveau d'origine |
| 4 | Choisir la stack, poser l'architecture, installer le strict nécessaire | `references/architecture-du-projet.md` + UI-Stealer | `npm run dev` affiche une page vide sans erreur |
| 5 | Construire gabarits, composants partagés, puis chaque page | `architecture-du-projet.md` §4–6 | toutes les routes de l'inventaire répondent |
| 6 | Interactions, animations, responsive | animation-stealer (§6–8) | chaque `A-xx` est implémenté et coupé par le mode réduit |
| 7 | Lancer le clone et le relais, comparer au site source, page par page, 4 largeurs | `references/valider-et-comparer.md` | les empreintes source et clone sont dans `.cloneme/mesures/` |
| 8 | Corriger les écarts, les plus visibles d'abord | `valider-et-comparer.md` §4 | plus aucun écart « fort » non expliqué |
| 9 | Vérifier navigation, interactions, tailles d'écran, synchro des fichiers, puis rapport | `valider-et-comparer.md` §5–6 | `tsc`, `vitest`, `build` et `verifier-synchro.mjs` passent |

Après l'étape 9 : copier les trois fichiers dans `.cloneme/instantane/`. C'est
la photo qui servira au mode Mettre à jour.

### Ordre de construction (étape 5)

```text
tokens.css  →  gabarit (en-tête, pied, conteneur)  →  composants partagés
→  page d'accueil  →  autres pages par type  →  pages d'état (404, vide, chargement)
```

Les composants partagés d'abord : une différence d'en-tête corrigée une fois
est corrigée partout.

---

## Les trois fichiers de référence

| Fichier | Contenu | Code qu'il pilote |
|---|---|---|
| `design.md` | pages et routes, gabarits, sections, composants `C-xx` et variantes, dimensions, typographie appliquée, états, responsive, correspondance source → clone | `src/pages/`, `src/gabarits/`, `src/composants/`, `src/routes.tsx` |
| `palette.md` | chaque token avec son nom de variable CSS, sa valeur, son origine | `src/styles/tokens.css` (valeur pour valeur) |
| `animation.md` | chaque animation `A-xx` : déclencheur, propriétés, durée, retard, courbe, réversibilité, mode réduit, implémentation | `src/lib/animations.ts`, `src/styles/animations.css`, composants marqués `A-xx` |

Règle de synchro : chaque ID (`P-xx` page, `C-xx` composant, `A-xx`
animation) écrit dans un fichier apparaît en commentaire dans le code qui
l'implémente, et inversement. Le script `scripts/verifier-synchro.mjs` le
contrôle :

```bash
node <dossier-CloneMe>/scripts/verifier-synchro.mjs <racine-du-projet>
```

Modèles complets : `references/fichiers-de-reference.md`. Exemple réel, produit
sur le modèle Stellar de HTML5 UP (3 pages, 0 écart aux 4 largeurs) :
`exemples/stellar/` — les trois fichiers, les cibles et le rapport.

---

## Quand demander

Par défaut, on avance sans questions. Trois exceptions, chacune posée une fois,
avec son contexte :

1. **Le site dépasse 40 pages après regroupement par type** : proposer le
   périmètre (types de pages + exemples), puis avancer.
2. **L'essentiel du site est derrière une connexion** : dire ce qui est
   visible, demander si l'on clone seulement cette partie.
3. **La stack d'origine est un framework autre que React** (Vue, Nuxt,
   Svelte, Angular, Astro) : demander laquelle garder. Sans réponse, stack
   maison. Un site React ou Next.js part en stack maison sans question.

Tout le reste se décide seul et se dit en une ligne dans le rapport.

---

## Le piège central de cet environnement

Le navigateur intégré ne compose pas quand son panneau est caché :
`requestAnimationFrame` ne rend pas la main, l'événement `scroll` n'est pas
émis, `IntersectionObserver` ne répond pas, les captures expirent. Les deux
skills partenaires le documentent ; le test de CloneMe l'a confirmé.

Deux autres limites, vues sur le test :

- `javascript_tool` coupe à **45 s** : un travail long se lance sans être
  attendu, et sa fin se guette côté shell ;
- une page publique ne peut pas appeler localhost (`ERR_BLOCKED_BY_CLIENT`).

Conséquences pour CloneMe :

- l'analyse lit le **code source et les styles calculés**, pas des captures ;
- la comparaison se fait par **empreintes mesurées**, enregistrées par le
  **relais** (`scripts/relais-cloneme.mjs`), qui sert aussi la source depuis
  localhost — détail dans `valider-et-comparer.md` §2 ;
- un comportement au défilement se teste en émettant `scroll` à la main, sur
  la source et sur le clone, avec la même séquence ;
- ce qui dépend de `requestAnimationFrame` se prouve par un test unitaire à
  horloge pilotée ;
- le rapport dit au user ce qu'il doit **regarder en direct**.

---

## Livrer

À la fin de chaque exécution, dans la réponse :

1. `design.md`, `palette.md`, `animation.md` — chemins, et ce qu'ils couvrent ;
2. le projet : comment le lancer (une commande), le port ;
3. les dépendances et technologies, avec la raison de chacune ;
4. le **rapport de validation** `RAPPORT-CLONAGE.md` : pages reproduites, tests
   faits, écarts restants, limites, ressources absentes ou protégées, droits.

Style : celui du user (français simple, sections `##`, chemins regroupés à la
fin).

---

## Erreurs à ne pas faire

| Tentation | Réalité |
|---|---|
| « L'accueil est identique, c'est fini » | Le périmètre, c'est l'inventaire. Chaque page a son statut dans le rapport. |
| Un fondu générique pour toutes les entrées | Chaque animation a sa durée, sa courbe, son seuil, lus dans la source. |
| Écrire `#1a1a1a` dans un composant « juste cette fois » | Le token existe ou on le crée dans `tokens.css` et `palette.md`. |
| Un bouton sans gestionnaire, « c'est la maquette » | Il ouvre, ferme, filtre, valide, ou dit qu'il attend le backend. |
| Inventer une réponse d'API plausible | Données de démo marquées, ou état vide. Jamais une fausse logique. |
| Prendre la palette Forêt d'UI-Stealer | La palette vient de la source. |
| Écrire la doc après coup, de mémoire | Les fichiers se remplissent pendant l'analyse ; le code suit les fichiers. |
| Un écart mesuré « pas grave » non noté | Il va dans le rapport, avec sa raison. |
| Crawler toute l'origine | Le périmètre est le dossier de l'URL donnée. Jamais un lien `download`, `logout`, panier. Une pause entre deux requêtes. |
| Mesurer seulement à 1440 px | Une gouttière ou une taille change dans un `@media` : comparer aux 4 largeurs. |
| Lire le HTML avec un filtre (`grep -v '^$'`) | Le texte recopié perd des lignes. Lire brut. |
| `0 0 0 1px #8cc9f0` dans un token d'ombre | `var(--couleur-accent)` : sinon changer l'accent ne change pas l'ombre. |
| Éditer un texte français avec `sed` ou un heredoc | L'apostrophe casse la commande shell. Outil d'édition de fichier. |

## Signaux d'arrêt

Si l'une de ces phrases passe par la tête, revenir à la porte de l'étape en
cours :

- « les autres pages se ressemblent, pas besoin de les ouvrir » ;
- « je mettrai les animations plus tard » ;
- « je synchroniserai les fichiers à la fin » ;
- « la valeur exacte ne se voit pas à l'œil ».

---

## Zone technique concernée

- `references/analyser-le-site.md` — crawl, stack, tokens, ressources, états
- `references/fichiers-de-reference.md` — modèles des trois fichiers
- `references/architecture-du-projet.md` — arborescence, tokens, routes, démo
- `references/valider-et-comparer.md` — empreintes, comparaison, rapport
- `references/modifier-via-les-references.md` — mode Mettre à jour
- `scripts/verifier-synchro.mjs` — fichiers ↔ code
- `scripts/relais-cloneme.mjs` — relaie la source en localhost, enregistre les relevés
- `scripts/mesurer.js` — empreintes en lot, côté navigateur (servi par le relais)
- `scripts/comparer-empreintes.mjs` — source ↔ clone
- skills partenaires : `../ui-stealer/`, `../animation-stealer/`

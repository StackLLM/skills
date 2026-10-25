# Les trois fichiers de référence

`design.md`, `palette.md` et `animation.md` sont posés à la **racine du projet
cloné**. Ils ne décrivent pas un idéal : ils décrivent **le code tel qu'il
est**. Quand l'un change, le code change ; quand le code change, ils changent.

---

## Conventions communes (lues par les scripts)

### Les identifiants

| Préfixe | Objet | Exemple |
|---|---|---|
| `P-xx` | une page ou un type de page | `P-03` article de blog |
| `C-xx` | un composant ou un gabarit | `C-01` en-tête |
| `A-xx` | une animation, une transition, une interaction animée | `A-07` menu mobile |

Un ID est **défini** quand il ouvre une ligne de tableau (`| C-01 | …`) ou un
titre (`### C-01 — En-tête`). Il ne change jamais, même si l'élément est
renommé. Un élément supprimé garde son ID, barré, avec la mention « retiré ».

Dans le code, l'ID est porté par un commentaire `cloneme:` en tête du fichier
ou au-dessus du bloc :

```tsx
/** cloneme: C-01 — En-tête. Collé en haut, fond plein après 80 px de scroll (A-02). */
```

```css
/* cloneme: A-04 — survol des cartes */
```

Plusieurs IDs : `cloneme: C-04, A-05`. `verifier-synchro.mjs` contrôle que
chaque ID défini dans les fichiers a sa marque dans le code, et inversement.

Une page **inaccessible** ou **non clonée** garde son `P-xx` : elle a quand même
une route, qui affiche la page « pas encore clonée » avec l'URL source. Cette
route porte la marque (`cloneme: P-05` dans la table des routes ou la page
d'attente). Ainsi aucune route n'est cassée et le contrôle reste juste.

### Les tokens

Une ligne de token dans `palette.md` ou `animation.md` commence par le **nom de
la variable CSS** puis la **valeur**, tous deux entre accents graves :

```md
| `--couleur-accent` | `#e5474b` | Relevé | boutons principaux, liens actifs |
```

La valeur écrite ici est **exactement** celle de `tokens.css`. Le script les
compare, à l'espace près.

### L'origine

Chaque ligne porte l'un des cinq niveaux : **Relevé**, **Mesuré**, **Déduit**,
**Approximé**, **Inaccessible** (définis dans `SKILL.md`). Une mesure porte sa
largeur : `56 px @1440`.

---

## Modèle — `design.md`

```md
# Design — <nom du site>

| | |
|---|---|
| Source | https://exemple.com/ |
| Relevé le | 2026-10-16 |
| Licence | CC BY 3.0 — attribution requise (pied de page) |
| Largeurs de référence | 1440 · 1024 · 768 · 375 |
| Stack source | HTML statique, jQuery 3, Sass compilé (Relevé) |
| Stack clone | Vite + React 18 + TypeScript + Tailwind 3 + framer-motion |

## 1. Pages et routes

| ID | Route clone | URL source | Type | Gabarit | Statut | Origine |
|---|---|---|---|---|---|---|
| P-01 | `/` | `/` | accueil | C-10 | cloné | Relevé |
| P-02 | `/generique` | `/generic.html` | page de contenu | C-10 | cloné | Relevé |
| P-99 | `*` | — | 404 | C-10 | cloné | Approximé |

## 2. Navigation et parcours

- Menu principal : liens, ordre, cible de chacun, lien actif (comment il est choisi).
- Menu mobile : seuil d'apparition, ouverture, fermeture.
- Pied de page : liens.
- Parcours clés : « accueil → section X → page Y », un par ligne.

## 3. Gabarits

### C-10 — Gabarit principal
- Structure : en-tête (C-01) · contenu · pied (C-02).
- Conteneur : largeur max `--largeur-contenu`, marges `--espace-page`.
- Fond de page : `--couleur-fond-page` + dégradé `--degrade-page`.
- Fichier : `src/gabarits/GabaritPrincipal.tsx`.

## 4. Pages, section par section

### P-01 — Accueil
| # | Section | Composants | Mise en page @1440 | @768 | @375 | Origine |
|---|---|---|---|---|---|---|
| 1 | Bandeau | C-03 | logo centré, titre, sous-titre | idem | logo 60 % | Mesuré |
| 2 | Introduction | C-04, C-05 | 2 colonnes 60/40, gouttière 48 px | 1 colonne | 1 colonne | Mesuré |

## 5. Composants

### C-01 — En-tête
- Rôle : navigation principale, collée en haut.
- Variantes : transparente (haut de page) · pleine (après défilement, A-02).
- Dimensions : hauteur 64 px @1440, 56 px @375 (Mesuré).
- Typographie : liens `--taille-menu`, `--graisse-menu`, majuscules (Relevé).
- États : survol (couleur `--couleur-accent`, Relevé `.nav a:hover`) · actif (souligné 2 px) · focus (anneau `--anneau-focus`).
- Comportement : lien actif = section visible (A-03).
- Fichier : `src/composants/EnTete.tsx`.

## 6. Typographie appliquée

| Niveau | Famille | Taille @1440 | @768 | @375 | Interligne | Graisse | Casse | Origine |
|---|---|---|---|---|---|---|---|---|
| h1 | `--police-titre` | `--taille-h1` (56 px) | 44 px | 32 px | 1.1 | 700 | — | Mesuré |

## 7. Responsive

| Point de rupture | Ce qui change | Origine |
|---|---|---|
| ≤ 980 px | grille 3 → 2 colonnes, menu → burger | Relevé `@media (max-width: 980px)` |

## 8. États de page

| État | Où | Rendu | Origine |
|---|---|---|---|
| 404 | toute route inconnue | titre, texte, retour accueil | Approximé |
| Chargement | liste d'articles | squelettes 3 cartes | Relevé `.skeleton` |
| Vide | recherche | message + bouton réinitialiser | Approximé |
| Erreur formulaire | contact | message sous le champ, bordure `--couleur-erreur` | Relevé |

## 9. Points d'intégration backend

| Fonction (`src/lib/api.ts`) | Utilisée par | Mode démo | À brancher |
|---|---|---|---|
| `envoyerContact(donnees)` | formulaire contact | renvoie `{ ok: true, demo: true }` après 600 ms | POST à définir |

## 10. Correspondance source → clone

| Élément | Sélecteur source | Composant | Sélecteur clone |
|---|---|---|---|
| titre du bandeau | `#header h1` | C-03 | `[data-ref="bandeau-titre"]` |

## 11. Limites

- Ce qui n'a pas pu être observé, et le choix fait (Approximé).
- Ressources absentes (voir `.cloneme/ressources.json`).
```

La section 10 alimente `.cloneme/cibles.json` (comparaison, voir
`valider-et-comparer.md`).

---

## Modèle — `palette.md`

```md
# Palette — <nom du site>

Ce fichier est la référence ; `ui/src/styles/tokens.css` en est le miroir
exact. Changer une valeur ici, puis demander « applique palette.md » : le code
suit.

## Couleurs

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--couleur-fond-page` | `#935d8c` | Relevé `body { background-color }` | fond de toutes les pages |
| `--couleur-surface` | `#ffffff` | Mesuré | cartes, contenu principal |
| `--couleur-texte` | `#636363` | Mesuré | corps de texte |
| `--couleur-titre` | `#555555` | Mesuré | titres |
| `--couleur-accent` | `#8cc9f0` | Relevé | liens, boutons principaux |
| `--couleur-erreur` | `#e5474b` | Approximé | messages d'erreur |

## Transparences et voiles

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--voile-menu` | `rgba(255, 255, 255, 0.95)` | Mesuré | en-tête collé |

## Dégradés

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--degrade-page` | `linear-gradient(45deg, #935d8c 15%, #49fcd4 85%)` | Relevé | fond fixe |

## Bordures et ombres

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--bordure-fine` | `1px solid #dddddd` | Mesuré | séparateurs |
| `--ombre-carte` | `0 6px 18px rgba(0, 0, 0, 0.12)` | Mesuré | cartes |

## Typographie

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--police-texte` | `"Source Sans Pro", Helvetica, sans-serif` | Relevé `@font-face` | tout le texte |
| `--taille-base` | `17px` | Mesuré @1440 | corps |
| `--taille-h1` | `2.25rem` | Relevé | titre de page |
| `--graisse-titre` | `300` | Mesuré | titres |
| `--interligne-texte` | `1.65` | Relevé | corps |
| `--lettres-titre` | `0.05em` | Relevé | titres |

## Rayons

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--rayon-carte` | `0.25em` | Relevé | cartes, boutons |

## Espacements et dimensions

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--largeur-contenu` | `64em` | Relevé | conteneur principal |
| `--espace-section` | `4em` | Relevé | padding vertical des sections |

## Couches

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--couche-entete` | `10000` | Relevé | en-tête collé |

## Points de rupture

Les `@media` ne lisent pas les variables CSS : ces valeurs vivent dans
`tailwind.config.js` (`theme.screens`).

| Nom Tailwind | Valeur | Origine |
|---|---|---|
| `md` | `max-width: 980px` | Relevé |

## Implémentation

- `tokens.css` déclare chaque variable ci-dessus dans `:root`.
- `tailwind.config.js` expose les tokens : `colors.accent = 'var(--couleur-accent)'`.
- Les composants utilisent les classes Tailwind ou `var(--…)`. Jamais une valeur en dur.
```

---

## Modèle — `animation.md`

```md
# Animations — <nom du site>

## Réglages globaux

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--duree-rapide` | `0.2s` | Relevé `transition: … .2s` | survols |
| `--courbe-standard` | `ease-in-out` | Relevé | survols, menus |

Constantes JS équivalentes : `DUREES`, `COURBES`, `RESSORTS`, `SEUILS` dans
`ui/src/lib/animations.ts`. Les valeurs sont les mêmes ; chaque constante dit
de quelle variable elle est la copie.

- Défilement lissé : oui / non (Relevé : `scroll-behavior: smooth` / Lenis).
- Bibliothèque source : GSAP 3 + ScrollTrigger (Relevé) → framer-motion.

## Inventaire

| ID | Élément | Pages | Déclencheur | Nature | Origine |
|---|---|---|---|---|---|
| A-01 | liens, boutons | toutes | survol | transition CSS | Relevé |
| A-02 | en-tête | P-01 | défilement > 80 px | classe posée par JS | Relevé |
| A-03 | menu, lien actif | P-01 | section visible | déclenché par le scroll, réversible | Relevé |
| A-04 | menu mobile | toutes @≤736 | clic burger | glissement | Relevé |

## Fiches

### A-02 — En-tête qui devient plein
- Déclencheur : `scrollY > 80` (Relevé, chunk `main.js`).
- Propriétés : `background-color` transparent → `--voile-menu` ; `box-shadow` none → `--ombre-entete`.
- Durée / retard / courbe : `--duree-rapide`, 0, `--courbe-standard`.
- Réversible : oui, en remontant.
- Mode réduit : changement immédiat, sans transition.
- Implémentation : `src/composants/EnTete.tsx` (hook `useDefilementDepasse(80)`), marque `cloneme: A-02`.

## Mode animations réduites

- `prefers-reduced-motion: reduce` respecté globalement (`animations.css`).
- Bascule manuelle : `FournisseurAnimations` (contexte UI-Stealer).
- Minuteries (carrousels) : arrêtées, contenu complet affiché.

## Ce qui n'a pas pu être lu

- A-09 : courbe exacte invisible (rAF), approchée par `power2.out` (Approximé).
```

---

## Remplir les fichiers pendant l'analyse

Les fichiers se remplissent **au fil des étapes 1 et 2**, pas à la fin :

| Relevé | Va dans |
|---|---|
| crawl, inventaire | `design.md` §1, `.cloneme/inventaire.json` |
| stack, licence | en-tête de `design.md` |
| tokens (§5) | `palette.md` |
| structure (§6) | `design.md` §3–4, §7 |
| états (§7) | `design.md` §5 (états) et, s'ils bougent, `animation.md` |
| interactions (§8) | `design.md` §2, §5, §9 |
| animations (§9) | `animation.md` |
| 404 / vide / chargement (§10) | `design.md` §8 |

Ensuite, pendant la construction, la colonne « Fichier » / « Implémentation »
est remplie au moment où le fichier de code est créé.

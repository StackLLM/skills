# Animations — Stellar (clone)

## Réglages globaux

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--duree-survol` | `0.2s` | Relevé `a`, `.button`, `#nav` | survols, menu qui se colle |
| `--courbe-lien` | `ease` | Relevé `a { transition }` | liens, menu |
| `--courbe-bouton` | `ease-in-out` | Relevé `.button`, `.icon` | boutons, icônes |
| `--duree-entete-texte` | `3s` | Relevé `#header.alt > *` | apparition du titre d'accueil |
| `--retard-entete-texte` | `0.5s` | Relevé `#header.alt > *` | retard avant cette apparition |
| `--duree-logo-fondu` | `1.25s` | Relevé `#header.alt .logo` | apparition du logo |
| `--duree-logo-rotation` | `0.5s` | Relevé `#header.alt .logo` | redressement du logo |
| `--courbe-entete` | `ease` | Relevé | les deux ci-dessus |

Constantes JS (`ui/src/lib/animations.ts`) :

| Constante | Valeur | Origine | Rôle |
|---|---|---|---|
| `RETARD_PRECHARGEMENT` | 100 ms | Relevé `main.js` : `setTimeout(…, 100)` après `load` | retire la classe `is-preload` |
| `DEFILEMENT.duree` | 1000 ms | Relevé `scrolly({ speed: 1000 })` | défilement vers une section |
| `DEFILEMENT.courbe` | `swing` = `0.5 − cos(π·t)/2` | Relevé `jquery.scrolly` (`easing: "swing"`, courbe jQuery) | idem |

- Défilement lissé global : **non**. Seuls les clics du menu défilent en douceur (A-04).
- Bibliothèque source : jQuery 3.6 + `jquery.scrollex` 0.2.1 + `jquery.scrolly` 1.0 (Relevé).
  Reproduit sans dépendance : écouteur de `scroll` + `requestAnimationFrame`.
- Pas d'`@keyframes` sur le site (Relevé : aucune règle `CSSKeyframesRule`).

## Inventaire

| ID | Élément | Pages | Déclencheur | Nature | Origine |
|---|---|---|---|---|---|
| A-01 | logo et textes de l'en-tête d'accueil | P-01 | 100 ms après le chargement | transition CSS, une seule fois | Relevé |
| A-02 | barre de navigation | P-01 | le haut de l'écran entre dans le bloc blanc | changement de classe, réversible | Relevé |
| A-03 | lien actif du menu | P-01 | le milieu de l'écran entre dans une section | changement de classe, sans transition | Relevé |
| A-04 | défilement vers une section | P-01 | clic sur un lien du menu | défilement animé en JS | Relevé |
| A-05 | liens de texte | toutes | survol | transition CSS | Relevé |
| A-06 | boutons | toutes | survol, appui | transition CSS | Relevé |
| A-07 | icônes rondes des réseaux | toutes | survol, appui | transition CSS | Relevé |
| A-08 | blocage des transitions au chargement | toutes | avant le retrait de `is-preload` | aucune transition ni animation | Relevé |

## Fiches

### A-01 — Entrée de l'en-tête d'accueil
- Déclencheur : la classe `is-preload` du `body` est retirée 100 ms après l'événement `load` (Relevé `main.js`).
- Textes (`h1`, `p`) : `opacity` 0 → 1, `--duree-entete-texte`, retard `--retard-entete-texte`, courbe `--courbe-entete`.
- Logo : `opacity` 0 → 1 en `--duree-logo-fondu` ; `transform` `scale(0.8) rotate(-30deg)` → `none` en `--duree-logo-rotation` ; retard 0.
- Réversible : non. Une fois par chargement de page. Sur la source, chaque page est un chargement complet : le clone repose `is-preload` à chaque changement de route pour garder ce comportement (`src/App.tsx`).
- Pages sans en-tête d'accueil (P-02, P-03) : pas d'entrée animée (Relevé : seul `#header.alt` est concerné).
- Mode réduit : état final affiché tout de suite.
- Implémentation : `src/composants/EnTete.css` (états `body.is-preload`), `src/main.tsx` (retrait de la classe). Marque `cloneme: A-01`.

### A-02 — Barre de navigation qui se colle
- Déclencheur : `scrollY` compris entre le haut et le bas du bloc blanc `#main` (Relevé : `scrollex({ mode: 'top' })` sur `#main`).
- Entrée : classe `alt` → `position: fixed; top: 0`, padding `1em` → `0.5em 1em`, fond `--couleur-nav-fond` → `--couleur-nav-fond-collee`, coins arrondis → carrés, marge des liens `0.35em` → `0.175em`, taille des liens `1em` → `0.9em`.
- Transitions : fond, coins et padding en `--duree-survol` `--courbe-lien` ; marge des `li` et taille des liens en `--duree-survol` `ease` (Relevé).
- Réversible : oui, la classe part dès que le haut de l'écran sort du bloc blanc.
- Masquée sous 736 px (Relevé `#nav { display: none }`).
- Mode réduit : changement d'état sans transition.
- Implémentation : `src/composants/NavSections.tsx` (écouteur de `scroll`, comme scrollex), `NavSections.css`. Marque `cloneme: A-02`.

### A-03 — Lien actif selon la section visible
- Déclencheur : le **milieu** de l'écran (`scrollY + hauteur/2`) entre dans une section liée (Relevé : `scrollex({ mode: 'middle' })`).
- Effet : le lien de cette section reçoit `active` (fond `--couleur-surface`, sans contour). Aucune transition de fond (Relevé : seule `font-size` est en transition sur ces liens).
- Verrou : un clic active son lien et le **verrouille** ; les sections traversées pendant le défilement ne changent plus le lien ; le verrou saute quand la section cible est atteinte (Relevé `active-locked`).
- Réversible : oui, en remontant.
- Implémentation : `src/composants/NavSections.tsx`. Marque `cloneme: A-03`.

### A-04 — Défilement doux vers une section
- Déclencheur : clic sur un lien `#ancre` du menu.
- Mouvement : `scrollTop` animé jusqu'au haut de la section, moins la hauteur de la barre de navigation (Relevé `offset: $nav.height()`).
- Durée 1000 ms, courbe `swing` (Relevé).
- Mode réduit : saut direct, sans animation.
- Implémentation : `src/lib/defilement.ts` (`defilerVers`), appelé par `NavSections.tsx`. Marque `cloneme: A-04`.

### A-05 — Survol des liens de texte
- `color` et `border-bottom` en `--duree-survol` `--courbe-lien` (Relevé `a`).
- Survol : soulignement pointillé → transparent ; couleur → `--couleur-blanc` sur le dégradé, `--couleur-texte` sur fond clair.
- Implémentation : `src/styles/base.css`. Marque `cloneme: A-05`.

### A-06 — Survol et appui des boutons
- `background-color` et `color` en `--duree-survol` `--courbe-bouton` (Relevé `.button`).
- Bouton simple : fond transparent → `--voile-clair` (survol) → `--voile-clair-fort` (appui) sur fond clair ; `--voile-inverse` / `--voile-inverse-fort` sur le dégradé.
- Bouton principal : `--couleur-accent` → `--couleur-accent-survol` → `--couleur-accent-appui`.
- Implémentation : `src/composants/Bouton.css`. Marque `cloneme: A-06`.

### A-07 — Survol des icônes rondes
- `background-color` en `--duree-survol` `--courbe-bouton` (Relevé `.icon`).
- Survol `--voile-clair` / appui `--voile-clair-fort` (fond clair) ; `--voile-inverse` / `--voile-inverse-fort` (dégradé).
- Implémentation : `src/composants/Icone.css`. Marque `cloneme: A-07`.

### A-08 — Pas de transition pendant le chargement
- Tant que `body.is-preload` est présent : `animation: none` et `transition: none` sur tous les éléments (Relevé `main.css` l. 109).
- Évite que les survols ou la barre de navigation s'animent au premier rendu.
- Implémentation : `src/styles/animations.css`. Marque `cloneme: A-08`.

## Mode animations réduites

- `prefers-reduced-motion: reduce` : toutes les durées passent à 0,01 ms
  (`animations.css`), le défilement A-04 devient un saut direct.
- Absent du site source (Relevé : aucune règle `prefers-reduced-motion`) :
  **ajout volontaire**, sans effet pour un visiteur sans cette préférence.

## Ce qui n'a pas été reproduit

- La classe `inactive` que `main.js` pose sur chaque section : aucune règle CSS
  ne l'utilise (Relevé). Sans effet visible, non reproduite.
- `noscript.css` : sert quand JavaScript est coupé. Le clone est une application
  React, il exige JavaScript.

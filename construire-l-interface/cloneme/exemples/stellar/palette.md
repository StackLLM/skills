# Palette — Stellar (clone)

Source unique des valeurs : `ui/src/styles/tokens.css`. Changer une valeur ici,
puis demander « applique palette.md » : le code suit.

Toutes les valeurs ci-dessous sont **Relevées** dans `assets/css/main.css` du
site source, sauf mention contraire. Mesures prises à 1440 px.

## Couleurs de fond

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--couleur-fond-page` | `#935d8c` | Relevé `body` | fond sous le dégradé, options de liste |
| `--degrade-page` | `linear-gradient(45deg, #e37682 15%, #5f4d93 85%)` | Relevé `body` | fond de toutes les pages |
| `--motif-page` | `url("/ressources/overlay.png")` | Relevé `body` | trame posée sur le dégradé |
| `--couleur-surface` | `#ffffff` | Relevé `#main` | bloc de contenu blanc, lien actif du menu |
| `--couleur-nav-fond` | `#f7f7f7` | Relevé `#nav` | barre de navigation |
| `--couleur-nav-fond-collee` | `rgba(247, 247, 247, 0.95)` | Relevé `#nav.alt` | barre collée en haut |

## Couleurs de texte

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--couleur-texte` | `#636363` | Relevé `#main` | texte et titres sur fond clair |
| `--couleur-texte-inverse` | `rgba(255, 255, 255, 0.65)` | Relevé `body` | texte sur le dégradé |
| `--couleur-blanc` | `#ffffff` | Relevé | titres, `strong`, survol des liens sur le dégradé |
| `--couleur-attenue` | `rgba(99, 99, 99, 0.25)` | Relevé `#main ::placeholder` | textes d'aide, icônes de bouton sur fond clair |
| `--couleur-attenue-inverse` | `rgba(255, 255, 255, 0.5)` | Relevé `::placeholder` | textes d'aide, icônes de bouton sur le dégradé |

## Couleurs d'accent

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--couleur-accent` | `#8cc9f0` | Relevé `.button.primary` | bouton principal, anneau de focus |
| `--couleur-accent-survol` | `#9acff2` | Relevé `.button.primary:hover` | survol du bouton principal |
| `--couleur-accent-appui` | `#7ec3ee` | Relevé `.button.primary:active` | appui du bouton principal |
| `--couleur-style1` | `#efa8b0` | Relevé `.icon.style1` | icônes et statistiques, teinte 1 |
| `--couleur-style2` | `#c79cc8` | Relevé `.icon.style2` | teinte 2 |
| `--couleur-style3` | `#a89cc8` | Relevé `.icon.style3` | teinte 3 |
| `--couleur-style4` | `#9bb2e1` | Relevé `.icon.style4` | teinte 4 |
| `--couleur-style5` | `#8cc9f0` | Relevé `.icon.style5` | teinte 5 (même valeur que l'accent) |
| `--degrade-titre` | `linear-gradient(90deg, #efa8b0, #a89cc8, #8cc9f0)` | Relevé `#main header.major h2:after` | barre sous les grands titres |

## Bordures et voiles

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--couleur-bordure` | `#dddddd` | Relevé `#main` | bordures sur fond clair |
| `--couleur-bordure-inverse` | `rgba(255, 255, 255, 0.35)` | Relevé | bordures sur le dégradé |
| `--voile-clair` | `rgba(222, 222, 222, 0.25)` | Relevé `#main .button:hover` | survol sur fond clair, champs, lignes paires |
| `--voile-clair-fort` | `rgba(222, 222, 222, 0.5)` | Relevé `#main .button:active` | appui sur fond clair |
| `--voile-inverse` | `rgba(255, 255, 255, 0.075)` | Relevé `.button:hover` | survol sur le dégradé, champs |
| `--voile-inverse-fort` | `rgba(255, 255, 255, 0.2)` | Relevé `.button:active` | appui sur le dégradé |

## Ombres

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--anneau-bouton` | `inset 0 0 0 1px #dddddd` | Relevé `#main .button` | contour des boutons sur fond clair |
| `--anneau-bouton-inverse` | `inset 0 0 0 1px rgba(255, 255, 255, 0.35)` | Relevé `.button` | contour des boutons sur le dégradé |
| `--anneau-focus` | `0 0 0 1px var(--couleur-accent)` | Relevé `input:focus` (`#8cc9f0` = l'accent) | focus des champs ; suit l'accent |

## Flèches des listes déroulantes

SVG en ligne repris tel quel de la source.

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--fleche-liste` | `url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' preserveAspectRatio='none' viewBox='0 0 40 40'%3E%3Cpath d='M9.4,12.3l10.4,10.4l10.4-10.4c0.2-0.2,0.5-0.4,0.9-0.4c0.3,0,0.6,0.1,0.9,0.4l3.3,3.3c0.2,0.2,0.4,0.5,0.4,0.9 c0,0.4-0.1,0.6-0.4,0.9L20.7,31.9c-0.2,0.2-0.5,0.4-0.9,0.4c-0.3,0-0.6-0.1-0.9-0.4L4.3,17.3c-0.2-0.2-0.4-0.5-0.4-0.9 c0-0.4,0.1-0.6,0.4-0.9l3.3-3.3c0.2-0.2,0.5-0.4,0.9-0.4S9.1,12.1,9.4,12.3z' fill='%23dddddd' /%3E%3C/svg%3E")` | Relevé `#main select` | fond clair |
| `--fleche-liste-inverse` | `url("data:image/svg+xml;charset=utf8,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='40' preserveAspectRatio='none' viewBox='0 0 40 40'%3E%3Cpath d='M9.4,12.3l10.4,10.4l10.4-10.4c0.2-0.2,0.5-0.4,0.9-0.4c0.3,0,0.6,0.1,0.9,0.4l3.3,3.3c0.2,0.2,0.4,0.5,0.4,0.9 c0,0.4-0.1,0.6-0.4,0.9L20.7,31.9c-0.2,0.2-0.5,0.4-0.9,0.4c-0.3,0-0.6-0.1-0.9-0.4L4.3,17.3c-0.2-0.2-0.4-0.5-0.4-0.9 c0-0.4,0.1-0.6,0.4-0.9l3.3-3.3c0.2-0.2,0.5-0.4,0.9-0.4S9.1,12.1,9.4,12.3z' fill='rgba(255, 255, 255, 0.35)' /%3E%3C/svg%3E")` | Relevé `select` | dégradé |

## Typographie

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--police-texte` | `"Source Sans Pro", Helvetica, sans-serif` | Relevé `body` | tout le texte |
| `--police-code` | `"Courier New", monospace` | Relevé `code` | code |
| `--police-icones` | `"Font Awesome 5 Free"` | Relevé `.icon:before` | icônes pleines et contour, coche des cases |
| `--police-icones-marques` | `"Font Awesome 5 Brands"` | Relevé `.icon.brands:before` | icônes de réseaux |
| `--taille-base` | `17pt` | Relevé `body` | taille de base au-delà de 1680 px |
| `--graisse-texte` | `300` | Relevé | texte et titres |
| `--graisse-forte` | `400` | Relevé `strong` | `strong`, `label`, `dt`, `th` |
| `--interligne-texte` | `1.65` | Relevé | corps |
| `--interligne-titre` | `1.5` | Relevé `h1…h6` | titres |
| `--lettres-titre` | `-0.025em` | Relevé | titres, chapeaux |
| `--taille-h1` | `2.5em` | Relevé | h1 |
| `--taille-h2` | `1.5em` | Relevé | h2 |
| `--taille-h3` | `1.25em` | Relevé | h3 |
| `--taille-h4` | `1.1em` | Relevé | h4 |
| `--taille-titre-majeur` | `2em` | Relevé `header.major h2` | grands titres de section |
| `--taille-chapeau` | `1.25em` | Relevé `header.major p` | phrase sous les grands titres |
| `--taille-titre-accueil` | `3.25em` | Relevé `#header.alt h1` | titre « Stellar » de l'accueil |

### Valeurs par largeur

Redéfinies dans les `@media` de `tokens.css` :

| Variable | ≤ 1680 px | ≤ 1280 px | ≤ 736 px | ≤ 480 px | ≤ 360 px |
|---|---|---|---|---|---|
| `--taille-base` | 14pt | 12pt | — | — | 11pt |
| `--taille-h1` | — | — | 2em | — | — |
| `--taille-titre-majeur` | — | — | 1.5em | — | — |
| `--taille-chapeau` | — | — | 1em | — | — |
| `--taille-titre-accueil` | — | — | 2.5em | — | — |
| `--retrait-site` | — | — | — | 2em | 0em |
| `--icone-majeure` | 5.5rem | 4.75rem | 3.5rem | — | — |
| `--gouttiere` | — | — | 1em | 1.25em | — |

## Rayons

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--rayon` | `8px` | Relevé | boutons, champs, images, statistiques |
| `--rayon-cadre` | `0.25em` | Relevé `#main`, `#nav` | bloc de contenu, haut de la navigation |

## Dimensions et espacements

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--largeur-site` | `64em` | Relevé `#wrapper` | largeur maximale du site |
| `--retrait-site` | `4em` | Relevé `#wrapper` | marge totale gauche + droite |
| `--hauteur-bouton` | `2.75em` | Relevé `.button` | hauteur des boutons et champs |
| `--largeur-min-bouton` | `9.25em` | Relevé `.button` | largeur minimale des boutons |
| `--gouttiere` | `1.5em` | Relevé `.row` | espace entre colonnes de grille |
| `--icone-majeure` | `6.25rem` | Relevé `.icon.major:before` | taille des grandes icônes rondes |
| `--marge-bloc` | `2em` | Relevé `p`, `ul`, `form` | espace sous paragraphes, listes, formulaires |

Les espacements de section, d'en-tête et de pied changent à chaque point de
rupture : ils sont écrits dans les fichiers CSS de leur composant, une ligne par
`@media`, avec la règle source en commentaire (voir `design.md`).

## Couches

| Variable | Valeur | Origine | Usage |
|---|---|---|---|
| `--couche-nav` | `10000` | Relevé `#nav.alt` | barre de navigation collée |

## Points de rupture

Les `@media` ne lisent pas les variables CSS : ces valeurs sont écrites
telles quelles dans les fichiers CSS.

| Nom source | Requête | Origine |
|---|---|---|
| xlarge | `max-width: 1680px` | Relevé `main.js` + `main.css` |
| large | `max-width: 1280px` | Relevé |
| medium | `max-width: 980px` | Relevé |
| small | `max-width: 736px` | Relevé |
| xsmall | `max-width: 480px` | Relevé |
| xxsmall | `max-width: 360px` | Relevé |

## Implémentation

- `tokens.css` déclare chaque variable ci-dessus dans `:root`, puis les valeurs
  par largeur dans des `@media`.
- Pas de Tailwind : le site source est écrit en CSS classique ; le clone garde
  un fichier CSS par composant, qui ne lit que des `var(--…)`.
- Icônes : paquet `@fortawesome/fontawesome-free@5.15.4`, mêmes classes que la
  source (`fa-code`, `fa-gem`…).

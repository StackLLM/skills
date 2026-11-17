# Design — Stellar (clone)

| | |
|---|---|
| Source | https://html5up.net/uploads/demos/stellar/ |
| Relevé le | 2026-10-16 |
| Licence | CC BY 3.0 — HTML5 UP, attribution requise (commentaire en tête du HTML et du CSS) |
| Photos | démo Unsplash (lien dans le pied de page source) |
| Largeurs de référence | 1440 · 1024 · 768 · 375 |
| Stack source | HTML statique, CSS compilé, jQuery 3.6, jquery.scrollex, jquery.scrolly, breakpoints.js (Relevé) |
| Stack clone | Vite 5 + React 18 + TypeScript + react-router-dom 6, CSS par composant + variables CSS |

## 1. Pages et routes

| ID | Route clone | URL source | Type | Gabarit | Statut | Origine |
|---|---|---|---|---|---|---|
| P-01 | `/` | `/` (`index.html`) | accueil à sections | C-01 | cloné | Relevé |
| P-02 | `/generique` | `/generic.html` | page de contenu | C-01 | cloné | Relevé |
| P-03 | `/elements` | `/elements.html` | catalogue d'éléments | C-01 | cloné | Relevé (page non liée, trouvée par sondage) |
| P-04 | `*` | toute URL inconnue | 404 | C-01 | cloné | Approximé (le serveur source rend une page générique) |

Les anciennes adresses `/generic.html`, `/elements.html` et `/index.html`
redirigent vers les routes du clone.

## 2. Navigation et parcours

- **Menu de sections** (C-03), accueil seulement : Introduction `#intro` ·
  First Section `#first` · Second Section `#second` · Get Started `#cta`.
  Lien actif = section au milieu de l'écran (A-03). Clic = défilement doux (A-04).
  Masqué sous 736 px (Relevé) : aucun menu mobile sur la source.
- **Boutons « Learn More » / « Get Started »** de l'accueil → `/generique` (Relevé `generic.html`).
- **Pied de page** : « Learn More » → `/generique` sur l'accueil, `#` sur les autres pages (Relevé).
  Liens réseaux et e-mail → `#` sur la source : liens de démonstration, centralisés dans `src/lib/configSite.ts`.
- **Liens externes** : `@ajlkn` (Twitter), HTML5 UP, Unsplash — gardés, nouvel onglet.
- **Aucun lien vers Elements** sur la source : la page existe mais n'est pas liée. Le clone fait pareil.
- Parcours clés : accueil → menu → section ; accueil → Learn More → Generic ; URL inconnue → 404 → accueil.

## 3. Gabarits

### C-01 — Gabarit principal (`#wrapper`)
- Structure : en-tête (C-02) · [menu C-03] · bloc blanc `main` · pied (C-04).
- Largeur : `--largeur-site` (64em), au plus `100% − --retrait-site` ; centré.
- Fond de page : `--motif-page` sur `--degrade-page`, sur `--couleur-fond-page`.
- Bloc blanc : fond `--couleur-surface`, texte `--couleur-texte`, coins `--rayon-cadre` ; carré sous 360 px.
- Retour en haut à chaque page ; défilement vers l'ancre si l'URL en a une.
- Fichier : `src/gabarits/GabaritPrincipal.tsx` + `.css`.

## 4. Pages, section par section

### P-01 — Accueil
| # | Section | Composants | @1440 | @768 | @375 | Origine |
|---|---|---|---|---|---|---|
| 0 | En-tête « Stellar » | C-02 (variante accueil) | logo 85 px, titre 3.25em, chapeau 1.25em | idem | titre 2.5em, chapeau 1em, sans retour à la ligne | Relevé |
| 1 | Menu | C-03 | barre grise centrée, 4 liens | idem | masqué | Relevé |
| 2 | `#intro` | C-05, C-06, C-08, C-09 | texte à gauche, image ronde 16em à droite | empilé, image au-dessus, centré | image 12em | Relevé |
| 3 | `#first` | C-05, C-06, C-10, C-08 | 3 fonctions par ligne | 2 par ligne | 1 par ligne | Relevé |
| 4 | `#second` | C-05, C-06, C-11, texte en 2 colonnes, C-08 | 5 statistiques en ligne | idem, chiffres 1.5em | empilées, 20em de large | Relevé |
| 5 | `#cta` | C-05, C-06, C-08 | 2 boutons centrés | idem | boutons pleine largeur (≤480) | Relevé |

### P-02 — Generic
| # | Section | Composants | Mise en page | Origine |
|---|---|---|---|---|
| 0 | En-tête « Generic » | C-02 (variante simple) | titre 2.5em, padding réduit | Relevé |
| 1 | `#content` | C-05, C-13 (principale) | image pleine largeur collée en haut du bloc blanc, 2 titres, 3 paragraphes | Relevé |

### P-03 — Elements
| # | Section | Composants | Origine |
|---|---|---|---|
| 0 | En-tête « Elements » | C-02 (simple) | Relevé |
| 1 | Text | C-19 (gras, italique, exposant, code, lien, hr, h2–h4, citation, bloc de code) | Relevé |
| 2 | Lists | C-14 (2 colonnes, 1 sous 980 px), listes simple / alternée / ordonnée, C-17 (icônes simples et rondes) | Relevé |
| 3 | Actions | C-14, C-08 (normale, petite, empilée, pleine largeur) | Relevé |
| 4 | Table | C-16 (défaut, alternée) | Relevé |
| 5 | Buttons | C-07 (principal, grand, petit, pleine largeur, icône, désactivé) | Relevé |
| 6 | Form | C-15 | Relevé |
| 7 | Image | C-18 (boîte sans cadre), C-14, C-13 (fit, gauche, droite) | Relevé |

### P-04 — 404
| # | Section | Composants | Origine |
|---|---|---|---|
| 0 | En-tête « Page introuvable » | C-02 (simple) | Approximé |
| 1 | Message + bouton retour accueil | C-05, C-08, C-07 | Approximé |

## 5. Composants

### C-02 — En-tête (`#header`)
- Variantes : **accueil** (`alt` : logo, titre 3.25em, padding 7em 5em 4em) · **simple** (titre 2.5em, padding 5em 5em 1em).
- Padding par largeur (Relevé) : ≤1280 `6em 4em 3em` / `4em 4em 0.1em` · ≤980 `5em 3em 2em` / `4em 3em 0.1em` · ≤736 `4em 2em 1em` / `3em 2em 0.1em` · ≤480 `4em 1.5em 1em` / `3em 1.5em 0.1em` · ≤360 `3.5em 1em 0.5em` / `2.5em 1em 0.1em` (accueil / simple).
- Logo : SVG 85 px, `max-width: 75%`, marge basse 1.5em.
- Animation : A-01 (variante accueil seulement).
- Fichier : `src/composants/EnTete.tsx` + `.css`.

### C-03 — Menu de sections (`#nav`)
- Largeur `--largeur-site`, au plus `100% − 4em` ; fond `--couleur-nav-fond` ; coins hauts `--rayon-cadre` ; padding 1em ; absolu au-dessus du bloc blanc (qui reçoit `padding-top: 4.25em`).
- Liens : hauteur 2.25em, padding `0 1.25em`, rayon `--rayon`, marge `0 0.35em` ; survol `--voile-clair` ; actif `--couleur-surface`.
- Variante collée (A-02) ; lien actif (A-03) ; clic (A-04).
- Masqué sous 736 px, et le bloc blanc perd son `padding-top`.
- Fichier : `src/composants/NavSections.tsx` + `.css`.

### C-04 — Pied de page (`#footer`)
- 2 colonnes à 50 % moins 2em, padding `5em 5em 3em` ; copyright pleine largeur, 0.8em, centré.
- ≤1280 padding `4em 4em 2em` · ≤980 une colonne, copyright aligné à gauche, padding `4em 3em 2em` · ≤736 `3em 2em 1em` · ≤480 `2.5em 1em 0.5em` (Relevé : la dernière règle écrase `3em 1.5em 1em`).
- Contenu : titre, texte, bouton · titre, liste de coordonnées (`dl.alt`), icônes rondes (C-17).
- Fichier : `src/composants/PiedDePage.tsx` + `.css`.

### C-05 — Section du bloc blanc (`#main > .main`)
- Padding `5em 5em 3em` ; ≤1280 `4em 4em 2em` ; ≤980 `4em 3em 2em` ; ≤736 `3em 2em 1em` ; ≤480 `3em 1.5em 1em` ; ≤360 `2.5em 1em 0.5em`.
- Séparateur `1px solid --couleur-bordure` entre sections.
- Variante `special` : texte centré.
- Fichier : `src/composants/SectionPrincipale.tsx` + `.css`.

### C-06 — Grand titre de section (`header.major`)
- `h2` en `--taille-titre-majeur`, barre de 3.25em × 2px sous le titre, dégradé `--degrade-titre` (fond clair) ou `--couleur-bordure-inverse` (dégradé).
- Chapeau `--taille-chapeau`, lettres `--lettres-titre`. Marge basse 3em (0 sous 736 px).
- Fichier : `src/composants/EnTeteMajeur.tsx` + `.css`.

### C-07 — Bouton
- Hauteur `--hauteur-bouton`, largeur min `--largeur-min-bouton` (0 sous 736 px), padding `0 1.5em`, rayon `--rayon`, contour `--anneau-bouton`.
- Variantes : `principal` (fond `--couleur-accent`, sans contour) · `petit` (0.8em) · `grand` (1.35em) · `pleineLargeur` · `icone` (icône Font Awesome à gauche) · `desactive` (opacité 0.25, non cliquable).
- Rendu : lien (`<Link>` interne, `<a>` externe ou `#`) ou `<button>` / `<input>` de formulaire.
- États : survol, appui (A-06).
- Fichier : `src/composants/Bouton.tsx` + `.css`.

### C-08 — Liste d'actions (`ul.actions`)
- Boutons en ligne, espacés de 1em. Variantes : `centree` (`special`) · `empilee` (`stacked`, 1.3em entre) · `pleineLargeur` (`fit`).
- Sous 480 px : empilée et pleine largeur.
- Fichier : `src/composants/Actions.tsx` + `.css`.

### C-09 — Projecteur (`.spotlight`)
- Texte flexible + image ronde 16em dans un anneau `1px --couleur-bordure`, padding 0.65em, marge gauche 4em.
- ≤980 : colonne inversée (image au-dessus), centré ; ≤736 : image 12em, padding 0.35em.
- Fichier : `src/composants/Projecteur.tsx` + `.css`.

### C-10 — Grille de fonctions (`.features`)
- 3 colonnes (33.33 % − 2em), gouttière 2em, 3em entre lignes ; ≤980 : 2 colonnes ; ≤736 : 1 colonne, 2em entre.
- Chaque fonction : icône majeure (C-12), `h3`, texte.
- Fichier : `src/composants/GrilleFonctions.tsx` + `.css`.

### C-11 — Statistiques (`.statistics`)
- 5 cases de même largeur, padding 1.5em, texte blanc centré, fonds `--couleur-style1` à `--couleur-style5`, coins extérieurs `--rayon`.
- Icône 2.75rem ; chiffre 2em (1.5em ≤980, 2.5em ≤736).
- ≤736 : empilées, largeur 20em centrée, coins en haut à droite / bas à gauche.
- Fichier : `src/composants/Statistiques.tsx` + `.css`.

### C-12 — Icône (`.icon`)
- Glyphes Font Awesome 5.15.4, styles `solid` (900) et `brands`.
- Variantes : `majeure` (double anneau rond, glyphe `--icone-majeure`) · `ronde` (`alt`, anneau 1px, glyphe 1.25em dans 2em) · teintes `style1…5`.
- États : survol / appui de la variante ronde (A-07).
- Fichier : `src/composants/Icone.tsx` + `.css`.

### C-13 — Image (`.image`)
- Rayon `--rayon`. Variantes : `principale` (pleine largeur, collée en haut du bloc blanc) · `pleine` (`fit`) · `gauche` / `droite` (40 % max, flottante).
- Fichier : `src/composants/Image.tsx` + `.css`.

### C-14 — Grille (`.row` / `.col-*`)
- Flex en ligne, gouttière `--gouttiere` ; `uniforme` ajoute la même gouttière en vertical.
- Colonnes en douzièmes, avec une largeur par point de rupture (`xlarge`, `large`, `medium`, `small`, `xsmall`, `xxsmall`).
- Fichier : `src/composants/Grille.tsx` + `.css`.

### C-15 — Formulaire de démonstration
- Champs : nom, e-mail, catégorie, priorité (radio), copie / pas un robot (cases), message.
- Bouton « Send Message » (principal) et « Reset ».
- Validation : nom et e-mail requis, e-mail au bon format ; message d'erreur sous le champ, bordure `--couleur-style1` (Approximé : la source n'en a pas, son formulaire n'a aucun contrôle).
- Envoi : `envoyerMessage()` de `src/lib/api.ts`, mode démo → « Message enregistré (mode démo, rien n'a été envoyé) ». Réinitialiser vide le formulaire et les messages.
- États : envoi en cours (bouton désactivé), succès, erreur (`?demo-erreur=1`).
- Fichier : `src/composants/FormulaireDemo.tsx` + `.css`.

### C-16 — Tableau
- Lignes séparées `1px --couleur-bordure`, une ligne sur deux `--voile-clair`, en-tête et pied séparés par 2px.
- Variante `alternee` : cellules encadrées.
- Défilement horizontal dans son conteneur si trop large.
- Fichier : `src/composants/Tableau.tsx` + `.css`.

### C-17 — Liste d'icônes (`ul.icons`)
- Icônes en ligne, espacées de 0.65em. Utilisée dans le pied (rondes) et sur Elements.
- Fichier : `src/composants/ListeIcones.tsx` + `.css`.

### C-18 — Boîte (`.box`)
- Cadre `1px`, rayon `--rayon`, padding 1.5em ; variante `sansCadre` (`alt`).
- Fichier : `src/composants/Boite.tsx` + `.css`.

### C-19 — Éléments HTML de base
- Typographie, liens, `strong`, `code`, `pre`, `blockquote`, `hr`, listes, `dl`, `sub`/`sup`, colonnes de texte (`p.content` : 2 colonnes de 20em, justifié).
- Couleurs claires dans le bloc blanc, inversées sur le dégradé.
- Fichier : `src/styles/base.css`.

## 6. Typographie appliquée

| Niveau | Famille | Taille | ≤736 | Interligne | Graisse | Origine |
|---|---|---|---|---|---|---|
| corps | `--police-texte` | `--taille-base` (17pt → 14pt ≤1680 → 12pt ≤1280 → 11pt ≤360) | — | 1.65 | 300 | Relevé |
| h1 | idem | 2.5em | 2em | 1.2 | 300 | Relevé |
| h1 accueil | idem | 3.25em | 2.5em | 1.2 | 300 | Relevé |
| h2 | idem | 1.5em | — | 1.5 | 300 | Relevé |
| h2 de section | idem | 2em | 1.5em | 1.5 | 300 | Relevé |
| h3 / h4 | idem | 1.25em / 1.1em | — | 1.5 | 300 | Relevé |
| chapeau | idem | 1.25em | 1em | 1.65 | 300 | Relevé |
| copyright | idem | 0.8em | — | 1.65 | 300 | Relevé |

Mesure de contrôle à 1440 px : corps 18.67 px, h2 de section 37.33 px, titre d'accueil 60.67 px (Mesuré).

## 7. Responsive

| Point de rupture | Ce qui change | Origine |
|---|---|---|
| ≤ 1680 px | corps 14pt, icônes majeures 5.5rem | Relevé |
| ≤ 1280 px | corps 12pt, paddings réduits, icônes 4.75rem | Relevé |
| ≤ 980 px | projecteur empilé, fonctions en 2 colonnes, pied en 1 colonne, chiffres 1.5em | Relevé |
| ≤ 736 px | menu masqué, titres réduits, fonctions en 1 colonne, statistiques empilées, boutons sans largeur min | Relevé |
| ≤ 480 px | actions empilées pleine largeur, retrait du site 2em | Relevé |
| ≤ 360 px | corps 11pt, bloc blanc sans coins ni retrait | Relevé |

## 8. États de page

| État | Où | Rendu | Origine |
|---|---|---|---|
| Chargement | toutes | `is-preload` : aucune transition, en-tête d'accueil caché puis révélé (A-01, A-08) | Relevé |
| 404 | route inconnue | en-tête « Page introuvable », message, bouton vers l'accueil | Approximé |
| Envoi du formulaire | Elements | en cours · succès démo · erreur | Approximé |
| Vide | — | aucune liste dynamique sur le site | sans objet |

## 9. Points d'intégration backend

| Fonction (`src/lib/api.ts`) | Utilisée par | Mode démo | À brancher |
|---|---|---|---|
| `envoyerMessage(donnees)` | C-15 | `{ ok: true, demo: true }` après 600 ms ; échoue si `?demo-erreur=1` | `POST /api/messages` — chemin d'exemple, à définir |

Liens de démonstration (`href="#"` sur la source) : `src/lib/configSite.ts`
(`RESEAUX`, `EMAIL_CONTACT`). À remplacer par les vraies adresses.

## 10. Correspondance source → clone

| Élément | Sélecteur source | Composant | Sélecteur clone |
|---|---|---|---|
| en-tête | `#header` | C-02 | `[data-ref=entete]` |
| titre d'en-tête | `#header h1` | C-02 | `[data-ref=entete-titre]` |
| menu | `#nav` | C-03 | `[data-ref=nav]` |
| bloc blanc | `#main` | C-01 | `[data-ref=bloc-blanc]` |
| section intro | `#intro` | C-05 | `#intro` |
| image ronde | `.spotlight .image` | C-09 | `[data-ref=projecteur-image]` |
| titre de section | `#first header.major h2` | C-06 | `#first [data-ref=titre-majeur]` |
| première fonction | `.features li` | C-10 | `[data-ref=fonction]` |
| première statistique | `.statistics li` | C-11 | `[data-ref=statistique]` |
| bouton principal | `#cta .button.primary` | C-07 | `#cta [data-ref=bouton-principal]` |
| pied | `#footer` | C-04 | `[data-ref=pied]` |
| copyright | `#footer .copyright` | C-04 | `[data-ref=copyright]` |

Le même tableau, en JSON, est dans `.cloneme/cibles.json`.

## 11. Limites

- Écart volontaire : sur Elements, le premier bouton « Icon » de la source porte la classe `solidfa-download` (espace manquant) et n'affiche pas d'icône. Le clone affiche l'icône `fa-download`.
- Gouttière de grille : 1.5em, puis 1em sous 736 px et 1.25em sous 480 px (Relevé ; trouvé à la comparaison, pas au premier relevé).
- 404 : la source n'a pas de page d'erreur propre (« File not found » générique du serveur). Page créée dans le style du site (Approximé).
- Formulaire : la source n'a ni validation ni envoi (`action="#"`). Validation et états ajoutés (Approximé), envoi en mode démo.
- E-mail du pied : masqué par Cloudflare dans le HTML source, lu après décodage dans la page (`information@untitled.tld`, adresse de démonstration).
- Script d'analyse Cloudflare (`beacon.min.js`) : non repris (mesure d'audience du site source).

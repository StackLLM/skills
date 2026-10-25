# Architecture du projet cloné

Base : le boilerplate d'**UI-Stealer** (`references/boilerplate.md`). On le
reprend, avec les différences listées ici. Lire d'abord celui d'UI-Stealer,
puis cette fiche.

---

## 1. Choisir la stack

| Situation relevée (étape 1) | Stack du clone |
|---|---|
| HTML statique, jQuery, WordPress, Webflow, Wix, Framer, React, Next | **stack maison** : Vite + React 18 + TypeScript + react-router-dom ; Tailwind 3 et framer-motion selon les deux règles ci-dessous |
| Vue / Nuxt, Svelte, Angular, Astro identifiés | demander (cas 3 de « Quand demander ») ; sans réponse, stack maison |
| Site qui dépend d'une bibliothèque visible (Swiper, Lottie, three.js, GSAP) | la même bibliothèque si l'effet n'existe pas sans elle ; sinon l'équivalent framer-motion (table d'animation-stealer) |
| Polices Google Fonts | paquet `@fontsource/<famille>` si disponible, sinon fichiers téléchargés + `@font-face` |
| Police d'icônes (Font Awesome…) | le paquet npm de la même famille et version majeure |

Une dépendance n'entre que si une page clonée l'utilise. La dire dans le
rapport avec sa raison.

### Comment écrire le style

| Le site source est écrit… | Le clone écrit son style… |
|---|---|
| en classes utilitaires (Tailwind, classes `px-4 md:…`) | en Tailwind, thème branché sur `tokens.css` (§4) |
| en CSS classique (une feuille, des classes par composant : HTML5 UP, WordPress, Bootstrap) | en **un fichier CSS par composant**, à côté du `.tsx`, qui ne lit que des `var(--…)`. Pas de Tailwind : le portage règle par règle est plus fidèle et plus court |

Même logique pour l'animation : framer-motion seulement si une animation en a
besoin (ressort, timeline, scroll accroché). Des transitions CSS et un
défilement en `requestAnimationFrame` n'en ont pas besoin. Sur le test
Stellar, le clone n'avait que 5 dépendances d'exécution.

### Porter le CSS sans le trahir

- **Garder la spécificité** des sélecteurs : `ul.actions:not(.fixed) li` ne se
  traduit pas en `ul.actions li` (il perdrait contre `ul.actions.stacked li`).
- **Garder l'ordre** des règles quand deux règles de même spécificité se
  battent (deux `@media (max-width: 480px)` : la seconde gagne).
- **Contextes de couleur** : quand un même composant change de couleurs selon
  la zone (texte clair sur fond coloré, foncé dans un bloc blanc), définir des
  variables de contexte (`--ctx-texte`, `--ctx-bordure`…) sur `body` et sur une
  classe `.contexte-clair`, et les faire lire par les composants. Une seule
  règle par composant au lieu d'une par zone.

---

## 2. Arborescence

```text
<Projet>/
├── design.md · palette.md · animation.md        ← références de travail
├── RAPPORT-CLONAGE.md                            ← rapport de validation
├── README.md                                     ← lancer, modifier, brancher
├── .cloneme/
│   ├── inventaire.json · ressources.json · cibles.json
│   ├── source/        relevés JSON du site d'origine (tokens, structure, états…)
│   ├── mesures/       empreintes source et clone (comparaison)
│   └── instantane/    copie des 3 .md au dernier état synchronisé
├── ui/
│   ├── index.html · package.json · vite.config.ts · [tailwind.config.js si Tailwind]
│   ├── postcss.config.js · tsconfig.json
│   ├── public/ressources/                        ← images, icônes, polices téléchargées
│   └── src/
│       ├── main.tsx · App.tsx · routes.tsx
│       ├── styles/
│       │   ├── tokens.css        ← palette.md + réglages globaux d'animation.md
│       │   ├── base.css          ← reset, typographie globale, éléments HTML nus
│       │   └── animations.css    ← @keyframes, transitions partagées, mode réduit
│       ├── lib/
│       │   ├── animations.ts     ← DUREES, COURBES, RESSORTS, SEUILS, variantes
│       │   ├── api.ts            ← points d'intégration backend (mode démo)
│       │   └── donneesDemo.ts    ← toutes les données de démonstration
│       ├── state/animations.tsx  ← contexte on/off (UI-Stealer), si framer-motion
│       ├── hooks/                ← si plusieurs composants partagent une logique
│       ├── gabarits/             ← GabaritPrincipal…
│       ├── composants/           ← EnTete, PiedDePage, Bouton, Carte, Modale…
│       ├── pages/                ← une page par route : PageAccueil, Page404…
│       └── test/                 ← setup.ts + tests de parcours
├── start-all.bat · stop-all.bat
└── .gitignore
```

Différences avec UI-Stealer :

- **pas de `server/`** : un clone est frontend seulement ; les points
  d'intégration sont dans `lib/api.ts` et listés dans `design.md` §9 ;
- `features/` devient `pages/` + `composants/` + `gabarits/` : le découpage
  suit `design.md` (P-xx, C-xx) ;
- **pas de React Query** sauf si une page simule un vrai chargement de liste ;
- Docker et `deploy.bat` : seulement si le user le demande ;
- **ports** : convention UI-Stealer (`600x`, créneau libre suivant). Vérifier
  qu'il est libre : `netstat -ano | findstr :600`.

---

## 3. Installer

Partir du `package.json` d'UI-Stealer (ses versions marchent ensemble) et le
réduire à ce que le clone utilise. Base validée sur le test Stellar :

```json
"dependencies": {
  "react": "^18.3.1", "react-dom": "^18.3.1", "react-router-dom": "^6.28.0",
  "@fontsource/<police-du-site>": "…", "<paquet d'icônes du site>": "<même version que la source>"
},
"devDependencies": {
  "@testing-library/dom": "^10.4.1", "@testing-library/jest-dom": "^6.9.1", "@testing-library/react": "^16.3.2",
  "@types/node": "^22.10.0", "@types/react": "^18.3.12", "@types/react-dom": "^18.3.1",
  "@vitejs/plugin-react": "^4.3.4", "jsdom": "^25.0.1", "typescript": "^5.6.3",
  "vite": "^5.4.11", "vitest": "^2.1.9"
}
```

Ajouter seulement si §1 le demande : `tailwindcss` + `postcss` +
`autoprefixer`, `framer-motion`. Ne pas reprendre de UI-Stealer ce qui est
propre à la charte Forêt : polices Inter et Instrument Serif, `lucide-react`,
`@tanstack/react-query`. Les icônes viennent du site (SVG en ligne ou police
d'icônes de la même version).

Activer les options de React Router v7 (`future={{ v7_startTransition: true,
v7_relativeSplatPath: true }}`) sur le routeur de l'application et sur celui
des tests : sinon chaque test affiche deux avertissements.

---

## 4. Tokens : une seule maison

### `src/styles/tokens.css`

```css
/* Source unique des valeurs visuelles. Miroir exact de palette.md et des
   réglages globaux d'animation.md : modifier les .md, puis le code. */
:root {
  /* Couleurs — palette.md §Couleurs */
  --couleur-fond-page: #935d8c;
  --couleur-surface: #ffffff;
  --couleur-texte: #636363;
  --couleur-accent: #8cc9f0;
  /* Typographie — palette.md §Typographie */
  --police-texte: "Source Sans Pro", Helvetica, sans-serif;
  --taille-base: 17px;
  /* Animations — animation.md §Réglages globaux */
  --duree-rapide: 0.2s;
  --courbe-standard: ease-in-out;
}
```

Une variable par ligne, `--nom: valeur;`, valeur identique au caractère près à
celle des `.md`. C'est ce que lit `verifier-synchro.mjs`.

**Un token composé réutilise les autres par `var()`.** Une ombre, un anneau de
focus ou un dégradé qui contient la couleur d'accent écrit
`0 0 0 1px var(--couleur-accent)`, pas `0 0 0 1px #8cc9f0`. Sinon, changer
l'accent dans `palette.md` laisse l'anneau à l'ancienne couleur. Trouvé au test
du mode Mettre à jour. Exception : deux tokens qui ont la même valeur par
hasard mais deux rôles différents (une teinte d'icône, une couleur d'accent)
restent séparés.

Une valeur qui change avec la largeur : la redéfinir dans un `@media` **dans
`tokens.css`**, pas dans le composant.

```css
@media (max-width: 736px) { :root { --taille-base: 14px; } }
```

### `tailwind.config.js` (si le clone utilise Tailwind)

```js
/** cloneme: les couleurs et polices pointent vers tokens.css. Aucune valeur ici. */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    screens: { petit: { max: '480px' }, mobile: { max: '736px' }, tablette: { max: '980px' } }, // Relevé @media
    extend: {
      colors: { fond: 'var(--couleur-fond-page)', surface: 'var(--couleur-surface)',
        texte: 'var(--couleur-texte)', accent: 'var(--couleur-accent)' },
      fontFamily: { texte: 'var(--police-texte)' },
      borderRadius: { carte: 'var(--rayon-carte)' },
      boxShadow: { carte: 'var(--ombre-carte)' },
      transitionDuration: { rapide: 'var(--duree-rapide)' },
    },
  },
  plugins: [],
}
```

Les `screens` reprennent **les vrais points de rupture du site** (souvent en
`max-width` : écrire `{ max: '980px' }`, pas le `md` par défaut).

Les modificateurs d'opacité Tailwind (`bg-accent/50`) ne marchent pas sur une
variable hexadécimale. Une transparence observée sur le site devient **son
propre token** (`--voile-menu`).

### Interdit dans `composants/`, `pages/`, `gabarits/`

Couleur (`#…`, `rgb(`, `hsl(`), famille de police, ombre, durée ou courbe en
dur — y compris en classe arbitraire Tailwind (`bg-[#e5474b]`). Les dimensions
propres à un seul composant (largeur d'une colonne relevée) sont autorisées en
classe arbitraire, avec la mesure d'origine en commentaire.

`verifier-synchro.mjs` signale, avec fichier et ligne : les couleurs, les
familles de police et les courbes `cubic-bezier(` écrites hors de
`tokens.css`. Il tolère les couleurs d'icônes SVG en ligne (`fill=`,
`stroke=`), les noms dans un `@font-face` et les lignes marquées
`cloneme-ok`. Il **ne voit pas** les ombres ni les durées en dur : les relire à
la main. Les courbes en tableau de `animations.ts` (`[0.22, 1, 0.36, 1]`) sont
permises ; en CSS, une courbe passe par une variable (`var(--courbe-…)`).

---

## 5. Pages et routes

### `src/routes.tsx`

```tsx
/** cloneme: table des routes — miroir de design.md §1. */
export const ROUTES = [
  { id: 'P-01', chemin: '/', page: PageAccueil, titre: 'Accueil' },
  { id: 'P-02', chemin: '/generique', page: PageGenerique, titre: 'Generic' },
] as const
```

`App.tsx` : `BrowserRouter` → `GabaritPrincipal` → `Routes` construites depuis
`ROUTES`, plus `path="*"` vers `Page404`.

Règles :

- **Route claire** : `/generic.html` devient `/generique` ; l'URL source reste
  écrite dans `design.md` §1. Ajouter une redirection depuis l'ancienne forme
  si des liens internes la portent.
- **Titre de page** : `document.title` mis à jour à chaque route (même texte
  que la source).
- **Ancres** (`/#intro`) : défilement vers l'élément après rendu, avec le
  décalage de l'en-tête collé s'il y en a un ; défilement lissé seulement si la
  source l'a.
- **Retour en haut** à chaque changement de page, sauf ancre.
- **Liens externes** du site source : gardés, `target="_blank" rel="noopener"`.
- **Page non reproduite** : une page « Cette page n'a pas encore été clonée »,
  dans le gabarit, avec l'URL source. Jamais une route cassée.

### Composants

Un composant = un fichier, nom en français et PascalCase (`EnTete`,
`CarteFonction`, `MenuMobile`), marque `cloneme: C-xx` en tête. Les variantes
sont des props (`variante="pleine"`), pas des copies.

Les **textes** du site vont dans les pages, pas dans les composants. Les
listes répétées (cartes, articles, membres) vont dans `donneesDemo.ts` quand
elles viennent d'une donnée dynamique, dans la page sinon.

### Les blancs que JSX supprime

Le HTML garde un espace entre deux balises séparées par un retour à la ligne ;
JSX le supprime. Deux cas changent le rendu :

```tsx
// Après un <br /> qu'un @media masque : sans l'espace, « template » et « built » se collent.
Just another free template<br />{' '}
built by @ajlkn

// Entre des <li> en inline-block (menu, icônes) : l'espace écarte les éléments.
{liens.map((l, i) => <Fragment key={l.id}>{i > 0 && ' '}<li>…</li></Fragment>)}
```

### Un site multi-page devenu application

Sur la source, chaque page est un **chargement complet**. Ce qui se joue « au
chargement » (classe `is-preload`, entrée animée de l'en-tête, compteur remis à
zéro) doit donc se rejouer à chaque changement de route dans le clone, sinon
l'animation ne se voit qu'une fois. Le faire dans le composant qui encadre
chaque route (`App.tsx`).

---

## 6. Données de démo et points d'intégration

### `src/lib/donneesDemo.ts`

```ts
/** cloneme: DONNÉES DE DÉMONSTRATION. Rien ici ne vient d'un serveur.
 *  Reprises du site source le 2026-10-16 (Relevé) ou inventées pour remplir
 *  la structure (marquées DEMO_INVENTE). */
export const ARTICLES_DEMO = [/* … */]
```

### `src/lib/api.ts`

```ts
/** cloneme: points d'intégration backend. Tant que MODE_DEMO vaut true, aucune
 *  requête ne part : chaque fonction rend une réponse de démonstration. */
export const MODE_DEMO = true

export async function envoyerContact(donnees: Contact): Promise<ReponseEnvoi> {
  if (MODE_DEMO) { await pause(600); return { ok: true, demo: true } }
  const r = await fetch('/api/contact', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(donnees) })
  if (!r.ok) throw new Error(`Envoi refusé (${r.status})`)
  return r.json()
}
```

- Une fonction par action qui irait au serveur (envoyer, rechercher, charger
  une liste, s'inscrire). Nom en français, types déclarés.
- Le chemin `/api/...` est un **exemple à définir**, écrit comme tel dans
  `design.md` §9. Pas d'invention de format métier au-delà des champs du
  formulaire source.
- L'interface montre l'état démo honnêtement : « Message enregistré (mode
  démo, rien n'a été envoyé) ».
- Chaque fonction a ses trois états dans l'UI : chargement, succès, erreur.
  Pour tester l'erreur : `?demo-erreur=1` dans l'URL fait échouer les
  fonctions en mode démo.

---

## 7. Animations dans le code

- `lib/animations.ts` : constantes nommées, chacune commentée avec son origine
  et l'ID `A-xx` qui l'utilise (règle d'animation-stealer : pas de valeur
  magique).
- Les durées et courbes partagées avec le CSS existent aussi en variable dans
  `tokens.css` ; la constante JS dit de quelle variable elle est la copie, et
  figure dans la table « Constantes JS » d'`animation.md` (nom + valeur) :
  `verifier-synchro.mjs` contrôle alors que le code a la même valeur.
- `animations.css` : `@keyframes` repris du site (même nom si lisible), et le
  garde global :

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; animation-iteration-count: 1 !important; transition-duration: 0.01ms !important; scroll-behavior: auto !important; }
}
```

- Si le clone utilise framer-motion : le contexte `FournisseurAnimations`
  d'UI-Stealer est repris tel quel ; chaque animation framer lit
  `useAnimations()` et sait se rendre immobile. Sans framer, le garde CSS
  ci-dessus et un test `matchMedia` dans le JS suffisent.
- Transitions de propriétés **nommées**, jamais `transition-all` sur un
  élément que framer anime (piège d'animation-stealer).

---

## 8. Lancer

`package.json` (scripts d'UI-Stealer) : `dev`, `build`, `preview`, `lint`,
`test`. `start-all.bat` et `stop-all.bat` d'UI-Stealer, **sans** la ligne
backend et sans Docker, en respectant ses règles `.bat` (aucune parenthèse
dans un `echo` à l'intérieur d'un bloc).

`README.md` du projet, quatre sections : lancer · les trois fichiers de
référence et comment les modifier · brancher un backend (`lib/api.ts`) ·
droits des ressources.

`.gitignore` : celui d'UI-Stealer, plus `.cloneme/mesures/`. Ne pas lancer
`git init` ni committer à la place du user : proposer la commande.

---

## 9. Si UI-Stealer est introuvable

Règles minimales à appliquer (le reste de cette fiche suffit) :

- Vite 5 + React 18 + TypeScript strict + react-router-dom 6 (+ Tailwind 3 et
  framer-motion 11 seulement si besoin, §1) +
  vitest 2 + jsdom + testing-library ;
- `tsconfig` : `strict`, `noUnusedLocals`, `jsx: react-jsx`, `moduleResolution: bundler` ;
- contexte animations : état initial = `!matchMedia('(prefers-reduced-motion: reduce)').matches`,
  écoute du changement, bouton de bascule ;
- validation : `npx tsc --noEmit`, `npx vitest run`, `npm run build` ;
- Windows : syntaxe PowerShell, pas de parenthèses dans les `echo` des blocs `.bat`.

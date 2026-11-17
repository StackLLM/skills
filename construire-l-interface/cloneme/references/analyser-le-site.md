# Analyser le site

Objectif : tout ce qu'on peut **lire** est lu avant d'écrire une ligne. Les
scripts ci-dessous se lancent dans le navigateur intégré avec
`javascript_tool`.

Un relevé volumineux (tokens, structure, états) n'a pas à revenir dans la
conversation : démarrer le **relais** dès l'analyse
(`valider-et-comparer.md` §2), ouvrir la source par lui
(`http://localhost:6099/…`), et terminer le script par un envoi :

```js
await fetch('http://127.0.0.1:6099/__cloneme/enregistrer?fichier=source/tokens@1440.json',
  { method: 'POST', body: JSON.stringify(resultat) })
```

Ne faire revenir dans la conversation que le résumé utile à la décision.

### Lire les fichiers bruts

Pour un site dont le HTML, le CSS et le JS sont lisibles (site statique,
WordPress, jQuery…), les télécharger dans `.cloneme/source/brut/` avec `curl`
(un fichier par requête, une pause entre deux) et les **lire en entier**. Une
valeur lue dans la feuille de style est **Relevée** ; la même lue dans un style
calculé n'est que **Mesurée** (et en `px`, alors que la source écrit souvent
`em`, `pt` ou `%`).

⚠️ Tout texte destiné à être recopié se lit **brut** : pas de `grep -v '^$'`,
pas de `sed` qui retire des blancs. Un filtre de lecture a supprimé deux lignes
d'un bloc de code pendant le test Stellar.

Pour une **section animée précise**, la méthode fine est celle
d'animation-stealer (`references/analyser-la-source.md`) : `outerHTML`, chunk
JS, timeline. Cette fiche couvre le **site entier**.

---

## 1. Ouvrir et fixer les largeurs

```text
preview_start { url: "https://exemple.com/" }
resize_window { width: 1440, height: 900 }
```

Quatre largeurs de référence, toujours les mêmes, notées à côté de chaque
mesure :

| Nom | Largeur × hauteur |
|---|---|
| bureau | 1440 × 900 |
| portable | 1024 × 768 |
| tablette | 768 × 1024 |
| mobile | 375 × 812 |

Si la navigation est refusée, essayer `www.` ou la variante sans. Une page
refusée par l'utilisateur est notée **Inaccessible**, on ne contourne pas.

Après chaque `resize_window`, recharger : certains sites calculent leur mise en
page au chargement.

---

## 2. Crawler les pages

Le crawl se fait **sans naviguer** : `fetch` + `DOMParser` depuis la page
ouverte. Trois garde-fous, appris sur un vrai test :

- **Périmètre = le dossier de départ**, pas toute l'origine. Un site hébergé
  dans un sous-dossier (`/uploads/demos/stellar/`) partage son origine avec le
  site parent : sans cette limite, le crawl part cloner le parent.
- **Jamais un lien d'action** : `download`, `logout`, `delete`, panier,
  `?action=`, attribut `download`. Un `fetch` sur ces liens déclenche l'action
  côté serveur.
- **Une pause entre deux requêtes**, arrêt net sur une réponse 429 (trop de
  requêtes) : on ne martèle pas le site.

```js
(async () => {
  const PERIMETRE = location.origin + location.pathname.replace(/[^/]*$/, '') // dossier de départ
  const MAX = 80, PAUSE = 350
  // Un segment d'URL entier, pas un mot dans un titre (« call-to-action-… » reste permis).
  const ACTION = /(^|\/)(download|downloads|telecharger|logout|log-out|deconnexion|signout|sign-out|delete|supprimer|cart|panier|checkout|add-to-cart)(\/|\.[a-z]+$|$)/i
  const vues = new Map(), ecartees = new Set(), file = [location.origin + location.pathname]
  const propre = (h, a) => { try { const u = new URL(h, location.href)
    if (a?.hasAttribute('download')) return null
    if (/\.(pdf|zip|rar|jpe?g|png|gif|webp|avif|svg|mp4|webm|mp3|xml|txt|json)$/i.test(u.pathname)) return null
    u.hash = ''; u.search = ''
    if (!u.href.startsWith(PERIMETRE) || ACTION.test(u.pathname)) { ecartees.add(u.href); return null }
    return u.href } catch { return null } }
  while (file.length && vues.size < MAX) {
    const url = file.shift(); if (vues.has(url)) continue
    try {
      const r = await fetch(url, { redirect: 'follow' })
      if (r.status === 429) { vues.set(url, { statut: 429 }); break }
      const html = await r.text()
      const d = new DOMParser().parseFromString(html, 'text/html')
      const liens = [...new Set([...d.querySelectorAll('a[href]')].map(a => propre(a.getAttribute('href'), a)).filter(Boolean))]
      vues.set(url, { statut: r.status, titre: d.title, h1: d.querySelector('h1')?.textContent.trim().slice(0, 80) ?? null,
        sections: d.querySelectorAll('section, main > *').length, liens: liens.length,
        corpsVide: (d.body?.textContent || '').replace(/\s+/g, ' ').trim().length < 50 })
      liens.forEach(l => { if (!vues.has(l)) file.push(l) })
    } catch (e) { vues.set(url, { statut: 'erreur', erreur: String(e) }) }
    await new Promise(r => setTimeout(r, PAUSE))
  }
  return { perimetre: PERIMETRE, pages: Object.fromEntries(vues), restantes: file.length,
    horsPerimetre: [...ecartees].slice(0, 40) }
})()
```

Le site cloné est **le dossier de l'URL donnée**. Si le user donne la racine
d'un domaine, le périmètre est tout le domaine. `horsPerimetre` liste ce qui a
été écarté : vérifier qu'aucune vraie page du site n'y est (un lien vers
`/blog` alors qu'on est parti de `/fr/`), et élargir `PERIMETRE` si besoin.

Lire le résultat :

- `corpsVide: true` sur toutes les pages ⇒ **site rendu côté client** (SPA). Le
  HTML brut ne contient rien. Refaire le crawl en naviguant (`navigate`) page
  par page et en lisant `document.querySelectorAll('a[href]')` après rendu.
- `restantes > 0` ⇒ plus de 80 pages. Regrouper par type (voir ci-dessous)
  avant d'aller plus loin.
- Chercher aussi `/sitemap.xml` et `/robots.txt` : ils révèlent des pages non
  liées. Respecter `robots.txt` pour le crawl.
- **Sonder les pages connues du gabarit** quand le site vient d'un modèle ou
  d'un CMS identifié : `elements.html`, `generic.html` (modèles HTML5 UP),
  `/blog`, `/contact`, `/mentions-legales`… Une page qui répond 200 sans être
  liée entre dans l'inventaire, marquée « trouvée par sondage ». Sur le test
  Stellar, la page la plus riche (Elements) n'était liée nulle part.
- Les liens du menu mobile, du pied de page et des modales comptent.

### Regrouper par type de page

Deux pages sont du même type si elles partagent le même gabarit : même suite de
sections, mêmes classes de conteneur, URL de même forme (`/blog/<slug>`).
Comparer la signature :

```js
// à lancer sur chaque page candidate (via fetch + DOMParser, comme ci-dessus)
const signature = d => [...d.querySelectorAll('body *')]
  .filter(e => /^(HEADER|NAV|MAIN|SECTION|ARTICLE|ASIDE|FOOTER|FORM)$/.test(e.tagName))
  .map(e => e.tagName + (e.id ? '#' + e.id : '') + (e.classList[0] ? '.' + e.classList[0] : ''))
  .join(' > ')
```

Écrire `.cloneme/inventaire.json` :

```json
{
  "url": "https://exemple.com/",
  "date": "2026-10-16",
  "pages": [
    { "id": "P-01", "url": "/", "type": "accueil", "statut": "à cloner" },
    { "id": "P-02", "url": "/blog/", "type": "liste-articles", "statut": "à cloner" },
    { "id": "P-03", "url": "/blog/<slug>", "type": "article", "exemples": ["/blog/a", "/blog/b"], "statut": "à cloner" },
    { "id": "P-04", "url": "/compte", "type": "compte", "statut": "inaccessible", "raison": "connexion requise" }
  ]
}
```

Statuts possibles : `à cloner`, `cloné`, `partiel`, `inaccessible`, `hors périmètre`.

---

## 3. Détecter la stack

```js
(() => {
  const q = s => !!document.querySelector(s)
  const scripts = [...document.scripts].map(s => s.src).filter(Boolean)
  const a = re => scripts.some(s => re.test(s))
  return {
    react: !!window.React || q('[data-reactroot], #root, #__next'),
    next: !!window.__NEXT_DATA__ || q('#__next') || a(/_next\//),
    vue: !!window.Vue || q('[data-v-app], [data-server-rendered]'), nuxt: !!window.__NUXT__,
    svelte: q('[class*="svelte-"]'), angular: q('[ng-version]'), astro: q('astro-island'),
    gatsby: q('#___gatsby'), wordpress: a(/wp-content|wp-includes/), webflow: q('html[data-wf-site]'),
    framer: q('[data-framer-name]'), wix: a(/wixstatic|parastorage/), shopify: !!window.Shopify,
    jquery: !!window.jQuery, bootstrap: q('[class*="col-md-"], .navbar-expand'),
    tailwind: q('[class*="px-"][class*="md:"], [class*="lg:"]'),
    gsap: !!window.gsap, scrollTrigger: !!window.ScrollTrigger, lenis: !!window.Lenis || q('.lenis'),
    locomotive: q('[data-scroll-container]'), aos: q('[data-aos]'), swiper: q('.swiper'),
    motion: q('[data-projection-id]'), lottie: q('lottie-player, [class*="lottie"]'),
    threejs: !!window.THREE || q('canvas'),
    meta: { generator: document.querySelector('meta[name=generator]')?.content ?? null,
      langue: document.documentElement.lang, viewport: document.querySelector('meta[name=viewport]')?.content },
    scripts,
    feuilles: [...document.styleSheets].map(s => s.href).filter(Boolean),
  }
})()
```

Noter dans `design.md` ce qui est **Relevé** (un script nommé `gsap.min.js`) et
ce qui est **Déduit** (des classes qui ressemblent à Tailwind).

`gsap: false` ne prouve rien sur un site Next, Nuxt ou Vite : la bibliothèque
est empaquetée et n'est pas posée sur `window`. Chercher `ScrollTrigger`,
`gsap`, `lenis`, `swiper` en texte dans les chunks JS (méthode
d'animation-stealer, `analyser-la-source.md` §3).

---

## 4. Licence et ressources

### Licence

Chercher dans le pied de page, les commentaires du HTML (`<!-- ... -->` en tête
de fichier), `/LICENSE`, `/license.txt`, les pages « mentions » ou « terms ».
L'écrire en tête de `design.md` et dans le rapport. Sans licence trouvée : « tous
droits réservés, à confirmer » — le clone reste une base de travail locale.

### Inventaire des ressources

```js
(async () => {
  const res = new Map()
  const ajoute = (url, type, ou) => { try { const u = new URL(url, location.href).href
    if (!u.startsWith('data:') && !res.has(u)) res.set(u, { type, ou }) } catch {} }
  document.querySelectorAll('img').forEach(i => { ajoute(i.currentSrc || i.src, 'image', 'img')
    ;(i.srcset || '').split(',').map(s => s.trim().split(' ')[0]).filter(Boolean).forEach(s => ajoute(s, 'image', 'srcset')) })
  document.querySelectorAll('source[srcset]').forEach(s => s.srcset.split(',').forEach(p => ajoute(p.trim().split(' ')[0], 'image', 'picture')))
  document.querySelectorAll('video[src], video source[src], audio[src]').forEach(v => ajoute(v.src, 'media', v.tagName))
  document.querySelectorAll('link[rel*=icon], link[rel=apple-touch-icon], link[rel=manifest]').forEach(l => ajoute(l.href, 'icone', l.rel))
  document.querySelectorAll('*').forEach(e => { const b = getComputedStyle(e).backgroundImage
    if (b && b !== 'none') for (const m of b.matchAll(/url\(["']?([^"')]+)["']?\)/g)) ajoute(m[1], 'image', 'css-fond') })
  for (const s of document.styleSheets) { let regles
    try { regles = [...s.cssRules] } catch { continue }
    for (const r of regles) if (r instanceof CSSFontFaceRule)
      for (const m of r.style.getPropertyValue('src').matchAll(/url\(["']?([^"')]+)["']?\)/g))
        ajoute(new URL(m[1], s.href || location.href).href, 'police', r.style.getPropertyValue('font-family')) }
  return { total: res.size, svgEnLigne: document.querySelectorAll('svg').length,
    ressources: [...res].map(([url, v]) => ({ url, ...v })) }
})()
```

Les feuilles d'une autre origine lèvent une erreur sur `cssRules` : les lire en
texte avec `fetch(s.href)` et chercher `@font-face` et `url(` dedans.

Les **SVG en ligne** (icônes) se récupèrent avec `outerHTML` et deviennent des
composants. Les **polices d'icônes** (Font Awesome…) : repérer la famille et la
version, installer le paquet npm correspondant plutôt que copier les fichiers.

### Télécharger

Images, polices, icônes, vidéos courtes : seulement. Jamais de script. Dans un
dossier dédié, depuis un terminal :

```bash
mkdir -p ui/public/ressources
curl -sSL --fail -o ui/public/ressources/<nom> "<url>"
```

Garder le nom d'origine quand il est lisible. Écrire `.cloneme/ressources.json` :

```json
[{ "url": "https://exemple.com/images/hero.jpg", "fichier": "ressources/hero.jpg",
   "statut": "téléchargé", "poids": "182 Ko", "droits": "CC BY 3.0 — attribution requise" },
 { "url": "https://cdn.exemple.com/video.mp4", "statut": "absent", "raison": "403" }]
```

Ressource en erreur (401, 403, 404, protégée) : statut `absent`, une image de
remplacement neutre de la même taille, et une ligne dans le rapport.

---

## 5. Relever les tokens

À lancer sur **chaque type de page**, à 1440 px, puis fusionner.

```js
(() => {
  const compte = {}
  const plus = (cat, v) => { if (!v || v === 'none' || v === 'normal' || v === '0px' || v === 'rgba(0, 0, 0, 0)') return
    ;(compte[cat] ??= {})[v] = (compte[cat][v] ?? 0) + 1 }
  for (const e of document.querySelectorAll('body, body *')) {
    if (!e.getClientRects().length) continue
    const c = getComputedStyle(e)
    plus('texte', c.color); plus('fond', c.backgroundColor)
    if (c.borderTopStyle !== 'none' && c.borderTopWidth !== '0px') plus('bordure', `${c.borderTopWidth} ${c.borderTopStyle} ${c.borderTopColor}`)
    plus('famille', c.fontFamily); plus('taille', c.fontSize); plus('graisse', c.fontWeight)
    plus('interligne', c.lineHeight); plus('espacement-lettres', c.letterSpacing)
    plus('rayon', c.borderRadius); plus('ombre', c.boxShadow); plus('ombre-texte', c.textShadow)
    if (c.backgroundImage.includes('gradient')) plus('degrade', c.backgroundImage)
    plus('opacite', c.opacity === '1' ? null : c.opacity)
    ;['paddingTop', 'paddingLeft', 'marginTop', 'marginBottom', 'gap', 'rowGap', 'columnGap'].forEach(p => plus('espacement', c[p]))
    plus('largeur-max', c.maxWidth)
  }
  const tri = o => Object.entries(o).sort((a, b) => b[1] - a[1]).slice(0, 25)
  const variables = {}
  for (const s of document.styleSheets) { let regles; try { regles = [...s.cssRules] } catch { continue }
    for (const r of regles) if (r.selectorText === ':root' || r.selectorText === 'html')
      for (const p of r.style) if (p.startsWith('--')) variables[p] = r.style.getPropertyValue(p).trim() }
  const medias = new Set()
  for (const s of document.styleSheets) { let regles; try { regles = [...s.cssRules] } catch { continue }
    for (const r of regles) if (r instanceof CSSMediaRule) medias.add(r.conditionText) }
  return { largeur: innerWidth, valeurs: Object.fromEntries(Object.entries(compte).map(([k, v]) => [k, tri(v)])),
    variablesCss: variables, pointsDeRupture: [...medias] }
})()
```

Lecture :

- **Variables CSS du site** (`variablesCss`) : si le site en a, reprendre ses
  noms tels quels dans `palette.md`. C'est **Relevé**.
- **Valeurs fréquentes** : les 5 à 10 couleurs les plus utilisées deviennent les
  tokens. Une couleur vue une seule fois est souvent un détail local : la noter,
  ne pas en faire un token sans raison.
- **Points de rupture** : les `@media` relevés sont les vrais seuils responsive.
  Les reprendre exactement (config Tailwind `screens`, ou `@media` du CSS).
- **Valeurs par largeur** : ce relevé ne voit que la largeur courante. Pour
  chaque token retenu, lire aussi les `@media` qui le redéfinissent (taille de
  base, gouttières, paddings). Sur le test Stellar, la gouttière de grille
  passait de 1.5em à 1em puis 1.25em : invisible à 1440 px, trouvée seulement à
  la comparaison.
- Typographie : relever aussi, par niveau (`h1`…`h6`, `p`, petit texte, bouton,
  lien de menu), la taille, l'interligne, la graisse, la casse, l'espacement
  des lettres — **à chaque largeur**. Les tailles fluides (`clamp()`, `vw`) se
  lisent dans la feuille de style, pas dans le style calculé.

```js
(() => Object.fromEntries(['h1','h2','h3','h4','p','a','button','li','small','label','input']
  .map(s => [s, document.querySelector(s)]).filter(([, e]) => e).map(([s, e]) => {
    const c = getComputedStyle(e)
    return [s, { famille: c.fontFamily, taille: c.fontSize, interligne: c.lineHeight, graisse: c.fontWeight,
      casse: c.textTransform, lettres: c.letterSpacing, couleur: c.color }] })))()
```

---

## 6. Structure d'une page

Pour chaque type de page, à chaque largeur :

```js
(() => {
  const b = e => { const r = e.getBoundingClientRect(); return { x: Math.round(r.x), y: Math.round(r.y + scrollY), l: Math.round(r.width), h: Math.round(r.height) } }
  const blocs = [...document.querySelectorAll('header, nav, main > *, section, article, aside, footer, form, dialog, [role=dialog]')]
  return { largeur: innerWidth, hauteurPage: document.documentElement.scrollHeight,
    blocs: blocs.map(e => { const c = getComputedStyle(e)
      return { balise: e.tagName.toLowerCase(), id: e.id || null, classe: e.className?.toString().slice(0, 80) || null,
        ...b(e), affichage: c.display, colonnes: c.gridTemplateColumns !== 'none' ? c.gridTemplateColumns : null,
        direction: c.display.includes('flex') ? c.flexDirection : null, gap: c.gap, padding: c.padding,
        position: c.position, fond: c.backgroundColor, image: c.backgroundImage !== 'none' ? c.backgroundImage.slice(0, 120) : null,
        titre: e.querySelector('h1,h2,h3')?.textContent.trim().slice(0, 60) ?? null } }) }
})()
```

De là sortent : l'ordre des sections, les grilles (`colonnes`), les largeurs de
conteneur, les éléments collés (`position: sticky/fixed`), et ce qui change
d'une largeur à l'autre (colonnes qui s'empilent, menu qui devient burger).

Pour une section complexe, dumper son `outerHTML` (méthode animation-stealer
§2) : les classes et styles inline donnent des mesures exactes.

---

## 7. États des composants

Les états `:hover`, `:focus`, `:active`, `:disabled`, `:checked` sont **écrits**
dans les feuilles de style. On les lit au lieu de les deviner :

```js
(() => {
  const etats = []
  const parcours = (regles, media) => { for (const r of regles) {
    if (r instanceof CSSMediaRule) parcours(r.cssRules, r.conditionText)
    else if (r.selectorText && /:(hover|focus|focus-visible|focus-within|active|disabled|checked|invalid|placeholder)|\.(is-|active|open|visible|selected|current)/.test(r.selectorText))
      etats.push({ selecteur: r.selectorText, media, regles: r.style.cssText }) } }
  for (const s of document.styleSheets) { try { parcours(s.cssRules, null) } catch {} }
  return { total: etats.length, etats: etats.slice(0, 300) }
})()
```

Classes d'état ajoutées par JS (`.is-active`, `.open`, `.visible`, `.scrolled`) :
les repérer ici, puis provoquer l'état (clic, défilement) et relire le DOM pour
savoir **qui** les pose et **quand**.

---

## 8. Interactions

Inventaire de tout ce qui réagit :

```js
(() => [...document.querySelectorAll('a[href], button, input, select, textarea, summary, [role=button], [aria-expanded], [aria-controls], [data-toggle], [data-bs-toggle], [onclick], [tabindex]:not([tabindex="-1"])')]
  .filter(e => e.getClientRects().length).map(e => ({
    balise: e.tagName.toLowerCase(), texte: (e.innerText || e.value || e.getAttribute('aria-label') || '').trim().slice(0, 40),
    href: e.getAttribute('href'), type: e.type || null, controle: e.getAttribute('aria-controls'),
    deplie: e.getAttribute('aria-expanded'), requis: e.required || null, motif: e.pattern || null })))()
```

Puis, pour chaque élément qui n'est pas un simple lien de page : le déclencher
(`element.click()` en JS — plus fiable que le clic par coordonnées) et comparer
le DOM avant / après. Noter dans `design.md` : déclencheur → effet → retour à
l'état initial (Échap, clic dehors, re-clic).

Liens `href="#"` de la source (réseaux, e-mail, échantillons de boutons) : ce
sont des liens de démonstration. Les garder tels quels, les regrouper dans un
fichier de configuration du clone, et les lister dans le rapport « à
configurer ». Ne pas inventer d'adresse.

Formulaires : lire `required`, `pattern`, `minlength`, `type=email`, les
messages d'erreur présents dans le HTML (souvent cachés), l'attribut `action`.
Ne **pas** soumettre un vrai formulaire du site source : l'envoi est hors
périmètre et la soumission n'appartient pas à l'utilisateur.

---

## 9. Animations

Pour chaque section qui bouge, appliquer animation-stealer en entier
(`analyser-la-source.md` §2–7, puis `gsap-vers-framer.md`). Les trois questions
d'animation-stealer (accroché ou déclenché, réversible ou non, piloté par le
scroll ou par une minuterie) sont tranchées **par animation** et écrites dans
`animation.md`.

Vue d'ensemble pour ne rien oublier :

```js
(() => {
  const anims = [], keyframes = {}
  for (const e of document.querySelectorAll('body *')) { const c = getComputedStyle(e)
    const nom = e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + (e.classList[0] ? '.' + e.classList[0] : '')
    if (c.animationName !== 'none') anims.push({ el: nom, animation: c.animationName, duree: c.animationDuration, courbe: c.animationTimingFunction, retard: c.animationDelay, repetition: c.animationIterationCount })
    if (c.transitionDuration.split(',').some(d => parseFloat(d) > 0)) anims.push({ el: nom, transition: c.transitionProperty, duree: c.transitionDuration, courbe: c.transitionTimingFunction, retard: c.transitionDelay }) }
  for (const s of document.styleSheets) { try { for (const r of s.cssRules) if (r instanceof CSSKeyframesRule) keyframes[r.name] = r.cssText.slice(0, 400) } catch {} }
  return { total: anims.length, anims: anims.slice(0, 200), keyframes,
    webAnimations: document.getAnimations?.().map(a => ({ id: a.id, cible: a.effect?.target?.tagName, ...a.effect?.getTiming?.() })) ?? [] }
})()
```

Ne pas oublier : en-tête qui change au défilement, lien actif du menu selon la
section visible, carrousels automatiques (chercher `setInterval`), compteurs,
apparitions au défilement, survol des cartes, ouverture du menu mobile,
ouverture des modales, transitions entre pages, curseur personnalisé, scroll
lissé.

---

## 10. États de chargement, vides, erreurs

- **404** : ouvrir `<origine>/cloneme-page-inexistante-404`. La page rendue est
  la vraie page d'erreur du site : **Relevé**. Si le serveur rend une page
  générique (nginx, Cloudflare), le noter et créer une 404 dans le style du site
  (**Approximé**).
- **Chargement** : squelettes, spinners, `[aria-busy]`, classes `loading`,
  `skeleton` dans le CSS (§7). Rarement visibles ici : les lire dans le CSS.
- **Vide** : liste sans résultat, recherche sans réponse. Si la recherche du
  site est en ligne, essayer un mot absurde. Sinon **Approximé**.
- **Erreur de formulaire** : messages cachés dans le HTML (§8) = **Relevé** ;
  sinon validation native du navigateur, dite **Approximé**.

Tout ce qui ne peut pas être observé va dans la section « Limites » de
`design.md`, avec le choix fait.

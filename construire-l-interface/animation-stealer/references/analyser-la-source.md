# Analyser la source

Objectif : sortir de la page **les vraies valeurs**, pas une impression. Tout ce
qui suit a été fait et vérifié sur un vrai site (Next.js + GSAP + ScrollTrigger).

---

## 1. Ouvrir la page

```text
preview_start { url: "https://exemple.com/en/" }
```

Si la navigation est refusée, essayer la variante du domaine (`www.`, tiret ou
non, `/en/`). Un refus de `preview_start` n’empêche pas `navigate` de marcher
ensuite sur une autre orthographe.

Puis fixer une taille d’écran de référence et **s’y tenir pour toutes les
mesures** :

```text
resize_window { width: 1440, height: 900 }
```

Toutes les valeurs relevées (hauteurs, colonnes, tailles de police) n’ont de sens
qu’à une largeur donnée. Noter la largeur à côté de chaque chiffre.

---

## 2. Isoler la section et dumper son DOM

La section porte souvent un `id` (`#about`, `#process`). Sinon, la retrouver par
son texte :

```js
(() => {
  const el = [...document.querySelectorAll('*')]
    .find(e => e.children.length === 0 && /how we work/i.test(e.textContent || ''))
  const sec = el.closest('section') || el.parentElement
  return { id: sec.id, cls: sec.className, html: sec.outerHTML.slice(0, 6000) }
})()
```

### Ce que le `outerHTML` donne gratuitement

**C’est l’étape la plus rentable de toute la skill.** Sur une section pas encore
franchie par le scroll, GSAP a déjà posé les valeurs de départ en style *inline*.
Le `from` de leur `fromTo` est donc écrit noir sur blanc :

```html
<div style="opacity: 0; transform: translate(0px, 30px);">120+</div>
<div style="opacity: 0; transform: translate(0px, 15px);">Engineers on Board</div>
<h2 style="filter: blur(6px); opacity: 0; transform: translate(0px, 40px);">…</h2>
<div style="transform: scale(0, 1);" class="origin-left">…</div>
```

Lecture directe : le chiffre monte de 30 px, son libellé de 15 px, le titre de
40 px avec un flou de 6 px, la jauge se déplie depuis la gauche (`scaleX`).
Aucune de ces valeurs n’a été devinée.

Relever aussi, dans le même dump :

- les classes utilitaires qui portent la géométrie (`lg:w-[28%]`, `py-[7.5rem]`,
  `h-[3px]`, `gap-1.5`, `max-w-[83rem]`) — ce sont des mesures exactes ;
- les états conditionnels (`w-8 bg-primary` contre `w-4 bg-azureish-white` sur
  la même liste : c’est l’élément « actif ») ;
- les `data-*` qui servent de sélecteur d’animation (`data-reveal`) : ils disent
  quels éléments partagent une même timeline et donc un même `stagger`.

---

## 3. Retrouver le code du composant

Le comportement n’est pas dans le DOM ; il est dans un chunk JavaScript. On le
retrouve en cherchant une **chaîne distinctive relevée dans le DOM** — une classe
utilitaire rare marche très bien.

```js
(async () => {
  const srcs = [...document.querySelectorAll('script[src]')].map(s => s.src)
  const hits = []
  for (const s of srcs) {
    try {
      const t = await (await fetch(s)).text()
      const marks = {}
      for (const k of ['lg:w-[28%]', 'h-[3px] rounded-full', 'data-reveal'])
        if (t.includes(k)) marks[k] = true
      if (Object.keys(marks).length) hits.push({ src: s, len: t.length, marks })
    } catch (e) {}
  }
  return hits
})()
```

Puis extraire la zone autour de la correspondance :

```js
(async () => {
  const t = await (await fetch('/_next/static/chunks/9be31…js')).text()
  const i = t.indexOf('lg:w-[28%]')
  return t.slice(Math.max(0, i - 6500), i + 2500)
})()
```

### Notes

- Chercher une **classe**, pas un texte visible : les textes des sites
  internationalisés vivent dans un dictionnaire séparé et ne sont pas dans le
  chunk du composant.
- Le code est minifié mais parfaitement lisible : `s.default.fromTo(…)`,
  `scrollTrigger:{trigger:…,start:"top 85%",toggleActions:"play none none none"}`
  survivent tels quels à la minification.
- Élargir la tranche si le `useEffect` est coupé : la logique tient souvent en
  6 à 10 ko autour du JSX.
- Si rien ne sort : la page est peut-être en CSS pur (`@keyframes`,
  `animation-timeline: view()`), en Web Animations API, ou en Framer/Webflow.
  Voir §6.

### Identifier la bibliothèque

```js
({
  gsap: !!window.gsap, scrollTrigger: !!window.ScrollTrigger,
  lenis: !!window.Lenis || !!document.querySelector('[class*=lenis]'),
  motion: !!document.querySelector('[data-projection-id]'),
  aos: !!document.querySelector('[data-aos]'),
  locomotive: !!document.querySelector('[data-scroll-container]'),
  next: !!window.__NEXT_DATA__ || !!document.querySelector('#__next'),
})
```

Un **scroll lissé** (Lenis, Locomotive) change la sensation autant que les
durées : si la source en a un et pas le projet cible, le dire.

---

## 4. Lire la timeline

Du code minifié, extraire pour **chaque élément animé** :

| À relever | Où | Exemple lu |
|---|---|---|
| valeurs de départ | 1er objet de `fromTo` | `{y:40, opacity:0, filter:'blur(6px)'}` |
| valeurs d’arrivée | 2e objet | `{y:0, opacity:1, filter:'blur(0px)'}` |
| durée | `duration` | `0.9` |
| décalage en série | `stagger` | `0.15` |
| retard | `delay` | `0.1` |
| courbe | `ease` | `power3.out` |
| seuil de départ | `scrollTrigger.start` | `"top 85%"` |
| seuil de fin | `scrollTrigger.end` | `"center 40%"`, `"+=2400"` |
| accroché ou non | `scrub` | absent = déclenché ; `1` = accroché, 1 s de retard |
| retour arrière | `toggleActions` | `"play none none reverse"` = oui |
| collage | `pin`, ou une classe `sticky` | |

Relever aussi les **minuteries** et les animations CSS, qui ne dépendent pas du
scroll du tout :

```js
(() => {
  const anim = []
  for (const e of document.querySelectorAll('#about *')) {
    const cs = getComputedStyle(e)
    if (cs.animationName !== 'none')
      anim.push({ nom: cs.animationName, duree: cs.animationDuration, timing: cs.animationTimingFunction })
    if (cs.transitionProperty !== 'all' && cs.transitionDuration !== '0s')
      anim.push({ transition: cs.transitionProperty, duree: cs.transitionDuration })
  }
  return anim
})()
```

Et dans le chunk : `setInterval`, `setTimeout`, `%` (un modulo sur une longueur
de tableau trahit une rotation en boucle).

---

## 5. Mesurer la géométrie

```js
(() => {
  const s = document.querySelector('#about')
  const b = e => { const r = e.getBoundingClientRect(); return { w: Math.round(r.width), h: Math.round(r.height) } }
  const colle = s.querySelector('.sticky, [class*=sticky]')
  return {
    section: b(s),
    paddingSection: getComputedStyle(s).padding,
    conteneur: b(s.firstElementChild),
    colle: colle && { ...b(colle), top: getComputedStyle(colle).top },
    // distance de scroll d'une scène collée = hauteur de section − hauteur collée
    courseScroll: colle ? Math.round(s.getBoundingClientRect().height - colle.getBoundingClientRect().height) : 0,
    colonnes: [...s.querySelectorAll('[class*="w-["]')].map(b),
  }
})()
```

Et les typographies, qui font partie du rythme visuel :

```js
(() => { const c = getComputedStyle(document.querySelector('#about h2'))
  return { taille: c.fontSize, interligne: c.lineHeight, graisse: c.fontWeight } })()
```

**Toujours noter la largeur d’écran à côté.** « h2 de 44 px sur 57,2 px
d’interligne, à 1440 px » est une mesure ; « un gros titre » n’en est pas une.

### Distance de scroll

- Scène **collée** : `hauteur de section − hauteur du bloc collé`. C’est la
  course utile, celle qui se convertit en pixels chez nous.
- Scène **épinglée** par GSAP : lire `end: "+=2400"` dans le chunk — 2400 px de
  course. À défaut, mesurer la hauteur totale de la section moins une hauteur
  d’écran.
- Exprimer la course **en pixels**, pas en hauteurs d’écran : le geste reste
  identique d’un portable à un grand écran.

---

## 6. Quand il n’y a pas de JS à lire

Par ordre de rendement :

1. **CSS pur** : chercher les `@keyframes` dans les feuilles de style
   (`[...document.styleSheets].flatMap(s => [...s.cssRules])` en filtrant les
   `CSSKeyframesRule`), et les `animation-timeline` / `view-timeline`.
2. **Web Animations API** : `document.getAnimations()` rend les timelines vivantes
   avec leurs `effect.getTiming()` — durée, retard, courbe, direction. Excellent.
3. **Échantillonnage** : faire défiler par pas et enregistrer les styles calculés.
   C’est la méthode de dernier recours, mais elle donne une courbe réelle :

```js
(async () => {
  const cible = document.querySelector('#process .etape')
  const releve = []
  const haut = document.querySelector('#process').getBoundingClientRect().top + scrollY
  for (let d = 0; d <= 2400; d += 150) {
    scrollTo(0, haut + d)
    await new Promise(r => setTimeout(r, 120))
    const c = getComputedStyle(cible)
    releve.push({ d, opacity: c.opacity, transform: c.transform })
  }
  return releve
})()
```

⚠️ Dans cet environnement les animations pilotées par `requestAnimationFrame`
n’avancent pas : cet échantillonnage ne marche que sur des transitions CSS ou
des transformations recalculées à chaque `scroll`. Si tous les relevés sont
identiques, c’est l’environnement, pas le site. Le dire, et se rabattre sur la
lecture du code.

---

## 7. Lire les captures

Une capture par état. Les lire toutes avec `Read`, dans l’ordre des noms.

Pour chacune, écrire :

- quels éléments sont **présents** et lesquels ne le sont pas encore ;
- la **position** de l’élément mobile dans le cadre (haut/milieu/bas, gauche/droite) ;
- l’état de l’**indicateur de progression** s’il y en a un (quel tiret est long,
  quel numéro est allumé) — c’est lui qui dit à quelle fraction on se trouve ;
- ce qui a **changé** par rapport à la capture précédente, et **seulement** cela.

Puis relier : *entre `step1` et `step2`, le troisième tiret s’allume et le visuel
a glissé d’un tiers* ⇒ à cet instant la progression vaut environ 2/5.

Les captures servent à **vérifier** la timeline lue dans le code, et à trancher
quand le code est ambigu. Elles ne la remplacent pas : deux images ne disent rien
de la courbe entre les deux.

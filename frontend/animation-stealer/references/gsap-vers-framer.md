# Traduire GSAP / ScrollTrigger vers framer-motion

La plupart des sites « à belle animation » tournent sous GSAP + ScrollTrigger.
La plupart de nos projets tournent sous framer-motion. Voici la table de passage,
établie en reproduisant deux sections réelles au comportement identique.

---

## Le partage fondamental

| GSAP | Nature | framer-motion |
|---|---|---|
| `scrollTrigger: { scrub: n }` | **accroché** au scroll, va et vient | `useScroll` + `useSpring` |
| `scrollTrigger: { toggleActions }` sans `scrub` | **déclenché** par un seuil, va au bout | `useInView` + `animate` |

Ne pas mélanger : un mouvement accroché rendu comme un déclenché saute au lieu de
glisser, et un déclenché rendu comme un accroché reste figé à mi-chemin dès qu’on
arrête la molette.

---

## Les seuils

ScrollTrigger écrit `start: "top 85%"` : « le haut du bloc atteint les 85 % de la
hauteur d’écran ».

### Pour un mouvement déclenché → `useInView`

`useInView` s’appuie sur `rootMargin`. Pour déclencher à **P %** de l’écran, on
rétrécit le bas de la racine de `100 − P` :

```ts
// "top 85%"  →  marge basse de -15 %
const vu = useInView(bloc, { margin: '0px 0px -15% 0px', once: true })
```

| ScrollTrigger | `margin` |
|---|---|
| `top 90%` | `'0px 0px -10% 0px'` |
| `top 88%` | `'0px 0px -12% 0px'` |
| `top 85%` | `'0px 0px -15% 0px'` |
| `top 80%` | `'0px 0px -20% 0px'` |
| `top 65%` | `'0px 0px -35% 0px'` |
| bande centrale (« l’étape en cours ») | `'-25% 0px -25% 0px'` |

### Pour un mouvement accroché → `useScroll`

La syntaxe d’`offset` de framer se lit dans le même sens : premier mot = le bord
du bloc, second = le point de l’écran, `0` en haut, `1` en bas.

```ts
// GSAP  start:"top 85%"  end:"center 40%"  scrub:1
const { scrollYProgress } = useScroll({ target: bloc, offset: ['start 0.85', 'center 0.4'] })
```

| ScrollTrigger | `offset` framer |
|---|---|
| `start: "top bottom"` | `'start end'` |
| `start: "top 85%"` | `'start 0.85'` |
| `start: "top top"` | `'start start'` |
| `end: "center 40%"` | `'center 0.4'` |
| `end: "bottom top"` | `'end start'` |

---

## `scrub` → ressort

`scrub: 1` veut dire « rattrape le scroll en 1 seconde ». framer n’a pas
d’équivalent direct ; un ressort mou donne exactement la même sensation :

```ts
export const ressortFilm = { stiffness: 34, damping: 30, mass: 1.1, restDelta: 0.0002 }
const trace = useSpring(scrollYProgress, ressortFilm)   // ≈ scrub: 1
```

| GSAP | Ressort |
|---|---|
| `scrub: true` (aucun retard) | pas de ressort, brancher `scrollYProgress` directement |
| `scrub: 0.3` — nerveux | `{ stiffness: 90, damping: 26, mass: 0.4 }` |
| `scrub: 1` — glissant | `{ stiffness: 34, damping: 30, mass: 1.1 }` |
| `scrub: 2` — très mou | baisser `stiffness` vers 20 |

---

## `toggleActions`

Quatre mots : `onEnter onLeave onEnterBack onLeaveBack`.

| Écrit dans la source | Sens | Chez nous |
|---|---|---|
| `"play none none none"` | une seule fois, jamais repris | `useInView(…, { once: true })` |
| `"play none none reverse"` | se rejoue à l’envers en remontant | `once` absent, et `animate` bascule entre deux états |

```ts
// "play none none reverse"
const vu = useInView(bloc, { margin: SEUILS.texte })
<motion.div
  initial={anime ? { y: 30, opacity: 0 } : false}
  animate={(!anime || vu) ? { y: 0, opacity: 1 } : { y: 30, opacity: 0 }}
  transition={{ duration: 0.6, ease: COURBE }}
/>
```

⚠️ Toujours prévoir le cas « animations coupées » : `initial={false}` et un
`animate` neutre, sinon un lecteur en mouvement réduit ne voit jamais le contenu.

---

## Les courbes

Les courbes de GSAP sont des **puissances pures** (`t^n`), pas des béziers : les
valeurs ci-dessous sont les équivalents standard, fidèles à ~1 %. Suffisant —
personne ne voit 1 % sur 0,6 s.

| GSAP | cubic-bezier |
|---|---|
| `power1.out` | `[0.25, 0.46, 0.45, 0.94]` |
| `power2.out` | `[0.215, 0.61, 0.355, 1]` |
| `power3.out` | `[0.165, 0.84, 0.44, 1]` |
| `power4.out` | `[0.23, 1, 0.32, 1]` |
| `power2.inOut` | `[0.645, 0.045, 0.355, 1]` |
| `power3.inOut` | `[0.77, 0, 0.175, 1]` |
| `back.out(1.7)` | `[0.34, 1.56, 0.64, 1]` |
| `expo.out` | `[0.19, 1, 0.22, 1]` |
| `none` / `linear` | `'linear'` |

**Dépassement fort** (`back.out(2.5)` et au-delà) : ne pas forcer un bézier, le
`y` s’envole et l’arrivée devient molle. Prendre un ressort :
`transition={{ type: 'spring', stiffness: 260, damping: 12 }}`.

Beaucoup de projets ont déjà leur courbe maison (chez nous `COURBE_DOUCE =
[0.22, 1, 0.36, 1]`, très proche de `power4.out`). **La préférer** quand la
source est en `power3`/`power4` : la cohérence du site vaut mieux qu’un écart de
2 %. Quand la source est en `power3.out` et que la différence s’entend — un
chiffre qui doit claquer, pas flotter — définir la courbe exacte localement dans
le fichier de la section, sans toucher à la bibliothèque partagée.

---

## Les propriétés animées

| GSAP | framer |
|---|---|
| `y: 40` | `y: 40` |
| `yPercent: -15` | `y: '-15%'` |
| `scaleX: 0` + `transform-origin: left` | `scaleX: 0` + classe `origin-left` |
| `filter: 'blur(6px)'` | `filter: 'blur(6px)'` — ou `useMotionTemplate` si piloté par le scroll |
| `clipPath: 'inset(0 100% 0 0)'` | idem |
| `drawSVG` / `strokeDashoffset` | `pathLength` sur un `motion.path` |
| `stagger: 0.15` | `delay: rang * 0.15` sur chaque enfant |

### Flou piloté par le scroll

`filter` n’est pas interpolable directement depuis une `MotionValue` : passer par
un gabarit.

```ts
const nettete = useTransform(progression, [debut, fin], [8, 0])
const filtre = useMotionTemplate`blur(${nettete}px)`
<motion.div style={{ filter: filtre }} />
```

### Point qui parcourt un tracé

```ts
useMotionValueEvent(trace, 'change', (v) => {
  const chemin = cheminRef.current
  const l = chemin.getTotalLength()
  const p = chemin.getPointAtLength(Math.min(1, Math.max(0, v)) * l)
  gauche.set(`${CADRE.gauche + (p.x / VB_W) * CADRE.largeur}%`)
  haut.set(`${CADRE.haut + (p.y / VB_H) * CADRE.hauteur}%`)
})
```

Le `viewBox` du SVG et le cadre en pourcentage doivent être **le même repère**,
sinon le point sort du tracé.

---

## Scènes collées et course en pixels

GSAP épingle avec `pin: true, end: "+=2400"`. On fait la même chose sans
bibliothèque, en CSS pur :

```tsx
// 2400 px de course après le premier écran. La valeur écrite dans la classe et
// la constante COURSE doivent rester égales : Tailwind ne lit que du texte.
const COURSE = 2400
<section ref={scene} className="relative h-[calc(100svh+2400px)]">
  <div className="sticky top-0 h-[100svh] overflow-hidden">…</div>
</section>
```

Repères de narration exprimés **en pixels de course**, puis ramenés en fractions.
On raisonne en « le titre commence à 495 px », qui se vérifie à la molette, et
jamais en « à 0,236 ».

```ts
const REPERES = { titre: [495, 750], chapeau: [705, 975] } as const
const fenetre = (c: keyof typeof REPERES) =>
  [REPERES[c][0] / COURSE, REPERES[c][1] / COURSE] as const
```

Faire **se chevaucher** les fenêtres : un bloc commence à se former avant que le
précédent ait fini. Sans recouvrement, la section se lit comme une liste qui
s’allume ligne à ligne.

---

## Autres bibliothèques

| Source | Traduction |
|---|---|
| **Lenis / Locomotive** (scroll lissé) | Si le projet cible en a un, ne rien faire. Sinon, ne pas en ajouter un pour une seule section : c’est un changement global. |
| **AOS** (`data-aos`, `data-aos-delay`) | Trivial : un `useInView` + un délai. Les durées AOS sont en ms. |
| **ScrollTrigger `snap`** | Pas d’équivalent framer. Le refaire à la main avec `scrollTo`, ou renoncer et le dire. |
| **`animation-timeline: view()`** (CSS) | Se transpose presque tel quel en `useScroll` + `useTransform`. Les `entry`/`exit` correspondent aux `offset`. |
| **Web Animations API** | `getAnimations()` donne durée, retard, courbe, direction : recopier tel quel. |

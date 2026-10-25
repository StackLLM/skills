# Reproduire dans le projet, puis valider

---

## 1. Lire le projet cible avant d’écrire

Trois questions, trois recherches. Aucune ligne de code avant d’y avoir répondu.

**Que fait déjà la section visée ?**
Lire son fichier en entier. Relever ce qu’elle anime, ce qu’elle rend, ce qui
dépend d’elle (une ancre, une entrée de menu, un test). Une section qu’on
remplace doit continuer à rendre le même contenu.

**Qu’est-ce que le projet sait déjà faire ?**

```text
grep -rn "useScroll\|useInView\|useSpring\|useTransform" ui/src
cat ui/src/lib/animations.ts        courbes et ressorts maison
cat ui/src/state/animations.tsx     le contexte prefers-reduced-motion
cat ui/src/composants/Revelation.tsx  le composant d'entrée déjà validé
cat ui/tailwind.config.js           couleurs, rayons, ombres, courbes
```

**Y a-t-il déjà un composant qui fait ça ?**
Une jauge de progression, une pastille d’étape, un bouton, une étiquette de
section existent probablement. Les réutiliser tels quels : c’est ce qui fait
qu’une section volée ne se voit pas comme une pièce rapportée.

---

## 2. Écrire

### Structure

Un fichier par section, des sous-composants nommés en français, et **un
en-tête de fichier qui explique le comportement** — pas ce que fait le code,
mais pourquoi il le fait comme ça : ce qui est accroché au scroll, ce qui est
déclenché, ce qui se rejoue à l’envers, ce qui ne bouge pas.

### Les constantes en tête, nommées et sourcées

```ts
/** Sortie de GSAP `power3.out`, la courbe de la référence. */
const COURBE_SORTIE = [0.165, 0.84, 0.44, 1] as const

/** Le chiffre change toutes les 3 s. Valeur relevée sur la référence. */
const TEMPO = 3000

/** Seuils d'entrée : 85 % pour le propos, 90 % pour la jauge, 88 % pour les cartes. */
const SEUILS = { propos: '0px 0px -15% 0px', jauge: '0px 0px -10% 0px' } as const
```

Une valeur sans commentaire est une valeur magique. Le commentaire dit **d’où
elle vient** et **ce qu’elle produit**.

### Le mode « animations coupées »

Chaque bloc animé doit savoir se rendre immobile et complet :

```ts
const { animations: anime } = useAnimations()
const montre = !anime || vu
initial={anime ? cache : false}
animate={montre ? net : cache}
```

Une rotation automatique ne doit pas tourner du tout en mouvement réduit : rendre
alors la liste complète, d’un coup.

### Accessibilité

Un carrousel ou un compteur qui tourne **cache** ce qu’il ne montre pas. Rendre
la liste complète en `sr-only` et marquer la partie visuelle `aria-hidden`.
Un numéro d’étape décoratif dans un bouton pollue son nom accessible : `aria-hidden`.

---

## 3. Les pièges rencontrés en vrai

| Symptôme | Cause | Correctif |
|---|---|---|
| L’effet **se répète** à chaque survol | `transition-all` transitionne aussi la propriété que `framer` anime (`clip-path`, `transform`) | Nommer les propriétés : `transition-[border-color,background-color,box-shadow]` |
| Le survol saccade une entrée animée | CSS et code animent le même `transform` | Séparer : `motion.div` extérieur pour l’entrée, élément intérieur pour le survol |
| Une parallaxe **annule** l’entrée | Deux `y` sur le même élément | Deux éléments imbriqués, un `y` chacun |
| Le texte « **redescend** » à l’ouverture | Ce n’est pas le texte : c’est le bord du conteneur qui grandit et le découvre | Retarder le fondu du texte après la fin de l’animation de hauteur ; retirer `mt-auto` |
| Un cadre rond **rogne** l’image | `border-radius: 600px` sur une boîte de 560 × 511 se ramène à une ellipse pleine | Un rayon par coin, ou un rayon ≤ moitié du plus petit côté |
| Des colonnes s’**effondrent** entre deux tailles | Le point de rupture choisi laisse une plage où le conteneur est trop étroit | Déplacer la bascule là où le conteneur est stable (souvent `xl` au lieu de `lg`) |
| Le tracé fait apparaître une **barre horizontale** | Le SVG déborde volontairement du bloc | `overflow-x-clip` sur le conteneur |
| Un compteur **gèle** | Sa minuterie est conditionnée à `useInView` | Une minuterie tourne toute seule |
| Une scène collée **déborde** de l’écran | On a ajouté un bloc sans compter la marge restante | Mesurer la marge avant, la reprendre sur les écarts, re-mesurer |

### La marge d’une scène collée

```js
(() => {
  const colle = document.querySelector('.sticky')
  const dedans = colle.querySelector('[class*=max-w-]')
  const cs = getComputedStyle(colle)
  return { marge: Math.round(colle.getBoundingClientRect().height)
    - parseInt(cs.paddingTop) - Math.round(dedans.getBoundingClientRect().height) }
})()
```

Marge négative = le contenu déborde en haut **et** en bas (centrage vertical).
Viser au moins 15 px.

---

## 4. Valider

### Ce qui ne marche pas dans cet environnement

Le navigateur intégré ne compose pas : `requestAnimationFrame` ne tourne pas,
`IntersectionObserver` ne se déclenche **jamais**, les captures expirent. Donc :

- pas de capture d’écran pour juger une animation ;
- un `useInView` reste faux pour toujours — un bloc à `opacity: 0` mesuré ici
  n’est **pas** un bug ;
- les valeurs `scaleX(0)`, `opacity: 0` relevées sont les états de départ, pas le
  résultat.

Le prouver plutôt que le supposer, avec une sonde :

```js
(async () => {
  const s = document.querySelector('#section')
  s.scrollIntoView({ block: 'center' })
  let vu = null
  const io = new IntersectionObserver(e => { vu = e.map(x => x.isIntersecting) })
  io.observe(s); await new Promise(r => setTimeout(r, 1200)); io.disconnect()
  return { rect: s.getBoundingClientRect().top, callbackIO: vu }   // vu === null ⇒ c'est l'environnement
})()
```

### Ce qui marche

**Toujours recharger en forçant avant de mesurer** — le HMR laisse des styles
calculés périmés qui envoient sur de fausses pistes.

```text
navigate { url: "http://localhost:PORT/…", force: true }
```

1. **Géométrie et styles calculés** — comparer point par point avec le tableau
   relevé sur la source : largeurs de colonnes, tailles de police, interlignes,
   rayons, couleurs, hauteur de section, course de scroll.
2. **Trois largeurs** : 1440, 768, 375. Vérifier à chaque fois l’empilement, la
   présence du bloc et `document.documentElement.scrollWidth > innerWidth`
   (débordement horizontal).
3. **Un test unitaire** pour tout ce qui est logique et non visuel : une
   minuterie, un index qui boucle, une bascule d’état. C’est le seul moyen de
   prouver un rythme ici.

```tsx
it('fait tourner le chiffre clé', () => {
  // Seules les minuteries sont truquées : rAF doit rester vrai, sinon le rendu s'arrête.
  vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval'] })
  try {
    afficherSite()
    const affiche = () => document.querySelector('#a-propos .overflow-hidden p').textContent
    expect(affiche()).toBe('12')
    act(() => void vi.advanceTimersByTime(3000))
    expect(affiche()).toBe('800+')
  } finally { vi.useRealTimers() }
})
```

⚠️ `vi.useFakeTimers()` sans `toFake` fige aussi `requestAnimationFrame` et le
rendu s’arrête. Et le `IntersectionObserver` de `jsdom` est un bouchon inerte :
ne jamais faire dépendre une logique testable d’un `useInView`.

4. **La chaîne complète** : `npx tsc --noEmit`, `npx vitest run`, `npm run build`.
   Les trois passent, sinon ce n’est pas fini.

### Ajuster tout seul

Si une mesure s’écarte de la source, corriger **sans demander au user de
décrire l’animation**. Ordre de correction, du plus probable au moins :

1. le **seuil** (`margin` / `offset`) — c’est ce qui se sent le plus ;
2. la **course** en pixels — trop courte, tout se bouscule ;
3. le **chevauchement** des fenêtres — sans lui, ça s’allume ligne à ligne ;
4. la **raideur du ressort** — trop raide, ça saute ; trop mou, ça traîne ;
5. la **durée** et le **décalage en série**, en dernier : ce sont eux qu’on lit
   dans la source, donc ceux qu’on a le moins de raisons de changer.

---

## 5. Rendre compte

Un tableau, source contre nous, ligne par élément :

| Élément | Relevé sur la source | Chez nous |
|---|---|---|
| Rotation | `setInterval` 3 000 ms | 3 000 ms |
| Chiffre | y 30 → 0, 0,5 s, `power3.out` | identique |
| Libellé | y 15 → 0, 0,5 s, retard 0,1 s | identique |
| Jauge | `scaleX` 0 → 1, 1 s, seuil 90 % | identique |
| Colonnes | 28 % / 72 %, gouttière 80 px | 308 / 792, gouttière 80 px |

Puis, en clair :

- ce qui a été **déduit** faute d’être lisible ;
- ce qui **diffère volontairement**, et pourquoi (charte, contenu, contrainte de
  hauteur) ;
- ce qui a été **mesuré** pour le prouver ;
- et le rappel que l’animation elle-même se juge en direct, pas ici.

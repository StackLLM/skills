---
name: animation-stealer
description: >
  Use when the user gives the URL of a live site (plus optionally one or more
  screenshots dropped at the project ROOT) and asks to reproduce a scroll-driven
  animation, a pinned/sticky section, a step-by-step sequence, a reveal timeline
  or any advanced interaction in their own project. Triggers: "reproduis
  l'animation de <url>", "même scroll que <site>", "comme la section How We Work
  de X", "analyse leur implémentation", an URL with a #ancre + screenshots at the
  root, "vole cette animation". The point is the BEHAVIOUR (rhythm, scroll
  distance, triggers, reverse), not the look. French project.
---

# Animation Stealer · reproduire le comportement, pas l’apparence

## Principe

Entrée = **une URL** (avec l’ancre de la section si possible) + **zéro à N
captures** déposées à la racine du projet. Sortie = la section reproduite dans le
projet cible, avec les **vraies valeurs** lues sur la source.

La règle qui commande tout le reste :

```text
même comportement → même rythme → même sensation → même logique de scroll
```

et **pas** « même apparence finale ». Une animation qui ressemble mais qui se
déclenche 200 px trop tôt, qui ne se rejoue pas à l’envers ou qui saute au lieu
de glisser est un échec, même si la capture d’écran est identique.

**Ne jamais inventer une valeur qui peut être lue.** Durée, retard, seuil,
distance de scroll, courbe : tout cela est dans leur code ou mesurable dans leur
page. On ne devine qu’en dernier recours, et on écrit alors dans le code que
c’est une déduction.

## Entrée

1. **URL** — avec l’ancre si elle existe (`…/en/#process`).
2. **Captures** à la racine du projet (`step1.png`, `step2.png`…). Elles ne sont
   pas décoratives : chacune est **un état de la timeline**. Les lire toutes avec
   `Read`, dans l’ordre des noms, et en tirer ce qui bouge d’un état à l’autre.
3. Éventuellement le nom de la section (« How We Work », « Who We Are »).

S’il n’y a pas de capture, on travaille depuis la source seule — c’est suffisant.
S’il n’y a pas d’URL, cette skill ne s’applique pas : passer à `UI-Stealer`.

## Déroulé

Chaque étape a sa fiche. Les suivre dans l’ordre, sans en sauter.

| # | Étape | Fiche |
|---|---|---|
| 1 | Ouvrir la page, isoler la section, **dumper son `outerHTML`** | `references/analyser-la-source.md` |
| 2 | Retrouver le **code minifié** du composant dans les chunks JS | idem |
| 3 | Lire la timeline réelle : durées, retards, seuils, courbes | idem |
| 4 | Mesurer la géométrie : hauteur, collage, distance de scroll | idem |
| 5 | Lire les captures et reconstruire l’ordre des états | idem |
| 6 | Traduire GSAP/ScrollTrigger → l’outil du projet | `references/gsap-vers-framer.md` |
| 7 | Lire le projet cible **avant** d’écrire une ligne | `references/reproduire-et-valider.md` |
| 8 | Implémenter avec les valeurs relevées, commentées | idem |
| 9 | Valider par mesures, pas par capture d’écran | idem |

## Les trois questions à trancher avant d’écrire du code

Elles décident de toute l’architecture. Y répondre **explicitement**, en citant
le code source lu.

1. **Le mouvement est-il accroché au scroll, ou déclenché par lui ?**
   *Accroché* (`scrub`) : il avance et recule avec la molette, il peut rester à
   mi-chemin. *Déclenché* : un seuil le lance et il va au bout tout seul.
   Un composant mélange souvent les deux — le tracé est accroché, les entrées
   sont déclenchées. Les distinguer une par une.

2. **Se rejoue-t-il à l’envers quand on remonte ?**
   GSAP l’écrit noir sur blanc : `toggleActions: "play none none reverse"`
   (oui) contre `"play none none none"` (non, une seule fois).
   C’est **la** différence qu’on sent le plus à l’usage.

3. **Le scroll pilote-t-il vraiment la progression ?**
   ⚠️ Piège rencontré en vrai : sur la section « Who We Are » de Digitalia, le
   passage d’un chiffre au suivant **n’est pas piloté par le scroll du tout**.
   C’est un `setInterval(…, 3000)`. Le scroll ne déclenche que les entrées.
   Chercher `setInterval`, `setTimeout`, `requestAnimationFrame` et
   `animation:` CSS avant de conclure « scroll-driven ».

## Non négociables

- **Réutiliser l’existant du projet cible** : composants, contexte d’animations,
  courbes maison, ressorts déjà définis, tokens de charte. On n’ajoute une
  dépendance que si l’effet est strictement impossible sans elle — et on le dit.
- **Ne jamais copier leur charte** : couleurs, typos, rayons, ombres viennent du
  projet cible. On vole le **timing**, pas le style.
- **Ne rien casser** : avant de toucher un fichier, lister ce qu’il anime déjà et
  ce qui dépend de lui. Ne pas modifier les autres sections, ni le contenu
  métier, ni supprimer une fonctionnalité.
- **Respecter `prefers-reduced-motion`** : le projet a presque toujours un
  contexte d’animations. Une minuterie et un mouvement accroché au scroll doivent
  tous deux savoir s’éteindre.
- **Commenter les valeurs volées** : `duration: 0.9` sans commentaire est une
  valeur magique. Écrire d’où elle vient (« relevé sur la référence ») et à quoi
  elle sert. Le prochain lecteur doit pouvoir la remettre en cause.

## Le piège central de cet environnement

Le navigateur intégré **ne compose pas** : `requestAnimationFrame` ne tourne pas,
`IntersectionObserver` ne se déclenche jamais, et les captures d’écran expirent
sur une animation infinie.

Conséquence directe : **on ne valide jamais une animation à l’œil ici.** On
valide par la structure DOM, les styles calculés, la géométrie mesurée, un test
unitaire pour ce qui est logique (minuterie, index, bascule d’état), puis
`tsc` + `vitest` + `build`. Et on dit au user de regarder en direct.

Corollaire : si une valeur mesurée paraît absurde, **recharger en forçant**
(`navigate … force: true`) avant de conclure. Le HMR laisse des styles calculés
périmés qui envoient sur de fausses pistes.

## Erreurs déjà commises — à ne pas refaire

| Erreur | Correctif |
|--------|-----------|
| Conclure « scroll-driven » sans lire le JS | C’était un `setInterval` de 3 s. Chercher les minuteries avant tout. |
| Approximer les seuils « à peu près 80 % » | Les seuils sont écrits dans le code : `start: "top 85%"`. Les convertir, pas les deviner. |
| `transition-all` sur un bloc dont `framer` anime le `clip-path` | La CSS et le code animent la même propriété et se battent. Nommer les propriétés une par une. |
| Coupler une minuterie à `useInView` | Si l’observateur ne répond pas, le compteur gèle pour toujours. Une minuterie tourne toute seule. |
| Deux transformations sur le même élément (parallaxe + entrée) | Les séparer sur deux éléments imbriqués. |
| Relancer des captures qui expirent | Mesurer le DOM et les styles calculés. |
| Poser un bloc de 51 px dans une scène collée à `100svh` sans compter | Mesurer la marge disponible **avant**, la reprendre sur les écarts, re-mesurer après. |
| Se fier au HMR pour mesurer | `navigate … force: true` d’abord. |

## Rendre compte

À la fin, livrer au user :

1. **le tableau des valeurs relevées** — une ligne par élément animé, avec la
   valeur source et ce qui a été mis chez nous ;
2. **ce qui n’a pas pu être lu** et a donc été déduit, dit franchement ;
3. **ce qui a été mesuré** après coup pour prouver la fidélité ;
4. **ce qui diffère volontairement**, et pourquoi.

Style de la réponse : celui du projet (français simple, sections `##`, chemins
regroupés à la fin).

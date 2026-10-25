# Animation Stealer

> Skill StackLLM · v0.1.0 · usage interne, pas encore commercialisée

**Une animation que vous aimez sur un site. La même sensation dans votre projet.**

Animation Stealer reproduit le **comportement** d'une section animée : rythme, distance de scroll, déclencheurs, lecture à l'envers. Pas seulement son apparence finale.

## Le problème

Une animation « presque pareille » se déclenche 200 px trop tôt, ne se rejoue pas à l'envers, ou saute au lieu de glisser. La capture est identique, la sensation est fausse.

## Ce que fait Animation Stealer

- Lit l'implémentation de la source : HTML, fichiers JavaScript, timeline, géométrie, minuteries.
- Relève les **vraies valeurs** : durées, retards, seuils, distances, courbes. Une valeur devinée est marquée comme déduction dans le code.
- Traduit les timelines GSAP en framer-motion (table de correspondance fournie).
- Gère le mode « animations réduites ».
- Valide par mesures : DOM, styles calculés, géométrie, tests unitaires, `tsc`, `vitest`, `build`.

## Pour qui

Développeurs front et studios qui doivent reproduire une interaction précise : section épinglée, séquence par étapes, révélation au scroll.

## Installation

Depuis la racine du dépôt `skills` :

```bash
./install.sh animation-stealer
```

Voir le [README du dépôt](../../README.md) pour l'installation complète.

## Utilisation

1. Donner l'URL, avec l'ancre de la section si possible (`…/#process`).
2. Optionnel : déposer des captures numérotées à la racine du projet (`step1.png`, `step2.png`…).
3. Dans Claude Code : « reproduis l'animation de <url> », « même scroll que <site> ».

## Prérequis

- Claude Code avec un navigateur piloté.
- Un projet cible React avec framer-motion.

## Limites connues

- Une section à la fois. Pour un site entier, utiliser CloneMe.
- Le navigateur intégré ne joue pas les animations : la validation finale à l'œil se fait par vous, en direct.
- Le style de la source n'est pas copié : la charte reste celle de votre projet.

## Contenu

| Chemin | Rôle |
|---|---|
| `SKILL.md` | principe, déroulé, non négociables |
| `references/analyser-la-source.md` | lire et mesurer l'implémentation |
| `references/gsap-vers-framer.md` | correspondance GSAP → framer-motion |
| `references/reproduire-et-valider.md` | construire et prouver |

## Mise à jour

`git pull` à la racine du dépôt. Les liens installés suivent automatiquement. Les changements sont dans `CHANGELOG.md`.

## Licence

Propriétaire, tous droits réservés. Voir le [LICENSE](../../LICENSE) du dépôt.

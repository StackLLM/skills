# Mode Mettre à jour — le code suit les fichiers

Le user modifie `design.md`, `palette.md` ou `animation.md`, puis dit
« applique les changements », « mets à jour le site », « j'ai changé la
palette ». CloneMe répercute **seulement** ce qui a changé.

---

## 1. Trouver ce qui a changé

La photo du dernier état synchronisé est dans `.cloneme/instantane/`. On
compare sans dépôt git nécessaire :

```bash
git diff --no-index --word-diff .cloneme/instantane/palette.md palette.md
git diff --no-index --word-diff .cloneme/instantane/design.md design.md
git diff --no-index --word-diff .cloneme/instantane/animation.md animation.md
```

(`git diff --no-index` marche hors dépôt ; code de sortie 1 = différences, pas
une erreur.)

Pas d'instantané (projet ancien, fichier supprimé) : lancer
`verifier-synchro.mjs`. Ses écarts « valeur différente » sont exactement les
changements de `palette.md` et `animation.md` non encore appliqués. Pour
`design.md`, demander au user ce qu'il a changé.

Écrire la liste des changements avant de toucher au code, une ligne par
changement :

| Fichier | Changement | IDs ou variables touchés |
|---|---|---|
| palette.md | `--couleur-accent` `#8cc9f0` → `#e5474b` | `--couleur-accent` |
| design.md | C-05 : 3 colonnes → 2 colonnes @1440 | C-05 |
| animation.md | A-04 : durée 0.2s → 0.35s | A-04, `--duree-rapide` |

---

## 2. Trouver le code concerné

| Changement | Où chercher |
|---|---|
| variable CSS (`--…`) | `tokens.css` — c'est tout l'intérêt ; plus `lib/animations.ts` si la table « Constantes JS » d'`animation.md` en a une copie |
| constante JS (`DEFILEMENT.duree`) | `lib/animations.ts` |
| ID `C-xx` ou `P-xx` | `grep -rn "cloneme:.*C-05" ui/src` |
| ID `A-xx` | `grep -rn "cloneme:.*A-04" ui/src` + `lib/animations.ts` |
| nouveau composant, nouvelle page | aucune marque encore : créer, marquer, ajouter à `routes.tsx` |
| point de rupture | `tailwind.config.js` `screens` + `@media` de `tokens.css` |

Si un changement de valeur oblige à toucher un composant (une couleur écrite en
dur), c'est une dette : la corriger en passant par un token, et le dire.

---

### Avant de toucher au code : la photo « avant »

Mesurer le clone tel qu'il est, dans un dossier à part (relais démarré,
`valider-et-comparer.md` §2) :

```js
(await import('http://127.0.0.1:6099/__cloneme/mesurer.js')).lancer({ cote: 'clone', sortie: 'clone-avant' })
```

C'est la base de la vérification : on comparera « avant » et « après », pas la
source (les écarts déjà acceptés avec la source resteraient sinon mélangés aux
nouveaux).

## 3. Appliquer, sans toucher au reste

- Modifier **uniquement** les fichiers trouvés à l'étape 2.
- Un token changé ne se « corrige » pas ailleurs : s'il produit un effet
  inattendu sur une autre page, c'est que le token est partagé — le dire au
  user, proposer un token séparé, ne pas le créer sans accord.
- Un changement de structure (`design.md`) suit l'ordre de construction de
  `SKILL.md` : composant partagé d'abord, pages ensuite.
- Un changement d'animation reprend les règles d'animation-stealer : valeur
  commentée, mode réduit, propriétés de transition nommées.
- Ce qui ne peut pas être fait tel quel (contradiction entre deux fichiers,
  valeur impossible) : ne pas deviner, poser la question avec son contexte.

---

## 4. Vérifier

1. `node <dossier-CloneMe>/scripts/verifier-synchro.mjs <projet>` — zéro écart.
2. `npx tsc --noEmit` · `npx vitest run` · `npm run build`.
3. Remesurer le clone (`lancer({ cote: 'clone' })`, après avoir effacé
   `mesures/clone/_fini.txt`) et comparer **avant / après** :

   ```bash
   node <dossier-CloneMe>/scripts/comparer-empreintes.mjs --dossier .cloneme/mesures --a clone-avant --b clone
   ```

   Les **seuls** écarts doivent être ceux voulus. Exemple réel (test Stellar,
   accent changé) : un seul écart,
   `bouton-principal backgroundColor rgb(140, 201, 240) → rgb(229, 71, 75)`.
4. Une **page non concernée** doit rester à zéro écart. C'est la preuve que le
   reste est préservé.
5. Chercher les tokens composés qui contiennent l'ancienne valeur en dur
   (`grep -n "<ancienne valeur>" tokens.css`) : une ombre ou un anneau qui
   devait suivre la couleur. Les relier par `var()` et le dire au user.

Le site source n'est plus la référence en mode Mettre à jour : **les fichiers
le sont**. Les écarts avec la source qui viennent d'un changement voulu ne sont
pas des défauts.

---

## 5. Clore

- Recopier les trois fichiers dans `.cloneme/instantane/`.
- Ajouter une ligne au journal en bas de `RAPPORT-CLONAGE.md` :
  `2026-10-20 — palette.md : accent passé en rouge (--couleur-accent) — 1 fichier de code modifié.`
- Dire au user : ce qui a changé, les fichiers de code touchés, ce qui a été
  mesuré, ce qu'il doit regarder en direct.

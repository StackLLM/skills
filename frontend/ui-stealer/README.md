# UI Stealer

> Skill StackLLM · v0.1.0 · usage interne, pas encore commercialisée

**Une image de maquette en entrée. Une interface React qui tourne en sortie.**

Vous déposez une maquette, une capture ou un export Figma dans `Template/`, et vous dites « go ». UI Stealer reproduit la structure de l'image dans une charte cohérente, sans reposer de questions déjà tranchées.

## Le problème

Passer d'une maquette à un front qui fonctionne demande une phase de découpe longue et répétitive. Les décisions de stack, d'arborescence et d'animation sont refaites à chaque projet.

## Ce que fait UI Stealer

- Lit chaque image de `Template/` : une image = un écran ou un état.
- Reproduit la **structure** de l'image, habillée à la **charte Forêt** (Encre, Papier, Forêt, Saphir · Inter + Instrument Serif), jamais la palette d'origine.
- Pose une stack et une arborescence prêtes : Vite, React, TypeScript, Tailwind, framer-motion, vitest.
- Fournit des recettes d'écran : accueil avec héros, cartes et zone de saisie, vue conversation.
- Livre les scripts de démarrage, d'arrêt et Docker.
- Vérifie avec `tsc --noEmit`, `vitest run` et `build`.

## Pour qui

Développeurs et équipes produit qui veulent passer vite d'une maquette à une interface vivante et propre.

## Installation

Depuis la racine du dépôt `skills` :

```bash
./install.sh ui-stealer
```

Voir le [README du dépôt](../../README.md) pour l'installation complète.

## Utilisation

1. Déposer une ou plusieurs images dans `Template/` à la racine du projet.
2. Dans Claude Code : « go », « construis », « même que l'image ».

## Prérequis

- Node.js et npm.
- Les scripts fournis visent Windows (`.bat`, PowerShell). Sur macOS ou Linux, les commandes `npm` restent valables ; les scripts de lancement sont à adapter.

## Limites connues

- Une image ne montre pas les états cachés (menus ouverts, erreurs) : ils sont déduits.
- Le périmètre par défaut est accueil + conversation pour une app de questions-réponses.
- La charte Forêt est imposée par défaut. Pour une autre charte, remplacer les jetons de `references/boilerplate.md`.
- Les captures du navigateur intégré figent sur les animations : la validation passe par le DOM et les tests.

## Contenu

| Chemin | Rôle |
|---|---|
| `SKILL.md` | instructions et défauts fermes |
| `references/boilerplate.md` | arborescence, configs, charte, scripts |
| `references/recettes-ui.md` | écrans types prêts à adapter |
| `references/pieges-et-livraison.md` | pièges connus, Git, partage réseau |

## Mise à jour

`git pull` à la racine du dépôt. Les liens installés suivent automatiquement. Les changements sont dans `CHANGELOG.md`.

## Licence

Propriétaire, tous droits réservés. Voir le [LICENSE](../../LICENSE) du dépôt.

# CloneMe

> Skill StackLLM · v0.1.0 · usage interne, pas encore commercialisée

**Une URL en entrée. Un projet frontend complet qui se lance en sortie.**

CloneMe reproduit un site entier : toutes les pages accessibles, leurs composants, leurs états et leurs animations. Le projet produit est piloté par trois fichiers de référence lisibles par un humain : `design.md`, `palette.md` et `animation.md`.

## Le problème

Refaire un site de référence à la main prend des jours. Le résultat ressemble souvent à la page d'accueil seulement, avec des valeurs devinées et des boutons qui ne font rien.

## Ce que fait CloneMe

- **Analyse** le site : pages, stack, licence, ressources, composants, états, animations, à 4 largeurs d'écran.
- **Écrit** trois fichiers de référence. Chaque valeur y porte son origine : lue, mesurée ou déduite.
- **Construit** le projet : gabarits, composants partagés, puis chaque page.
- **Compare** le clone au site source, page par page, à 1440, 1024, 768 et 375 px.
- **Corrige** les écarts, les plus visibles d'abord, puis rend un rapport.
- **Mode mise à jour** : vous modifiez `palette.md` ou `design.md`, et le code suit.

Chaque étape a une porte de contrôle. On ne passe pas à la suivante tant qu'elle n'est pas franchie. La dernière exige `tsc`, `vitest`, `build` et la vérification de synchro au vert.

## Pour qui

Développeurs front, agences et freelances qui partent d'un site existant pour une maquette, une refonte ou une base de développement.

## Exemple vérifié

`exemples/stellar/` contient les fichiers de référence et le rapport d'un clone du thème Stellar (HTML5 UP, CC BY 3.0). Résultat : 3 pages sur 3, 13 tests, 0 écart fort ou moyen sur 3 pages × 4 largeurs.

## Installation

Depuis la racine du dépôt `skills` :

```bash
./install.sh cloneme
```

Voir le [README du dépôt](../../README.md) pour l'installation complète.

CloneMe s'appuie sur UI Stealer et Animation Stealer, rangées à côté dans `frontend/`. Pour les avoir toutes les trois :

```bash
./install.sh cloneme ui-stealer animation-stealer
```

Sans les deux partenaires, CloneMe le signale et continue avec des règles minimales.

## Utilisation

Dans Claude Code :

- « CloneMe https://exemple.com »
- « clone ce site », « reproduis https://… à l'identique »
- « j'ai modifié palette.md, applique au code »

## Prérequis

- Claude Code avec un navigateur piloté (pour lire et mesurer le site).
- Node.js (scripts `scripts/*.mjs`, sans dépendance externe).

## Limites connues

- Frontend seulement : aucun backend n'est reproduit. Les appels d'API deviennent des données de démo marquées ou des états vides.
- Pages derrière une connexion, un CAPTCHA ou un paywall : non clonées, par principe.
- Publier un clone avec les textes, logos et images d'origine demande les droits du site source. Le rapport le rappelle.
- Une animation ne se valide pas à l'œil dans le navigateur intégré : la validation passe par le DOM, les styles calculés et les tests.

## Contenu

| Chemin | Rôle |
|---|---|
| `SKILL.md` | instructions et règles d'exécution |
| `references/` | méthode détaillée : analyse, fichiers de référence, architecture, validation, mise à jour |
| `scripts/` | relais local, mesure, comparaison d'empreintes, vérification de synchro |
| `exemples/stellar/` | cas complet validé |

## Mise à jour

`git pull` à la racine du dépôt. Les liens installés suivent automatiquement. Les changements sont dans `CHANGELOG.md`.

## Licence

Propriétaire, tous droits réservés. Voir le [LICENSE](../../LICENSE) du dépôt.

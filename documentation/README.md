# Docs Premium

> Suite de Skills StackLLM · v0.1.0 · usage interne, pas encore commercialisée

**Des livrables de documentation au rendu « cabinet conseil », produits à partir du vrai projet.**

Quatre Skills qui partagent la même charte (charte Forêt : vert sapin, papier crème, Inter et JetBrains Mono) et se citent entre elles. Elles sont rangées ensemble pour cette raison.

| Skill | Livrable |
|---|---|
| `pdf-premium` | PDF A4 : rapport, dossier, note, livrable client. Couverture, sommaire, sections, page de fin. C'est la base de la charte. |
| `fiche-technique` | Fiche technique de référence d'une application : Markdown dans le dépôt, schéma draw.io, PDF. 18 parties, fonction par fonction, avec fichiers et raisons des choix. |
| `guide-utilisateur` | Guide d'utilisation PDF avec captures annotées : référence rapide, démarrage en 5 minutes, fonctions écran par écran, dépannage, FAQ, glossaire. |
| `diagram-premium` | Diagramme `.drawio` prêt à ouvrir : parcours, navigation, cycle de vie, architecture. |

## Le problème

La documentation est souvent écrite à la fin, de mémoire, avec une mise en page refaite à chaque fois. Elle vieillit vite et inspire peu confiance.

## Ce que fait la suite

- Part du code et de l'application réels. Règle commune : aucun fait, chiffre ou écran inventé.
- Applique une structure et un style constants d'un livrable à l'autre.
- Contient tout ce qu'il faut pour produire le rendu : CSS complet, blocs HTML, commandes de rendu. Utilisable par d'autres modèles que Claude.

## Pour qui

Freelances, agences et équipes produit qui livrent de la documentation à des clients ou à une direction.

## Installation

Depuis la racine du dépôt `skills` :

```bash
./install.sh pdf-premium fiche-technique guide-utilisateur diagram-premium
```

## Utilisation

Dans Claude Code : « fais-moi un PDF premium », « fiche technique de ce projet », « guide d'utilisation avec captures », « diagramme du parcours utilisateur ».

Avant le rendu, remplir la marque (`<Votre marque>`, ou `MARQUE` dans le script de la fiche technique) et déposer `logo.jpg` à côté du HTML.

## Prérequis

- WeasyPrint (`pip install weasyprint`) pour les PDF. Sous Windows : runtime GTK3.
- draw.io / diagrams.net pour ouvrir les diagrammes.
- Polices Inter et JetBrains Mono conseillées. Sans elles, les polices système prennent le relais.

## Limites connues

- Pas de script séparé : le code de rendu est dans chaque `SKILL.md`, à copier.
- Le guide utilisateur exige de vraies captures de l'application.
- La charte Forêt est intégrée. Pour une autre charte, remplacer les jetons de couleur.

## Mise à jour

`git pull` à la racine du dépôt. Les liens installés suivent automatiquement.

## Licence

Propriétaire, tous droits réservés. Voir le [LICENSE](../LICENSE) du dépôt.

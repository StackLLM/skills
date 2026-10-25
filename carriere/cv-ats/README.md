# cv-ats

> Skill StackLLM · v0.1.0 · usage interne, pas encore commercialisée

**Un ancien CV en entrée. Trois CV d'une page, lisibles par les logiciels de recrutement, en sortie.**

cv-ats reconstruit un CV à partir d'un Markdown ou d'un ancien CV (PDF, texte, image). Il livre 3 PDF A4 au même contenu, en trois couleurs (bleu, émeraude, bordeaux), contrôlés automatiquement.

## Le problème

Beaucoup de CV sont mal lus par les ATS (logiciels de tri des candidatures) : colonnes mélangées, texte en image, sections non reconnues. Les refaire proprement prend du temps, et la mise en page casse à chaque modification.

## Ce que fait cv-ats

- Lit la source, y compris un ancien PDF tel qu'un ATS le lit.
- Détecte le domaine et le niveau du candidat, et adapte la structure.
- **N'invente rien** : une information manquante va dans une liste « à confirmer ».
- Ajuste le contenu à la page, recadre la photo, génère les 3 PDF.
- Contrôle chaque PDF : lecture ATS, mise en page, cohérence. Produit un rapport et des aperçus.

Le travail est partagé : le modèle comprend et rédige, les scripts mettent en page et contrôlent.

## Pour qui

Candidats, recruteurs, cabinets et coachs carrière. Fonctionne aussi en anglais.

## Installation

Depuis la racine du dépôt `skills` :

```bash
./install.sh cv-ats
```

Voir le [README du dépôt](../../README.md) pour l'installation complète.

## Utilisation

Dans Claude Code : « refais mon CV », « reconstruis ce CV pour les ATS », en joignant la source.

Scripts utilisables seuls :

```bash
python3 scripts/cv.py --help        # construire, detecter, photo
```

## Prérequis

- **macOS** avec `python3` et `swiftc` (Xcode Command Line Tools).
- Rien d'autre : l'outil natif `scripts/cvtool.swift` se compile au premier lancement.

## Validation

```bash
python3 tests/lancer_tests.py
```

6 profils de test fictifs (développeur, ingénieur maintenance, finance senior, marketing UK, junior data, senior au parcours long). Les 6 passent sur la version 0.1.0. Les résultats sont dans `tests/resultats/`.

Après un lancement, les rapports `tests/resultats/*/_controle/rapport.json` contiennent des chemins absolus de votre poste. Les nettoyer avant de les partager.

## Limites connues

- macOS uniquement (rendu PDF via WebKit, recadrage photo via Vision).
- Un CV de parcours très long peut passer sur 2 pages (cas de test 6).

## Contenu

| Chemin | Rôle |
|---|---|
| `SKILL.md` | déroulé et règle absolue |
| `references/` | schéma des données, domaines, design, contrôle qualité |
| `scripts/` | construction, détection, rendu, vérifications, outil natif Swift |
| `assets/` | CSS, ajustement, police Geist (OFL), profil modèle |
| `tests/` | profils et résultats de référence |

## Mise à jour

`git pull` à la racine du dépôt. Les liens installés suivent automatiquement. Les changements sont dans `CHANGELOG.md`.

## Licence

Propriétaire, tous droits réservés. La police Geist reste sous SIL Open Font License. Voir le [LICENSE](../../LICENSE) du dépôt.

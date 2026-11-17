# Libellé de commit

> Skill StackLLM · v0.1.1 · usage interne, pas encore commercialisée

**Chaque changement de code se termine par un libellé de commit qui dit ce qui a été livré, et de quel type.**

```text
feat: fonctionnalité — ajoute l'export des factures en PDF
```

## Ce que fait la skill

- S'applique seule, à la fin de chaque réponse qui a modifié, créé ou supprimé un fichier.
- Forme fixe : préfixe technique, l'un des douze types de livraison (de `création d'application` à `sans valeur`), puis l'objectif en français.
- Donne une seule commande prête à coller : `git add -A; git commit -m "…"`. Le point-virgule passe aussi sous PowerShell 5.1.
- Découpe deux intentions sans rapport dans une seule commande, sans perdre de fichier.
- Ne lance jamais `git add`, `git commit` ni `git push` : le commit reste le geste du dev.

## Installation

```bash
./install.sh libelle-de-commit
```

Ou comme plugin Claude Code (voir le README racine) :

```bash
/plugin install libelle-de-commit --marketplace StackLLM/skills
```

## Limites connues

- Les types de livraison sont en français. Une équipe qui écrit ses commits en anglais doit adapter la table.

## Licence

Propriétaire, tous droits réservés. Voir le [LICENSE](../../LICENSE) du dépôt.

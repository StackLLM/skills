# Changelog

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) · versions : [SemVer](https://semver.org/lang/fr/).

## [0.2.0] — 2026-11-14

### Ajouté
- Fusion avec la skill `security-audit` de Cloudflare (licence MIT) : voir `ORIGINES.md`.
- Deux modes : conseil (une question, une revue ciblée) et audit complet.
- `references/classes-attaque.md`, `references/couverture.md`, `references/execution-sure.md`.
- Registre de couverture : ce qui a été regardé et ce qui ne l'a pas été. Relecture indépendante de chaque constat.

### Modifié
- Un constat n'existe que s'il franchit une frontière de confiance et produit un résultat concret.
- Méthode d'attaque, format du rapport et scripts mis à jour.

## [0.1.0] — 2026-10-25

### Ajouté
- Première version versionnée, issue de la version utilisée en interne.
- `README.md` et `CHANGELOG.md`.

### Modifié
- Cache Python (`__pycache__`) retiré.

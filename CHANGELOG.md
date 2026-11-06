# Changelog de la gamme

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) · versions : [SemVer](https://semver.org/lang/fr/). Le détail de chaque Skill est dans son propre `CHANGELOG.md`.

## [0.3.0] — 2026-11-06

### Ajouté
- Skill **Technical Mentor** (catégorie `carriere/`) : une notion technique mal maîtrisée devient une fiche HTML pour la comprendre, la mettre en œuvre et la défendre en entretien.
- Skill **Map projet** (catégorie `gestion-projet/`) : deux maps visuelles d'un projet ou d'une organisation, avec scripts de collecte et de rendu et 36 tests.

### Retiré
- Skill **Roadmap projets**, remplacée par Map projet.

## [0.2.0] — 2026-11-05

### Ajouté
- Skill **Roadmap projets** (catégorie `gestion-projet/`) : roadmap visuel d'une organisation ou d'un projet, volet par volet, avec ce qui avance, les actions attendues et les décalages.
- Marketplace de plugins Claude Code : les 12 Skills s'installent comme plugins (`/plugin install <nom> --marketplace StackLLM/skills`). Voir le README.

## [0.1.0] — 2026-10-25

### Ajouté
- Dépôt unique `skills`, rangé en 5 catégories : frontend, qualité et production, documentation, carrière, commun.
- 11 Skills en version 0.1.0 : CloneMe, UI Stealer, Animation Stealer, Security Auditor, Deployment Advisor, PDF premium, Fiche technique, Guide utilisateur, Diagramme premium, cv-ats, Explainer.
- Catalogue (`README.md`), positionnement, conventions, licence propriétaire provisoire.
- `install.sh` : installation par liens symboliques dans `~/.claude/skills`.

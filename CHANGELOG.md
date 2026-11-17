# Changelog de la gamme

Format : [Keep a Changelog](https://keepachangelog.com/fr/1.1.0/) · versions : [SemVer](https://semver.org/lang/fr/). Le détail de chaque Skill est dans son propre `CHANGELOG.md`.

## [0.8.0] — 2026-11-17

### Modifié
- **Un plugin par volet**, au nom du dossier : `maniere-de-travailler`, `apprendre-et-evoluer`, `piloter-les-projets`, `construire-l-interface`, `securiser-et-deployer`, `documentation`. Ils remplacent les 18 plugins d'une skill chacun. Une skill s'appelle `<volet>:<skill>`.
- CloneMe trouve UI Stealer et Animation Stealer dans le même plugin.
- Conventions, README et carte mis à jour.

## [0.7.0] — 2026-11-17

### Ajouté
- Skill **Plan par lots** 0.1.0 (volet `piloter-les-projets/`) : plan de travail en phases et en lots, fichier Markdown à structure fixe, mis à jour à la fin de chaque lot.
- `CARTE-DES-SKILLS.html` et `outils/` : la carte du dépôt, générée depuis `outils/skills.json` au rendu de map-projet.

### Modifié
- Le dépôt est rangé par **volets**, comme le dossier de travail : `maniere-de-travailler/` (ex `commun/`), `apprendre-et-evoluer/` (ex `carriere/`), `construire-l-interface/` (ex `frontend/`), `securiser-et-deployer/` (ex `qualite-production/`). `deploy-advisor/` devient `deployment-devops-advisor/`, du nom de sa skill.
- README réécrit : comment lire le dépôt, les 6 volets avec la maturité de chaque skill, les trois endroits, installation, publication.

## [0.6.0] — 2026-11-15

### Ajouté
- Skill **Guide d'exploitation** 0.1.0 (catégorie `documentation/`) : guide PDF de déploiement, d'hébergement et de maintenance, adapté au type de projet, prix datés et sourcés, charte « nacre et bronze » sans logo.

## [0.5.0] — 2026-11-14

### Ajouté
- Skill **Libellé de commit** (catégorie `commun/`) : libellé « préfixe: type de livraison — objectif » proposé après chaque changement, avec la commande prête à coller.

## [0.4.1] — 2026-11-14

### Corrigé
- Suite **Piloter les projets** : commandes en `python3`, plus aucune mention d'un employeur.

## [0.4.0] — 2026-11-14

### Ajouté
- Catégorie **Piloter les projets** (`piloter-les-projets/`), qui remplace `gestion-projet/` : `map-projet-reponse` 0.1.0, `map-projet` 0.5.0, `adviser-dev` 0.1.0.

### Modifié
- **Security Auditor** 0.2.0 : fusion avec la skill `security-audit` de Cloudflare (MIT), deux modes, registre de couverture, relecture indépendante.
- **Map projet** 0.5.0 : retour à la version de l'auteur, en fichiers. L'affichage dans la conversation passe à Map projet dans la réponse.

## [0.3.3] — 2026-11-06

### Corrigé
- **Map projet** 0.4.1 : commandes en `python3`, rendu sans débordement en 3 colonnes et sur téléphone.

## [0.3.2] — 2026-11-06

### Modifié
- **Map projet** 0.4.0 : choix de 1, 2 ou 3 colonnes de cartes.

## [0.3.1] — 2026-11-06

### Modifié
- **Map projet** 0.3.0 : les maps sont dessinées directement dans la conversation, sans Chrome ni Edge.

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

# StackLLM Skills

> Dépôt privé · v0.1.0 · aucune Skill n'est encore commercialisée

Les Skills StackLLM sont des **outils d'automatisation spécialisés pour Claude Code**. Chacune prend en charge un travail complet, de l'analyse jusqu'au livrable vérifié. Elle suit une méthode fixe et passe des contrôles avant de livrer.

Ce ne sont pas de simples prompts. Une Skill embarque des instructions d'exécution, des références détaillées et, quand c'est utile, des scripts et des tests.

## La gamme

11 Skills en 5 catégories.

### Frontend — reproduire une interface ou une interaction

| Skill | Entrée → sortie | Maturité |
|---|---|---|
| [**CloneMe**](frontend/cloneme/) | URL → projet frontend complet, piloté par 3 fichiers de référence | A |
| [**UI Stealer**](frontend/ui-stealer/) | image de maquette → interface React | B |
| [**Animation Stealer**](frontend/animation-stealer/) | section animée d'un site → même comportement dans votre projet | B |

CloneMe orchestre les deux autres.

### Qualité et production — sécuriser et déployer

| Skill | Entrée → sortie | Maturité |
|---|---|---|
| [**Security Auditor**](qualite-production/security-auditor/) | projet ou dépôts → rapport d'audit de sécurité HTML | B+ |
| [**Deployment Advisor**](qualite-production/deploy-advisor/) | projet ou dépôts → rapport de déploiement HTML + checklists | B+ |

### Documentation — livrables au rendu « cabinet conseil »

Quatre Skills qui partagent la charte Forêt. Présentation commune : [documentation/](documentation/).

| Skill | Entrée → sortie | Maturité |
|---|---|---|
| [**PDF premium**](documentation/pdf-premium/) | contenu → rapport, dossier ou note en PDF | B |
| [**Fiche technique**](documentation/fiche-technique/) | projet → fiche technique de référence (Markdown, draw.io, PDF) | B |
| [**Guide utilisateur**](documentation/guide-utilisateur/) | application + captures → guide d'utilisation PDF | B |
| [**Diagramme premium**](documentation/diagram-premium/) | parcours ou architecture → fichier `.drawio` | B |

### Carrière

| Skill | Entrée → sortie | Maturité |
|---|---|---|
| [**cv-ats**](carriere/cv-ats/) | ancien CV → 3 PDF compatibles ATS, contrôlés | A |

### Commun

| Skill | Rôle |
|---|---|
| [**Explainer**](commun/explainer/) | charte d'écriture partagée : français simple, réponse directe, sections séparées |

**Maturité** : **A** = scripts et cas ou tests validés · **B+** = scripts et exemple · **B** = méthode complète, sans test automatique.

Public, problème résolu, bénéfices et limites de chaque Skill : [POSITIONNEMENT.md](POSITIONNEMENT.md).

## Installation

Claude Code lit les Skills dans `~/.claude/skills/`. Le script crée un lien vers chaque Skill du dépôt :

```bash
git clone https://github.com/StackLLM/skills.git ~/stackllm/skills
cd ~/stackllm/skills
./install.sh                     # toutes les Skills
./install.sh cloneme cv-ats      # seulement celles-ci
```

Les noms à passer sont ceux déclarés dans chaque `SKILL.md` : `cloneme`, `ui-stealer`, `animation-stealer`, `security-auditor`, `deployment-devops-advisor`, `pdf-premium`, `fiche-technique`, `guide-utilisateur`, `diagram-premium`, `cv-ats`, `explainer`.

Le script ne remplace jamais un dossier existant qui n'est pas un lien vers ce dépôt. Autre dossier cible : `CLAUDE_SKILLS_DIR=/chemin ./install.sh`.

## Mise à jour

```bash
cd ~/stackllm/skills && git pull
```

Les liens suivent automatiquement. Les changements de la gamme sont dans [CHANGELOG.md](CHANGELOG.md), ceux de chaque Skill dans son propre `CHANGELOG.md`.

## Organisation du dépôt

```text
skills/
├── README.md            ce catalogue
├── POSITIONNEMENT.md    public, problème, bénéfices, limites
├── CONVENTIONS.md       règles communes à toutes les Skills
├── CHANGELOG.md         versions de la gamme
├── LICENSE              licence propriétaire + composants tiers
├── install.sh           installation dans ~/.claude/skills
├── frontend/            cloneme · ui-stealer · animation-stealer
├── qualite-production/  security-auditor · deploy-advisor
├── documentation/       pdf-premium · fiche-technique · guide-utilisateur · diagram-premium
├── carriere/            cv-ats
└── commun/              explainer
```

Règles de rangement : [CONVENTIONS.md](CONVENTIONS.md).

## Statut

Aucune Skill n'est en vente. Aucun prix n'est fixé. Le dépôt reste privé. La licence définitive et les conditions commerciales restent à établir.

## Licence

Propriétaire, tous droits réservés. Voir [LICENSE](LICENSE).

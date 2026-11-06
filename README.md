# StackLLM Skills

> Dépôt privé · v0.3.3 · aucune Skill n'est encore commercialisée

Les Skills StackLLM sont des **outils d'automatisation spécialisés pour Claude Code**. Chacune prend en charge un travail complet, de l'analyse jusqu'au livrable vérifié. Elle suit une méthode fixe et passe des contrôles avant de livrer.

Ce ne sont pas de simples prompts. Une Skill embarque des instructions d'exécution, des références détaillées et, quand c'est utile, des scripts et des tests.

## La gamme

13 Skills en 6 catégories.

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

### Gestion de projet — savoir où on en est

| Skill | Entrée → sortie | Maturité |
|---|---|---|
| [**Map projet**](gestion-projet/map-projet/) | organisation ou projet → deux maps dessinées dans la conversation (volets, lots, phases) et un verdict | A |

### Carrière

| Skill | Entrée → sortie | Maturité |
|---|---|---|
| [**cv-ats**](carriere/cv-ats/) | ancien CV → 3 PDF compatibles ATS, contrôlés | A |
| [**Technical Mentor**](carriere/technical-mentor/) | notion mal maîtrisée → fiche HTML pour la comprendre, la faire et la défendre en entretien | B+ |

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

Les noms à passer sont ceux déclarés dans chaque `SKILL.md` : `cloneme`, `ui-stealer`, `animation-stealer`, `security-auditor`, `deployment-devops-advisor`, `pdf-premium`, `fiche-technique`, `guide-utilisateur`, `diagram-premium`, `map-projet`, `cv-ats`, `technical-mentor`, `explainer`.

Le script ne remplace jamais un dossier existant qui n'est pas un lien vers ce dépôt. Autre dossier cible : `CLAUDE_SKILLS_DIR=/chemin ./install.sh`.

## Installation comme plugin

Le dépôt est aussi un marketplace de plugins Claude Code (`.claude-plugin/marketplace.json`). Une Skill y devient un plugin en recevant son propre `.claude-plugin/plugin.json` : aucun fichier n'est dupliqué.

```bash
gh auth login && gh auth setup-git      # une fois : le dépôt est privé
/plugin marketplace add StackLLM/skills
/plugin install map-projet --marketplace StackLLM/skills
```

Les 13 Skills sont des plugins, au même nom que leur Skill : `cloneme`, `ui-stealer`, `animation-stealer`, `security-auditor`, `deployment-devops-advisor`, `pdf-premium`, `fiche-technique`, `guide-utilisateur`, `diagram-premium`, `map-projet`, `cv-ats`, `technical-mentor`, `explainer`.

Deux précautions :

- Une Skill ne doit pas être installée à la fois par `install.sh` et comme plugin : elle apparaîtrait en double.
- Chaque plugin est installé dans son propre dossier. CloneMe ne retrouve donc pas UI Stealer et Animation Stealer à côté de lui : il le dit et continue avec des règles minimales. Pour la version complète, installer les trois par `install.sh`.

## Mise à jour

```bash
cd ~/stackllm/skills && git pull
```

Après une modification, une seule commande publie et met à jour les plugins installés :

```bash
./publier.sh "message du commit"
```

Elle valide le marketplace et chaque plugin, committe, pousse sur chaque URL de push d'`origin`, puis met à jour le marketplace `stackllm-skills` et les plugins installés.

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
├── publier.sh           commit, push et mise à jour des plugins
├── frontend/            cloneme · ui-stealer · animation-stealer
├── qualite-production/  security-auditor · deploy-advisor
├── documentation/       pdf-premium · fiche-technique · guide-utilisateur · diagram-premium
├── gestion-projet/      map-projet
├── carriere/            cv-ats · technical-mentor
└── commun/              explainer
```

Règles de rangement : [CONVENTIONS.md](CONVENTIONS.md).

## Statut

Aucune Skill n'est en vente. Aucun prix n'est fixé. Le dépôt reste privé. La licence définitive et les conditions commerciales restent à établir.

## Licence

Propriétaire, tous droits réservés. Voir [LICENSE](LICENSE).

# StackLLM Skills

> Dépôt privé · v0.7.0 · aucune Skill n'est encore commercialisée

Ce dépôt contient **18 skills vivantes** pour Claude Code, rangées en **6 volets**.
Un volet = un besoin. Une skill = un dossier avec un `SKILL.md`.

Une skill n'est pas un simple prompt : elle prend en charge un travail complet,
de l'analyse jusqu'au livrable vérifié, avec ses références et, quand c'est
utile, ses scripts et ses tests.

Pour voir tout le dépôt d'un coup d'œil : **[CARTE-DES-SKILLS.html](CARTE-DES-SKILLS.html)**.
Une carte par volet, et dans chaque carte chaque skill avec ce à quoi elle sert,
son nom de plugin, sa version et sa maturité.

Quand une skill arrive, part ou change de place : modifier sa ligne dans
`outils/skills.json`, puis régénérer.

```bash
python3 outils/carte-des-skills.py
```

Trois colonnes par défaut. En deux, les cartes sont plus larges :

```bash
python3 outils/carte-des-skills.py --colonnes 2
```

> La représentation est celle de la skill `map-projet` : bandeau, frise,
> compteurs, matrice, légende, puis une carte par volet. L'axe des colonnes,
> ici, c'est **la maturité** de chaque skill. Les comptes se calculent depuis
> le fichier, et le script vérifie que chaque dossier existe avec le bon nom :
> la carte ne peut pas contredire le dépôt.

**Maturité** : **A** = scripts et cas ou tests validés · **B+** = scripts et
exemple · **B** = méthode complète, sans test automatique · **—** = charte ou
règle d'écriture, rien à tester.

---

## Comment lire ce dépôt

| Tu cherches | Va dans |
|---|---|
| Comment Claude doit répondre et nommer les commits | `maniere-de-travailler/` |
| Comprendre une notion technique, refaire son CV | `apprendre-et-evoluer/` |
| Savoir où en est un projet, le planifier, le construire proprement | `piloter-les-projets/` |
| Copier un site, une maquette ou une animation | `construire-l-interface/` |
| Vérifier qu'une app est sûre et déployable | `securiser-et-deployer/` |
| Sortir un document à montrer à un client | `documentation/` |

---

## Les 6 volets

### `maniere-de-travailler/` — la grille de toutes les réponses

| Skill | Ce qu'elle fait | Maturité |
|---|---|---|
| `explainer` | La manière d'expliquer de référence : français simple, phrases courtes, réponse directe, sections séparées. | — |
| `libelle-de-commit` | Propose le libellé de commit à la fin de chaque réponse qui a changé du code. Ne commite jamais à ta place. Le commit `livraison` se pose à la fin d'une phase, pour la mettre en production. | — |

### `apprendre-et-evoluer/` — maîtriser pour de vrai

| Skill | Ce qu'elle fait | Maturité |
|---|---|---|
| `technical-mentor` | Transforme une notion technique mal maîtrisée en fiche HTML : problème, mécanisme, mise en œuvre, questions d'entretien. Deux modes : **notion** et **architecture**. | B+ |
| `cv-ats` | Un ancien CV devient 3 PDF d'une page compatibles ATS, contrôlés automatiquement. macOS seulement. | A |

### `piloter-les-projets/` — savoir où on en est, et avancer droit

| Skill | Ce qu'elle fait | Maturité |
|---|---|---|
| `map-projet-reponse` | La map d'avancement d'un projet ou d'une orga GitHub, **affichée dans la réponse**. Réglage 1, 2 ou 3 colonnes. Aucun fichier créé. | A |
| `map-projet` | La même map **en fichiers** : 2 PNG et 2 HTML, à garder, imprimer ou envoyer. Le PNG demande Chrome ou Edge. | A |
| `plan-par-lots` | Le plan de travail en phases et en lots, dans un fichier Markdown à structure fixe : but, décisions, constats, lots, actions à faire soi-même. Mis à jour à la fin de chaque lot. | B |
| `adviser-dev` | Le tech lead : audit du socle d'un projet existant, ou socle front et back depuis le `plan.md`. Tests, CI, Docker, livraison. Sur appel seulement (`/adviser-dev`). | B+ |

### `construire-l-interface/` — le front

| Skill | Ce qu'elle fait | Maturité |
|---|---|---|
| `cloneme` | Reproduit un site entier depuis son URL, dans un projet frontend exécutable, vérifié par des mesures. S'appuie sur les deux suivantes. | A |
| `ui-stealer` | Construit un front React/Vite à partir d'une image de maquette déposée dans `Template/`. | B |
| `animation-stealer` | Reproduit le **comportement** d'une animation au scroll : rythme, déclencheurs, retour arrière. | B |

### `securiser-et-deployer/` — avant la mise en production

| Skill | Ce qu'elle fait | Maturité |
|---|---|---|
| `security-auditor` | Cherche les chemins d'attaque. Un constat n'existe que s'il franchit une frontière de confiance. Deux modes (conseil, audit complet), relecture indépendante, registre de couverture, rapport HTML, secrets masqués. Fusionnée avec la skill de Cloudflare (MIT) — voir son `ORIGINES.md`. | B+ |
| `deployment-devops-advisor` | Cherche les causes du « ça marche chez moi mais pas en prod » et compare les architectures de déploiement avec leur coût. | B+ |

### `documentation/` — ce qu'on montre dehors

| Skill | Ce qu'elle fait | Maturité |
|---|---|---|
| `pdf-premium` | Rapport, dossier ou note en PDF, au rendu « cabinet conseil » (charte Forêt). | B |
| `fiche-technique` | La fiche de référence d'une application : Markdown dans le dépôt, schéma draw.io, PDF. | B |
| `guide-utilisateur` | Le guide d'utilisation en PDF, avec captures annotées. | B |
| `diagram-premium` | Un diagramme `.drawio` prêt à ouvrir : parcours, navigation, cycle de vie, architecture. | B |
| `guide-exploitation` | Le guide PDF de déploiement, d'hébergement et de maintenance, adapté au type de projet (charte « nacre et bronze »). | B |

Public, problème résolu, bénéfices et limites de chaque skill : [POSITIONNEMENT.md](POSITIONNEMENT.md).

---

## Les trois endroits

| Endroit | À quoi il sert | Qui le lit |
|---|---|---|
| `Documents/SKILLS/` | **Le dossier de travail**, rangé comme ce dépôt. On y dépose une nouvelle version, et on y garde les archives (`_archives/`, jamais publié). | Moi |
| `~/stackllm/skills/` | **La source publiée** : le clone de ce dépôt, où l'on modifie avant de publier. | `publier.sh` |
| Plugin `stackllm-skills` | La copie installée, la même sur tous les postes. | Claude Code |

**Les 18 skills sont dans le plugin.** Le dépôt est poussé à deux endroits à
chaque publication : [StackLLM/skills](https://github.com/StackLLM/skills) et
[oussamaalmouallim/skills](https://github.com/oussamaalmouallim/skills) (privé).

---

## Installation

Le dépôt est un marketplace de plugins Claude Code (`.claude-plugin/marketplace.json`).
Chaque skill y est un plugin, au même nom que sa skill.

```bash
gh auth login && gh auth setup-git      # une fois : le dépôt est privé
claude plugin marketplace add StackLLM/skills
claude plugin install map-projet-reponse@stackllm-skills
```

Une commande `install` par skill voulue. Les noms : `explainer`,
`libelle-de-commit`, `technical-mentor`, `cv-ats`, `map-projet-reponse`,
`map-projet`, `plan-par-lots`, `adviser-dev`, `cloneme`, `ui-stealer`,
`animation-stealer`, `security-auditor`, `deployment-devops-advisor`,
`pdf-premium`, `fiche-technique`, `guide-utilisateur`, `diagram-premium`,
`guide-exploitation`.

Sans plugin, `install.sh` crée un lien par skill dans `~/.claude/skills/` :

```bash
git clone https://github.com/StackLLM/skills.git ~/stackllm/skills
cd ~/stackllm/skills && ./install.sh cloneme cv-ats
```

Ne jamais installer une même skill par les deux moyens : elle apparaîtrait en
double. Installée comme plugin, CloneMe ne retrouve pas UI Stealer et Animation
Stealer à côté d'elle : pour sa version complète, installer les trois par
`install.sh`.

---

## Publier une skill

```bash
cd ~/stackllm/skills && ./publier.sh "message du commit"
```

Le script valide le marketplace et chaque plugin, committe, pousse sur les deux
dépôts, puis met à jour le marketplace et les plugins installés. Redémarrer
Claude Code pour charger les nouvelles versions. Les changements de la gamme
sont dans [CHANGELOG.md](CHANGELOG.md), ceux de chaque skill dans son propre
`CHANGELOG.md`. Règles de rangement : [CONVENTIONS.md](CONVENTIONS.md).

---

## Organisation du dépôt

```text
skills/
├── README.md                ce catalogue
├── CARTE-DES-SKILLS.html    la carte du dépôt (générée)
├── outils/                  skills.json et carte-des-skills.py
├── POSITIONNEMENT.md        public, problème, bénéfices, limites
├── CONVENTIONS.md           règles communes à toutes les skills
├── CHANGELOG.md             versions de la gamme
├── LICENSE                  licence propriétaire + composants tiers
├── install.sh               installation par liens dans ~/.claude/skills
├── publier.sh               commit, push et mise à jour des plugins
├── maniere-de-travailler/   explainer · libelle-de-commit
├── apprendre-et-evoluer/    technical-mentor · cv-ats
├── piloter-les-projets/     map-projet-reponse · map-projet · plan-par-lots · adviser-dev
├── construire-l-interface/  cloneme · ui-stealer · animation-stealer
├── securiser-et-deployer/   security-auditor · deployment-devops-advisor
└── documentation/           pdf-premium · fiche-technique · guide-utilisateur · diagram-premium · guide-exploitation
```

## Statut

Aucune skill n'est en vente. Aucun prix n'est fixé. Le dépôt reste privé. La
licence définitive et les conditions commerciales restent à établir.

## Licence

Propriétaire, tous droits réservés. Voir [LICENSE](LICENSE).

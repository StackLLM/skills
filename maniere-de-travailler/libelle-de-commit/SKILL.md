---
name: libelle-de-commit
description: "Propose un libellé de commit à la fin de chaque réponse qui a changé du code, dans n'importe quel projet. Le libellé porte un préfixe technique, le type de livraison (création d'application, fonctionnalité, amélioration métier, amélioration, interface, parcours, intégration, déploiement, correction technique, documentation, norme du métier, sans valeur) puis l'objectif, en français. Il dit, sans lire le code, ce qui a été livré et pourquoi. S'applique à chaque changement, sans qu'on le demande ; ne commite jamais à la place du dev."
---

# Libellé de commit — dire ce qu'on a livré, et de quel type

> **Toujours appliquer.** Chaque réponse qui a modifié, créé ou supprimé un fichier se termine par une section `## Libellé de commit`. Pas de changement : pas de section.

Le commit est la trace que l'équipe laisse de son travail. Ceux qui relisent
l'historique — un responsable, un client, le dev lui-même six mois plus tard —
doivent comprendre, sans lire le code, **ce qui a été fait et pourquoi**. Un
libellé flou — `update`, `wip`, `fix stuff` — est du travail que personne ne
pourra relire.

## 1. La forme

```text
<préfixe>: <type de livraison> — <objectif, en français>
```

Trois morceaux, toujours dans cet ordre :

| Morceau | Ce que c'est | Exemple |
|---|---|---|
| le préfixe | le type technique, en anglais | `feat`, `fix`, `refactor`, `perf`, `docs`, `test`, `chore`, `style`, `ci`, `build` |
| le type de livraison | **l'un des douze types** de la section 2, en français, mot pour mot | `fonctionnalité`, `amélioration métier`, `correction technique` |
| l'objectif | ce qui change pour l'utilisateur ou pour l'équipe, pas le chemin technique | `ajoute l'export des factures en PDF` |

```text
feat: fonctionnalité — ajoute l'export des factures en PDF
fix: correction technique — corrige le calcul de TVA sur les avoirs
fix: norme du métier — ferme le port de la base au réseau local
```

Le préfixe peut porter une portée entre parenthèses : `feat(portail): interface — …`.

Règles :

- **Une ligne, 90 caractères au plus.** Un corps de message seulement si le
  pourquoi ne tient pas dans la ligne.
- **L'objectif dit le résultat, pas le chemin.** « ajoute le filtre par
  client », pas « modifie Filtres.tsx et api.ts ».
- **Pas de mot creux** : `update`, `changes`, `misc`, `wip`, `stuff`, « divers
  ajustements ». Si on ne sait pas quoi écrire, c'est qu'il faut découper.
- **Un commit = une intention = un type.** Un commit qui mélange interface et
  fonctionnalité se lit comme l'un des deux, jamais les deux. Le découper est
  possible — voir « Plusieurs intentions dans la même réponse » — mais jamais
  en donnant deux commandes au dev.
- **Pas de secret, pas de ticket seul** : `fix: #142` ne dit rien.

## 2. Les douze types de livraison

Le mot du milieu est **l'un d'eux, écrit tel quel**. Ils vont du plus gros au
plus petit apport.

| Type à écrire | Ce que c'est | Préfixe qui va avec |
|---|---|---|
| `création d'application` | une application qui n'existait pas — seulement le premier commit du dépôt | `feat` |
| `fonctionnalité` | une capacité nouvelle dans une application qui existe : page, module, export, rapport, connecteur | `feat` |
| `amélioration métier` | le cœur du métier renforcé : un moteur, un algorithme, une extraction, une règle métier, un calcul automatique | `feat`, `refactor` |
| `amélioration` | ce qui existait marche mieux : plus fiable, plus simple, plus rapide, unifié | `refactor`, `perf`, `feat` |
| `interface` | ce que l'écran montre : écran, bouton, menu, carte, mise en page, thème | `feat`, `style` |
| `parcours` | ce que l'écran fait faire : navigation, formulaire, filtre, recherche, étapes | `feat` |
| `intégration` | un service ou un outil externe branché à l'application | `feat` |
| `déploiement` | mise en production et outillage : docker, sauvegarde, migration de base | `chore`, `ci`, `build` |
| `correction technique` | un défaut corrigé : erreur, chemin, encodage, date, cas vide | `fix` |
| `documentation` | un guide, une fiche, un README qui explique | `docs` |
| `norme du métier` | ce qu'un dev doit faire de toute façon : fermer un port, sécuriser un accès, régler une marge, tenir le cahier des charges | `fix`, `chore` |
| `sans valeur` | du rangement : faute de frappe, lint, dépendances, nettoyage | `chore`, `style`, `test` |

Deux conséquences :

- Un commit qui **est** la norme ou du rangement se dit tel quel :
  `fix: norme du métier — ferme le port de la base au réseau local`,
  `chore: sans valeur — met à jour les dépendances`. Le déguiser en
  fonctionnalité gonfle l'historique et trompe celui qui le relit.
- Un commit qui **livre** quelque chose le dit avec son type et ses mots :
  `feat: fonctionnalité — ajoute l'export des factures`, pas `fix: export`.

**En cas de doute entre deux types, prendre le plus petit.** `amélioration
métier` se réserve au cœur du métier, pas à une amélioration ordinaire.

## 3. Le geste, à la fin de la réponse

Après tout le reste, une section avec la commande prête, puis **une ligne qui
dit le type et l'objectif** en clair, pour qui ne lit pas les commits :

```text
## Libellé de commit

```bash
git add -A; git commit -m "feat: fonctionnalité — ajoute l'export des factures en PDF"
```

Type : fonctionnalité. Objectif : le comptable récupère ses factures sans les recopier.
```

**La commande commence toujours par `git add -A;`**, dans le même bloc et sur
la même ligne. Un commit qui oublie un fichier neuf livre une moitié de
travail. Le dev n'a qu'un bouton à presser, et rien à compléter à la main.

Le séparateur est un **point-virgule**, jamais `&&`. PowerShell 5.1, sous
Windows, refuse `&&` : « Le jeton « && » n'est pas un séparateur d'instruction
valide. » Le point-virgule passe dans PowerShell comme dans bash.

Une seule commande par bloc. Le libellé **est proposé, jamais exécuté** : le
dev commite lui-même, quand il veut. Ne jamais lancer `git add`, `git commit`
ni `git push` sans qu'on le demande explicitement.

### Plusieurs intentions dans la même réponse

**Ne jamais donner deux blocs `git add -A; git commit`.** Collés à la suite,
ils ne font pas deux commits : le premier `git add -A` prend tout le travail,
le premier commit l'emporte sous son libellé, et le second échoue faute de
quoi que ce soit à valider. Le dev se retrouve avec **un commit au mauvais
type**.

Quand les intentions sont réelles, elles se découpent **dans une seule
commande**, en ne validant que les fichiers de chacune :

```bash
git add -A -- <les fichiers de la première>; git commit -m "<libellé 1>"; git add -A; git commit -m "<libellé 2>"
```

`git add -A -- <chemins>` ne prend que ces chemins, suppressions comprises. Le
dernier `git add -A`, sans chemin, ramasse tout le reste : rien ne peut être
oublié.

Trois conditions, sinon **un seul libellé** :

- les intentions touchent des **fichiers différents** — un fichier modifié par
  les deux ne se coupe pas en deux commits ;
- elles sont **vraiment sans rapport** — une suppression faite en passant
  appartient à la livraison, elle ne mérite pas son propre commit ;
- il y en a **deux, pas cinq**. Au-delà, c'est la réponse qu'il fallait
  découper, pas le commit.

Quand on retombe sur un seul libellé, il porte le type de **ce qui a le plus de
valeur** dans la livraison, et l'objectif peut nommer le reste.

## 4. Le commit « livraison » : la fin d'une phase

Le commit vide `livraison` se pose **quand une phase est finie** : il la fait
passer en version de production (branche `dev` → `main`). Ce n'est pas un
commit de fin de lot, ni de fin de réponse.

C'est **la décision du dev**. Ne jamais le proposer de soi-même sous un
libellé. Seulement si le dev dit que la phase est finie, lui rappeler les
commandes, sur la branche de recette :

```bash
git switch dev; git pull; git commit --allow-empty -m "livraison"; git push
```

Puis, CI verte, le script de livraison du projet (`livrer`) pousse vers `main`.

## 5. Exemples

| Situation | Libellé |
|---|---|
| Première version d'une app | `feat: création d'application — nouvelle application de réservation, prototype des trois écrans` |
| Page nouvelle dans une app existante | `feat: fonctionnalité — ajoute la page des statistiques par client` |
| Un moteur, un calcul, une règle du métier | `feat: amélioration métier — le moteur détecte les factures en double` |
| Le calcul existant marche mieux | `feat: amélioration — le budget du projet se partage au prorata` |
| Un bouton, une carte, une couleur | `feat: interface — ajoute le bouton de déconnexion au menu du compte` |
| Un formulaire plus court | `feat: parcours — l'inscription tient en deux étapes` |
| Un service externe branché | `feat: intégration — envoi des mails par un service externe` |
| Passage en production | `chore: déploiement — mise en production docker de l'API` |
| Le calcul de TVA était faux | `fix: correction technique — corrige le calcul de TVA qui bloquait la facturation des avoirs` |
| Un guide, une fiche technique | `docs: documentation — guide d'installation du poste de dev` |
| Port fermé, marge du hero | `fix: norme du métier — ferme le port de la base au réseau local` |
| Lint, dépendances | `chore: sans valeur — met à jour les dépendances` |

## 6. Ce qu'on ne fait pas

| À ne pas faire | Pourquoi |
|---|---|
| `git commit` ou `git push` de soi-même | le commit est le geste du dev, pas de l'IA |
| Un `git commit` sans `git add -A;` devant | un fichier neuf reste hors du commit |
| `&&` pour enchaîner les deux | PowerShell 5.1 le refuse ; le point-virgule passe partout |
| Un libellé sans le type de livraison | on ne sait plus ce que le commit apporte |
| Un type qui n'est pas dans la table | le libellé ne se range plus avec les autres |
| Un libellé en anglais entier | le français après le préfixe, pour qui relit sans lire le code |
| `fonctionnalité` pour une marge ou un port | c'est la norme, pas une livraison |
| `amélioration métier` pour une amélioration ordinaire | le réserver au cœur du métier |
| Un seul commit pour deux types | il se lit comme l'un des deux, jamais les deux |
| **Deux blocs `git add -A; git commit` à la suite** | le premier prend tout : un commit, au mauvais type, et le second échoue |
| Les mots « sans valeur » ou « norme du métier » dans un libellé qui livre | ils font passer une livraison pour du rangement |
| Oublier la section après un changement | la trace se perd, le dev tape `update` |
| Proposer `livraison` sous un libellé ordinaire | il met une phase en production : c'est la décision du dev, à la fin d'une phase |

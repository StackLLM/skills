---
name: roadmap-projets
description: Montre où en sont les projets avec un roadmap visuel affiché directement dans la conversation, suivi de trois sections — ce qui avance, ce qui attend une action de l'utilisateur, les décalages à corriger. Deux modes. Mode organisation : tous les projets d'une organisation GitHub (StackLLM ou une autre) ou d'un dossier de projets, placés sur les phases Cadrage → Construction → Pré-production → Bêta → Lancement, avec une carte par projet. Mode projet : un seul projet, découpé volet par volet (IA, front, backend, base de données, infra, sécurité…), chaque carte de volet montrant ses lots ou ses étapes sur une timeline d'avancement. Se fonde sur les plans, contextes, roadmaps, suivis de lots, README et l'historique Git ; n'invente rien. Se déclenche sur « on est où dans nos projets », « où on en est », « roadmap de l'orga », « fais-moi le point sur X », « je suis perdu dans ce projet », « état d'avancement », « montre-moi le roadmap ».
---

# Roadmap projets — voir où on en est, d'un coup d'œil

L'utilisateur se perd entre ses projets, ou dans un projet. Il veut **une image
qui dit où on en est**, puis **trois listes courtes** : ce qui avance, ce qu'il
doit faire lui-même, ce qui ne colle pas.

Le rendu est toujours le même. Seul le contenu s'adapte : à l'organisation, ou
au projet.

---

## 1. Les règles qui priment

### 1. Lire avant de placer

Aucun projet, volet ou lot n'est placé avant d'avoir lu ce qui le décrit. La
méthode de travail de l'utilisateur laisse **toujours** une trace écrite :
un plan, un contexte, un suivi de lots, une roadmap. On la trouve d'abord
(`references/collecte.md`), puis on regarde le code et l'historique Git pour
confirmer.

### 2. Ne rien inventer, ne rien oublier

- Chaque statut vient d'une source : un document, un commit, un fichier.
- Un document dit « fait » mais le code dit autre chose : c'est un **décalage**,
  pas un choix à trancher en silence.
- Pas de source : le dire (« pas de plan trouvé, état déduit du code »).
- **Tous** les projets de l'organisation apparaissent, même vides, archivés ou
  sans dépôt. **Tous** les volets du projet apparaissent, même à peine commencés.
- Un pourcentage n'est jamais inventé. Une barre de progression se calcule :
  lots terminés ÷ lots prévus, étapes faites ÷ étapes prévues ; sans lots,
  phases terminées ÷ 5. Le texte sous la barre dit ce qu'elle compte.

### 3. Distinguer livré et validé

« Livré, à valider » n'est pas « terminé ». C'est souvent ce qui attend
l'utilisateur. Le roadmap le montre avec son propre état.

### 4. Dater

Un état vaut à une date. Citer la date du document (« au 18 octobre ») ou du
dernier commit. Un document vieux de plus de deux semaines alors que le dépôt a
bougé depuis : le signaler.

### 5. Ne rien modifier

La Skill lit et montre. Corriger un décalage se fait **après**, et seulement si
l'utilisateur le demande.

---

## 2. Choisir le mode

| Demande | Mode | Périmètre |
|---|---|---|
| « on est où dans nos projets », « roadmap de l'orga », un nom d'organisation | **Organisation** | tous les dépôts de l'organisation GitHub (StackLLM par défaut), plus les projets annoncés sans dépôt |
| « je suis perdu dans X », « fais le point sur ce projet », dans le dossier d'un projet | **Projet** | un seul projet : son plan, son code, son historique |
| Ambigu | demander en une ligne : « l'organisation entière ou le projet X ? » | — |

Dans le dossier d'un projet sans autre précision : mode projet.

---

## 3. Déroulé

1. **Collecter** — `references/collecte.md` : où chercher, quelles commandes,
   comment lire un suivi de lots.
2. **Classer**
   - Organisation : chaque projet reçoit une phase par colonne (§ 4).
   - Projet : découper en volets, chaque volet en lots ou étapes (§ 5).
3. **Repérer les décalages** — `references/collecte.md` § 4.
4. **Afficher le roadmap** dans la conversation (§ 6) avec le gabarit :
   `references/gabarit-orga.html` ou `references/gabarit-projet.html`.
5. **Écrire la réponse** autour, dans l'ordre exact du § 7.

---

## 4. Mode organisation — les phases

Cinq colonnes, toujours les mêmes :

| Phase | Le projet est là quand… |
|---|---|
| **Cadrage** | plan, étude, maquette ou prototype sans backend |
| **Construction** | les fonctions se codent, lot par lot |
| **Pré-production** | les fonctions sont là ; on prépare l'hébergement, la sécurité, les sauvegardes, la licence |
| **Bêta** | des utilisateurs réels, sur invitation |
| **Lancement** | ouvert au public ou en vente |

Pour un produit qui ne se déploie pas (une gamme de Skills, une bibliothèque),
on garde les colonnes et on adapte le texte de la cellule (« licence, prix »).

Chaque cellule d'une ligne est : **terminée**, **en cours** (une seule par
ligne) ou **à venir**. Son texte est court et réel : « lots 0–32 », « P3 sur
P9 », « études ».

Sous la frise : **une carte par projet** — deux phrases sur l'état, une barre de
progression, « Manque : » ou « Ensuite : », et l'action humaine s'il y en a une.

---

## 5. Mode projet — les volets

### Trouver les volets

Un volet est un **pôle technique ou métier** du projet : IA, Front, Backend,
Base de données, Infra et déploiement, Sécurité, Contenu, Données, Tests,
Documentation…

- Si le plan est déjà rangé par volets : reprendre ses volets et ses mots.
- Si le plan est rangé par lots ou phases : rattacher chaque lot au volet qu'il
  touche le plus. Un lot vraiment transversal va dans un volet **Transverse**.
- Ne créer **aucun volet vide**. Un projet de refonte d'interface peut n'avoir
  qu'un volet, Front, dont les lots sont les pages ou les étapes.

### Dans chaque carte de volet

1. Nom du volet, icône, badge d'état (terminé, en cours, à valider, bloqué,
   à venir).
2. Barre de progression et compte (« 4 / 7 lots »).
3. **La timeline d'avancement** : la liste des lots ou étapes, de haut en bas,
   chacun avec son point d'état. Le lot en cours est marqué « vous êtes ici ».
   Plus de 6 lots terminés à la suite : les regrouper en une ligne
   (« Lots 0 à 12 · terminés »).
4. « Ensuite : » — le prochain lot, ou ce qui bloque.

Au-dessus des cartes : la frise des cinq phases pour le projet entier, et 2 à 4
chiffres clés réels (lots faits, tests, dernier commit, lots à valider).

---

## 6. Afficher le roadmap

- Le roadmap s'affiche **dans la conversation**, au milieu de la réponse, avec
  l'outil de visualisation en ligne (`show_widget`). Charger d'abord son guide
  (`read_me`, modules `interactive` et `diagram`) sans le mentionner.
- **Pas d'artifact, pas de fichier HTML à part, pas de lien.**
- Partir du gabarit et ne changer que les données. Garder sa structure, ses
  classes et ses couleurs : c'est le rendu que l'utilisateur a choisi.
- Aucun titre ni paragraphe dans le widget : le texte va dans la réponse.
- Premier élément : un `<h2 class="sr-only">` d'une phrase qui résume l'état.
- Sans outil de visualisation disponible : un tableau Markdown par phase ou par
  volet, mêmes informations, même ordre.

---

## 7. La réponse — ordre exact

Modèle complet : `references/exemple-reponse.md`.

1. **Le verdict, en 2 à 4 phrases, avant tout.** Qui est le plus avancé, qui
   est où, ce qui manque. En mode projet : le volet le plus avancé, celui qui
   bloque, la phase du projet.
2. **Les sources, en une phrase.** « J'ai construit ce roadmap à partir de… »,
   avec les fichiers réellement lus (`docs/lots.md`, `Plan.md`…).
3. **Le roadmap** (widget).
4. `## Ce qui avance` — les projets ou volets actifs, avec la preuve (dernier
   commit, lot livré, nombre de tests).
5. `## Ce qui attend une action de votre part` — uniquement ce que
   l'utilisateur doit faire lui-même : valider des lots, annoter, relire,
   décider, réunir des personnes, signer. Une puce par projet ou volet.
6. `## Décalages à corriger` — documents qui se contredisent, statut public
   faux, README périmé, projet annoncé sans dépôt, lot « fait » sans code.
   Aucun décalage : une ligne « Aucun décalage repéré. »
7. Si des décalages existent : proposer de les corriger, sans le faire.

Style : la Skill `explainer` — français simple, phrases courtes, pas de
blabla, chemins techniques en `code`.

---

## 8. Vérifications avant d'envoyer

- [ ] Chaque projet de l'organisation, ou chaque volet du projet, est présent.
- [ ] Chaque statut a une source, et la source est citée dans la réponse.
- [ ] Les barres sont calculées, pas estimées.
- [ ] Une seule cellule « en cours » par ligne de frise.
- [ ] « Livré, à valider » est distingué de « terminé ».
- [ ] Les actions humaines sont dans leur section, pas mêlées à ce qui avance.
- [ ] Le widget n'a ni titre ni paragraphe, et suit le gabarit.
- [ ] Rien n'a été modifié dans les dépôts.

---

## Fichiers

| Fichier | Rôle |
|---|---|
| `references/collecte.md` | où chercher, commandes, lecture des suivis, repérage des décalages |
| `references/gabarit-orga.html` | widget du mode organisation |
| `references/gabarit-projet.html` | widget du mode projet, cartes de volet avec timeline |
| `references/exemple-reponse.md` | une réponse réelle complète, à imiter |

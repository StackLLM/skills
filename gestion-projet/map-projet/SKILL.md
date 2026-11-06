---
name: map-projet
description: À utiliser quand on veut voir d'un coup d'œil où en est un projet ou toute une organisation GitHub de plusieurs dépôts — volets (front, back, IA…), lots faits et restants, phase (cadrage, construction, pré-production, bêta, lancement), verdict. Les deux maps sont dessinées directement dans la conversation, avec la version HTML à télécharger, sans créer de dossier. Se déclenche sur « fais-moi la map du projet », « map de l'orga », « où en est ce projet », « où en sont mes projets », « état d'avancement », « map par volet », « map par lot », « quels lots il me reste ».
---

# Map projet — deux maps, un verdict

Tu produis **deux maps visuelles** qui disent où en est le travail.
La map se lit en moins d'une minute. Le lecteur doit savoir ce qu'il a.

| Demande | Map 1 | Map 2 |
|---|---|---|
| Un projet | `par-volet` : volets × phases, une carte par volet, avec ses lots en titres | `par-lot` : tous les lots de chaque volet, en détail |
| Une orga | `par-projet` : projets × phases, une carte par projet | `lots-restants` : ce qui reste sur chaque projet |

Mode non précisé : un dossier ou un dépôt, c'est `projet`. Un nom d'orga, c'est `orga`.

**Les maps se dessinent dans la conversation**, avec l'outil de visualisation
en ligne (`show_widget`). Deux maps à regarder, deux HTML à télécharger. Aucun
dossier n'est créé dans le projet ni dans Documents.

## La règle qui prime

**La map ne dit que ce qui se prouve.**

Chaque lot porte sa source : fichier, commit, ticket, ou la demande de
l'utilisateur avec sa date. Sans preuve, le lot passe en `a_confirmer`.
Le script refuse un lot sans source.

Tu écris les faits. Le script calcule le reste : couleurs, phase, ligne
d'avancement, verdict de chaque carte. Il refuse ces valeurs dans le fichier.

La map observe. Les projets restent intacts :

- Lecture seule sur les dépôts, les bases et GitHub.
- Application et tests ne se lancent pas.
- Un fichier `.env` ne s'ouvre jamais, même pour voir si une clé est vide.

## 1. Collecter

**Projet :**

```bash
python scripts/collecter_projet.py <chemin> -o inventaire.json
```

**Orga :**

```bash
python scripts/collecter_orga.py <orga> --racine <dossier-des-clones> -o inventaire-orga.json
```

Le script dit où chercher. Il ne remplace pas la lecture.

## 2. Lire

**Vérifier d'abord la source.** Sur une orga, regarder pour chaque dépôt :

| Champ de l'inventaire | Si… | Alors |
|---|---|---|
| `clone_a_jour` | `false` | Lire GitHub, pas le clone |
| `dernier_push_branche` | autre que `branche_principale` | Lire aussi cette branche |
| `clone_trouve_par_le_nom` | `true` | Vérifier que c'est le bon dépôt |

Lecture sur GitHub :

```bash
gh api "repos/<orga>/<depot>/contents/<chemin>?ref=<branche>" -H "Accept: application/vnd.github.raw"
```

**Puis lire les documents de suivi.** Commencer par ceux de la racine. Un document
de plus de 500 lignes : lire son sommaire et ses sections de suivi.

**Trancher les contradictions :**

| Cas | Statut |
|---|---|
| Le code ou un commit plus récent prouve que le document est périmé | Le code gagne |
| Deux documents se contredisent | Le plus récent par commit gagne |
| Rien ne permet de trancher | `a_confirmer`, avec le désaccord en `detail` |

**Tests :** la preuve est la CI ou le dernier résultat écrit. Sans CI, marquer
« non relancés » dans `detail`.

**Utilisateurs réels :** chercher dans cet ordre.

1. Base locale, ouverte en lecture seule, comptages seulement : comptes, messages,
   dossiers créés. Aucune donnée personnelle ne sort.
2. Journaux, statistiques, retours écrits.
3. Rien trouvé : le lot reste `a_confirmer`.

**Orga :** carte complète pour chaque dépôt `actif`. Avec plus de cinq dépôts
actifs, lancer un agent par groupe de dépôts. Chaque agent rend des éléments
au format de la carte. `dormant`, `archive`, `fork` et `gabarit` sont comptés dans
`hors_carte`, avec le nombre total dans `depots_total`. Si l'utilisateur veut
un de ces dépôts, il va sur la map.

Un projet parti vers un autre dépôt : le dire dans `resume`, et prendre la date
du dépôt où le travail continue pour `derniere_activite`.

## 3. Comparer le plan et l'application

La map ne décrit pas le code. Elle dit **où en est le plan**. Il faut donc deux
listes, puis leur écart.

| Liste | Où elle se lit |
|---|---|
| Ce que le plan prévoit | cahier des charges, feuille de route, jalons, tickets, cases à cocher |
| Ce que l'application fait vraiment | code de la branche principale, pages, routes, tables, commits |

Trois cas, et chacun donne un lot :

| Cas | Le lot devient |
|---|---|
| Prévu, et présent dans l'application | `fait`, source = le fichier ou le commit |
| Prévu, absent de l'application | ce qui reste : `en_cours`, `a_faire`, `a_fournir`, `a_trancher` ou `bloquant` |
| Présent dans l'application, absent du plan | `fait` quand même, source = le code. C'est le plan qui était en retard |

**Ce que l'utilisateur veut ajouter fait partie du plan.** Ce qu'il demande dans
la conversation entre dans la map comme un cahier des charges, avec sa demande
et la date en source. Sans ça, la map montrerait un projet presque fini alors
qu'il reste du travail déjà décidé.

Ce qui n'est écrit nulle part et que personne n'a demandé n'entre pas. Une étape
évidente mais sans trace devient un lot `a_confirmer`.

## 4. Découper en volets et en lots

**Les volets viennent du projet.** Front, back, IA n'est qu'un exemple. Prendre
les grands morceaux que le projet a vraiment : 3 à 7 volets, `Qualité` et
`Mise en ligne` compris quand le projet a ce travail. Noms en mots simples.

**Le `sous_titre` d'un volet dit à quoi il sert, pas où il est dans le code.**
Il s'affiche sous le nom, dans la colonne de gauche du tableau : il doit ajouter
du sens, pas une adresse.

| À écrire | À ne pas écrire |
|---|---|
| Ce que voit le client | `frontend/src/site`, 10 pages générées |
| Où le client modifie son site | /admin, Vite, React, TypeScript |
| Être trouvé sur Google, et le mesurer | SEO, GA4, Places API |

Aucun chemin de fichier, aucune liste de technos, aucun compte de fichiers. Rien
d'utile à dire : laisser le champ vide, le nom du volet suffit.

**Un lot** est une unité de travail livrable. Reprendre les lots du plan avec leur
numéro. Un lot énorme se découpe par fonction, numéro gardé. Des cases à cocher très
fines se regroupent. Viser 6 à 14 lots par volet.

Sans plan écrit, reconstruire les lots dans cet ordre : jalons, tickets, cases à
cocher, TODO, puis commits regroupés par fonction.

**Le titre d'un lot se lit seul.** Dans la carte du volet, il s'affiche derrière
une case à cocher, sans son statut et sans son détail : « Vrais prix et tailles »,
pas « D2 ». Mots simples, pas de jargon, 44 caractères au plus.

La case dit trois choses, et rien de plus :

| Case | Le lot est… |
|---|---|
| cochée | `fait` |
| barrée d'un trait | `en_cours` : commencé, pas fini |
| vide | tout le reste : il n'est pas fait |
| vide, bord en pointillés | `a_confirmer` : on ne sait pas |

Le statut exact et la source s'affichent au survol. Le détail complet est sur
la map par lot, qui garde ses pastilles de couleur.

**Les lots sont rangés en deux paquets**, avec leur compte : `Fait` d'abord,
`Reste` ensuite. Dans `Reste`, ce qui bouge passe devant — en cours, bloquant,
à trancher, à fournir, à faire — et ce qui est flou ferme la marche : à venir,
à confirmer. Sur une map d'orga, la carte d'un projet ne montre que `Reste` :
le nombre de lots faits est déjà sur la ligne d'avancement.

Un projet sans aucune trace de plan : `lots` vide, `phase_estimee` et `source_phase`.

## 5. Placer chaque lot dans une phase

| Phase | Le lot sert à… | Preuve d'un lot `fait` |
|---|---|---|
| Cadrage | décider quoi faire | cahier des charges, ADR, décision écrite |
| Construction | fabriquer | code sur la branche principale |
| Pré-production | préparer le vrai service | environnement de test en ligne, vraies données, réglages |
| Bêta | faire tester à de vrais utilisateurs | des personnes hors de l'équipe de dev s'en servent, et des données le montrent |
| Lancement | ouvrir le service pour de vrai | production en ligne, usage réel mesuré |

- Une décision va dans la phase qu'elle bloque.
- Un bug va dans la phase où il a été vu.
- Déployer n'est pas lancer.
- Un projet non lancé garde ses lots jusqu'au Lancement, en `a_venir` ou `a_confirmer`.

`bloquant` veut dire : ce volet ou ce projet ne peut pas passer à la phase suivante.
Sinon c'est `a_trancher` ou `a_faire`. Une même cause sur plusieurs cartes porte
le même champ `cause`, et compte une seule fois.

## 6. Écrire carte.json et générer

Format complet : `references/format-carte.md`.

**Rien ne s'écrit dans le projet ni dans Documents.** Le `carte.json` et les
fichiers produits vont dans le dossier de travail temporaire de la session.
Ce sont les maps qu'on livre, pas un chemin de dossier.

```bash
python scripts/generer_maps.py <dossier-temporaire>/carte.json --verifier
python scripts/generer_maps.py <dossier-temporaire>/carte.json
python scripts/generer_maps.py <dossier-temporaire>/carte.json --colonnes 3   # si demandé
```

Le script refuse la carte tant qu'une règle n'est pas respectée. Corriger et relancer.

Si l'utilisateur fournit le `carte.json` d'une map plus ancienne, repartir de lui
et revérifier chaque lot non fait.

Le `verdict` donne la situation et sa cause, sans adjectif :

> Le site marche en local. Il ne peut pas partir en ligne : les vrais prix et tailles manquent.

`prochaine_action` donne une seule action, celle qui débloque le plus.

## 7. Contrôler, puis livrer dans la conversation

Le script écrit deux fichiers par map :

| Fichier | Rôle |
|---|---|
| `<map>.widget.html` | fragment à dessiner dans la conversation |
| `<map>.html` | page complète, à télécharger, avec les sources au survol |

Pour un projet, `<map>` vaut `par-volet` puis `par-lot`. Pour une orga, `par-projet`
puis `lots-restants`.

**Dessiner les deux maps dans la conversation :**

1. Charger le guide de l'outil (`read_me`, module `mockup`), sans le mentionner.
2. Lire `par-volet.widget.html` et passer son contenu **tel quel** à `show_widget`.
   Ne rien réécrire à la main : le script a calculé chaque couleur et chaque case.
3. Une phrase dans la réponse, puis la seconde map de la même façon.
4. Envoyer les deux `.html` avec `SendUserFile`, en `attach`.

Ne jamais répondre avec un chemin de dossier à ouvrir.

**Colonnes.** Au-dessus des cartes, trois boutons font passer la map en 1, 2 ou
3 colonnes, sans régénérer. Elle s'ouvre en 2 colonnes. Si l'utilisateur demande
un nombre précis (« en 3 colonnes »), régénérer avec `--colonnes 3` : la map
s'ouvre alors en 3 colonnes, et le HTML à télécharger aussi.

Sans outil de visualisation dans la session : envoyer les deux `.html` avec
`SendUserFile` en `render`. Seulement si l'utilisateur demande une image :
relancer avec `--png` (Chrome ou Edge nécessaire) et envoyer les PNG.

Relire la map dessinée : texte coupé, carte vide, lot absent de sa carte ou
verdict qui contredit les lots, corriger `carte.json` et régénérer.

Réponse à l'utilisateur, dans cet ordre :

1. Le verdict et la phase.
2. Les bloquants et les décisions à trancher.
3. Ce qui reste à confirmer.

## Erreurs fréquentes

| Erreur | Correction |
|---|---|
| Map rangée dans un dossier, chemin donné en réponse | Les maps se dessinent dans la conversation |
| Map envoyée en image ou en fichier alors que `show_widget` est là | Dessiner le `.widget.html` avec `show_widget` |
| Fragment retouché à la main avant `show_widget` | Le passer tel quel ; corriger `carte.json` et régénérer |
| Map construite depuis le code seul | Lire le plan, et montrer l'écart entre les deux |
| Ce que l'utilisateur veut ajouter n'est pas dans la map | Sa demande est du plan : un lot, avec la date en source |
| Volets copiés de l'exemple front, back, IA | Partir des dossiers et des documents du projet |
| Titre de lot illisible seul : « D2 », « Lot 16.4 » | Le titre s'affiche nu dans la carte : des mots |
| `sous_titre` qui donne un chemin de code | Dire à quoi sert le volet, ou laisser vide |
| Lecture d'un clone en retard | Regarder `clone_a_jour` avant de lire |
| Tâche marquée `fait` parce que le plan le dit | Vérifier dans le code ou les commits |
| `Lancement` parce qu'une URL répond | Chercher une preuve d'usage réel |
| Lots futurs imaginés pour remplir la map | Écrit nulle part : `a_confirmer` |
| Même bloquant compté sur trois projets | Leur donner le même `cause` |
| Résumé qui raconte l'histoire du projet | Dire ce qui existe aujourd'hui |

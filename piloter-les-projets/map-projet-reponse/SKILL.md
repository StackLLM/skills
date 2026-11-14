---
name: map-projet-reponse
description: La map d'avancement d'un projet ou d'une organisation GitHub, affichée directement dans la réponse — volets, lots faits et restants, phase (cadrage, construction, pré-production, bêta, lancement), bloquants, verdict. Deux maps à faire défiler et à agrandir sur place, téléchargeables en image ou en HTML. Aucun fichier, aucun dossier. Se déclenche sur « fais-moi la map du projet », « map de l'orga », « où en est ce projet », « où en sont mes projets », « état d'avancement », « montre-moi la map ici », « map par volet », « map par lot », « quels lots il me reste ».
---

# Map projet — une map dans la réponse

Tu produis **une map visuelle affichée dans la conversation**.
Elle se lit en moins d'une minute. Le lecteur doit savoir ce qu'il a.

Une seule, et c'est voulu : deux images dans une réponse, on en regarde une.
Celle-ci porte déjà les lots, rangés en cases à cocher. Le détail de chaque lot
tient dans l'infobulle — statut, précision, preuve.

| Demande | La map |
|---|---|
| Un projet | volets × phases, puis une carte par volet, avec ses lots en cases à cocher |
| Une orga | projets × phases, puis une carte par projet, avec ce qui lui reste |

Mode non précisé : un dossier ou un dépôt, c'est `projet`. Un nom d'orga, c'est `orga`.

**Rien n'est livré en fichier.** La map s'affiche dans la réponse. Le lecteur
fait défiler, agrandit, et télécharge en image ou en HTML s'il veut. Aucun
dossier n'est créé, ni dans le projet, ni dans Documents.

La skill `map-projet` fait l'inverse : elle écrit deux PNG et deux HTML sur le
disque, dont une map par lot détaillée, pour qui veut garder ou envoyer. Même
façon de lire, même format de carte, même moteur.

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
python3 "<chemin-de-la-skill>/scripts/collecter_projet.py" <chemin> -o inventaire.json
```

**Orga :**

```bash
python3 "<chemin-de-la-skill>/scripts/collecter_orga.py" <orga> --racine <dossier-des-clones> -o inventaire-orga.json
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
`hors_carte`, avec le nombre total dans `depots_total`.

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

**Rien ne s'écrit dans le projet ni dans Documents.** Le `carte.json` et les deux
fragments vont dans le dossier de travail temporaire de la session. Ce ne sont
pas des livrables : ce sont des brouillons que la réponse va afficher.

```bash
python3 "<chemin-de-la-skill>/scripts/generer_widget.py" <dossier-temporaire>/carte.json --verifier
python3 "<chemin-de-la-skill>/scripts/generer_widget.py" <dossier-temporaire>/carte.json
```

Le script refuse la carte tant qu'une règle n'est pas respectée. Corriger et relancer.

Si l'utilisateur fournit le `carte.json` d'une map plus ancienne, repartir de lui
et revérifier chaque lot non fait.

Le `verdict` donne la situation et sa cause, sans adjectif :

> Le site marche en local. Il ne peut pas partir en ligne : les vrais prix et tailles manquent.

`prochaine_action` donne une seule action, celle qui débloque le plus.

## 7. Afficher la map dans la réponse

Le script écrit un fichier, `map.widget.html`. Ce n'est **pas une page** : pas
de doctype, pas de `<html>`, pas de fond. C'est un fragment prêt pour l'outil
d'affichage de la conversation.

Lire le fichier, et passer son contenu **tel quel** à
`mcp__visualize__show_widget`, dans `widget_code`. Un seul appel, avec pour
`title` `map_<projet>`.

**Une seule image.** Ne pas en fabriquer une deuxième, ni découper la map en
morceaux : deux images dans une réponse, on en regarde une. Le détail de chaque
lot est déjà dans l'infobulle de sa ligne.

**Ne rien changer au fragment.** Pas de reformatage, pas de couleur ajoutée, pas
de titre ajouté dans le HTML : le texte va dans la réponse, le visuel dans
l'outil.

### Ce que le fragment respecte déjà, et qu'il ne faut pas casser

| Contrainte | Pourquoi |
|---|---|
| Largeur 680 px, cartes sur trois colonnes | C'est la largeur de l'affichage dans la conversation. Sur une colonne, la map est trois fois trop haute |
| Un réglage « Colonnes 1 2 3 » en haut | Le lecteur élargit les cartes lui-même pour lire une ligne entière |
| Aucune couleur écrite en dur | Les couleurs viennent de l'interface, et suivent le mode clair ou sombre |
| Pas de doctype, pas de fond | La conversation fournit le cadre |
| Un seul `<script>`, en toute fin | Celui du réglage. Il ne fait que changer une classe |

### Le coût

Le fragment passe en entier par la réponse. Un projet de 7 volets et 75 lots
fait environ 20 Ko. Au-delà de 14 lots par volet, le script prévient :
regrouper, sinon la map devient très longue.

## 8. Contrôler, puis répondre

Relire la map affichée. Texte coupé, carte vide, lot absent de sa carte,
sous-titre de volet qui n'apprend rien, verdict qui contredit les lots :
corriger `carte.json`, régénérer, réafficher.

Réponse à l'utilisateur, dans cet ordre :

1. Le verdict et la phase.
2. Les bloquants et les décisions à trancher.
3. Ce qui reste à confirmer.

Ne jamais répondre avec un chemin de fichier : la map est déjà dans la réponse.

## Les deux skills de map

| | `map-projet` | `map-projet-reponse` |
|---|---|---|
| Sortie | 2 PNG + 2 HTML, envoyés en fichiers | 1 map dans la réponse |
| Largeur | 1216 px, 3 colonnes de cartes | 680 px, 1 colonne |
| Couleurs | sa propre charte, mode clair | celles de l'interface, clair et sombre |
| Besoin | Chrome ou Edge, pour le PNG | rien |
| Pour | garder la map, l'imprimer, l'envoyer | la regarder tout de suite |

Le format de `carte.json` est le même. Une carte faite pour l'une marche
telle quelle dans l'autre.

## Erreurs fréquentes

| Erreur | Correction |
|---|---|
| Map rangée dans un dossier, chemin donné en réponse | La map s'affiche dans la réponse |
| Fragment retouché avant l'affichage | Le passer tel quel : il est déjà aux bonnes contraintes |
| Deux images affichées | Une seule. Le détail des lots est dans l'infobulle |
| `sous_titre` qui donne un chemin de code | Dire à quoi sert le volet, ou laisser vide |
| Map construite depuis le code seul | Lire le plan, et montrer l'écart entre les deux |
| Ce que l'utilisateur veut ajouter n'est pas dans la map | Sa demande est du plan : un lot, avec la date en source |
| Volets copiés de l'exemple front, back, IA | Partir des dossiers et des documents du projet |
| Titre de lot illisible seul : « D2 », « Lot 16.4 » | Le titre s'affiche nu dans la carte : des mots |
| Lecture d'un clone en retard | Regarder `clone_a_jour` avant de lire |
| Tâche marquée `fait` parce que le plan le dit | Vérifier dans le code ou les commits |
| `Lancement` parce qu'une URL répond | Chercher une preuve d'usage réel |
| Lots futurs imaginés pour remplir la map | Écrit nulle part : `a_confirmer` |
| Même bloquant compté sur trois projets | Leur donner le même `cause` |
| Résumé qui raconte l'histoire du projet | Dire ce qui existe aujourd'hui |

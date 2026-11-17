# Dimensionner une IA locale

Quand un projet fait tourner un modèle sur sa propre machine — Granite, Llama,
Mistral, Qwen — la question est toujours la même :

> **Cette machine peut servir combien de personnes en même temps ?**

On y répond avec des chiffres, et **toujours avec les hypothèses qui vont
avec**. Un chiffre sans hypothèse est une promesse qu'on ne tiendra pas.

---

## 1. Les quatre choses à établir

| Quoi | Pourquoi ça compte |
|---|---|
| Le modèle et sa taille | 3 milliards de paramètres et 70 milliards ne jouent pas dans la même cour |
| La quantification | c'est elle qui décide de la mémoire nécessaire |
| La machine | carte graphique et sa mémoire, ou processeur et mémoire vive |
| L'usage réel | longueur des demandes, longueur des réponses, personnes en même temps |

Si l'une manque, on le dit et on ne conclut pas à sa place.

---

## 2. La mémoire du modèle

Règle de calcul, valable pour l'ordre de grandeur :

```text
mémoire du modèle ≈ nombre de paramètres × octets par paramètre
```

| Quantification | Octets par paramètre | Ce que ça change |
|---|---|---|
| 16 bits | 2 | qualité maximale, mémoire maximale |
| 8 bits | 1 | perte très faible |
| 4 bits | 0,5 | perte visible sur les tâches fines, **le choix courant** |

Exemple, un modèle de 8 milliards de paramètres :

```text
16 bits : 8 × 2   = 16 Go
 8 bits : 8 × 1   =  8 Go
 4 bits : 8 × 0,5 =  4 Go
```

**Ce n'est pas tout.** Il faut ajouter :

- le **cache de contexte**, qui grandit avec la longueur de la conversation et
  avec le nombre de demandes en même temps ;
- une marge pour le système et le moteur d'inférence.

En pratique, compter **le poids du modèle plus 30 à 50 %** pour une seule
demande à la fois.

```text
Modèle 8 milliards en 4 bits  →  4 Go
+ contexte et marge           →  6 à 7 Go au total
Une carte de 8 Go passe. Une carte de 6 Go, non.
```

---

## 3. Combien de personnes en même temps

C'est la question qui compte, et la plus mal posée. **Ce n'est pas le nombre
de comptes.** C'est le nombre de demandes qui tournent à la même seconde.

```text
demandes en parallèle ≈ (mémoire disponible − mémoire du modèle) / mémoire d'un contexte
```

Le modèle est chargé **une seule fois**. Ce qui se multiplie, c'est le
contexte de chaque demande.

Ordre de grandeur à vérifier sur la machine réelle :

| Mémoire de la carte | Modèle 8 milliards en 4 bits | Demandes en parallèle |
|---|---|---|
| 8 Go | passe | 1 à 2 |
| 12 Go | passe | 3 à 4 |
| 16 Go | passe | 5 à 8 |
| 24 Go | passe large | 10 et plus |

Et le lien entre demandes en parallèle et utilisateurs :

```text
Une réponse prend 5 secondes.
Un utilisateur pose une question toutes les 2 minutes.
Un utilisateur occupe donc la machine 5 / 120 = 4 % du temps.
Avec 2 demandes en parallèle → environ 50 utilisateurs actifs.
```

**Ce calcul suppose que les demandes arrivent régulièrement.** Elles arrivent
par vagues : tout le monde à 9 h, personne à midi. Diviser le résultat par
deux ou trois pour rester honnête.

---

## 4. Sur processeur, sans carte graphique

Possible, mais il faut le dire franchement : **c'est lent**.

| | Carte graphique | Processeur seul |
|---|---|---|
| Vitesse | 20 à 100 mots par seconde | 2 à 10 mots par seconde |
| Réponse de 300 mots | 3 à 15 secondes | 30 secondes à 3 minutes |
| Plusieurs demandes | possible | une à la fois, en pratique |

Sur processeur, la mémoire vive remplace la mémoire de la carte, et le nombre
de cœurs pilote la vitesse.

Un modèle sur processeur convient à une tâche de fond — classer des documents
la nuit. Pas à une conversation où quelqu'un attend.

---

## 5. Ce qu'il faut aussi prévoir

| Poste | Ordre de grandeur |
|---|---|
| Disque pour le modèle | la taille du fichier, plus de la place pour en essayer d'autres |
| Temps de chargement | 10 secondes à 2 minutes au démarrage |
| Électricité | une carte graphique tire 200 à 400 W en charge |
| Refroidissement | une machine qui chauffe ralentit |
| Montée en charge | un modèle local **ne s'ajuste pas tout seul** |
| Plan de repli | que se passe-t-il si la machine tombe ? |

Le plan de repli est souvent oublié. Deux réponses possibles : basculer sur
une API le temps de la panne, ou afficher un message clair. Une troisième
n'existe pas.

---

## 6. Comment l'écrire dans le rapport

Toujours avec les hypothèses, toujours avec l'invitation à mesurer.

> **Estimation** — Avec une carte de 12 Go et ce modèle en 4 bits, la machine
> tient **3 à 4 demandes en même temps**, soit **environ 40 utilisateurs
> actifs**.
>
> **Hypothèses** : contexte de 4 000 jetons, réponses de 300 mots, une
> question toutes les deux minutes par personne, aucune autre application sur
> la machine, arrivée régulière des demandes.
>
> **Confiance : À vérifier.** Ces chiffres viennent d'un calcul, pas d'une
> mesure. Charger le modèle, lancer dix demandes en parallèle, regarder la
> mémoire occupée et le temps de réponse. **Mesurer avant de s'engager auprès
> d'utilisateurs.**

Ne jamais écrire « la machine supportera 100 utilisateurs » sans avoir mesuré.
C'est une promesse, pas une estimation.

---

## 7. Local ou API : la comparaison honnête

| | Modèle local | API d'un fournisseur |
|---|---|---|
| Données | ne sortent pas | sortent, avec les conditions du fournisseur |
| Coût | fixe, même sans usage | à l'appel, nul sans usage |
| Vitesse | dépend de la machine | régulière |
| Montée en charge | limitée par la machine | quasi illimitée |
| Qualité | celle des modèles ouverts | souvent supérieure |
| Mise en place | pilotes, mémoire, réglages | une clé d'API |
| Panne | à votre charge | à la leur |

**À dire quand la question se pose** : si la confidentialité n'est pas une
obligation, l'API coûte souvent moins cher qu'une machine à carte graphique
tant que le volume reste modéré. Le point de bascule se calcule — nombre
d'appels par mois × prix par appel, comparé au prix mensuel de la machine.

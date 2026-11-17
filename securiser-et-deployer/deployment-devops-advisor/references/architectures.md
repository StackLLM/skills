# Les architectures de déploiement

On présente **au moins deux options**, jamais une seule. Chacune avec son
coût, sa complexité, sa maintenance et ce qu'elle donne en charge.

Les prix sont des **ordres de grandeur** en euros par mois, à vérifier chez le
fournisseur avant de s'engager. Ils bougent.

---

## 1. La grille de comparaison

Chaque option se présente ainsi. Pas de ligne vide : si on ne sait pas, on
l'écrit.

```text
Ce que c'est, en une phrase
Coût mensuel, ordre de grandeur
Complexité de mise en place
Maintenance : qui fait quoi, combien de fois par mois
Charge : jusqu'où ça tient
Sécurité : ce qui est à votre charge
Disponibilité : que se passe-t-il si la machine tombe
Avantages
Inconvénients
Quand la choisir
```

---

## 2. Les options

### VPS unique

Un serveur loué, on y installe tout soi-même.

| | |
|---|---|
| Coût | 5 à 40 € |
| Mise en place | moyenne — il faut installer et configurer |
| Maintenance | **à votre charge** : mises à jour système, certificats, sauvegardes, supervision. Comptez une demi-journée par mois. |
| Charge | quelques centaines d'utilisateurs actifs pour une application simple |
| Sécurité | tout est à vous : pare-feu, accès SSH, mises à jour |
| Disponibilité | la machine tombe, le service tombe |
| Avantages | le moins cher, contrôle total, aucune limite de plateforme |
| Inconvénients | c'est vous l'administrateur système |
| Quand | outil interne, budget serré, équipe prête à apprendre |

### VPS + Docker Compose

Le même serveur, mais les services dans des conteneurs décrits par un fichier.

| | |
|---|---|
| Coût | 10 à 60 € |
| Mise en place | moyenne |
| Maintenance | idem VPS, mais **les redéploiements deviennent simples et reproductibles** |
| Charge | idem VPS |
| Avantages | même comportement en local et en production, redémarrage automatique, retour arrière rapide |
| Inconvénients | il faut apprendre les conteneurs |
| Quand | **le meilleur rapport simplicité / contrôle pour une petite équipe** |

### Plateforme managée

On pousse le code, la plateforme construit et fait tourner.

| | |
|---|---|
| Coût | 0 à 100 € selon l'usage |
| Mise en place | faible |
| Maintenance | **presque nulle** — système, certificats et mise à l'échelle sont gérés |
| Charge | s'ajuste toute seule, dans les limites du forfait |
| Sécurité | le système est à jour sans vous ; l'application reste à vous |
| Disponibilité | bonne, gérée par le fournisseur |
| Avantages | on se concentre sur le code |
| Inconvénients | coût qui monte vite, limites de plateforme, dépendance au fournisseur, souvent pas de disque persistant |
| Quand | équipe sans temps d'administration, application web classique |

### Hébergement statique pour le frontend

Le frontend construit en fichiers, servis par un réseau de diffusion.

| | |
|---|---|
| Coût | 0 à 20 € |
| Mise en place | faible |
| Maintenance | nulle |
| Avantages | très rapide partout, certificat automatique |
| Inconvénients | ne sert qu'au frontend ; le backend vit ailleurs |
| Quand | **presque toujours**, dès que le frontend est séparé |

### Base de données managée

La base gérée par un fournisseur : sauvegardes, mises à jour, supervision.

| | |
|---|---|
| Coût | 0 à 50 € pour une petite base |
| Maintenance | **sauvegardes automatiques incluses** |
| Avantages | c'est la partie qu'on n'a pas envie de perdre |
| Inconvénients | plus cher qu'une base sur le VPS |
| Quand | dès qu'il y a des données de clients |

> **Avis à donner sans détour** : si on n'a pas le temps de gérer des
> sauvegardes soi-même, la base managée est le premier poste sur lequel
> dépenser. Une application se réinstalle en une heure. Une base perdue ne se
> retrouve pas.

### Serverless

Le code s'exécute à la demande, on paie à l'appel.

| | |
|---|---|
| Coût | souvent 0 à faible volume |
| Mise en place | faible pour une fonction, élevée pour une application entière |
| Charge | excellente sur des pointes |
| Avantages | rien à administrer, coût proportionnel à l'usage |
| Inconvénients | latence au premier appel, durée d'exécution limitée, connexions à la base délicates, pas d'état, mise au point difficile |
| Quand | tâches ponctuelles, webhooks, traitements courts — **rarement pour une application complète** |

### Kubernetes

Un orchestrateur de conteneurs sur plusieurs machines.

| | |
|---|---|
| Coût | 100 € et plus, plus le temps humain |
| Mise en place | élevée |
| Maintenance | élevée — c'est un métier |
| Charge | très grande |
| Avantages | mise à l'échelle fine, déploiements progressifs, résistance aux pannes |
| Inconvénients | **complexité sans rapport avec les besoins d'une petite équipe** |
| Quand | plusieurs équipes, plusieurs dizaines de services, une personne dédiée |

> **À dire clairement** : pour une application interne de quelques dizaines
> d'utilisateurs, Kubernetes coûte plus cher en temps qu'il ne rapporte. Le
> proposer serait une faute de conseil.

### Machine avec carte graphique

Pour une IA qui tourne chez soi.

| | |
|---|---|
| Coût | 150 à 1 500 € en location, ou l'achat d'une machine |
| Mise en place | élevée : pilotes, bibliothèques, modèle |
| Avantages | les données ne sortent pas, coût fixe au lieu du coût à l'appel |
| Inconvénients | cher à l'arrêt comme en marche, dimensionnement délicat |
| Quand | confidentialité obligatoire, ou volume qui rend l'API plus chère |

Dimensionnement : [ia-locale.md](ia-locale.md).

---

## 3. Trois combinaisons qui marchent

| Situation | Proposition |
|---|---|
| Outil interne, 20 à 100 personnes | frontend statique + backend sur un VPS avec Docker Compose + base managée |
| Application client, trafic irrégulier | frontend statique + backend sur plateforme managée + base managée |
| Application avec IA locale | frontend statique + backend sur VPS + machine à carte graphique séparée pour le modèle |

Ce sont des points de départ, pas des réponses. Les confronter aux réponses de
l'étape de cadrage.

---

## 4. Ce qui coûte plus cher que l'hébergement

À rappeler quand on compare des prix.

| Poste | Pourquoi on l'oublie |
|---|---|
| Le temps d'administration | ne figure sur aucune facture |
| Les sauvegardes et leur test | on les découvre le jour de l'incident |
| La supervision | sans elle, on apprend les pannes par les utilisateurs |
| Le nom de domaine et le certificat | petits montants, gros blocage si oubliés |
| Le trafic sortant | facturé au-delà d'un seuil, chez presque tous |
| Les environnements | une recette double une partie de la facture |

Un VPS à 10 € qui demande une demi-journée par mois n'est pas moins cher
qu'une plateforme à 40 € qui n'en demande aucune. **Le dire.**

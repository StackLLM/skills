# Le registre de couverture, et la vérification

Deux idées qui changent la valeur d'un audit :

1. **Un audit ne finit jamais un sujet.** On dit ce qu'on a regardé, et ce qu'on
   n'a pas regardé. Jamais « l'application est sécurisée ».
2. **Celui qui trouve ne valide pas.** Une relecture indépendante passe après.

> Adapté de la skill `security-audit` de Cloudflare (MIT). Voir `ORIGINES.md`.

---

## 1. Le registre de couverture

Avant de chercher, on écrit **la liste de ce qu'on va regarder**. Après chaque
passe, on met à jour cette liste. Elle finit dans le rapport.

Une **unité de couverture** = une surface × une frontière × une classe d'attaque.

| Surface | Frontière | Classe |
|---|---|---|
| L'API des dossiers | visiteur → serveur | Contrôle des accès |
| L'API des dossiers | client A → client B | Cloisonnement des données |
| Le formulaire d'upload | visiteur → disque | Ressources et fichiers |
| Le code du navigateur | serveur → navigateur | Côté client |

Chaque unité porte un état :

| État | Ce qu'il veut dire |
|---|---|
| `prévu` | dans le plan, pas encore regardé |
| `assigné` | une passe est en cours dessus |
| `couvert` | regardé, avec une trace de ce qui a été lu |
| `à vérifier` | regardé, mais un fait manque pour conclure |
| `reporté` | laissé de côté, avec la raison |
| `hors périmètre` | exclu dès le départ |

**`hors périmètre` n'est jamais `couvert`.** Un audit limité se présente comme
limité.

### Le tableau à mettre dans le rapport

```text
| Surface | Frontière | Classe | État | Ce qui a été lu |
|---|---|---|---|---|
| API dossiers | visiteur → serveur | Accès | couvert | routes/dossiers.py, middleware/auth.py |
| API dossiers | client A → client B | Cloisonnement | à vérifier | le filtre par client vient d'une variable absente du dépôt |
| Déploiement | internet → machine | Cloud | hors périmètre | pas d'accès à l'infrastructure |
```

### La phrase finale, obligatoire

Le rapport se termine sur une phrase de ce type :

> Cet audit a couvert 14 unités sur 19. Trois attendent un fait extérieur au
> dépôt. Deux sont hors périmètre faute d'accès à l'infrastructure. Aucune passe
> ne rend un sujet complet : ce qui n'est pas listé ici n'a pas été regardé.

---

## 2. Les trois profils d'audit

Le profil change la **largeur**, jamais le niveau de preuve exigé.

| Profil | Pour quoi | Ce qui change |
|---|---|---|
| **rapide** | petit projet, première passe, nouvelle passe après correction | unités grossières, une seule passe de recherche, une relecture finale |
| **standard** | le défaut | le déroulé complet des six temps |
| **profond** | gros projet, données sensibles, avant une mise en ligne qui engage | unités découpées par sous-système, passes de recherche jusqu'à ce qu'une passe ne trouve plus rien, double relecture |

Un audit **ciblé** — un dossier, un sous-système, un seul domaine, ou l'écart
entre deux versions — se dit ciblé dans la première phrase du rapport.

Ce qu'un profil ne change **jamais** :

- la règle de la frontière franchie et du résultat concret,
- le niveau de confiance sur chaque constat,
- la séparation entre criticité et certitude,
- la relecture indépendante des constats confirmés.

---

## 3. La relecture indépendante

Un constat trouvé pendant la recherche est un **candidat**, pas un constat.

```text
Recherche  →  candidat  →  relecture indépendante  →  constat
```

La relecture ne reprend pas le raisonnement de la recherche. Elle repart du
code, et elle répond à quatre questions :

1. **La frontière existe-t-elle vraiment ?** Nommer le principal de moindre
   confiance, et ce qu'il n'est pas censé pouvoir faire.
2. **Le chemin tient-il ?** Chaque étape se lit dans le code, fichier et ligne.
3. **Le résultat est-il concret ?** Une donnée lue, un état changé, un service
   arrêté. Pas « cela pourrait permettre ».
4. **Le correctif proposé ferme-t-il vraiment le chemin ?**

Si une réponse manque : le candidat tombe en « À vérifier », avec **le fait
précis** qui manque — jamais en « Confirmé affaibli ».

Quand la relecture est faite par un agent séparé, lui donner le code et la
question, **pas** la conclusion de la recherche. Un relecteur à qui on donne
l'hypothèse la confirme.

### Le journal des candidats écartés

Un candidat écarté se note, avec la raison. Cela évite de le retrouver à la
passe suivante, et cela montre le travail réel.

```text
| Candidat | Écarté parce que |
|---|---|
| Requête SQL par concaténation dans rapports.py | la valeur vient d'une constante interne, pas de l'utilisateur |
| Cookie sans HttpOnly | il ne contient qu'une préférence d'affichage |
```

---

## 4. Reprendre un audit précédent

Si un audit existe déjà sur ce projet :

| Situation | Ce qu'on fait |
|---|---|
| Constat confirmé, code inchangé | on le reprend, mais il repasse par la relecture |
| Constat confirmé, code changé | nouvelle unité : il n'est confirmé que si on le reprouve |
| Constat « À vérifier » | redevient du travail à faire |
| Unité couverte, code inchangé | informe la priorité, mais reste visible dans le registre |
| Constat écarté | n'empêche pas de regarder à nouveau la même surface |

Un audit précédent **ne vaut jamais** « le reste va bien ».

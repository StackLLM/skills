# Le parcours — un domaine à la fois

On ne saute pas d'un domaine à l'autre au gré des envies. **On termine un
domaine, puis on passe au suivant.** Les fiches d'un même domaine se renforcent
entre elles : la septième s'appuie sur la deuxième, et la révision devient
cumulative au lieu d'être dispersée.

## La règle

| Règle | Pourquoi |
|---|---|
| Un domaine ouvert à la fois | sinon aucun n'atteint le niveau où l'on tient face à un expert |
| L'ordre des fiches suit les **dépendances** | une fiche ne doit jamais supposer une notion non écrite |
| Une fiche hors domaine est permise | si un blocage réel survient au travail — mais elle ne change pas le domaine en cours |
| Un domaine est terminé quand ses fiches « socle » existent | les fiches marquées *socle* ci-dessous |

Quand une fiche en cours a besoin d'une notion d'un autre domaine, deux
possibilités : la définir en trois lignes dans le bloc `.prerequis`, ou la noter
pour plus tard. On n'ouvre pas le domaine voisin pour autant.

---

## Ordre des domaines

L'ordre n'est pas libre. Chaque domaine s'appuie sur le précédent.

| # | Domaine | Pourquoi à cette place |
|---|---|---|
| 1 | **Développement logiciel** | tout le reste en dépend : HTTP, données, erreurs, concurrence |
| 2 | **DevOps et systèmes** | fait tourner ce que le premier a construit |
| 3 | **Cloud, réseau et infrastructure** | relie et expose ce que le deuxième fait tourner |
| 4 | **Cybersécurité** | attaque et défend les trois précédents ; incompréhensible sans eux |
| 5 | **Intelligence artificielle** | largement indépendant — peut se prendre plus tôt si le besoin est réel |

---

## 1. Développement logiciel

| Ordre | Fiche | Socle |
|---|---|---|
| 1 | HTTP : ce qui part vraiment sur le réseau | ✓ |
| 2 | Les codes de statut, et celui qu'on choisit | |
| 3 | Les cookies, les sessions et les jetons | ✓ |
| 4 | Authentification : qui tu es, et comment on le prouve | ✓ |
| 5 | Autorisation, contrôle d'accès et IDOR | ✓ |
| 6 | Index : pourquoi une requête met 4 secondes | ✓ |
| 7 | Transactions et niveaux d'isolation | |
| 8 | Migrations de base de données | |
| 9 | Concurrence : course critique, verrou, file | ✓ |
| 10 | Idempotence et réessai | |
| 11 | Gestion des erreurs : ce qu'on remonte, ce qu'on cache | |
| 12 | Tests : ce qu'on isole, ce qu'on simule | |
| 13 | Mesurer une performance : moyenne, p95, p99 | |

## 2. DevOps et systèmes

| Ordre | Fiche | Socle |
|---|---|---|
| 1 | Processus, PID, signaux, code de sortie | ✓ |
| 2 | Permissions Unix, utilisateurs, capacités | ✓ |
| 3 | **Docker et virtualisation** — *écrite* | ✓ |
| 4 | Images, couches et cache de construction | |
| 5 | Volumes : où vit l'état | ✓ |
| 6 | cgroups : plafonner processeur et mémoire | |
| 7 | Services, démarrage, redémarrage automatique | |
| 8 | Journaux : log, métrique, trace | ✓ |
| 9 | CI/CD : déclencheur, agent, artefact, secret | ✓ |
| 10 | Sauvegarde et restauration testée | ✓ |
| 11 | Déploiement : rupture, sans coupure, retour arrière | ✓ |

## 3. Cloud, réseau et infrastructure

| Ordre | Fiche | Socle |
|---|---|---|
| 1 | TCP : la connexion, avant tout HTTP | ✓ |
| 2 | DNS : enregistrements, TTL, propagation | ✓ |
| 3 | TLS : la poignée de main, le certificat, le SNI | ✓ |
| 4 | **Reverse proxy et load balancing** — *écrite* | ✓ |
| 5 | Sondes de santé : vivacité et disponibilité | ✓ |
| 6 | Cache et CDN : ce qui est servi sans toucher l'application | |
| 7 | Stockage : bloc, fichier, objet | |
| 8 | IAM : identité, rôle, politique, moindre privilège | ✓ |
| 9 | Haute disponibilité : point unique de panne, bascule | |
| 10 | Passage à l'échelle : horizontal, vertical, état partagé | ✓ |
| 11 | Systèmes distribués : idempotence, partition réseau | |

## 4. Cybersécurité et hacking éthique

| Ordre | Fiche | Socle |
|---|---|---|
| 1 | **Injection SQL** — *écrite* | ✓ |
| 2 | XSS : quand le texte devient du script | ✓ |
| 3 | CSRF et les cookies `SameSite` | ✓ |
| 4 | Hachage des mots de passe : sel, coût, argon2 | ✓ |
| 5 | **Rate limiting face au DoS** — *écrite* | ✓ |
| 6 | Secrets : où ils vivent, comment on les tourne | ✓ |
| 7 | En-têtes de sécurité et CSP | |
| 8 | Dépendances vulnérables et chaîne de construction | |
| 9 | Durcissement d'un serveur Linux | |
| 10 | Analyse de journaux et détection | |
| 11 | Réponse à incident : contenir, corriger, notifier | ✓ |

## 5. Intelligence artificielle

| Ordre | Fiche | Socle |
|---|---|---|
| 1 | Token, fenêtre de contexte, coût d'un appel | ✓ |
| 2 | Embedding : la distance entre deux textes | ✓ |
| 3 | RAG : découpage, index, recherche, reclassement | ✓ |
| 4 | Ce qui entre vraiment dans l'invite | ✓ |
| 5 | Agent : boucle, outils, condition d'arrêt | |
| 6 | Inférence : lot, cache, latence du premier jeton | |
| 7 | Ajustement fin et LoRA | |
| 8 | Évaluer un modèle : jeu de test, métrique, variance | ✓ |
| 9 | Servir un modèle : GPU, file d'attente, limite de débit | |

---

## Suivre l'avancement

L'index des fiches (`Technical-words/index.html`) groupe par domaine et compte
les fiches. Le domaine en cours est celui qui n'a pas encore toutes ses fiches
*socle*.

Pour lancer la suite, il suffit de nommer la fiche : *« la fiche HTTP »*.
La skill reprend l'ordre ci-dessus.

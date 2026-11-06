# Ce que l'expert demande, domaine par domaine

Chaque domaine a ses questions de relance. Elles reviennent presque toujours.
Une fiche qui n'y répond pas laissera le lecteur bloqué au deuxième échange.

---

## 1. Développement logiciel

**La question de fond de l'expert** : *qu'est-ce qui part sur le réseau, et que
se passe-t-il quand ça rate ?*

| Sujet | Relances à couvrir |
|---|---|
| HTTP | méthode, en-têtes, codes de statut, corps, qui ferme la connexion, keep-alive |
| API | contrat, versionnage, pagination, idempotence, codes d'erreur, délai d'attente |
| Authentification | où vit la preuve, durée de vie, révocation, renouvellement, vol de jeton |
| Base de données | index utilisé ou non, transaction, niveau d'isolation, verrou, N+1 |
| Concurrence | état partagé, course critique, verrou, file d'attente, ordre des opérations |
| Mémoire | ce qui est alloué, ce qui est libéré, la fuite, le ramasse-miettes |
| Tests | ce qu'on isole, ce qu'on simule, ce qui reste non couvert |
| Performance | où est la mesure, quel percentile, quel goulot |
| Débogage | la trace, le log, le point d'arrêt, la reproduction minimale |

**Toujours montrer** : une requête complète, sa réponse complète, et le cas
d'erreur.

---

## 2. DevOps, Linux et systèmes

**La question de fond** : *qu'est-ce que le noyau fait réellement, et où vit
l'état ?*

| Sujet | Relances à couvrir |
|---|---|
| Processus | PID, parent, signaux, code de sortie, processus zombie |
| Permissions | utilisateur, groupe, bits, `root` dans un conteneur, capacités |
| Services | démarrage, redémarrage automatique, dépendances, journal |
| Docker | image et couches, conteneur et processus, namespace, cgroup, volume, réseau |
| Virtualisation | hyperviseur, noyau invité, coût de démarrage, isolation réelle |
| CI/CD | déclencheur, agent, cache, artefact, secret, droit de déploiement |
| Observabilité | log, métrique, trace, cardinalité, rétention |
| Sauvegarde | quoi, où, à quelle fréquence, et **la restauration testée** |
| Déploiement | rupture ou sans coupure, retour arrière, migration de base |

**Toujours montrer** : la commande qui prouve l'état réel
(`ps`, `ss`, `lsof`, `docker inspect`, `systemctl status`, `journalctl`).

---

## 3. Cloud, réseau et infrastructure

**La question de fond** : *dessine-moi le chemin exact d'un paquet, et dis-moi
ce qui tombe.*

| Sujet | Relances à couvrir |
|---|---|
| DNS | enregistrement, TTL, cache, résolveur, propagation, délégation |
| TLS | qui termine le chiffrement, certificat, chaîne, SNI, renouvellement |
| Proxy inverse | ce qu'il réécrit, `X-Forwarded-For`, délais, tampon |
| Répartition de charge | algorithme, sonde de santé, session collante, drainage |
| Haute disponibilité | point de défaillance unique, bascule, quorum, temps de reprise |
| Passage à l'échelle | horizontal ou vertical, état partagé, démarrage à froid |
| Stockage | bloc, fichier, objet, durabilité, cohérence, coût de sortie |
| IAM | identité, rôle, politique, moindre privilège, jeton temporaire |
| Systèmes distribués | horloge, idempotence, exactement-une-fois, partition réseau |

**Toujours montrer** : où se termine le TLS, et ce que voit l'application
derrière le proxy.

---

## 4. Intelligence artificielle

**La question de fond** : *qu'est-ce qui est calculé, qu'est-ce qui est stocké,
et combien coûte un appel ?*

| Sujet | Relances à couvrir |
|---|---|
| Modèle | architecture, taille, quantification, mémoire nécessaire |
| Token | découpage, fenêtre de contexte, coût entrée/sortie |
| Embedding | dimension, distance, normalisation, modèle utilisé |
| RAG | découpage, indexation, recherche, reclassement, ce qui entre dans l'invite |
| Agent | boucle, outils, état, condition d'arrêt, échec en cascade |
| Inférence | lot, cache de contexte, débit, latence du premier jeton |
| Entraînement | ajustement fin, LoRA, jeu de données, surapprentissage |
| Évaluation | jeu de test, métrique, juge, variance entre exécutions |
| Déploiement | GPU ou CPU, mise à l'échelle, file d'attente, limite de débit |

**Toujours montrer** : l'invite réellement envoyée, et ce que coûte un appel.

---

## 5. Cybersécurité et hacking éthique

**La question de fond** : *quelle est la condition exacte d'exploitation, et
quelle défense tient vraiment ?*

| Sujet | Relances à couvrir |
|---|---|
| Vulnérabilité | condition d'exploitation, prérequis, impact, portée |
| Injection | où la donnée devient code, l'échappement qui marche, celui qui ne marche pas |
| Contrôle d'accès | vérification côté serveur, appartenance de la ressource, IDOR |
| Authentification | hachage, sel, facteur, session, révocation |
| Déni de service | couche visée, amplification, coût pour l'attaquant |
| Durcissement | surface d'attaque, moindre privilège, valeurs par défaut sûres |
| Journalisation | ce qu'on garde, ce qu'on ne garde jamais, rétention |
| Test de sécurité | périmètre écrit, outil, faux positif, preuve |
| Réponse à incident | contenir, préserver, corriger, restaurer, notifier |

**Les trois règles non négociables**

1. Toute manipulation se fait sur une machine dont on est propriétaire, ou sur
   une plateforme d'entraînement qui l'autorise par écrit.
2. La défense est dans la même fiche que l'attaque, jamais dans une suite.
3. Pas de charge utile prête à l'emploi contre une cible réelle, pas de
   technique d'évasion de détection, pas de ciblage de masse.

**Toujours montrer** : la ligne de code vulnérable, la même ligne corrigée, et
ce qu'on voit dans les journaux.

---

## 6. Quand le sujet est à cheval

Beaucoup de sujets touchent plusieurs domaines. Le rate limiting est à la fois
du développement, du réseau et de la sécurité.

La règle : prendre le domaine **qui pose le plus de questions de relance**, et
emprunter aux autres ce qui manque. Le domaine choisi va dans la métadonnée
`mentor-domaine`.

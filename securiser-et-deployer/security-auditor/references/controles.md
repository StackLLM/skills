# La matrice des contrôles

Ce qu'on passe en revue, domaine par domaine. **Un filet, pas une commande** :
un domaine absent du projet ne produit pas de section.

Chaque ligne se lit comme une question à poser au code, pas comme une case à
cocher.

---

## 1. Authentification — prouver qui on est

| Question au code | Ce qui alerte |
|---|---|
| Comment un mot de passe est-il stocké ? | en clair, MD5, SHA-1, SHA-256 seul, sans sel |
| Quel algorithme de hachage ? | tout ce qui n'est pas prévu pour les mots de passe |
| Le mot de passe a-t-il une longueur minimale ? | aucune règle, ou des règles absurdes de composition |
| Combien d'essais avant blocage ? | aucun blocage, aucun ralentissement |
| Le jeton dure combien de temps ? | plusieurs jours sans renouvellement |
| Le secret du jeton vient d'où ? | une valeur par défaut, une valeur dans le code |
| Peut-on révoquer un jeton ? | non, il reste valable jusqu'à expiration |
| Le mot de passe oublié : le lien expire ? | non, ou réutilisable |
| L'inscription est-elle ouverte ? | oui, sur une application censée être interne |

### Hachage, chiffrement, encodage — trois choses différentes

À expliquer dès que le sujet apparaît. C'est la confusion la plus fréquente.

| | Ce que c'est | Peut-on revenir en arrière ? | Pour quoi |
|---|---|---|---|
| **Encodage** | changer la forme d'écriture (base64) | oui, sans clé | transporter, jamais protéger |
| **Chiffrement** | brouiller avec une clé | oui, avec la clé | des données qu'on devra relire |
| **Hachage** | empreinte à sens unique | non | des mots de passe |

> *Un mot de passe haché, c'est une empreinte digitale : elle identifie sans
> permettre de reconstruire la personne.*

Base64 **n'est pas** une protection. Voir un mot de passe en base64 dans une
base, c'est voir un mot de passe en clair.

Pour les mots de passe, il faut un algorithme **lent et salé**, conçu pour ça :
argon2, bcrypt, scrypt, PBKDF2. Vérifier la recommandation en vigueur plutôt
que de citer des paramètres de mémoire.

---

## 2. Autorisation — prouver qu'on a le droit

Le domaine qui produit le plus de failles graves, et le plus souvent oublié.

| Question au code | Ce qui alerte |
|---|---|
| L'adresse vérifie-t-elle le **propriétaire** de la ressource ? | elle vérifie seulement que l'utilisateur est connecté |
| La requête filtre-t-elle sur l'utilisateur ? | elle cherche par identifiant seul |
| Les adresses d'administration sont-elles protégées côté serveur ? | le bouton est caché, l'adresse est ouverte |
| Les rôles sont-ils vérifiés à chaque appel ? | seulement à la connexion |
| Un utilisateur peut-il changer son propre rôle ? | le champ passe dans le corps de la requête |
| Les fichiers sont-ils servis avec un contrôle ? | dossier public, nom devinable |
| Les exports respectent-ils les filtres de l'écran ? | l'export sort tout |

**Le test simple, à faire sur chaque ressource :** deux comptes, A et B.
A ouvre sa ressource, remplace le numéro par celui de B. Si ça s'affiche, le
problème est confirmé.

Répondre « 404 » et non « 403 » quand la ressource existe mais n'appartient pas
à la personne : un 403 confirme qu'elle existe.

---

## 3. Les adresses de l'API

| Question au code | Ce qui alerte |
|---|---|
| Quelles adresses sont accessibles sans connexion ? | plus que la connexion et les pages publiques |
| Les données entrantes sont-elles validées ? | on fait confiance au corps de la requête |
| La sortie contient-elle plus que nécessaire ? | l'objet complet de la base, avec le hachage du mot de passe |
| Les anciennes versions sont-elles encore servies ? | oui, sans les contrôles récents |
| Y a-t-il des adresses de debug ? | actives en production |
| Les webhooks vérifient-ils la signature de l'appelant ? | non, n'importe qui peut appeler |
| La pagination a-t-elle une limite haute ? | demander 100 000 lignes fonctionne |
| Y a-t-il une limite de débit ? | aucune |

---

## 4. Injection et données non fiables

| Question au code | Ce qui alerte |
|---|---|
| Les requêtes SQL sont-elles paramétrées ? | concaténation avec une valeur de l'utilisateur |
| Les commandes système reçoivent-elles des données utilisateur ? | oui, sans liste blanche |
| Un chemin de fichier vient-il de l'utilisateur ? | oui, sans normalisation — `../` passe |
| Du HTML est-il construit depuis une saisie ? | insertion directe dans la page |
| Une valeur est-elle évaluée comme du code ? | `eval`, `exec`, désérialisation non sûre |
| Les modèles côté serveur reçoivent-ils du brut ? | oui, injection de gabarit possible |

Vérifier **d'où vient la valeur** avant d'alerter. Une concaténation avec une
constante interne n'est pas une injection.

---

## 5. Fichiers et uploads

| Question au code | Ce qui alerte |
|---|---|
| Le type de fichier est-il vérifié par son contenu ? | seulement par l'extension, ou par l'en-tête envoyé |
| La taille est-elle limitée ? | non |
| Le nom est-il conservé tel quel ? | oui — `../` et caractères spéciaux passent |
| Où atterrit le fichier ? | dans un dossier servi publiquement |
| Le dossier peut-il exécuter ? | oui |
| Le téléchargement vérifie-t-il le droit ? | non, l'adresse suffit |

---

## 6. Secrets et configuration

Procédure complète : [secrets.md](secrets.md).

| Question au code | Ce qui alerte |
|---|---|
| Des clés sont-elles dans le code ? | oui, surtout côté frontend |
| Le `.env` est-il dans le dépôt ? | oui, ou absent du `.gitignore` |
| L'historique Git contient-il des secrets ? | oui |
| Des secrets apparaissent-ils dans les journaux ? | jeton, mot de passe, en-tête complet |
| Y a-t-il des valeurs par défaut dangereuses ? | `SECRET_KEY = "changeme"` utilisé si la variable manque |
| Le mode debug est-il coupé en production ? | non — la page d'erreur montre le code et la config |

---

## 7. Transport, en-têtes, navigateur

| Question au code | Ce qui alerte |
|---|---|
| Tout passe-t-il en HTTPS ? | des appels en clair, une redirection absente |
| La configuration CORS est-elle ouverte ? | `*` avec des identifiants autorisés |
| Les cookies de session sont-ils protégés ? | sans `HttpOnly`, `Secure`, `SameSite` |
| Les en-têtes de sécurité sont-ils posés ? | pas de CSP, pas de `X-Content-Type-Options` |
| Le serveur annonce-t-il sa version ? | oui, dans les en-têtes |

---

## 8. Données personnelles

| Question au code | Ce qui alerte |
|---|---|
| Quelles données personnelles sont stockées ? | plus que nécessaire |
| Sont-elles chiffrées au repos quand c'est justifié ? | non, sur des données sensibles |
| Apparaissent-elles dans les journaux ? | oui |
| Y a-t-il une durée de conservation ? | aucune |
| Peut-on supprimer un utilisateur et ses données ? | non |
| Les sauvegardes sont-elles protégées ? | accès non restreint |

Rappeler que ce point a aussi une dimension réglementaire, sans jouer au
juriste : signaler, ne pas trancher.

---

## 9. Dépendances

| Question au projet | Ce qui alerte |
|---|---|
| Les versions sont-elles figées ? | non, tout en `^` ou en `latest` |
| Les alertes connues sont-elles traitées ? | des vulnérabilités critiques ouvertes |
| Le code appelle-t-il la partie vulnérable ? | à vérifier avant d'alerter |
| Y a-t-il des paquets inutilisés ? | oui, surface inutile |
| Des paquets viennent-ils d'une source inhabituelle ? | dépôt privé non documenté, nom proche d'un paquet connu |

Une alerte d'outil **n'est pas** un constat. Vérifier que le code utilise la
fonction touchée avant de monter le niveau.

---

## 10. Dépôt, CI/CD, infrastructure

| Question au projet | Ce qui alerte |
|---|---|
| Les secrets de CI sont-ils dans les fichiers de workflow ? | oui, en clair |
| Les workflows s'exécutent-ils sur des PR extérieures ? | avec accès aux secrets |
| Le conteneur tourne-t-il en root ? | oui |
| L'image part-elle d'une base à jour ? | non |
| Les ports sont-ils tous exposés ? | la base de données est joignable de l'extérieur |
| Le dépôt est-il public ? | alors tout l'historique l'est aussi |
| Qui a accès au dépôt ? | des comptes qui ne devraient plus |

---

## Correspondance avec OWASP

À citer **après** l'explication simple, jamais à la place.

| Domaine ci-dessus | OWASP Top 10 | OWASP API |
|---|---|---|
| Autorisation | A01 — contrôle d'accès | API1, API5 |
| Hachage, chiffrement | A02 — défaillance cryptographique | — |
| Injection | A03 — injection | API8 |
| Architecture | A04 — conception non sûre | — |
| Configuration, secrets, CORS | A05 — mauvaise configuration | API8 |
| Dépendances | A06 — composants vulnérables | — |
| Authentification, sessions | A07 — identification défaillante | API2 |
| CI/CD, intégrité | A08 — intégrité des données et du logiciel | — |
| Journaux | A09 — journalisation insuffisante | API9 |
| Appels sortants | A10 — falsification de requête | API7 |
| Débit, pagination | — | API4 |

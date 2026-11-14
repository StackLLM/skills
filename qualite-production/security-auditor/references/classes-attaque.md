# Les classes d'attaque

Chaque classe est **un angle de recherche**, pas une case à cocher. On en prend
celles qui existent vraiment dans le projet, et on en ajoute s'il en manque.

> Adapté de la skill `security-audit` de Cloudflare (MIT). Voir `ORIGINES.md`.

## Choisir les classes

Après avoir reconstruit l'architecture (temps 2), ouvrir cette liste et cocher
ce qui s'applique. Une application web classique en utilise 5 ou 6. Un gros
projet se découpe : une passe par sous-système.

| Le projet contient… | Classes à ouvrir |
|---|---|
| Un site, une API, des comptes | Injection, Contrôle des accès, Web et authentification, Logique métier, Les évidences |
| Du JavaScript dans le navigateur | Côté client |
| Des fichiers envoyés par les utilisateurs | Ressources et fichiers |
| Plusieurs clients dans la même base | Cloisonnement des données |
| Un appel à un modèle d'IA, un agent, un MCP | IA et modèles de langage |
| Un déploiement, des conteneurs, du cloud | Cloud et déploiement |
| Des dépendances, une CI, des mises à jour | Chaîne logicielle |
| Un travail lourd déclenché par l'utilisateur | Épuisement des ressources |
| Du C, du C++, du Rust `unsafe`, du binaire | Mémoire et binaire |
| Une application de bureau ou mobile | Bureau, mobile et IPC local |

---

## Injection

Suivre une donnée non fiable, de son entrée jusqu'à l'endroit dangereux où elle
finit. L'endroit dangereux dépend du projet :

| Type de projet | Les endroits dangereux |
|---|---|
| Site web | requêtes SQL, sortie HTML, commandes système, moteurs de gabarits, chemins de fichiers, redirections, désérialisation |
| Bibliothèque | toute fonction qui traite la donnée de l'appelant sans la valider |
| Outil en ligne de commande | construction de commandes, chemins, variables d'environnement |
| Service | construction de requêtes, sérialisation de messages, journaux, LDAP |

**Ne pas s'arrêter au chemin direct.** Les trois pièges les plus courants :

1. **L'injection indirecte.** La donnée est stockée proprement, puis relue plus
   tard par un autre bout de code qui, lui, la met dans un endroit dangereux.
2. **L'injection par les noms.** Pas seulement par les valeurs : les noms de
   champs, les clés, les en-têtes, les métadonnées.
3. **L'injection dans les systèmes secondaires.** Journaux, caches, index de
   recherche, outils de statistiques.

---

## Contrôle des accès

La vraie question n'est pas « le contrôle existe-t-il », mais « est-ce **le bon**
contrôle, sur **la bonne** ressource, par **le bon** mécanisme ».

- Existe-t-il un autre chemin vers le même changement, protégé par un contrôle
  plus faible ?
- Un champ du corps de la requête peut-il écraser ce que le contrôle voulait
  interdire ?
- Y a-t-il des adresses qui vérifient qu'on est connecté, mais pas qu'on a le
  droit ?
- La même ressource a-t-elle plusieurs chemins d'accès, avec des contrôles
  différents ?
- Les opérations en lot — import, export, suppression multiple — vérifient-elles
  le droit **sur chaque élément** ?

---

## Ressources et fichiers

- **Traversée de chemin** : lire ou écrire en dehors du dossier prévu, y compris
  par un lien symbolique, une séquence encodée, un octet nul.
- **SSRF** : faire chercher au serveur une adresse choisie par l'attaquant. Y
  compris après une redirection, ou via une différence entre deux analyseurs
  d'URL.
- **Désérialisation non sûre**, extraction d'archive (`zip slip`), fichiers
  temporaires.
- **Course entre la vérification et l'usage** : le fichier change entre le
  moment où on le contrôle et le moment où on s'en sert.

---

## Chiffrement et secrets

- Hasard faible pour une valeur qui doit être imprévisible : jeton, clé, nonce.
- Secrets en dur, secrets dans les journaux, dans les messages d'erreur, dans
  une URL, dans une réponse visible du navigateur.
- Dérivation de clé cassée, signature non vérifiée, nonce réutilisé.
- Comparaison de secret sensible au temps de réponse.
- Mauvais usage des primitives : mode ECB, chiffrement sans authentification,
  vecteur d'initialisation fixe.
- **Que se passe-t-il quand l'opération échoue ?** Le chemin d'erreur retombe-t-il
  sur « pas de chiffrement du tout » ?

---

## Logique métier

Les failles que les outils ne trouvent jamais, et qui font les vrais incidents.
Pour chaque parcours important :

| Piste | La question à se poser |
|---|---|
| Machine à états | Peut-on sauter une étape ? Revenir en arrière ? Rejouer un parcours terminé ? Si l'étape 2 sur 3 échoue, l'étape 1 est-elle annulée ? |
| Courses | Deux opérations en même temps produisent-elles un état invalide ? Double paiement, double validation, mise à jour perdue |
| Nombres | Valeurs négatives, zéro, dépassement, perte de précision, texte converti en nombre |
| Confiance implicite | Une donnée venue de la base, de la config ou d'un autre composant, supposée saine « parce qu'on l'a validée à l'entrée ». Et si un autre chemin l'avait écrite ? |
| Temps | Expiration, planification, fenêtres de limitation, décalage d'horloge. Que se passe-t-il à la seconde exacte de la limite ? |
| Valeurs par défaut | Quelle est la posture quand la config manque ? Quand une option est désactivée ? Quand une dépendance est injoignable ? Pendant une migration ? |

---

## Détournement de fonctionnalité et fuite de données

Des fonctions légitimes, utilisées autrement. Chercher le défaut de conception,
pas seulement le défaut de code.

- **L'export comme exfiltration.** Un utilisateur peu privilégié peut-il
  déclencher un export, une sauvegarde ou un instantané qui contient plus que ce
  qu'il a le droit de voir ? Les brouillons ? Les éléments supprimés ?
  L'historique des versions ?
- **L'import comme injection.** L'import peut-il écraser des données
  existantes ? Créer des enregistrements qui échappent à la validation
  habituelle ? Respecte-t-il le même modèle de droits que l'interface ?
- **La recherche comme oracle.** Une requête peut-elle révéler qu'un contenu
  existe, sans y donner accès ? Un tri sur un champ caché révèle-t-il ses
  valeurs par l'ordre des résultats ?
- **L'énumération par les effets de bord.** Les messages d'erreur diffèrent-ils
  entre « n'existe pas » et « pas le droit » ? Les temps de réponse ? Les codes
  HTTP ? Peut-on énumérer les comptes par le mot de passe oublié ou
  l'inscription ?
- **La fuite par la prévisualisation.** Un jeton d'aperçu ouvre-t-il un seul
  élément, ou plus ? Un brouillon est-il trouvable par la recherche, un flux
  RSS, un plan du site ? Un en-tête de cache peut-il faire servir du contenu
  privé par un CDN ?
- **Le webhook comme SSRF.** L'utilisateur peut-il donner une adresse de rappel
  que le serveur ira chercher ? Est-elle contrôlée contre les réseaux internes ?
  Et après une redirection ?

---

## Chaînes et frontières de confiance

Un comportement anodin pris seul devient une faille quand un autre composant
s'appuie dessus en supposant plus.

- **Trous entre composants.** A valide et passe à B. Comparer **exactement** ce
  que A garantit avec ce que B suppose : troncature, conversion de type,
  normalisation, périmètre du client.
- **Usage au second degré.** Une donnée sûre au stockage devient dangereuse plus
  tard : un nom de champ devient un chemin JSON, un identifiant lisible devient
  un chemin de fichier, un texte échappé entre dans un rendu brut.
- **Les droits qui grossissent.** Un jeton, une clé d'API, une extension ou un
  agent gagnent des droits après délégation, renouvellement, mise en cache ou
  changement de rôle. Nommer l'opération précise que le résultat ne devrait pas
  pouvoir faire.
- **Retour en arrière.** Restauration, annulation, rétablissement d'une version :
  appliquent-ils le propriétaire, la validation et les droits **actuels** ?

---

## Côté client

Pour tout ce qui tourne dans le navigateur : application monopage, extension,
webview, service worker.

- XSS par le DOM : une donnée écrite dans la page sans échappement.
- Pollution de prototype.
- `postMessage` qui ne vérifie pas l'origine de l'émetteur.
- Stockage navigateur (`localStorage`) utilisé pour un jeton de session.
- CORS trop large, surtout `*` combiné avec `Access-Control-Allow-Credentials`.
- Cookies sans `HttpOnly`, `Secure` ou `SameSite`.
- Ce que le code téléchargé par le navigateur contient : clés, adresses
  internes, commentaires, cartes de sources.

---

## Web et authentification

- Sessions : création, renouvellement, expiration, déconnexion réelle côté
  serveur.
- Jetons JWT : algorithme accepté, signature vérifiée, `exp` contrôlé, secret.
- OAuth et OIDC : `state`, `redirect_uri` contrôlée, code à usage unique.
- Récupération de compte et liaison de comptes : le chemin le plus souvent
  oublié, et le plus rentable pour l'attaquant.
- Deuxième facteur : peut-on le contourner par un autre chemin de connexion ?
- Clés d'API : portée, rotation, révocation.
- CSRF sur les actions qui changent l'état.
- Différences entre le proxy inverse et l'application sur l'interprétation d'une
  requête HTTP.

---

## Cloisonnement des données

Pour toute application qui sert plusieurs clients, équipes ou organisations.

- Chaque requête porte-t-elle le périmètre du client, **côté serveur**, et pas
  seulement dans le filtre de l'interface ?
- Les caches et les index de recherche sont-ils cloisonnés eux aussi ?
- Les liens entre objets peuvent-ils traverser deux clients ?
- Les exports, sauvegardes, migrations et restaurations respectent-ils le
  cloisonnement ?
- La suppression supprime-t-elle vraiment ? Dans les sauvegardes aussi ?

---

## Cloud et déploiement

- Droits de la machine ou du conteneur : le moindre privilège est-il appliqué ?
- Infrastructure déclarée en code : qu'ouvre-t-elle vraiment ?
- Conteneurs : utilisateur `root`, montages, secrets passés en variables
  visibles dans l'image.
- Entrée réseau : qui peut atteindre quoi, depuis l'extérieur ?
- Configuration au démarrage : que vaut la posture quand une variable manque ?

> **Prudence.** Ces contrôles vivent souvent hors du dépôt. S'ils sont absents du
> code, ne pas conclure qu'ils sont absents en production. Statut
> « Non vérifiable », avec le fait précis qui manque.

---

## Chaîne logicielle

- Les dépendances sont-elles figées ? Le fichier de verrouillage est-il commité ?
- Des failles connues dans l'arbre des dépendances — et le code appelle-t-il
  vraiment la partie vulnérable ?
- La CI : qui peut lancer un travail ? Avec quels secrets ? Un contributeur
  extérieur peut-il déclencher un travail privilégié ?
- La publication : qui signe, qui promeut, qui peut remplacer une version ?
- Les mises à jour automatiques et les extensions : par où entrent-elles ?

---

## IA et modèles de langage

Pour les agents, les RAG, les serveurs MCP, tout ce qui assemble un prompt.

- **Injection de prompt indirecte** : un document, une page ou un ticket lus par
  le modèle contiennent des instructions. Elles ne sont **jamais** des ordres.
- **Mémoire empoisonnée** : ce que le modèle retient d'une session sert dans une
  autre.
- **Liaison action / autorisation** : l'outil que le modèle appelle vérifie-t-il
  les droits de l'utilisateur final, ou ceux du service ?
- **Schéma d'outil** : un paramètre libre peut-il devenir une commande, un
  chemin, une URL ?
- **Sortie du modèle** : est-elle rendue en HTML brut ? Exécutée ? Mise dans une
  requête ?

---

## Épuisement des ressources

Une action peu coûteuse pour l'attaquant, très coûteuse pour vous.

- Un travail lourd déclenché sans compte, ou sans limite par compte.
- Une entrée qui fait exploser le temps de calcul : expression régulière, image,
  archive, requête imbriquée.
- Une quota payante consommée par un visiteur : appel d'IA, SMS, envoi d'e-mail.
- Connexions, fils d'exécution, files : peut-on les saturer ?

> **Jamais de test de charge sur un service en ligne ou partagé.** On lit le code
> et on raisonne. Voir `execution-sure.md`.

---

## Mémoire et binaire

Seulement si le projet contient du C, du C++, du Rust `unsafe`, du FFI, un
analyseur de format, un chargeur binaire ou du firmware.

Dépassement de tampon, usage après libération, dépassement d'entier, différences
d'ABI, courses entre fils d'exécution, interfaces privilégiées.

---

## Bureau, mobile et IPC local

Liens profonds, ponts webview, composants exportés, assistants privilégiés,
démons locaux, sockets Unix, D-Bus, Binder, XPC.

La question : **qui d'autre, sur la même machine, peut parler à ce composant ?**

---

## Les évidences

Cette passe n'a pas besoin d'être maligne. Elle doit être **complète et
littérale**. Elle rattrape ce que tout le monde suppose déjà vérifié.

- [ ] Mots de passe, clés, jetons en dur dans le code ?
- [ ] Commentaires `TODO`, `FIXME`, `HACK` qui parlent de sécurité ?
- [ ] Le mode debug est-il bien fermé ? Peut-on le rallumer par une variable,
      un paramètre d'URL, un en-tête ?
- [ ] Des identifiants de test ou d'exemple qui marchent en production ?
- [ ] Une adresse `/debug`, `/admin`, `/status`, `/metrics`, `/env`, `/config`
      sans protection ?
- [ ] Des fichiers `.env`, `credentials.json`, `*.pem`, `*.key` dans le dépôt ?
- [ ] Le `.gitignore` couvre-t-il vraiment les secrets, les uploads, la config
      locale ?
- [ ] Les dépendances sont-elles figées ? Des failles connues ?
- [ ] Des `eval`, `exec`, `child_process`, `Function()` avec une entrée
      dynamique ?
- [ ] CORS à `*` ? Combiné avec les identifiants ?
- [ ] Cookies sans `HttpOnly`, `Secure`, `SameSite` ?
- [ ] Des redirections ouvertes — paramètres `redirect`, `next`, `url`, `goto` ?
- [ ] HTTPS imposé partout ?
- [ ] Les erreurs de production renvoient-elles une trace, un chemin interne,
      une erreur SQL ?

> **Un drapeau n'est pas un constat.** Si un cookie n'a pas `HttpOnly`, vérifier
> d'abord ce qu'il contient et si le JavaScript a besoin de le lire. Tracer
> l'impact avant d'écrire quoi que ce soit.

---

## La passe libre

Une passe sans catégorie, pour ce qui tombe entre les classes. Elle garde les
mêmes exigences que les autres : frontière franchie, résultat concret.

- Quel est le code le plus bizarre du projet ? Pourquoi existe-t-il ?
- Quelles fonctions semblent à moitié finies, expérimentales, rajoutées après
  coup ? Ce sont celles qui ont été le moins relues.
- Que se passe-t-il si on appelle l'API comme l'interface ne le fait jamais ?
  L'interface contraint l'utilisateur ; l'API, non.
- Des adresses, paramètres ou en-têtes non documentés ?
- Que donne le mélange de deux fonctions jamais prévues ensemble ? Traduction +
  aperçu + cache. Import + extensions + webhooks.
- L'historique Git : un correctif de sécurité annulé, un contrôle commenté, un
  secret ajouté puis retiré ?
- Quelles hypothèses le code fait-il sur son environnement ? Que la base est
  locale, que l'horloge est juste, que le DNS est fiable ?
- Les tests : que **ne** testent-ils **pas** ? Comparer les cas limites prévus
  avec ceux qui ne le sont pas.

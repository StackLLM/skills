# Production — ce qu'un service doit avoir dès le premier jour

Les grandes équipes ne rajoutent pas la santé, les limites et les journaux
« plus tard ». Ils font partie du premier commit, parce que c'est le jour de
la première panne qu'on en a besoin, et ce jour-là il est trop tard.

Repères : OWASP Top 10:2025, OWASP ASVS 5.0 (niveau 1 minimum, niveau 2 pour
un SaaS avec des données de clients), Google SRE (les quatre signaux).

## Sommaire

1. La santé (health checks)
2. Les limites d'essais (rate limiting)
3. Les en-têtes de sécurité
4. Les comptes et les sessions
5. Les journaux
6. Les métriques et les alertes
7. Les données : migrations, sauvegarde, restauration
8. Démarrage et arrêt propres
9. Les dépendances
10. La liste avant la première mise en ligne

---

## 1. La santé

Deux adresses, deux questions différentes :

| Adresse | Question | Répond 200 quand | Qui l'appelle |
|---|---|---|---|
| `GET /sante/vivant` | le processus tourne-t-il ? | toujours, si le serveur répond | Docker (`HEALTHCHECK`), l'orchestrateur : s'il échoue, on redémarre |
| `GET /sante/pret` | peut-il servir des requêtes ? | la base répond, le disque est inscriptible, la config est valide | le répartiteur de charge, la surveillance extérieure |

Règles :

- `/sante/vivant` ne touche **rien** (ni base, ni réseau) : il doit rester
  rapide même quand tout va mal, sinon on redémarre un serveur qui n'est pas en cause.
- `/sante/pret` renvoie **503** si une dépendance manque, avec un corps court :
  `{"etat": "panne", "controles": {"base": "ok", "disque": "panne"}}`.
  Jamais de détail sensible (chemins complets, versions précises, messages d'erreur bruts).
- Pas de limite d'essais sur ces deux adresses, pas de journal par appel
  (elles sont appelées toutes les 30 secondes).

**Contrôles réguliers** (comme la « santé du site » du CMS La Fourchette) : un
contrôle toutes les 15 minutes du service publié (pages, poids, certificat,
liens externes), un état vert / orange / rouge, une alerte quand il change.

**La limite que tout le monde oublie** : un serveur arrêté ne peut pas
prévenir de sa propre panne. Il faut une **surveillance extérieure** (Uptime
Kuma, Better Stack, UptimeRobot…) qui appelle `/sante/pret` toutes les minutes
et envoie un mail ou un message. À brancher à la mise en ligne.

---

## 2. Les limites d'essais

Sans limite, un robot essaie 10 000 mots de passe par minute, ou remplit la
base de faux formulaires.

| Ce qu'on limite | Par quoi | Exemple de seuil |
|---|---|---|
| Connexion | adresse + identifiant, adresse seule, identifiant seul | 5 / 20 / 200 essais par 15 min |
| Formulaires publics (contact, réservation) | adresse | 5 par heure |
| Inscription, mot de passe oublié | adresse, adresse mail | 3 par heure |
| API d'un SaaS | compte ou clé d'API | selon l'offre ; en-têtes `RateLimit-*` |
| Envoi de fichiers | compte | taille et nombre par jour |

Règles :

- Réponse **429** avec l'en-tête `Retry-After`, et un message qui dit quand réessayer.
- **Un essai réussi rend l'essai compté** : le vrai utilisateur n'est pas puni
  pour une faute de frappe d'avant.
- Les compteurs survivent au redémarrage (base) ; avec **plusieurs instances**,
  ils vivent dans un stockage partagé (Redis, PostgreSQL), sinon chaque instance
  compte de son côté et la limite est multipliée.
- **Derrière un proxy** (Caddy, tunnel, hébergeur), l'adresse du visiteur est
  dans `X-Forwarded-For`. On ne la lit **que** si le serveur est réellement
  derrière un proxy de confiance (variable `…_PROXY=1`), sinon n'importe qui
  choisit son adresse et contourne la limite.
- Le seuil le plus large (par identifiant) reste haut : un inconnu ne doit pas
  pouvoir bloquer le vrai client à volonté.

---

## 3. Les en-têtes de sécurité

Posés par le serveur de l'application (pas seulement par le proxy) : ils sont
les mêmes en local et en ligne, et un test les vérifie.

| En-tête | Valeur de départ |
|---|---|
| `Content-Security-Policy` | `default-src 'self'` puis on ouvre seulement ce qui sert. En mode `-Report-Only` d'abord, puis bloquante |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` (seulement servi en HTTPS) |
| `X-Content-Type-Options` | `nosniff` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=()` |
| `X-Frame-Options` / `frame-ancestors` | `DENY` ou `'self'` |
| `Cross-Origin-Opener-Policy` | `same-origin` |

- Espace d'administration : politique plus stricte que le site public, et
  `Cache-Control: no-store` sur ses réponses.
- **CORS** : liste des origines autorisées, lue dans la config. Jamais `*` avec des cookies.
- Les requêtes qui modifient (POST, PUT, DELETE) vérifient l'**origine**
  (en-tête `Origin`) : protection contre la falsification de requête (CSRF).
- Tailles max sur chaque corps de requête ; **413** au-delà.

---

## 4. Les comptes et les sessions

- **Accès par jeton** (une équipe, pas de comptes) : le jeton fait **32 caractères aléatoires au moins**
  (`secrets.token_urlsafe(32)`), il est comparé en temps constant, et les routes qu'il ouvre ont une
  limite d'essais. Un jeton court « facile à retenir » se trouve en quelques secondes par un robot.
- Mots de passe hachés avec **argon2id** (ou bcrypt à défaut). Jamais en clair,
  ni en base, ni dans `.env`, ni dans les journaux.
- Session : cookie `HttpOnly`, `Secure`, `SameSite=Lax` (ou `Strict` pour l'admin),
  durée limitée, renouvelée à la connexion. Jeton aléatoire long (≥ 128 bits).
- Déconnexion = la session est supprimée côté serveur, pas seulement le cookie.
- Changement de mot de passe = toutes les autres sessions se ferment.
- Messages de connexion identiques que le compte existe ou non
  (« Identifiant ou mot de passe incorrect »).
- **Autorisation vérifiée côté serveur à chaque requête** (OWASP A01). Cacher un
  bouton dans l'interface ne protège rien.
- SaaS multi-clients : **chaque requête en base filtre par client** ; un test
  vérifie qu'un client ne lit jamais les données d'un autre.

---

## 5. Les journaux

- **Une ligne par requête**, structurée (JSON en production, lisible en local) :
  heure UTC, niveau, identifiant de requête, méthode, route, statut, durée en ms.
- **Identifiant de requête** : repris de `X-Request-Id` s'il vient d'un proxy
  de confiance, sinon généré ; renvoyé dans la réponse. Le support retrouve
  l'erreur d'un utilisateur en une recherche.
- **Niveaux** : `debug` (local seulement), `info` (événements normaux),
  `warning` (anormal mais traité), `error` (une action a échoué).
- **Jamais dans un journal** : mot de passe, jeton, clé, cookie, contenu de
  formulaire complet, numéro de carte. Masquer avant d'écrire.
- Les journaux vont sur la **sortie standard** : c'est Docker ou l'hébergeur
  qui les range (Twelve-Factor, principe 11). Pas de fichier de journal dans le conteneur.
- Les événements de sécurité ont leur propre ligne : connexion réussie, échec,
  blocage, changement de mot de passe, action d'administration (OWASP A09).

---

## 6. Les métriques et les alertes

Les quatre signaux (Google SRE) :

| Signal | Mesure | Alerte quand |
|---|---|---|
| **Latence** | durée des requêtes (p50, p95) | p95 > seuil fixé pendant 5 min |
| **Trafic** | requêtes par minute | chute brutale (le site ne reçoit plus rien) |
| **Erreurs** | part des réponses 5xx | > 1 % pendant 5 min |
| **Saturation** | disque, mémoire, CPU | disque > 80 % |

Pour un petit projet, la surveillance extérieure + les journaux + le contrôle
du disque dans `/sante/pret` suffisent. On ajoute Prometheus / OpenTelemetry
quand le projet a plusieurs instances ou des clients payants.

Une alerte doit dire **quoi faire**. Une alerte qui sonne pour rien est une
alerte qu'on finit par ignorer.

---

## 7. Les données

- **Migrations versionnées** (voir `normes-code.md`, section 6).
- **Sauvegarde automatique** quotidienne, gardée hors de la machine (au moins
  7 jours + 4 semaines). SQLite : copie cohérente (`VACUUM INTO` ou
  `.backup`), jamais une copie brute du fichier pendant qu'il tourne.
- **La restauration est testée.** Une sauvegarde jamais restaurée n'est pas
  une sauvegarde. Le script `restaurer.sh` existe et a été lancé au moins une fois.
- Les données du client (base, contenu, fichiers envoyés) vivent sur **un seul
  disque de données** monté en volume : c'est lui qu'on sauvegarde.
- RGPD : savoir quelles données personnelles on garde, combien de temps, et
  comment les supprimer sur demande.

---

## 8. Démarrage et arrêt propres

- Au démarrage : lire et valider la config → ouvrir la base → migrations →
  écouter. Si une étape échoue : message clair, code de sortie ≠ 0.
- À l'arrêt (`SIGTERM`, envoyé par Docker) : arrêter d'accepter, finir les
  requêtes en cours (délai max ~10 s), fermer la base, sortir. Sinon une
  écriture peut être coupée en deux à chaque déploiement.
- Le serveur écoute sur `0.0.0.0` dans un conteneur, sur `127.0.0.1` sur un
  poste ou derrière un proxy local.

---

## 9. Les dépendances

- Fichier de verrouillage commité (`package-lock.json`, `uv.lock`) ; la CI
  installe **exactement** ces versions (`npm ci`, `uv sync --frozen`).
- Dependabot (ou Renovate) ouvre les mises à jour chaque semaine ; la CI les vérifie.
- `npm audit` / `pip-audit` dans la CI, en avertissement d'abord.
- Les actions GitHub sont épinglées sur une version majeure vérifiée
  (`gh api repos/actions/checkout/releases/latest`).
- Image Docker de base précise (`node:24.14.0-bookworm-slim`), jamais `latest`.
- OWASP A03:2025 (chaîne d'approvisionnement) : chaque dépendance est du code
  qui tourne avec nos droits. On en ajoute peu, on les choisit maintenues.

---

## 10. La liste avant la première mise en ligne

- [ ] `/sante/vivant` et `/sante/pret` répondent ; `HEALTHCHECK` dans l'image
- [ ] surveillance extérieure branchée, alerte reçue au moins une fois (test)
- [ ] limites sur connexion et formulaires, testées
- [ ] en-têtes de sécurité présents, vérifiés par un test
- [ ] aucun secret dans Git (historique compris) ; `.env` hors du dépôt
- [ ] mots de passe en empreinte argon2id
- [ ] journaux structurés, sans secret, avec identifiant de requête
- [ ] arrêt propre sur `SIGTERM`
- [ ] sauvegarde automatique + restauration testée
- [ ] CI verte sur le commit livré
- [ ] retour arrière possible (image précédente, version précédente du site)

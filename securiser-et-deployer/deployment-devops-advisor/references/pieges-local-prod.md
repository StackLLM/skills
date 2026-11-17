# « Ça marche en local »

Le catalogue des raisons pour lesquelles une application qui tourne
parfaitement sur un poste tombe une fois déployée.

Chaque ligne se lit : **le symptôme**, puis **la cause**, puis **le correctif**.

Le script `verifier_prod.py` relève une partie de ces motifs. Il en reste qui
demandent de lire le code.

---

## 1. Les réglages

### L'adresse écrite en dur

**Symptôme** — le site s'affiche, mais aucune donnée n'arrive. La console du
navigateur montre des appels vers `localhost`.

**Cause** — l'adresse du backend est écrite dans le code, ou lue depuis une
variable absente au moment du build.

**Correctif**

1. Sortir l'adresse dans une variable d'environnement.
2. Pour un frontend : **la variable est lue au moment du build**, pas au
   démarrage. Elle doit donc exister sur la machine qui construit.
3. Vérifier dans les fichiers produits qu'aucun `localhost` ne reste.

*C'est le piège numéro un des applications en deux dépôts.*

### La variable absente

**Symptôme** — le service démarre puis s'arrête, en boucle. Ou une
fonctionnalité échoue sans message clair.

**Cause** — une variable utilisée dans le code n'est déclarée nulle part, ou
n'a pas été saisie sur l'hébergeur.

**Correctif**

1. Lister toutes les variables utilisées dans le code.
2. Les déclarer dans un `.env.example` à jour.
3. Les saisir sur l'hébergeur.
4. **Faire échouer le démarrage** quand une variable obligatoire manque, avec
   un message explicite. Mieux vaut un arrêt net qu'un comportement faux.

### La valeur par défaut dangereuse

**Symptôme** — tout marche, et pourtant la configuration est fausse.

**Cause** — le code prend une valeur de repli quand la variable manque :
`os.getenv("DB_URL", "sqlite:///local.db")`. En production, la vraie base
n'est jamais atteinte, et personne ne le voit.

**Correctif** — pas de valeur de repli sur un réglage critique. Pour les
réglages optionnels, garder le repli et le documenter.

---

## 2. Le réseau

### Le port figé

**Symptôme** — l'hébergeur déclare l'application « en mauvaise santé ».

**Cause** — le code écoute un port fixe. Beaucoup de plateformes imposent le
leur par une variable `PORT`.

**Correctif** — lire le port depuis l'environnement, avec le port local en
repli. Écouter sur `0.0.0.0`, pas sur `127.0.0.1` : dans un conteneur,
`127.0.0.1` n'est joignable que de l'intérieur.

### CORS

**Symptôme** — ça marche en local, et en production le navigateur bloque les
appels.

**Cause** — la liste des origines autorisées contient l'adresse de
développement, pas celle de production.

**Correctif** — mettre la liste dans une variable d'environnement, une valeur
par environnement. Ne pas ouvrir à `*` : c'est un trou de sécurité, et ça ne
marche de toute façon pas avec des cookies.

### Les adresses de retour

**Symptôme** — la connexion par un service externe tourne en rond, ou le
paiement ne confirme jamais.

**Cause** — l'adresse de retour enregistrée chez le fournisseur pointe vers
`localhost`.

**Correctif** — enregistrer l'adresse de production chez chaque fournisseur
concerné : connexion externe, paiement, webhook.

### Les connexions longues

**Symptôme** — le temps réel marche en local, se coupe toutes les minutes en
production.

**Cause** — le proxy coupe les connexions inactives, ou ne sait pas les faire
passer.

**Correctif** — activer le passage des connexions longues sur le proxy,
allonger le délai d'inactivité, et prévoir une reconnexion côté client.

---

## 3. Les fichiers

### Le disque qui disparaît

**Symptôme** — les fichiers envoyés disparaissent après un redémarrage ou un
nouveau déploiement.

**Cause** — sur la plupart des hébergeurs, le disque du conteneur est remis à
zéro à chaque démarrage.

**Correctif** — ranger les fichiers dans un stockage prévu pour ça, ou monter
un volume persistant. Ce point se décide **avant** le premier déploiement :
après, les fichiers sont déjà perdus.

### Les chemins Windows

**Symptôme** — « fichier introuvable » sur le serveur, alors que tout marche
sur le poste.

**Cause** — un chemin écrit avec des antislashs, ou une lettre de lecteur.

**Correctif** — construire les chemins avec l'outil du langage (`Path`,
`path.join`), jamais par collage de chaînes.

### La casse des noms

**Symptôme** — un import ou une image échoue en production seulement.

**Cause** — Windows ne distingue pas les majuscules, Linux si. `Bouton.tsx`
et `bouton.tsx` sont deux fichiers différents sur le serveur.

**Correctif** — vérifier que chaque import correspond exactement au nom du
fichier.

---

## 4. La base de données

### Les migrations non jouées

**Symptôme** — le service démarre, puis échoue dès la première requête :
colonne inconnue.

**Cause** — le code attend un schéma que la base n'a pas encore.

**Correctif** — jouer les migrations dans l'étape de déploiement, avant de
démarrer la nouvelle version. Et vérifier que la migration est **réversible**,
sinon le retour arrière est impossible.

### La base inaccessible

**Symptôme** — « connexion refusée » au démarrage.

**Cause** — la chaîne de connexion pointe vers `localhost`, ou la base
n'autorise pas l'adresse du serveur, ou elle exige une connexion chiffrée.

**Correctif** — chaîne de connexion en variable d'environnement, adresse du
serveur autorisée côté base, option de chiffrement activée si elle est exigée.

### Trop de connexions

**Symptôme** — tout marche, puis l'application se fige sous quelques
utilisateurs.

**Cause** — chaque requête ouvre une connexion sans la rendre, ou la taille du
réservoir de connexions dépasse ce que la base accepte.

**Correctif** — utiliser un réservoir de connexions, et le régler sous la
limite de la base. Compter aussi les travailleurs de fond.

---

## 5. Le build et l'exécution

### La version du langage

**Symptôme** — le build échoue, ou une fonction n'existe pas.

**Cause** — la version installée sur le serveur n'est pas celle du poste.

**Correctif** — fixer la version dans le projet (`engines`, `.nvmrc`,
`.python-version`, image de base du conteneur) et la vérifier sur
l'hébergeur.

### Le fichier de verrouillage absent

**Symptôme** — le build passe un jour, casse le lendemain sans qu'on ait rien
changé.

**Cause** — pas de fichier de verrouillage, donc une version différente à
chaque installation.

**Correctif** — commiter le fichier de verrouillage, et installer avec la
commande qui le respecte (`npm ci`, et non `npm install`).

### Les dépendances de développement

**Symptôme** — « module introuvable » en production.

**Cause** — un paquet utilisé par le code applicatif est déclaré comme
dépendance de développement, donc absent en production.

**Correctif** — déplacer le paquet dans les dépendances normales.

### Le processus qui s'arrête

**Symptôme** — l'application tourne, puis disparaît après la fermeture de la
session.

**Cause** — lancée à la main, sans gestionnaire de service.

**Correctif** — la faire gérer par un service système ou par le
redémarrage automatique du conteneur, avec relance en cas d'arrêt.

---

## 6. La visibilité

### Aucune page de santé

**Symptôme** — l'hébergeur ne sait pas si l'application est vivante, et ne la
redémarre jamais quand elle est bloquée.

**Correctif** — une adresse qui répond « tout va bien » **et qui vérifie
vraiment** : la base répond, les services essentiels aussi. Une page qui
renvoie toujours 200 ne sert à rien.

### Les journaux perdus

**Symptôme** — une erreur en production, et rien à lire.

**Cause** — les journaux sont écrits dans un fichier du conteneur, effacé au
redémarrage.

**Correctif** — écrire sur la sortie standard, que l'hébergeur collecte. Et
ne **jamais** y écrire un jeton, un mot de passe ou une donnée personnelle.

### Aucune sauvegarde

**Symptôme** — on s'en aperçoit le jour où on en a besoin.

**Correctif** — sauvegarde automatique de la base, conservée ailleurs que sur
le serveur, et **une restauration testée au moins une fois**. Une sauvegarde
jamais restaurée n'est pas une sauvegarde.

---

## 7. Les limites de l'hébergeur

| Limite | Ce qu'elle casse |
|---|---|
| Mémoire | le processus est tué sans message clair |
| Temps de réponse maximum | les traitements longs sont coupés |
| Taille des envois | les gros fichiers sont refusés |
| Mise en veille | le premier visiteur attend plusieurs secondes |
| Connexions simultanées à la base | l'application se fige |
| Trafic sortant | facturé au-delà d'un seuil |

Ces limites se lisent **avant** de choisir, pas après la première coupure.

# Le parcours du déploiement

Le chemin complet, du code à la production. **À adapter au projet** : une
application sans base n'a pas d'étape de migration.

À chaque étape : ce qu'on fait, ce qui casse le plus souvent, comment vérifier
que c'est passé.

```text
Code → Build → Variables → Infrastructure → Base → Migration
     → Backend → Frontend → Proxy → HTTPS → DNS
     → Santé → Tests → Supervision → Sauvegarde → Production
```

---

## 1. Code

**Ce qu'on fait** — figer ce qui part : une version, une étiquette, un commit.

**Ce qui casse** — on déploie une branche qui bouge. Impossible de savoir
ensuite ce qui tourne.

**Vérifier** — la version déployée est identifiable, et l'application sait
dire laquelle elle est.

## 2. Build

**Ce qu'on fait** — installer les dépendances depuis le fichier de
verrouillage, construire.

**Ce qui casse** — version du langage différente, fichier de verrouillage
absent, dépendance de développement utilisée par le code applicatif, variable
de build absente.

**Vérifier** — le build passe sur une machine vierge, pas seulement sur le
poste.

## 3. Variables

**Ce qu'on fait** — saisir tous les réglages sur l'hébergeur.

**Ce qui casse** — une variable oubliée, ou une valeur de repli silencieuse
qui fait tourner l'application sur la mauvaise base.

**Vérifier** — la liste des variables du code est comparée ligne à ligne avec
celle de l'hébergeur. Le démarrage échoue si une variable obligatoire manque.

## 4. Infrastructure

**Ce qu'on fait** — la machine, le réseau, le pare-feu, les accès.

**Ce qui casse** — la base joignable depuis Internet, le port SSH ouvert à
tous, aucune règle de pare-feu.

**Vérifier** — depuis l'extérieur, seuls les ports 80 et 443 répondent.

## 5. Base de données

**Ce qu'on fait** — créer la base, l'utilisateur, les droits, la connexion.

**Ce qui casse** — chaîne de connexion vers `localhost`, adresse du serveur
non autorisée, connexion chiffrée exigée et non configurée.

**Vérifier** — se connecter à la base depuis le serveur, avec les identifiants
de production.

## 6. Migration

**Ce qu'on fait** — amener le schéma au niveau attendu par le code, **avant**
de démarrer la nouvelle version.

**Ce qui casse** — migration oubliée, migration non réversible qui interdit le
retour arrière, migration longue qui bloque la table.

**Vérifier** — la migration passe, et la migration inverse existe.

## 7. Backend

**Ce qu'on fait** — démarrer le service, sous un gestionnaire qui le relance
s'il tombe.

**Ce qui casse** — port figé, écoute sur `127.0.0.1` au lieu de `0.0.0.0`,
processus lancé à la main qui meurt avec la session.

**Vérifier** — le service répond depuis le serveur, et redémarre tout seul
après un arrêt forcé.

## 8. Frontend

**Ce qu'on fait** — publier les fichiers construits.

**Ce qui casse** — l'adresse du backend est figée **au moment du build**.
Construit avec `localhost`, le site appelle `localhost` chez chaque visiteur.

**Vérifier** — chercher `localhost` dans les fichiers publiés. Aucun résultat.

## 9. Proxy inverse

**Ce qu'on fait** — l'outil qui reçoit les visiteurs et les envoie vers la
bonne application.

**Ce qui casse** — taille maximale des envois trop basse, délai trop court
pour les traitements longs, connexions longues non transmises, en-têtes
d'origine perdus.

**Vérifier** — envoyer le plus gros fichier prévu, et laisser une connexion
longue ouverte cinq minutes.

## 10. HTTPS

**Ce qu'on fait** — le certificat, et le renouvellement automatique.

**Ce qui casse** — renouvellement non automatique — le site tombe trois mois
plus tard. Contenu appelé en clair depuis une page sécurisée, bloqué par le
navigateur.

**Vérifier** — le certificat est valide, son renouvellement est planifié, et
aucun appel en clair ne reste.

## 11. DNS

**Ce qu'on fait** — faire pointer le nom vers le serveur.

**Ce qui casse** — propagation pas encore faite, sous-domaine oublié, ancien
enregistrement laissé en place.

**Vérifier** — le nom résout vers la bonne adresse depuis l'extérieur.

## 12. Page de santé

**Ce qu'on fait** — une adresse qui dit si l'application va bien.

**Ce qui casse** — une page qui renvoie toujours « tout va bien » sans rien
vérifier. L'hébergeur croit le service sain alors que la base ne répond plus.

**Vérifier** — couper la base, la page de santé doit échouer.

## 13. Tests

**Ce qu'on fait** — parcourir les chemins réels : connexion, une lecture, une
écriture, un envoi de fichier, un e-mail.

**Ce qui casse** — on teste la page d'accueil, et on déclare que ça marche.

**Vérifier** — chaque parcours principal a été fait à la main, en production.

## 14. Supervision

**Ce qu'on fait** — savoir que ça casse **avant** les utilisateurs.

**Ce qui casse** — les journaux dans un fichier du conteneur, effacés au
redémarrage. Aucune alerte.

**Vérifier** — provoquer une erreur, et constater qu'elle remonte quelque part
où quelqu'un la verra.

## 15. Sauvegarde

**Ce qu'on fait** — sauvegarde automatique de la base et des fichiers,
conservée ailleurs.

**Ce qui casse** — sauvegarde sur le même serveur. Sauvegarde jamais restaurée.

**Vérifier** — **restaurer une sauvegarde sur un environnement de test.** Tant
que ça n'a pas été fait une fois, il n'y a pas de sauvegarde.

## 16. Retour arrière

**Ce qu'on fait** — savoir revenir à la version précédente, et en combien de
temps.

**Ce qui casse** — l'ancienne version n'est plus disponible, ou la migration
est irréversible.

**Vérifier** — la procédure est écrite, quelqu'un sait l'exécuter, et la durée
est connue en minutes.

---

## Le tableau à remplir pour le projet

| Étape | Concernée | Qui la fait | Vérification | État |
|---|---|---|---|---|
| Code | | | | |
| Build | | | | |
| Variables | | | | |
| Infrastructure | | | | |
| Base | | | | |
| Migration | | | | |
| Backend | | | | |
| Frontend | | | | |
| Proxy | | | | |
| HTTPS | | | | |
| DNS | | | | |
| Santé | | | | |
| Tests | | | | |
| Supervision | | | | |
| Sauvegarde | | | | |
| Retour arrière | | | | |

Une étape sans responsable est une étape qui ne sera pas faite.

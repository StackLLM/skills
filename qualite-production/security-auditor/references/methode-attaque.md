# La méthode d'attaque

Revue adverse, dans un cadre défensif et autorisé : on cherche les chemins
pour les fermer, sur un projet qu'on a le droit d'auditer.

On ne cherche pas « des failles ». On cherche **un chemin entre quelqu'un et
quelque chose qui a de la valeur**.

---

## 1. Commencer par ce qui a de la valeur

Avant de chercher une porte, savoir ce qu'il y a derrière. Lister les biens du
projet, du plus sensible au moins sensible.

| Bien | Exemples |
|---|---|
| Données personnelles | noms, adresses, téléphones, pièces d'identité |
| Données de clients | dossiers, contrats, montants, documents |
| Accès | comptes, mots de passe, jetons, sessions |
| Moyens | clés d'API payantes, quotas, capacité de calcul |
| Intégrité | pouvoir modifier une donnée sans être vu |
| Disponibilité | pouvoir faire tomber le service |

Une faille qui ne touche aucun de ces biens n'est pas CRITIQUE, quel que soit
son nom savant.

---

## 2. Choisir un profil d'attaquant

On raisonne **par profil**, jamais par liste de vulnérabilités. Chaque profil
part d'un point différent et voit une application différente.

| Profil | Ce qu'il a déjà | Ce qu'il cherche d'abord |
|---|---|---|
| **Visiteur** | le site public, le code téléchargé | une clé dans le code, une adresse ouverte, un formulaire |
| **Utilisateur légitime** | un compte, un jeton | les données des autres, les fonctions d'administration |
| **Client concurrent** | un compte sur la même plateforme | les données d'un autre client |
| **Ancien salarié** | des identifiants, un accès au dépôt | ce qui n'a pas été révoqué |
| **Dépendance compromise** | l'exécution de code dans l'app | les secrets en mémoire, la base |
| **Personne sur le réseau** | la position entre client et serveur | ce qui circule en clair |

Sur une application interne, les trois premiers profils comptent le plus.
Sur une application exposée, le premier et le dernier aussi.

---

## 3. Chercher le chemin

Un chemin part d'un profil et arrive à un bien. Chaque étape est une **porte
qui aurait dû être fermée**.

### Le chemin du secret

```text
Visiteur du site
   ↓
Ouvre le code téléchargé par son navigateur
   ↓
Trouve une clé d'API
   ↓
Appelle le service directement, hors de l'application
   ↓
Consommation facturée, ou données lues
```

### Le chemin de l'accès horizontal

```text
Utilisateur connecté, sans droit particulier
   ↓
Adresse qui vérifie la connexion mais pas la propriété
   ↓
Numéro changé dans l'URL
   ↓
Donnée d'un autre utilisateur
```

### Le chemin de l'accès vertical

```text
Utilisateur ordinaire
   ↓
Adresse d'administration non protégée côté serveur
   ↓
Le bouton est caché dans l'interface, l'adresse ne l'est pas
   ↓
Fonction d'administration exécutée
```

### Le chemin du fichier

```text
Formulaire d'envoi de fichier
   ↓
Type et taille mal vérifiés, nom conservé tel quel
   ↓
Fichier déposé dans un dossier servi publiquement
   ↓
Fichier rappelé par son adresse, exécuté ou distribué
```

### Le chemin de l'injection

```text
Champ de recherche
   ↓
Valeur collée directement dans une requête
   ↓
La requête change de sens
   ↓
Lecture ou modification hors du périmètre prévu
```

### Le chemin de la session

```text
Jeton récupéré (poste partagé, journal, lien)
   ↓
Durée de vie longue, aucune révocation possible
   ↓
Compte utilisable jusqu'à expiration
   ↓
Changer le mot de passe ne change rien
```

**Ces six chemins sont des modèles, pas une liste à cocher.** Le vrai chemin
du projet s'écrit avec les vrais noms de ses adresses et de ses écrans.

---

## 4. Prouver, ou ne pas affirmer

Pour chaque chemin trouvé, une seule question : **qu'est-ce qui le prouve ?**

| Ce qu'on a | Confiance | Comment l'écrire |
|---|---|---|
| Le code de la fonction, lu, sans contrôle de propriété | Confirmé | « la fonction rend le dossier sans vérifier à qui il appartient » |
| L'adresse et le routeur, mais pas le middleware | Probable | « aucun contrôle visible ; à confirmer en lisant le middleware X » |
| Une valeur de configuration d'exemple | À vérifier | « si la production utilise la même valeur, alors… » |
| Aucun accès à la production | Non vérifiable | « la configuration de production n'a pas pu être lue » |

On peut **toujours** donner la manière de vérifier soi-même. C'est le champ
« comment le constater ». Sans lui, le lecteur doit croire sur parole.

---

## 5. Les angles morts fréquents

Ce que les développeurs sérieux oublient le plus souvent. À passer un par un,
même quand le reste semble propre.

| Angle mort | La question à se poser |
|---|---|
| La frontière entre deux dépôts | le backend fait-il confiance au frontend pour un contrôle ? |
| Le contrôle côté interface seulement | le bouton est caché — l'adresse l'est-elle ? |
| Les messages d'erreur | disent-ils si un compte existe, si un dossier existe ? |
| Les journaux | un jeton, un mot de passe ou un numéro y atterrit-il ? |
| Les adresses de test ou de debug | restent-elles ouvertes en production ? |
| Les webhooks entrants | la signature de l'appelant est-elle vérifiée ? |
| Les anciennes versions de l'API | encore servies, sans les contrôles récents ? |
| Le mot de passe oublié | le lien expire-t-il ? est-il à usage unique ? |
| L'inscription ouverte | quelqu'un peut-il créer un compte tout seul ? |
| Les exports | un export contourne-t-il les filtres de l'écran ? |
| La pagination | demander 10 000 lignes d'un coup fonctionne-t-il ? |
| Le rate limiting | combien d'essais de mot de passe avant blocage ? |
| L'historique Git | un secret retiré y est-il encore ? |
| Les sauvegardes | où sont-elles, qui y accède ? |

---

## 6. Ce qu'on ne fait pas

- **Aucun test contre un système en production** sans accord écrit et explicite.
- **Aucune exploitation réelle.** On montre le chemin, on ne le parcourt pas.
- **Aucun test contre un service tiers.** Le fournisseur n'a rien autorisé.
- **Aucune donnée réelle recopiée** dans le rapport, même pour illustrer.

Une vérification qui demande d'attaquer un système vivant se transforme en
**instruction à donner au propriétaire** : « voici comment le constater
vous-même, sur votre environnement de test ».

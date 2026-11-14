# Normes d'écriture — du code qui tient en production

Le but n'est pas un code « joli ». C'est un code qu'un autre dev modifie un an
plus tard, en production, sans casser autre chose.

## Sommaire

1. Règles communes à tous les langages
2. TypeScript et Node
3. React
4. Python et FastAPI
5. HTML et CSS
6. SQL et base de données
7. Ce qu'on refuse en relecture

---

## 1. Règles communes

### Nommer

- **Français** pour tout ce qu'on écrit : variables, fonctions, fichiers,
  commentaires, commits. Les mots du langage et des bibliothèques restent anglais.
- Une fonction = un **verbe** (`calculerTva`, `lire_compte`). Un booléen = une
  question (`estPublie`, `a_expire`). Une liste = un pluriel.
- Pas d'abréviations obscures (`tmp`, `data2`, `mgr`). Le nom dit ce que c'est.

### Structurer

- **Une fonction fait une chose.** Au-delà de ~40 lignes ou de 3 niveaux
  d'indentation, découper.
- **Retour anticipé** plutôt que `if` imbriqués :

  ```ts
  // Non
  if (compte) { if (compte.actif) { ... } }
  // Oui
  if (!compte?.actif) return refuser()
  ...
  ```

- **Fonctions pures** dès que possible : mêmes entrées → même sortie, sans effet de bord.
  Les effets (base, réseau, fichiers, horloge) restent aux bords.
- **Injection des dépendances** : l'horloge, `fetch`, la base se passent en
  paramètre, avec une valeur par défaut. Le test donne une fausse horloge.

### Erreurs

- **Ne jamais avaler une erreur.** Un `catch` vide doit avoir un commentaire
  qui dit pourquoi c'est sans risque (`/* pas encore prêt : on réessaie */`).
- **Erreur attendue ≠ panne.** Une saisie refusée renvoie un 400 avec un message
  pour l'utilisateur. Une panne renvoie un 500 générique, et le détail part
  dans le journal, jamais dans la réponse.
- **Classes d'erreurs métier** (`ContenuRefuse`, `CompteBloque`) plutôt que des
  chaînes : la route sait quoi répondre sans lire un message.
- Les messages d'erreur disent **quoi faire** : « Il manque CMS_ORIGINE dans
  backend/.env », pas « config error ».

### Valeurs et limites

- **Aucune valeur magique** : `const TAILLE_MAX_PHOTO = 8 * 1024 * 1024`.
- **Toute entrée a une limite** : taille du corps, longueur d'un texte, nombre
  d'éléments d'une liste, délai d'une requête sortante. Sans limite, un seul
  appel peut remplir la mémoire ou le disque.
- **Toute requête sortante a un délai max** (`AbortSignal.timeout(8000)`,
  `httpx.Timeout(8.0)`).

### Commentaires

- En tête de chaque fichier : à quoi il sert, et sa limite principale.
- Dans le code : le **pourquoi**, quand il n'est pas évident.
- Jamais de code mort commenté : Git s'en souvient.

### Sécurité de base

- Aucun secret dans le code, les tests ou les journaux.
- Comparaison de secrets en **temps constant** (`timingSafeEqual`, `hmac.compare_digest`).
- Requêtes SQL **paramétrées**, toujours.
- Chemins de fichiers venant de l'utilisateur : **résolus puis vérifiés** dans le dossier autorisé.

---

## 2. TypeScript et Node

- `tsconfig` : `strict`, `noUnusedLocals`, `noUnusedParameters`,
  `verbatimModuleSyntax`, `erasableSyntaxOnly` (Node lit le TS sans compilation).
- **Jamais `any`**. `unknown` + vérification, ou un type précis.
- Les types de données externes se vérifient à l'entrée (fonction de
  validation, ou Zod). Un `as Type` sur une donnée externe est un mensonge.
- `import type` pour les types seuls.
- `node:` devant les modules natifs (`node:fs`, `node:http`).
- Fonctions `async` : toujours `await` ou retourner la promesse ; jamais de
  promesse flottante (une erreur perdue = un serveur qui meurt sans trace).
- `process.on('unhandledRejection')` journalise et arrête proprement.
- Les modules exportent des **fabriques** (`creerApplication(config, outils)`)
  plutôt que des objets globaux : chaque test crée sa propre instance.
- Pas de dépendance pour trois lignes. Chaque dépendance est du code qu'on ne
  relit pas et qu'il faudra mettre à jour.

---

## 3. React

- **Composants fonctions**, un composant par fichier, nom en `PascalCase`.
- Un composant de plus de ~150 lignes se découpe.
- **L'état au plus près** de là où il sert ; on le remonte seulement s'il est partagé.
- **Les effets** (`useEffect`) servent à se synchroniser avec l'extérieur, pas à
  calculer une valeur : une valeur dérivée se calcule pendant le rendu.
- Chaque `useEffect` qui lance une requête **annule** au démontage (`AbortController`).
- Les appels au backend passent par `services/` ; le composant reçoit des données et des états (`chargement`, `erreur`, `vide`).
- **Les quatre états** de chaque écran de données : chargement, erreur, vide, rempli.
- Clés de liste stables (`id`), jamais l'index si la liste peut bouger.
- Pas de `dangerouslySetInnerHTML` sur un contenu saisi par quelqu'un.

---

## 4. Python et FastAPI

- **Python ≥ 3.12**, outils : `uv` (environnement), `ruff` (lint + format),
  `mypy --strict` ou `pyright` (types), `pytest`.
- **Annotations partout**, y compris les retours. `ruff` avec les règles
  `E, F, I, B, UP, SIM, S, N, RUF`.
- **Pydantic** pour toute entrée et sortie d'API (`modeles.py`). Le schéma de
  sortie empêche de renvoyer un champ par erreur (le hash d'un mot de passe…).
- **Pydantic Settings** pour la configuration (`config.py`), validée au démarrage.
- **Fabrique d'application** : `creer_application(config) -> FastAPI`. Les tests
  créent leur application avec leur config.
- **Dépendances FastAPI** (`Depends`) pour la session, la base, la config :
  elles se remplacent dans les tests (`app.dependency_overrides`).
- Routes `async` seulement si tout ce qu'elles appellent est asynchrone. Un
  appel bloquant dans une route `async` bloque tout le serveur.
- Pas de `except Exception: pass`. Pas de `print` : le module `logging`, configuré dans `journal.py`.
- Chemins avec `pathlib.Path`, jamais de concaténation de chaînes.
- Dates en **UTC avec fuseau** (`datetime.now(UTC)`), converties seulement à l'affichage.

---

## 5. HTML et CSS

### HTML

- **Sémantique d'abord** : `header`, `nav`, `main`, `section`, `article`,
  `footer`, `button` pour une action, `a` pour aller ailleurs. Une `div`
  cliquable est un bouton cassé (ni clavier, ni lecteur d'écran).
- **Un seul `h1` par page**, des titres dans l'ordre (`h2` puis `h3`).
- Chaque image a un `alt` (vide `alt=""` si décorative) et ses dimensions
  (`width`, `height`) : la page ne saute pas au chargement.
- Chaque champ de formulaire a son `label`. Le type juste (`email`, `tel`).
- `lang="fr"` sur `<html>`, `<meta name="viewport">`, une `title` et une
  `meta description` par page.
- Liens externes ouverts dans un nouvel onglet : `rel="noopener noreferrer"`.
- Pas de script en ligne sans empreinte dans la politique de sécurité (CSP).

### CSS

- **Des variables** (`--couleur-texte`, `--espace-2`) : une seule source pour les couleurs et les espaces.
- **Mobile d'abord** : les règles de base pour le téléphone, `@media (min-width: …)` pour élargir.
- Unités relatives (`rem`) pour le texte ; contraste AA minimum (4,5:1).
- Respect de `prefers-reduced-motion` pour les animations.
- Pas de `!important` sauf pour écraser une bibliothèque externe, commenté.

---

## 6. SQL et base de données

- **Migrations versionnées**, appliquées au démarrage ou par un script ; jamais
  de changement de schéma à la main en production.
- Une migration ne casse pas la version d'avant pendant le déploiement :
  ajouter une colonne, déployer, puis retirer l'ancienne dans une livraison suivante.
- Requêtes **paramétrées** ; jamais de concaténation avec une saisie.
- Clés étrangères et contraintes (`NOT NULL`, `UNIQUE`, `CHECK`) : la base
  protège les données même quand le code se trompe.
- Index sur les colonnes filtrées souvent ; vérifier avec `EXPLAIN`.
- Transactions pour toute écriture en plusieurs étapes.
- SQLite en production : mode `WAL`, `busy_timeout`, une seule instance du serveur.

---

## 7. Ce qu'on refuse en relecture

| Refusé | Pourquoi |
|---|---|
| `any`, `# type: ignore` sans raison écrite | les types ne protègent plus rien |
| `catch {}` ou `except: pass` sans commentaire | une panne silencieuse en prod |
| Valeur écrite en dur qui change selon l'environnement | marche chez le dev, casse en ligne |
| Fonction de 120 lignes | personne ne la relit vraiment |
| Requête SQL construite avec une saisie | injection |
| Secret, token ou mot de passe dans le code ou un test | fuite dès le premier push |
| Code ajouté sans test, sur une règle métier | la prochaine modification le cassera sans bruit |
| Fichier de 800 lignes qui mélange HTTP, métier et base | impossible à tester par morceaux |
| Dépendance ajoutée pour trois lignes | surface d'attaque et mises à jour pour rien |
| `console.log` / `print` de débogage oublié | journaux pollués, parfois des données personnelles |

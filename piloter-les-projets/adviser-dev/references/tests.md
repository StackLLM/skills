# Tests — prouver que le service marche, et qu'il marchera encore demain

Un test n'est pas là pour faire monter un pourcentage. Il est là pour qu'une
modification qui casse quelque chose soit **vue avant la production**.

## Sommaire

1. Les trois niveaux
2. Quoi tester en priorité
3. Écrire un bon test
4. Organisation et outils
5. Les tests avant un refactoring
6. Ce que la CI exige

---

## 1. Les trois niveaux

| Niveau | Ce qu'il vérifie | Vitesse | Part |
|---|---|---|---|
| **Unitaire** | une fonction ou un module seul : règle métier, calcul, validation | millisecondes | la majorité |
| **Intégration** | plusieurs morceaux ensemble : vraie route HTTP + vraie base (temporaire) + vrais en-têtes | dixièmes de seconde | les parcours importants |
| **Bout en bout** | le navigateur sur le vrai service (Playwright) | secondes | quelques parcours critiques seulement |

Un test d'intégration lance l'application **dans le test** (port aléatoire ou
client de test), avec une base dans un dossier temporaire. Pas de serveur à
lancer à la main, pas de réseau externe.

---

## 2. Quoi tester en priorité

Dans cet ordre :

1. **Les règles métier** : calculs, statuts, droits. C'est là que l'argent et la confiance se perdent.
2. **La sécurité** : un non-connecté reçoit 401 ; un client ne lit pas les
   données d'un autre ; la limite d'essais bloque au bon moment et se lève ;
   les en-têtes de sécurité sont là ; un corps trop grand reçoit 413.
3. **Les entrées refusées** : champ manquant, texte trop long, fichier pas du bon type, chemin `../`.
4. **La santé** : `/sante/vivant` 200 ; `/sante/pret` 503 quand la base manque.
5. **Les parcours** : connexion → modification → publication.
6. **Chaque bug corrigé** : d'abord un test qui échoue, puis la correction.
   Le bug ne revient jamais sans bruit.

On ne teste pas : le code des bibliothèques, les accesseurs triviaux, les détails de mise en page.

---

## 3. Écrire un bon test

- **Le nom dit le comportement**, en français :
  `refuse une photo de plus de 8 Mo`, `bloque après cinq essais ratés`.
- **Une idée par test.** Structure : préparer → agir → vérifier.
- **Indépendant** : chaque test crée ses données et son dossier temporaire ;
  l'ordre des tests ne change rien.
- **Déterministe** : horloge injectée, aléatoire fixé, aucun appel réseau réel
  (les services externes sont remplacés par un faux).
- **Vérifier ce qui se voit** : la réponse HTTP, le contenu en base, le texte
  affiché. Pas l'appel interne d'une fonction privée : sinon chaque refactoring
  casse des tests sans casser le produit.
- Un test qui échoue au hasard (flaky) se corrige ou se supprime le jour même :
  sinon l'équipe apprend à ignorer le rouge.

---

## 4. Organisation et outils

| Partie | Outil | Où |
|---|---|---|
| Frontend | Vitest + Testing Library + jsdom | `frontend/tests/*.test.tsx` |
| Backend Node | `node --test` (intégré, sans dépendance) | `backend/tests/*.test.ts` |
| Backend Python | pytest + `fastapi.testclient` (ou `httpx.AsyncClient`) | `backend/tests/test_*.py` |
| Bout en bout | Playwright | `e2e/` (seulement si le projet en a besoin) |

Python : les fixtures (`conftest.py`) créent la config de test, l'application
et le client. Node : une fonction `demarrer()` dans le test crée l'application
sur un port libre et la ferme à la fin.

Couverture : on la regarde pour trouver les **trous** sur le métier, pas pour
atteindre un chiffre. Repère : le métier et la sécurité couverts presque
entièrement ; le reste selon le bon sens.

---

## 5. Les tests avant un refactoring

Dans un projet existant, avant de déplacer du code :

1. Écrire des **tests de caractérisation** : ils figent ce que fait le code
   aujourd'hui (même si c'est bizarre), par l'extérieur (routes HTTP, fonctions publiques).
2. Faire le refactoring par petits pas ; lancer les tests à chaque pas.
3. Les tests restent verts : le comportement n'a pas changé.
4. Seulement après, corriger les comportements bizarres, chacun avec son test.

Un refactoring sans tests, c'est réécrire et espérer.

---

## 6. Ce que la CI exige

- Tous les tests passent, à chaque push, sur toutes les branches.
- Les tests tournent **sans `.env`** : la config de test est écrite dans les tests.
- Durée totale de la CI sous ~10 minutes ; au-delà, on parallélise ou on allège.
- Un test désactivé (`skip`) porte un commentaire avec la raison et une date.

# Audit — la grille et le gabarit du rapport

## Sommaire

1. Méthode
2. La grille, bloc par bloc
3. Classer les constats
4. Découper en lots
5. Le gabarit du rapport

---

## 1. Méthode

1. `scripts/auditer.py <dossier> -o audit.json --en-ligne` : l'inventaire automatique (présent / partiel / absent, et les alertes).
2. Lire, dans cet ordre : README → plan ou cahier des charges → `package.json`
   ou `pyproject.toml` → point d'entrée du backend → configuration → une route
   complète (de la requête à la base) → **la sécurité d'accès** (comment on entre dans l'admin, avec quel secret,
   combien d'essais) → deux composants du frontend → la CI → chaque Dockerfile.
3. Lancer `npm run verifier` (ou l'équivalent) **seulement si le dev est
   d'accord** : ça installe et ça peut être long. Sinon, lire le dernier résultat de CI (`gh run list`).
4. Remplir la grille. Chaque ligne a sa **preuve** : un fichier, une ligne, une sortie de commande.
5. Revoir chaque indice du script : confirmé → dans la grille ; faux → dans « Faux positifs écartés », avec la raison.

Lecture seule pendant tout l'audit. Aucun `.env` ouvert : on vérifie seulement
s'il est suivi par Git (`git ls-files | grep -E '(^|/)\.env$'`).

---

## 2. La grille

| Bloc | Présent quand… | Questions à se poser |
|---|---|---|
| 1. Structure | `frontend/`, `backend/`, `infra/`, `docs/`, scripts communs à la racine | Le métier est-il dans des routes ? Des dossiers fourre-tout (`utils/` de 40 fichiers) ? Les noms diffèrent-ils (`web/`, `api/`) ? → décision : renommer, ou exception écrite |
| 2. Configuration | un module de config, `.env.example` complet, validation au démarrage | Des `localhost` en dur ? Des secrets dans le code ? `.env` suivi par Git ? |
| 3. Écriture | types stricts, petites fonctions, erreurs traitées, entrées validées | `any` ? `catch` vides ? Fichiers de 800 lignes ? Valeurs magiques ? |
| 4. Tests | unitaires + intégration, qui passent | Le métier et la sécurité sont-ils testés ? Des tests désactivés ? |
| 5. CI | `ci.yml` sur chaque push : install exacte, types, lint, tests, build, pour **chaque** langage | Actions à jour (`--en-ligne`) ? `permissions` minimales ? Versions de Node / Python encore maintenues, et **les mêmes** en CI, dans l'image et chez l'hébergeur ? L'image attend-elle la CI (`needs`) ? Dépendances de test épinglées ? |
| 6. Branches / livraison | `dev` + `main` protégée, `livrer`, job `pret-pour-main` | Qui pousse sur `main`, et comment ? |
| 7. Docker | **chaque** Dockerfile sans root, avec `HEALTHCHECK` et un `.dockerignore` dans son dossier | Image de base épinglée ? Données dans un volume ? nginx en `nginx-unprivileged` ? |
| 8. Santé | `/sante/vivant`, `/sante/pret` | `/sante/pret` contrôle-t-il vraiment la base ? L'adresse révèle-t-elle un état interne (admin ouverte, versions) ? Surveillance extérieure prévue ? |
| 9. Protection | limites d'essais **sur chaque entrée d'authentification et chaque formulaire public**, en-têtes, tailles max, empreintes de mots de passe | Un secret d'accès (jeton, mot de passe) peut-il être court ? Combien d'essais avant blocage ? `X-Forwarded-For` lu sans proxy de confiance ? Autorisation côté serveur ? |
| 10. Journaux | une ligne structurée par requête, identifiant de requête | Des secrets ou données personnelles dans les journaux ? |
| 11. Données | migrations, sauvegarde, restauration testée | Que perd-on si le disque meurt ce soir ? |
| 12. Documentation | README qui lance le projet ; décisions écrites | Un nouveau dev lance-t-il le projet seul en 5 minutes ? |

État de chaque bloc : **présent**, **partiel** (existe mais incomplet ou
faux), **absent**.

---

## 3. Classer les constats

| Gravité | Définition | Exemple |
|---|---|---|
| **Bloquant** | empêche la mise en production, ou met des données en danger | secret dans Git ; pas d'autorisation côté serveur ; authentification sans limite d'essais ; secret d'accès court |
| **Important** | casse probable en production, ou maintenance très difficile | pas de tests sur le métier ; `localhost` en dur ; pas de health check ; aucun journal ; aucune sauvegarde ; version de Node plus maintenue ; image publiée sans CI |
| **Amélioration** | rend le code plus sûr ou plus lisible, sans risque immédiat | fonctions trop longues ; noms flous ; actions GitHub anciennes |

Chaque constat porte aussi sa certitude : **Fait** (vu), **À vérifier** (probable).

---

## 4. Découper en lots

Ordre par défaut, qui protège la production :

| Lot | Contenu | Fini quand |
|---|---|---|
| 0 | Filet : CI minimale + tests de caractérisation des parcours importants | CI verte, parcours couverts |
| 1 | Configuration et secrets | `.env.example` complet, validation au démarrage, aucun secret dans Git |
| 2 | Structure | dossiers au socle, scripts communs, aucun changement visible |
| 3 | Écriture | défauts « bloquants » et « importants » corrigés, avec tests |
| 4 | Santé, protection, journaux | `/sante/*`, limites, en-têtes, journaux structurés, testés |
| 5 | Docker et données | image, volume, sauvegarde, restauration testée |
| 6 | Branches et livraison | `dev`, protections, `pret-pour-main`, `livrer` |
| 7 | Documentation | README, décisions |

Un lot = une branche = une PR. Un lot trop gros (> 1 jour, > 30 min de
relecture) se coupe en deux.

---

## 5. Le gabarit du rapport

Le rapport suit la manière d'expliquer de l'équipe (français simple, sections
courtes, chemins en fin). Il s'écrit dans `docs/audit-socle-AAAA-MM-JJ.md` du
projet (avec l'accord du dev), et se résume dans la réponse.

```markdown
# Audit du socle — <projet> — <date>

## Verdict
<deux phrases : où en est le projet ; ce qui bloque la production>

## Les douze blocs
| Bloc | État | Preuve | Gravité |
|---|---|---|---|
| Structure | partiel | le métier est dans les routes (backend/routes/commandes.py) | important |
| … | | | |

Faux positifs de l'inventaire, vérifiés et écartés :
- <fichier:ligne> — <pourquoi ce n'est pas un défaut>

## Refactoring d'architecture
### Ce qui doit bouger
- **<changement>** — pourquoi : <risque évité>. Fait / À vérifier.

## Refactoring d'écriture
### Bloquant
- <constat> — <fichier:ligne> — <correction proposée>
### Important
- …
### Amélioration
- …

## Les lots
| Lot | Contenu | Risque | Fini quand | Durée estimée (à confirmer) |
|---|---|---|---|---|

## Décisions à prendre
### Décision 1 — <sujet>
**Pourquoi la question se pose** : …
**Options**
- **A — …** → conséquence : …
- **B — …** → conséquence : …
**Avis technique** : …
**À trancher** : A ou B ?

## Zone technique concernée
- <fichiers, dossiers, workflows>
```

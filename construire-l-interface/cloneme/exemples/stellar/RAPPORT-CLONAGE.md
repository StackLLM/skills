# Rapport de clonage — Stellar (HTML5 UP)

## En bref

- Source : https://html5up.net/uploads/demos/stellar/ · relevé le 2026-10-16 · licence CC BY 3.0.
- Pages : **3 clonées sur 3 identifiées** + une page 404 créée (la source n'en a pas).
- Chaîne : tsc ✅ · vitest ✅ 13 tests · build ✅ · synchro fichiers ↔ code ✅ (66 tokens, 31 identifiants).
- Comparaison source ↔ clone : **0 écart fort, 0 moyen** sur 3 pages × 4 largeurs (1440, 1024, 768, 375).
- Lancer : `start-all.bat`, ou `cd ui && npm run dev` → http://localhost:6090.

## Pages

| ID | Page | Statut | Écarts forts restants | Remarque |
|---|---|---|---|---|
| P-01 | Accueil `/` | cloné | 0 | menu collé, lien actif, défilement doux reproduits |
| P-02 | Generic `/generique` | cloné | 0 | |
| P-03 | Elements `/elements` | cloné | 0 | page non liée sur la source, trouvée par sondage |
| P-04 | 404 `*` | créée | — | Approximé : la source rend une page serveur générique |

## Ce qui a été testé

| Vérification | Comment | Résultat |
|---|---|---|
| Empreintes source ↔ clone | 12 relevés par côté (styles calculés + géométrie de 6 à 14 éléments par page), script `comparer-empreintes.mjs` | 0 fort, 0 moyen |
| Hauteur des pages | même relevé | identique au pixel (ex. accueil 4018 px à 1440, 5146 px à 375) |
| Menu collé et lien actif (A-02, A-03) | même séquence de défilement sur la source et le clone | même comportement, cas limite compris |
| Défilement doux (A-04) | test unitaire, horloge et images pilotées à la main | 1000 ms, mi-chemin à 500 ms, courbe « swing » |
| Liens internes | chaque lien de chaque page ouvert dans un cadre | tous résolus ; ancres présentes ; `/generic.html` redirige |
| Route inconnue | ouverture | 404 avec retour à l'accueil |
| Formulaire | test de parcours | erreurs, envoi « mode démo », réinitialisation |
| Boutons sans effet | recherche dans le DOM | aucun hors formulaire |
| Modification de `palette.md` (lot 6) | accent changé, détecté, appliqué, mesuré, puis remis | seul le bouton principal a changé ; Generic identique |

## Corrections faites pendant la comparaison

| Écart mesuré | Cause | Correction |
|---|---|---|
| Bloc de code trop court de 53 px | lignes vides perdues à la lecture du HTML | texte repris tel quel |
| Formulaire décalé sous 736 px | gouttière de grille différente par largeur, non vue à 1440 px | `--gouttiere` : 1em ≤ 736, 1.25em ≤ 480 |
| Boutons empilés trop espacés sous 480 px | sélecteur porté avec une spécificité plus faible | `ul.actions:not(.fixe)` comme la source |
| Mots collés sous 736 px (« templatebuilt ») | JSX supprime l'espace après `<br />` | `{' '}` rétabli |
| Liens du menu trop serrés | JSX supprime l'espace entre les `<li>` en ligne | espace rétabli |
| Fin de page Elements décalée de 30 px | paragraphe recopié de travers | texte exact de la source |

## Écarts restants

| Où | Écart | Raison | Gravité |
|---|---|---|---|
| Elements, 1er bouton « Icon » | icône affichée | la source a une faute de classe (`solidfa-download`) | volontaire |
| Toutes pages | mode animations réduites respecté | absent de la source, ajout d'accessibilité | volontaire |
| Formulaire | validation et états d'envoi | la source n'en a pas (`action="#"`) | Approximé |

## Limites

- Non vérifiable ici : le rendu **animé** (entrée de l'en-tête A-01, transitions de survol, défilement doux à l'écran). Le navigateur intégré, caché, ne dessine pas d'images. Logique testée, valeurs relevées dans le code source. **À regarder en direct.**
- Les événements `scroll` ne partent pas dans un onglet caché : ils ont été déclenchés à la main pour tester A-02 et A-03, sur la source comme sur le clone.
- Script d'audience Cloudflare et `noscript.css` non repris.
- Liens réseaux, e-mail et boutons d'exemple : `#` sur la source, gardés tels quels et centralisés dans `configSite.ts`.

## Dépendances et technologies

| Paquet | Version | Pourquoi |
|---|---|---|
| react, react-dom | 18.3.1 | stack maison |
| react-router-dom | 6.30.6 | 3 pages + 404 + redirections des anciennes adresses |
| @fontsource/source-sans-pro | 5.3.0 | police de la source (300, 400), sans appel à Google Fonts |
| @fortawesome/fontawesome-free | 5.15.4 | même version d'icônes que la source |
| vite | 5.4.21 | serveur de dev et build |
| typescript | 5.9.3 | typage strict |
| vitest, jsdom, @testing-library/* | 2.1.9 / 25.0.1 / 16.3.3 | tests |

Non installés, volontairement : Tailwind (la source est en CSS classique, porté
en un fichier CSS par composant), framer-motion (aucune animation ne le
demande : transitions CSS et un défilement en `requestAnimationFrame`), jQuery
et ses greffons (logique reprise en React, sans dépendance).

## Droits

- Modèle CC BY 3.0 : garder « Design: HTML5 UP » en cas de publication.
- Photos Unsplash de démonstration, logo et trame : à remplacer avant tout usage public.

## Journal

- 2026-10-16 — clonage initial.
- 2026-10-16 — `palette.md` : `--anneau-focus` relié à `--couleur-accent` (il contenait la couleur en dur). Test du mode Mettre à jour : accent changé puis remis.

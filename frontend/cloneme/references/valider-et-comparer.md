# Valider et comparer au site source

On ne juge pas un clone à l'œil dans cet environnement (captures qui figent,
animations qui ne tournent pas). On le juge par **empreintes** : les mêmes
mesures prises sur la source et sur le clone, puis comparées par un script.

La méthode de validation d'animation-stealer (`reproduire-et-valider.md` §4)
s'applique à chaque animation. Cette fiche couvre le **site entier**.

---

## 1. Les cibles à comparer

`.cloneme/cibles.json`, tiré de `design.md` §10. Par page, les éléments qui
comptent : titres, conteneurs, cartes, boutons, en-tête, pied — et au moins un
élément **en bas de page** : un décalage se voit en cumulé tout en bas.
`source` est l'URL réelle (le script en déduit le chemin relayé), `clone`
l'adresse locale du clone.

```json
{
  "P-01": {
    "source": "https://exemple.com/",
    "clone": "http://localhost:6010/",
    "cibles": {
      "entete":         { "source": "#header",        "clone": "[data-ref=entete]" },
      "bandeau-titre":  { "source": "#header h1",     "clone": "[data-ref=bandeau-titre]" },
      "contenu":        { "source": "#main",          "clone": "main" },
      "bouton-principal": { "source": ".button.primary", "clone": "[data-ref=bouton-principal]" }
    }
  }
}
```

Dans le clone, un attribut `data-ref` sur les éléments comparés évite les
sélecteurs fragiles. Il ne sert qu'à la mesure ; le garder, il ne coûte rien.

---

## 2. Relever les empreintes — le relais

Une empreinte = styles calculés + géométrie de chaque cible, plus la hauteur de
page et quelques compteurs. Trois obstacles, rencontrés en vrai, et leur
solution :

| Obstacle | Solution |
|---|---|
| Recopier chaque relevé à la main coûte cher (≈ 5 000 tokens par page et par largeur) | les relevés partent directement dans des fichiers, par le **relais** |
| Le navigateur intégré **bloque** les appels d'un site public vers localhost (`ERR_BLOCKED_BY_CLIENT`) | le relais **sert la source depuis localhost** : source et clone se mesurent pareil |
| Redimensionner la fenêtre pour chaque largeur est lent | chaque page s'ouvre dans un **cadre caché** à la largeur voulue : ses `@media` suivent le cadre |

### Démarrer le relais

En tâche de fond, depuis la racine du projet :

```bash
node <dossier-CloneMe>/scripts/relais-cloneme.mjs --dossier .cloneme --source https://exemple.com
```

- Il enregistre ce que le navigateur lui envoie, sous `.cloneme/` seulement.
- Avec `--source`, `http://localhost:6099/<chemin>` affiche `https://exemple.com/<chemin>`
  (lecture seule, GET uniquement).
- Contrôle : ouvrir une page relayée et comparer une mesure avec le vrai site
  (hauteur de page, taille du `h1`). Sur le test Stellar : identiques.
- Limite : un site qui exige une connexion, vérifie son nom de domaine ou
  charge tout depuis un autre domaine peut mal s'afficher dans le relais. Le
  dire, et mesurer alors la source directement (résultat recopié avec Write).

### Mesurer en lot

1. Ouvrir dans le navigateur intégré **une page relayée de la source**
   (`http://localhost:6099/…`) et **une page du clone** (`http://localhost:<port>/`).
2. Dans chaque onglet, une seule ligne :

```js
(await import('http://127.0.0.1:6099/__cloneme/mesurer.js')).lancer({ cote: 'source' })
```

```js
(await import('http://127.0.0.1:6099/__cloneme/mesurer.js')).lancer({ cote: 'clone' })
```

Options : `pages: ['P-03']`, `largeurs: [1440, 375]`, `attente: 1500` (ms
laissées aux entrées animées ; 4000 par défaut).

3. L'appel rend la main tout de suite : `javascript_tool` coupe à **45 s**, et
   12 pages-largeurs prennent environ une minute. Attendre la fin avec une
   boucle shell sur le fichier témoin :

```bash
until [ -f .cloneme/mesures/clone/_fini.txt ]; do sleep 2; done
```

Effacer `_fini.txt` avant de relancer une mesure du même côté.

Les fichiers arrivent dans `.cloneme/mesures/<source|clone>/<P-xx>@<largeur>.json`.
Le code de l'empreinte est dans `scripts/mesurer.js` (fonction `empreinte`).

Après une modification du clone, les cadres rechargent la page : pas besoin de
forcer le rechargement de l'onglet.

### Les sections animées

Dans le cadre caché, rien ne défile et rien ne s'anime : chaque côté reste à
son **état de départ**. Une entrée GSAP (`from: { y: 40, opacity: 0 }`) ou un
`useInView` du clone restent donc à `opacity: 0` décalés. On compare état de
départ à état de départ, avec trois règles pour les cibles :

- viser le **conteneur** d'une section animée (la `section`, la grille), pas
  l'élément qui entre : le conteneur ne bouge pas ;
- pour un carrousel, viser le cadre du carrousel, pas la diapositive (une
  minuterie change le texte affiché) ;
- un écart sur un élément animé lui-même (`y`, `opacity`) se juge avec la
  fiche `A-xx` et les valeurs `from` relevées, pas par la comparaison.

Le script signale à part l'opacité 0 d'un seul côté.

---

## 3. Comparer

```bash
node <dossier-CloneMe>/scripts/comparer-empreintes.mjs .cloneme/mesures/source/P-01@1440.json .cloneme/mesures/clone/P-01@1440.json
```

Le script rend un tableau d'écarts classés :

| Gravité | Règle |
|---|---|
| **fort** | cible absente d'un côté · couleur différente · famille de police différente · écart de taille ou de position > 8 px et > 5 % · débordement horizontal côté clone · hauteur de page > 10 % |
| **moyen** | écart 3–8 px · graisse, interligne, rayon, ombre, padding différents |
| **faible** | écart ≤ 2 px · différences d'écriture équivalentes (`0px` / `0`) |

Pour comparer toutes les pages d'un coup :

```bash
node <dossier-CloneMe>/scripts/comparer-empreintes.mjs --dossier .cloneme/mesures
```

---

## 4. Corriger, dans cet ordre

1. **Cibles absentes** — une section manque, un composant n'est pas rendu.
2. **Familles de police** — une police non chargée décale tout le reste.
3. **Couleurs et fonds** — corriger le token dans `tokens.css` **et**
   `palette.md`, jamais dans le composant.
4. **Largeurs de conteneur et grilles** — elles décident de toutes les
   positions en dessous.
5. **Tailles de texte et interlignes** — elles décident des hauteurs.
6. **Espacements** — paddings de section, gouttières.
7. **Détails** — rayons, ombres, bordures.

Puis remesurer. Une correction qui touche un token touche toutes les pages :
remesurer toutes les pages, pas seulement celle corrigée.

Un écart qu'on garde volontairement (police payante remplacée, ressource
absente, faute évidente de la source corrigée) est écrit dans le rapport avec
sa raison.

### Causes déjà rencontrées

Chercher d'abord ici : sur le test Stellar, ces six causes expliquaient tous
les écarts.

| Symptôme mesuré | Cause | Correctif |
|---|---|---|
| un bloc préformaté trop court | lignes vides perdues en lisant le HTML (filtre `grep -v '^$'`, `sed`) | relire le HTML **brut**, sans filtre, pour tout texte recopié |
| décalage qui n'apparaît qu'à une largeur | une valeur change dans un `@media` que le relevé à 1440 px ne voit pas (gouttière de grille) | relire les `@media` de la règle concernée, ajouter la valeur par largeur dans `tokens.css` |
| une règle responsive sans effet | sélecteur porté avec une spécificité plus faible que la source (`:not(.fixed)` oublié) | garder la spécificité d'origine |
| mots collés sous une largeur (`templatebuilt`) | JSX supprime le blanc après `<br />` | écrire `<br />{' '}` |
| éléments en ligne plus serrés (menu, icônes) | JSX supprime le blanc entre deux `<li>` `inline-block` | rétablir `' '` entre les éléments |
| décalage en fin de page | texte recopié de travers | reprendre le texte exact depuis le HTML brut |

---

## 5. Vérifications finales

### Navigation

- Chaque route de `design.md` §1 répond, avec le bon titre.
- Chaque lien interne de chaque page mène à une route existante :

```js
(async () => {
  const liens = [...new Set([...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')))]
    .filter(h => h && !/^(https?:|mailto:|tel:)/.test(h))
  return liens.map(h => ({ lien: h, existe: h.startsWith('#') ? !!document.querySelector(h) || h === '#' : null }))
})()
```

  et, pour les chemins, ouvrir chacun dans un cadre caché (même méthode que
  `mesurer.js`) et lire son `h1` : on ne doit pas tomber sur la 404 (sauf lien
  qui la vise). Les anciennes adresses de la source (`/page.html`) doivent
  rediriger vers la nouvelle route.
- Une route inconnue rend la 404.

### Interactions

Pour chaque interaction de `design.md` (menu mobile, modale, accordéon,
onglets, carrousel, formulaire) : la déclencher par `element.click()`, relire
le DOM (élément ouvert, `aria-expanded`, classe d'état), fermer (Échap, clic
dehors), relire. Écrire le résultat dans le rapport, une ligne par interaction.

#### Ce qui ne se déclenche pas dans l'onglet caché

Quand le panneau navigateur est caché, la page tourne en arrière-plan :

- `requestAnimationFrame` ne rend jamais la main — un `await` dessus bloque le
  script jusqu'au délai de 45 s ;
- l'événement `scroll` **n'est pas émis** après un `scrollTo()` ;
- l'`IntersectionObserver` ne répond pas.

Donc, pour un comportement lié au défilement :

1. faire défiler puis émettre l'événement à la main :
   `scrollTo(0, y); dispatchEvent(new Event('scroll'))` ;
2. lancer **la même séquence sur la source relayée et sur le clone**, et
   comparer les états (classe posée, lien actif, position) — c'est la preuve
   de fidélité ;
3. tester ce qui dépend de `requestAnimationFrame` (défilement animé, compteur)
   par un **test unitaire** où l'horloge et les images sont pilotées à la main
   (`vi.spyOn(performance, 'now')`, `vi.stubGlobal('requestAnimationFrame', …)`).

Aucun bouton sans effet :

```js
(() => [...document.querySelectorAll('button, [role=button]')].filter(b => b.getClientRects().length)
  .map(b => ({ texte: (b.innerText || b.getAttribute('aria-label') || '').trim().slice(0, 30),
    type: b.getAttribute('type'), dansForm: !!b.closest('form'), desactive: b.disabled })))()
```

puis, pour chacun, vérifier dans le code qu'il a un gestionnaire ou qu'il
soumet un formulaire.

### Tailles d'écran

À 1440, 1024, 768, 375 : pas de débordement horizontal
(`scrollWidth > innerWidth`), menu adapté, grilles empilées comme sur la
source (empreintes §2).

### Tests automatiques

Dans `ui/src/test/` :

- un test par page : la route rend son titre `h1` et ses sections ;
- un test par interaction logique : menu qui s'ouvre et se ferme, formulaire
  qui affiche une erreur puis l'état « envoyé (démo) », minuterie de
  carrousel (faux minuteurs limités à `setInterval`, voir animation-stealer) ;
- un test de la 404.

Ne jamais faire dépendre un test d'un `useInView` (bouchon inerte dans jsdom).

### La chaîne complète

```bash
cd ui
npx tsc --noEmit
npx vitest run
npm run build
node <dossier-CloneMe>/scripts/verifier-synchro.mjs ..
```

Les quatre passent, sinon ce n'est pas fini.

---

## 6. Le rapport — `RAPPORT-CLONAGE.md`

```md
# Rapport de clonage — <site>

## En bref
- Source : <url> · relevé le <date> · licence : <…>
- Pages : 6 clonées sur 7 identifiées (1 inaccessible)
- Chaîne : tsc ✅ · vitest ✅ 14 tests · build ✅ · synchro ✅
- Lancer : `start-all.bat` ou `cd ui && npm run dev` → http://localhost:6010

## Pages
| ID | Page | Statut | Écarts forts restants | Remarque |
|---|---|---|---|---|

## Ce qui a été testé
| Vérification | Comment | Résultat |
|---|---|---|
| Comparaison d'empreintes | 4 largeurs × 6 pages | 0 fort, 5 moyens |
| Liens internes | 38 liens | tous résolus |
| Menu mobile | clic, Échap, clic dehors | ✅ |

## Écarts restants
| Où | Écart | Raison | Gravité |
|---|---|---|---|

## Limites
- Inaccessible : … · Approximé : … · Ressources absentes : …
- À regarder en direct (non vérifiable ici) : animations au défilement A-03, A-05.

## Dépendances et technologies
| Paquet | Version | Pourquoi |
|---|---|---|

## Droits
- Licence du site, ressources reprises, ce qu'il faut remplacer avant publication.
```

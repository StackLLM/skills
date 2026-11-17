# Gabarit HTML — fiche Technical Mentor

> Autonome. Coller le squelette, puis assembler les briques.
> La charte de base vient de `CSS.css` (fond clair, cartes blanches, bleu `#2563eb`).
> Ce fichier ajoute **uniquement** les composants propres à la pédagogie.

---

## 1. Le squelette

```html
<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rate limiting — fiche Technical Mentor</title>
<meta name="mentor-domaine" content="Sécurité">
<meta name="mentor-date" content="2026-10-26">
<!-- mode architecture seulement : <meta name="mentor-mode" content="architecture"> -->
<meta name="mentor-resume" content="Compter les requêtes par client pour qu'un abus n'emporte pas le service.">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-light.min.css">
<style id="charte">/* CHARTE:DEBUT *//* CHARTE:FIN */</style>
</head>
<body>
<div class="container">

  <header class="hero">
    <span class="badge">Fiche technique · Sécurité</span>
    <h1>Rate limiting</h1>
    <p>Une phrase qui dit le problème résolu, pas la définition.</p>
    <div class="meta-fiche">
      <span>Prérequis : HTTP, adresse IP</span>
      <span>Lecture : 18 min</span>
      <span>26 octobre 2026</span>
    </div>
  </header>

  <!-- parcours, sommaire, les étapes, pied de page -->

</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/http.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/nginx.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/dockerfile.min.js"></script>
<script>if (window.hljs) hljs.highlightAll();</script>
</body>
</html>
```

La coloration syntaxique est **optionnelle** : hors ligne, le script ne charge
pas et le code reste lisible en noir sur fond clair.

**Langages de code.** Le fichier `highlight.min.js` ne contient que les langages
courants : `bash`, `javascript`, `json`, `yaml`, `sql`, `plaintext`, `python`,
`typescript`, `ini`, `xml`, `css`, `diff`… Les autres demandent leur module,
chargé **après** lui : `http`, `nginx` et `dockerfile` sont déjà dans le
squelette ; en ajouter un autre sur le même modèle
(`…/11.9.0/languages/<nom>.min.js`). Un langage sans module officiel (Terraform /
`hcl`) s'écrit `language-plaintext`. Sinon la console affiche
« Could not find the language ». `verifier.py` le contrôle.

---

## 2. Le style : rien à écrire

La fiche ne contient **aucun CSS**. Elle porte seulement ce bloc vide :

```html
<style id="charte">/* CHARTE:DEBUT *//* CHARTE:FIN */</style>
```

`scripts/indexer.py --maj-charte` y colle, dans l'ordre :

| Source | Ce qu'elle apporte |
|---|---|
| `REVISION-TECHNIQUE/CSS.css` | la charte de la maison : fond clair, cartes, tableaux, hero, sommaire |
| `references/mentor.css` | les composants pédagogiques listés ci-dessous |

Conséquence : la fiche est **autonome** — un seul fichier, déplaçable et
partageable — alors que la charte reste à un seul endroit. Modifier `CSS.css`
puis relancer la commande met à jour toutes les fiches.

### Les composants disponibles

| Famille | Classes |
|---|---|
| En-tête | `.meta-fiche`, `.parcours` + `.p-num` + `.p-lab` |
| Étape | `.etape`, `.etape-tete`, `.etape-num`, `.etape-kick` |
| Niveau | `.niv` + `.n-essentiel` / `.n-oeuvre` / `.n-avance` |
| Vocabulaire | `.terme`, `.def`, `.prerequis` |
| Progression | `ol.pas` |
| Schéma | `.schema` + SVG inline |
| Code | `.code-bloc`, `.code-tete`, `table.expl` |
| Encadrés | `.bloc` + `.cle` / `.piege` / `.verif` / `.limite` / `.danger-bloc`, `.cadre-legal` |
| Solution | `.decision` + `.d-q` / `.d-opt` / `.d-choix`, `.a-dire` |
| Marques | `.danger`, `.chip` + `.fait` / `.pratique` / `.contexte` / `.a-confirmer` |
| Entretien | `.expert`, `.rep`, `.rep.longue`, `.relance`, `.ne-pas-dire` |
| Contrôle | `.quiz`, `<details>`, `.q-num`, `.q-txt`, `.q-rep` |

Le détail de chaque règle est dans `references/mentor.css`.

---

## 3. Les briques HTML

### Parcours (juste sous le hero)

```html
<nav class="parcours">
  <a href="#probleme"><span class="p-num">01</span><span class="p-lab">Le problème</span></a>
  <a href="#mecanisme"><span class="p-num">02</span><span class="p-lab">Le mécanisme</span></a>
  <a href="#solution"><span class="p-num">03</span><span class="p-lab">La solution</span></a>
  <a href="#oeuvre"><span class="p-num">04</span><span class="p-lab">Mise en œuvre</span></a>
  <a href="#ingenieur"><span class="p-num">05</span><span class="p-lab">Niveau ingénieur</span></a>
  <a href="#expert"><span class="p-num">06</span><span class="p-lab">Face à l'expert</span></a>
  <a href="#controle"><span class="p-num">07</span><span class="p-lab">Contrôle</span></a>
</nav>
```

En **mode architecture**, les deux premiers liens changent, le lien
« La solution » disparaît, et les suivants reprennent les numéros 03 à 06 :

```html
  <a href="#vue"><span class="p-num">01</span><span class="p-lab">Vue d'ensemble</span></a>
  <a href="#mecanisme"><span class="p-num">02</span><span class="p-lab">Les échanges</span></a>
```

### Briques du mode architecture

**Fonction → pièce nécessaire** (ouvre l'étape 1, remplace le problème) :

```html
<table>
  <tr><th>Fonction</th><th>Ce qu'elle oblige à avoir</th></tr>
  <tr><td>Publier un texte avec une photo</td><td>un stockage de fichiers, un traitement en arrière-plan</td></tr>
</table>
```

**Les zones** :

```html
<table>
  <tr><th>Zone</th><th>Pièces</th><th>Où ça tourne</th></tr>
  <tr><td><b>Client</b></td><td>le frontend React</td><td>dans le navigateur de chaque utilisateur</td></tr>
</table>
```

**Rôle de chaque pièce** : un `.def` par boîte du schéma complet, dans l'ordre
du schéma.

**Environnements** :

```html
<table>
  <tr><th></th><th>Local (dev)</th><th>Staging</th><th>Production</th></tr>
  <tr><td>Adresse</td><td><code>localhost:5173</code></td><td><code>staging.app.exemple.com</code></td><td><code>app.exemple.com</code></td></tr>
</table>
```

**Échange montré en texte** (étape 2) : un `.code-bloc` qui contient la requête
puis la réponse, suivi d'un `table.expl` qui explique chaque ligne importante.

**Règles qui tiennent l'ensemble** : un tableau règle → conséquence, puis un
`.bloc.cle` « À retenir — à redessiner de mémoire ».

### Étape 03 — la solution en mots (aucun code ici)

L'étape se compose toujours des cinq mêmes blocs, dans cet ordre.

```html
<section class="etape anchor" id="solution">
  <div class="etape-tete">
    <div class="etape-num">03</div>
    <div><div class="etape-kick">Ce qu'on fait</div><h2>La solution, en mots</h2></div>
  </div>

  <!-- 1. la solution en une phrase -->
  <div class="bloc cle">
    <div class="b-tete">La solution en une phrase</div>
    <p>...une seule phrase, qu'on doit pouvoir répéter de mémoire.</p>
  </div>

  <!-- 2. les décisions : trois au minimum -->
  <h3>Les décisions à prendre <span class="niv n-essentiel">Essentiel</span></h3>

  <div class="decision">
    <div class="d-q">La question posée par la solution ?</div>
    <div class="d-opt"><b>Option A</b> — ce qu'elle apporte, ce qu'elle coûte.</div>
    <div class="d-opt"><b>Option B</b> — ce qu'elle apporte, ce qu'elle coûte.</div>
    <div class="d-choix"><b>Retenu :</b> le choix, et sa conséquence directe.</div>
  </div>

  <!-- 3. le raccord au problème -->
  <h3>Ce que la solution règle, point par point</h3>
  <table>
    <thead><tr><th>Ce qui cassait (étape 1)</th><th>Ce que la solution en fait</th></tr></thead>
    <tbody>
      <tr><td>...</td><td>...</td></tr>
    </tbody>
  </table>

  <!-- 4. ce qu'on dit à l'oral -->
  <div class="a-dire">
    <div class="b-tete">Ce que je dis, sans montrer de code</div>
    <p>...dix à vingt lignes, prononçables telles quelles.</p>
  </div>

  <!-- 5. les limites assumées -->
  <div class="bloc limite">
    <div class="b-tete">Ce que ça ne règle pas</div>
    <p>...et ce qu'il faut en plus.</p>
  </div>
</section>
```

| Règle | Détail |
|---|---|
| Aucun `<pre>`, aucun `<code>` de bloc | le code vit dans l'étape 04 |
| Trois `.decision` au minimum | une décision sans conséquence écrite n'est pas une décision |
| Le tableau de raccord | reprend les points de l'étape 1 **dans le même ordre** |
| `.a-dire` | se lit à voix haute et tient tout seul |

### Tête d'étape

```html
<section class="etape anchor" id="mecanisme">
  <div class="etape-tete">
    <div class="etape-num">02</div>
    <div>
      <div class="etape-kick">Comment ça marche</div>
      <h2>Le mécanisme, de l'intérieur</h2>
    </div>
  </div>
  ...
</section>
```

### Terme et définition

```html
<p>Le serveur garde un <span class="terme">compteur</span> par client.</p>
<div class="def"><b>Compteur</b> — une valeur entière, rangée en mémoire,
qui monte de 1 à chaque requête et retombe à zéro à la fin de la fenêtre.</div>
```

### Prérequis

```html
<div class="prerequis">
  <h4>Avant de lire : deux choses à savoir</h4>
  <p><b>En-tête HTTP</b> — une ligne <code>Nom: valeur</code> envoyée avant le corps de la réponse.</p>
  <p><b>Adresse IP source</b> — l'adresse de la machine qui ouvre la connexion.</p>
</div>
```

### Bloc de code avec explication ligne par ligne

```html
<div class="code-bloc">
  <div class="code-tete"><span class="pt"></span>api/middleware/limite.js · Node 20 + Express 4</div>
  <pre><code class="language-javascript">const seau = new Map()</code></pre>
  <table class="expl">
    <tr><td>ligne 1</td><td>Une table en mémoire : une entrée par client. Elle disparaît au redémarrage.</td></tr>
  </table>
</div>
```

### Encadrés

```html
<div class="bloc cle"><div class="b-tete">À retenir</div>…</div>
<div class="bloc piege"><div class="b-tete">⚠ Piège</div>…</div>
<div class="bloc verif"><div class="b-tete">✓ Vérifier</div>…</div>
<div class="bloc danger-bloc"><div class="b-tete">Commande destructive</div>…</div>
```

### Niveaux

```html
<h3>Le seau à jetons <span class="niv n-avance">Approfondissement</span></h3>
```

### Entretien

```html
<section class="etape anchor" id="expert">
  <div class="etape-tete">
    <div class="etape-num">05</div>
    <div><div class="etape-kick">Savoir le défendre</div><h2>Face à l'expert</h2></div>
  </div>

  <div class="expert">
    <div class="rep">
      <div class="r-lab">Réponse courte — entretien</div>
      <p>…</p>
    </div>

    <div class="rep longue">
      <div class="r-lab">Réponse approfondie — discussion d'ingénieur</div>
      <p>…</p>
    </div>

    <h3>Les relances probables</h3>
    <div class="relance">
      <div class="q">« À quel niveau tu le places ? »</div>
      <div class="a">Ce qu'il faut savoir : …</div>
    </div>

    <div class="ne-pas-dire">
      <div class="b-tete">À ne pas dire</div>
      <p>…</p>
    </div>
  </div>
</section>
```

### Contrôle

```html
<div class="quiz">
  <div class="q-num">Question 1</div>
  <div class="q-txt">Deux instances, une limite de 100 requêtes par minute. Que se passe-t-il ?</div>
  <details>
    <summary>Voir la correction</summary>
    <div class="q-rep">…</div>
  </details>
</div>
```

### Cadre légal (sujets offensifs)

```html
<div class="cadre-legal">
  <b>Cadre légal.</b> Les manipulations de cette fiche se font sur une machine
  dont on est propriétaire, ou sur une plateforme d'entraînement qui l'autorise
  par écrit. Les mener sur un système tiers est un délit.
</div>
```

---

## 4. Les schémas SVG

Deux familles suffisent. Toujours en SVG inline, jamais d'image.

### A. Chaîne de composants (flux d'une requête)

```html
<figure class="schema">
<svg viewBox="0 0 840 170" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Le chemin d'une requête">
  <defs>
    <marker id="fl" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
      <polygon points="0 0, 9 3.5, 0 7" fill="#7FB3E0"/>
    </marker>
    <style>
      .bx{fill:#fff;stroke:#C8DEF3;stroke-width:1.5;rx:12}
      .bx-a{fill:#F2F7FD;stroke:#7FB3E0}
      .bx-b{fill:#FBF5EA;stroke:#E6D5BA}
      .t{font:600 13px Inter,system-ui,sans-serif;fill:#1e3a8a;text-anchor:middle}
      .s{font:11px Inter,system-ui,sans-serif;fill:#64748b;text-anchor:middle}
      .ln{stroke:#7FB3E0;stroke-width:1.6;marker-end:url(#fl)}
      .lb{font:10px Inter,system-ui,sans-serif;fill:#64748b;text-anchor:middle}
    </style>
  </defs>

  <rect class="bx bx-a" x="10"  y="55" width="150" height="58"/>
  <text class="t" x="85"  y="80">Client</text>
  <text class="s" x="85"  y="98">navigateur</text>

  <line class="ln" x1="166" y1="84" x2="214" y2="84"/>
  <text class="lb" x="190" y="76">HTTP</text>

  <rect class="bx bx-b" x="220" y="55" width="170" height="58"/>
  <text class="t" x="305" y="80">nginx</text>
  <text class="s" x="305" y="98">proxy inverse</text>

  <line class="ln" x1="396" y1="84" x2="444" y2="84"/>

  <rect class="bx" x="450" y="55" width="170" height="58"/>
  <text class="t" x="535" y="80">API Node</text>
  <text class="s" x="535" y="98">port 3000</text>
</svg>
<figcaption>Chaque boîte porte un nom réel du système décrit.</figcaption>
</figure>
```

### B. Diagramme de séquence (qui dit quoi, dans quel ordre)

Trois colonnes verticales, des flèches horizontales numérotées.
Même palette. Les lignes de vie en `stroke="#E3EEFA"` et `stroke-dasharray="4 4"`.

```html
<figure class="schema">
<svg viewBox="0 0 760 300" xmlns="http://www.w3.org/2000/svg" role="img"
     aria-label="Séquence d'une requête limitée">
  <defs><marker id="fl2" markerWidth="9" markerHeight="7" refX="8" refY="3.5" orient="auto">
    <polygon points="0 0, 9 3.5, 0 7" fill="#7FB3E0"/></marker>
    <style>
      .act{fill:#F2F7FD;stroke:#7FB3E0;stroke-width:1.5;rx:10}
      .t{font:600 12px Inter,sans-serif;fill:#1e3a8a;text-anchor:middle}
      .vie{stroke:#E3EEFA;stroke-width:1.5;stroke-dasharray:4 4}
      .msg{stroke:#7FB3E0;stroke-width:1.5;marker-end:url(#fl2)}
      .ml{font:11px Inter,sans-serif;fill:#334155}
    </style>
  </defs>
  <rect class="act" x="40" y="14" width="130" height="34"/><text class="t" x="105" y="36">Client</text>
  <line class="vie" x1="105" y1="48" x2="105" y2="280"/>
  <!-- ... autres acteurs et messages ... -->
</svg>
</figure>
```

**Règles des schémas**

| Règle | Pourquoi |
|---|---|
| Chaque boîte porte un nom réel | un schéma générique n'apprend rien |
| Pas plus de 6 boîtes | au-delà, couper en deux schémas — sauf la carte complète du mode architecture |
| Classes préfixées par schéma (`va-bx`, `vs-msg`…) et `id` de marqueur unique | les `<style>` des SVG inline s'appliquent à **toute** la page : deux schémas qui définissent `.lb` se mélangent (texte décalé, rogné) |
| Pas de texte en travers d'une flèche | faire passer la flèche par le bord, ou déplacer l'étiquette |
| Les flèches sont étiquetées | sinon on ne sait pas ce qui circule |
| `viewBox` + `max-width:100%` | lisible sur téléphone |
| `role="img"` + `aria-label` | la fiche reste accessible |

---

## 5. Pied de page

```html
<footer class="footer">
  Fiche Technical Mentor · Rate limiting · 26 octobre 2026<br>
  Prochaine étape conseillée : <a href="reverse-proxy.html">reverse proxy</a>.
</footer>
```

---

## 6. Après avoir écrit la fiche

```bash
cd <dossier de la skill>/scripts
python indexer.py --maj-charte
python verifier.py
```

`indexer.py --maj-charte` injecte le style dans chaque fiche et réécrit
`index.html` à partir des métadonnées. `verifier.py` contrôle la checklist :
étapes manquantes, correction visible, analogie interdite, bloc d'entretien
absent, commande destructive non marquée.

Puis **ouvrir le HTML et le regarder**. Les deux scripts ne voient pas le rendu.

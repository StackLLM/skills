---
name: diagram-premium
description: Use when the user wants a premium diagram to present a project, an app, or a feature — navigation map, user flow, lifecycle / state diagram, sitemap — to be opened in draw.io (diagrams.net). Produces a self-contained .drawio (mxGraph XML) file with the Forêt design charter. Self-contained: every style string, layout recipe, escaping rule and a working template is in this file, so any LLM (Claude, Kimi, etc.) can reproduce the exact look without the project repo. Adapt the content to the app/feature the user describes.
---

# Skill — Diagramme premium (draw.io / diagrams.net)

## Ce que produit cette skill

Un fichier **`.drawio`** (XML mxGraph) que l'utilisateur ouvre dans
**app.diagrams.net → File → Open From → Device** : le diagramme apparaît **déjà mis
en page**, look « cabinet conseil », charte Forêt (vert sapin, bleu, papier crème, titres
serif, ombres, coins arrondis, dégradés). Plusieurs pages = plusieurs onglets dans
draw.io. Exportable en **PNG / PDF** (File → Export as) pour une présentation.

Trois usages typiques :
1. **Présenter une app entière** → 3 pages : *Parcours principal* · *Navigation complète* · *Cycle de vie*.
2. **Présenter une feature** → 1-2 pages : *Flux de la feature* (+ *Avant / Après* ou *États & cas limites*).
3. **Présenter un projet / une logique** → 1 page : schéma d'architecture ou de décision.

**Règles d'or :** on n'invente ni chiffre ni fait ; on utilise les **vraies données**
de l'app/feature (codes, noms, statuts) comme exemples. Français soigné, orthographe
vérifiée. Pas de cases surchargées (titre en gras + 1 à 3 lignes max).

---

## Workflow en 5 étapes

1. **Cadrer le sujet.** Récupérer auprès de l'utilisateur : l'app ou la feature à
   illustrer, son déroulé, et **2-3 exemples réels** (un code, un nom, un statut). Si
   c'est une feature seule → 1-2 pages ; si c'est l'app entière → 3 pages.
2. **Choisir le ou les gabarits** (section *Gabarits de page*).
3. **Assembler les cellules** avec les *Styles réutilisables* + la *Recette de mise en
   page*. Router chaque flèche avec des ancres (`exitX/entryX`) pour qu'**aucun
   libellé ne tombe sur une case**.
4. **Valider le XML** (section *Validation*). Un fichier mal formé ne s'ouvre pas.
5. **Livrer** le `.drawio` + dire comment l'ouvrir et l'exporter (PNG/PDF).

---

## Charte Forêt (jetons de couleur & polices)

| Rôle | Couleur | Dégradé | Bordure |
|---|---|---|---|
| Fond papier (canvas) | `#FAF8F4` | — | — |
| Encre (titres, bandeaux) | `#0E1A24` | — | — |
| **Vert primaire** (étapes, actions) | `#3F8A3D` | `#4FA34C` | `#2C6A2A` |
| **Bleu secondaire** (entrée, aval, admin) | `#1B5F8C` | `#2A74A6` | `#13476A` |
| **Or** (décision, point clé) | `#B8860B` | `#D4A017` | `#8A6608` |
| **Émeraude** (succès / état final) | `#10B981` | `#34D399` | `#0B7A5E` |
| **Rouge** (échec / blocage) | `#EF4444` | `#F87171` | `#B91C1C` |
| Carte blanche | `#FFFFFF` | — | `#3F8A3D` ou `#CBD5C0` |
| Panneau de groupe | `#F1EEE8` | — | `#E2DBCF` |
| Encadré or doux (exemple) | `#FCF6E8` | — | `#B8860B` |
| Texte secondaire | `#475569` / `#64748B` | — | — |

**Échelle d'alerte (réutilisable comme légende)** : Confortable `#3F8A3D` · Correct
`#06B6D4` · Court `#F59E0B` · Critique `#EF4444` · Dépassé `#111827` · (état spécial
« validé/déposé » `#10B981`).

**Polices** : titres et bandeaux en **serif** `fontFamily=Georgia` (rendu « Instrument
Serif » dans la charte Forêt) ; corps et cartes en **`fontFamily=Helvetica`**. draw.io connaît
Georgia et Helvetica par défaut → aucun réglage requis.

---

## Styles réutilisables (chaînes `style=` à copier telles quelles)

> Coller dans l'attribut `style="…"` d'un `mxCell vertex="1"`. Tous incluent
> `rounded=1;whiteSpace=wrap;html=1;shadow=1` pour le look premium.

```
NŒUD ENTRÉE / AVAL (bleu)
rounded=1;whiteSpace=wrap;html=1;arcSize=12;fillColor=#1B5F8C;gradientColor=#2A74A6;strokeColor=#13476A;fontColor=#FFFFFF;fontFamily=Helvetica;shadow=1;

NŒUD ÉTAPE / ACTION (vert)
rounded=1;whiteSpace=wrap;html=1;arcSize=12;fillColor=#3F8A3D;gradientColor=#4FA34C;strokeColor=#2C6A2A;fontColor=#FFFFFF;fontFamily=Helvetica;shadow=1;

NŒUD POINT CLÉ / VERDICT (or)
rounded=1;whiteSpace=wrap;html=1;arcSize=12;fillColor=#B8860B;gradientColor=#D4A017;strokeColor=#8A6608;fontColor=#FFFFFF;fontFamily=Helvetica;shadow=1;

NŒUD SUCCÈS / ÉTAT FINAL (émeraude)
rounded=1;whiteSpace=wrap;html=1;arcSize=12;fillColor=#10B981;gradientColor=#34D399;strokeColor=#0B7A5E;fontColor=#0E1A24;fontFamily=Helvetica;fontStyle=1;shadow=1;

NŒUD ÉCHEC / BLOCAGE (rouge)
rounded=1;whiteSpace=wrap;html=1;arcSize=12;fillColor=#EF4444;gradientColor=#F87171;strokeColor=#B91C1C;fontColor=#FFFFFF;fontFamily=Helvetica;shadow=1;

CARTE (blanc, bord vert) — pour listes d'actions / sous-pages
rounded=1;whiteSpace=wrap;html=1;arcSize=10;fillColor=#FFFFFF;strokeColor=#3F8A3D;fontColor=#0E1A24;fontFamily=Helvetica;align=left;spacingLeft=10;spacingRight=8;shadow=1;

BANDEAU DE SECTION (barre encre)
rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#0E1A24;strokeColor=none;fontColor=#FFFFFF;fontFamily=Georgia;fontSize=14;fontStyle=1;shadow=1;

PANNEAU DE GROUPE (fond derrière une colonne de cartes)
rounded=1;whiteSpace=wrap;html=1;arcSize=8;fillColor=#F1EEE8;strokeColor=#E2DBCF;

ENCADRÉ EXEMPLE (or doux)
rounded=1;whiteSpace=wrap;html=1;arcSize=10;fillColor=#FCF6E8;strokeColor=#B8860B;fontColor=#0E1A24;fontFamily=Helvetica;align=left;spacingLeft=14;spacingRight=14;shadow=1;

DÉCISION (losange or)
rhombus;whiteSpace=wrap;html=1;fillColor=#B8860B;gradientColor=#D4A017;strokeColor=#8A6608;fontColor=#FFFFFF;fontFamily=Helvetica;fontStyle=1;shadow=1;

TITRE DE PAGE (texte, sans fond)
text;html=1;align=left;verticalAlign=middle;fontFamily=Georgia;fontSize=30;fontStyle=1;fontColor=#0E1A24;

SOUS-TITRE (texte, sans fond)
text;html=1;align=left;verticalAlign=middle;fontFamily=Helvetica;fontSize=15;fontColor=#475569;

BADGE MARQUE (coin haut-droit)
rounded=1;whiteSpace=wrap;html=1;arcSize=18;fillColor=#3F8A3D;gradientColor=#4FA34C;strokeColor=none;fontColor=#FFFFFF;fontFamily=Georgia;fontSize=15;fontStyle=1;shadow=1;
```

**Flèches (`mxCell edge="1"`)** — toujours `edgeStyle=orthogonalEdgeStyle;rounded=1` :

```
FLÈCHE VERTE (flux normal)
edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;strokeColor=#3F8A3D;strokeWidth=2.5;fontColor=#2C6A2A;fontSize=11;fontStyle=1;

FLÈCHE BLEUE (entrée / aval)
edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;strokeColor=#1B5F8C;strokeWidth=2.5;fontColor=#1B5F8C;fontSize=11;fontStyle=1;

FLÈCHE EN POINTILLÉ (boucle / secondaire)  → ajouter : dashed=1;
FLÈCHE ROUGE (branche d'échec)              → strokeColor=#B91C1C;fontColor=#B91C1C;
```

---

## Règle anti-chevauchement (la plus importante)

Le défaut le plus fréquent : un **libellé de flèche se pose sur le texte d'une case**
parce que la flèche traverse la boîte. Deux règles l'évitent :

1. **Ancrer chaque flèche** avec les points de sortie/entrée dans le `style` de
   l'arête :
   - chaîne horizontale (gauche→droite) : `exitX=1;exitY=0.5;entryX=0;entryY=0.5;`
   - transition verticale (haut→bas) : `exitX=0.5;exitY=1;entryX=0.5;entryY=0;`
2. **Ne jamais faire passer une flèche à travers une rangée de boîtes.** Si la cible
   est « plus bas, de l'autre côté », place plutôt la cible sur une autre page
   (gabarit *Navigation complète*) ou laisse un espace vide dédié. Les **libellés se
   posent dans les zones vides** (les écarts entre rangées), jamais sur une case.

Astuce groupe sans spaghetti : pour lister des sous-pages/actions sous un titre,
utilise un **PANNEAU** (fond) + un **BANDEAU** (en-tête) + des **CARTES** empilées,
**sans flèches internes**. L'alignement suffit à montrer le groupe.

---

## Recette de mise en page (coordonnées)

- **Canvas papier** : sur `mxGraphModel`, mettre `background="#FAF8F4"`. Régler
  `pageWidth` / `pageHeight` au contenu (ex. `1760 × 1040`).
- **En-tête** : titre `x=60 y=28`, sous-titre `x=62 y=74`, badge marque en haut à
  droite `x=1500 y=32 w=200 h=70`.
- **Chaîne d'étapes** (flux) : boîtes `w=250 h=150`, **pas de 274** (24 px de
  gouttière). Départ `x=70`. → x = 70, 344, 618, 892, 1166, 1440.
- **Transition entre rangées** : flèche verticale, **libellé dans l'écart** (laisser
  ≥ 50 px de vide entre deux rangées).
- **Colonnes (sitemap)** : 6 colonnes sur 1760 → panneaux `w=264`, pas de 276
  (x = 54, 330, 606, 882, 1158, 1434). En-tête `h=42` en haut du panneau, cartes
  `w=248 h≈86` empilées tous les ~94 px.
- **Légende** : barre encre (BANDEAU) + pastilles colorées de l'échelle d'alerte en
  rangée.

---

## Échappement du texte des cases (à respecter à la lettre)

Le `value` d'une case est de l'**HTML dans un attribut XML**. Donc :

| Pour afficher… | Écrire dans `value="…"` |
|---|---|
| retour à la ligne | `&lt;br&gt;` |
| gras | `&lt;b&gt;…&lt;/b&gt;` · italique `&lt;i&gt;…&lt;/i&gt;` |
| petite taille | `&lt;span style='font-size:11px'&gt;…&lt;/span&gt;` |
| un `&` littéral | `&amp;amp;` (devient `&amp;` en HTML, qui affiche `&`) |
| accents é è à ç … | **directement** (fichier en UTF-8) |
| emoji 🔒 ✓ → | **directement** (draw.io les rend) |

- **Guillemets** dans les styles inline : utiliser des **apostrophes** (`style='…'`),
  jamais de `"` (qui casserait l'attribut XML).
- Toujours **enregistrer le fichier en UTF-8**.

---

## Squelette de fichier (structure mxGraph)

```xml
<mxfile host="app.diagrams.net" type="device">
  <diagram name="1 · Titre de page" id="page-1">
    <mxGraphModel dx="1024" dy="720" grid="0" guides="1" page="1"
        pageWidth="1760" pageHeight="1040" background="#FAF8F4">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <!-- … cellules (vertex) puis flèches (edge) … -->
      </root>
    </mxGraphModel>
  </diagram>
  <!-- pages supplémentaires = <diagram> supplémentaires (onglets) -->
</mxfile>
```

- `id="0"` et `id="1"` sont obligatoires (couche racine). Tout le reste a
  `parent="1"`.
- Les **ids doivent être uniques dans une même page** ; on peut les répéter d'une page
  à l'autre, mais **préfixer par page** (`p1_`, `p2_`…) évite toute confusion.
- Une flèche : `edge="1"` + `source="idA"` + `target="idB"` + un enfant
  `<mxGeometry relative="1" as="geometry" />`.

---

## Gabarits de page

### A. Parcours principal (flux « commence ici »)
Entrée → Point central → **chaîne d'étapes** (l'assistant/feature) → sortie/livrable.
Ajouter un **ENCADRÉ EXEMPLE** (fil rouge avec vraies données) et une **légende** si
une échelle existe. Flux strictement linéaire, sans branche qui croise.

### B. Navigation complète (sitemap)
Un **hub central** en haut (le point de départ) → flèches vers N **panneaux-colonnes**
(les grandes sections). Chaque panneau : BANDEAU (nom de section) + CARTES (les
sous-pages / actions). Idéal pour montrer « tout ce que fait l'app ».

### C. Cycle de vie / états (scénarios)
Suite d'**états** avec un **losange de DÉCISION** qui ouvre 2 branches (ex.
succès vert / échec rouge), des **actions latérales** (cartes) et des **boucles** en
pointillé (réessai, réévaluation). Marquer les actions verrouillées (🔒) et l'expliquer
en légende.

> Feature seule : souvent **A + C** suffisent (le flux + les cas limites / états).

---

## Gabarit minimal prêt à l'emploi (valide, à adapter)

```xml
<mxfile host="app.diagrams.net" type="device">
  <diagram name="1 · Parcours" id="p1">
    <mxGraphModel dx="1024" dy="720" grid="0" guides="1" page="1" pageWidth="1300" pageHeight="560" background="#FAF8F4">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="t" value="Titre du parcours" style="text;html=1;align=left;verticalAlign=middle;fontFamily=Georgia;fontSize=28;fontStyle=1;fontColor=#0E1A24;" vertex="1" parent="1"><mxGeometry x="40" y="24" width="800" height="40" as="geometry"/></mxCell>
        <mxCell id="bdg" value="MARQUE&lt;br&gt;&lt;span style='font-size:10px;font-weight:normal'&gt;sous-titre&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;arcSize=18;fillColor=#3F8A3D;gradientColor=#4FA34C;strokeColor=none;fontColor=#FFFFFF;fontFamily=Georgia;fontSize=14;fontStyle=1;shadow=1;" vertex="1" parent="1"><mxGeometry x="1080" y="24" width="180" height="60" as="geometry"/></mxCell>
        <mxCell id="a" value="&lt;b&gt;1. Entrée&lt;/b&gt;&lt;br&gt;&lt;span style='font-size:11px'&gt;point de départ&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;arcSize=12;fillColor=#1B5F8C;gradientColor=#2A74A6;strokeColor=#13476A;fontColor=#FFFFFF;fontFamily=Helvetica;shadow=1;" vertex="1" parent="1"><mxGeometry x="40" y="150" width="240" height="100" as="geometry"/></mxCell>
        <mxCell id="b" value="&lt;b&gt;2. Étape clé&lt;/b&gt;&lt;br&gt;&lt;span style='font-size:11px'&gt;&lt;i&gt;ex. donnée réelle&lt;/i&gt;&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;arcSize=12;fillColor=#3F8A3D;gradientColor=#4FA34C;strokeColor=#2C6A2A;fontColor=#FFFFFF;fontFamily=Helvetica;shadow=1;" vertex="1" parent="1"><mxGeometry x="360" y="150" width="240" height="100" as="geometry"/></mxCell>
        <mxCell id="c" value="&lt;b&gt;3. Résultat&lt;/b&gt;&lt;br&gt;&lt;span style='font-size:11px'&gt;livrable&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;arcSize=12;fillColor=#10B981;gradientColor=#34D399;strokeColor=#0B7A5E;fontColor=#0E1A24;fontFamily=Helvetica;fontStyle=1;shadow=1;" vertex="1" parent="1"><mxGeometry x="680" y="150" width="240" height="100" as="geometry"/></mxCell>
        <mxCell id="ex" value="&lt;b&gt;Exemple fil rouge&lt;/b&gt;&lt;br&gt;&lt;span style='font-size:11px'&gt;remplacer par un cas concret avec de vraies données.&lt;/span&gt;" style="rounded=1;whiteSpace=wrap;html=1;arcSize=10;fillColor=#FCF6E8;strokeColor=#B8860B;fontColor=#0E1A24;fontFamily=Helvetica;align=left;spacingLeft=14;shadow=1;" vertex="1" parent="1"><mxGeometry x="40" y="330" width="880" height="80" as="geometry"/></mxCell>
        <mxCell id="e1" value="démarrer" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;strokeColor=#1B5F8C;strokeWidth=2.5;fontColor=#1B5F8C;fontSize=11;fontStyle=1;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="a" target="b"><mxGeometry relative="1" as="geometry"/></mxCell>
        <mxCell id="e2" style="edgeStyle=orthogonalEdgeStyle;rounded=1;html=1;endArrow=block;strokeColor=#3F8A3D;strokeWidth=2.5;exitX=1;exitY=0.5;entryX=0;entryY=0.5;" edge="1" parent="1" source="b" target="c"><mxGeometry relative="1" as="geometry"/></mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

---

## Validation (obligatoire avant de livrer)

Vérifier que le XML est bien formé — sinon draw.io refuse le fichier :

```bash
python -c "import xml.dom.minidom as m; d=m.parse('mon-diagramme.drawio'); print('Pages:', len(d.getElementsByTagName('diagram')), '— OK')"
```

Si erreur de parsing : presque toujours un `<` / `>` / `&` non échappé dans un `value`,
ou un `"` à l'intérieur d'un attribut. Reprendre la section *Échappement*.

---

## Adapter à une app ou une feature (protocole)

1. **Demander à l'utilisateur** : le sujet (app entière ou feature), son déroulé, et
   **les vraies données** à montrer (codes, noms, statuts, états). Charte Forêt par
   défaut (sinon, remplacer les jetons de couleur du tableau *Charte*).
2. **Choisir les pages** : app → A + B + C ; feature → A (+ C si elle a des états/cas
   limites). 1 page = 1 `<diagram>`.
3. **Remplir les cases** avec les exemples réels — **jamais de données inventées**. Si
   une info manque, la demander plutôt que la fabriquer.
4. **Assembler** : styles ci-dessus + recette de mise en page + ancres de flèches.
5. **Valider** le XML, puis **livrer** le `.drawio` avec le mode d'emploi ci-dessous.

**Mode d'emploi à donner à l'utilisateur :**
> Ouvrir **app.diagrams.net → File → Open From → Device** et choisir le fichier. Les
> pages sont des **onglets en bas**. Pour une présentation : **File → Export as →
> PNG / PDF** (page par page ou tout).

---

## Garde-fous

- **Vraies données uniquement** ; pas de chiffres ni de faits inventés.
- **Français soigné**, orthographe vérifiée (c'est un livrable de présentation).
- **Cases concises** : titre en gras + 1 à 3 lignes. Le détail va dans la légende ou
  un encadré, pas dans la boîte.
- **Une légende** par diagramme dès qu'il y a une échelle codée (niveaux, couleurs,
  verrous 🔒).
- **Toujours valider le XML** avant de livrer.
- Ne pas surcharger une page : si ça déborde, **ajouter une page** (onglet) plutôt que
  tout entasser.

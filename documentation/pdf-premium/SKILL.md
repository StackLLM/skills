---
name: pdf-premium
description: Use when the user asks for a PDF deliverable — fiche technique, rapport, dossier, note de présentation, livrable client — and wants the premium "cabinet conseil" look (charte Forêt) (cover page, sections, cards, page de fin). Self-contained : everything needed (CSS, HTML blocks, render command) is in this file, so any LLM (Claude, Kimi, etc.) can reproduce the exact template without the project repo.
---

# Skill — PDF premium (template « cabinet conseil »)

## Ce que produit cette skill

Un PDF A4 élégant et professionnel : page de couverture pleine, sommaire, sections
numérotées, cartes / encadrés / exemples, tableaux soignés, pastilles de statut,
page de fin. Charte **Forêt** (vert sapin + papier crème, polices
Inter / JetBrains Mono). Optimisé pour **WeasyPrint** (HTML → PDF).

**Règle d'or :** on n'invente pas de chiffres ni de faits. Pas de captures d'écran
(texte structuré uniquement). Français soigné, orthographe vérifiée.

## Workflow en 3 étapes

1. **Rédiger le contenu** en suivant les *Règles d'écriture* (plus bas).
2. **Monter le HTML** : coller le `<style>` complet (section *CSS complet*) puis
   assembler les *Briques HTML* (couverture → sommaire → sections → page de fin).
3. **Rendre le PDF** avec le snippet WeasyPrint (section *Rendu PDF*).

Livrer **les deux** fichiers : le `.html` source + le `.pdf`.

---

## Règles d'écriture (le « joli » texte)

- **Un paragraphe d'accroche (`.lead`)** en tête de chaque grande section : il pose
  l'idée en 2-3 phrases avant le détail.
- **Phrases courtes, mots concrets.** Mode simple et direct, mais technique juste :
  on explique ce que font réellement les choses, sans jargon condescendant.
- **Mettre en gras** les termes qui portent l'information (`<strong>`), pas pour décorer.
- **Un `.callout`** par section pour le point à retenir ; un `.example` (encadré
  pointillé) dès qu'un cas concret illustre mieux qu'une explication.
- **Tableaux `.grid`** pour comparer / récapituler. **Pastilles `.pill-*`** pour les
  statuts (OK / KO / en attente).
- **Bandeaux de volet** (`.volet`) pour séparer deux grandes parties (ex. DEV vs MÉTIER).
- Ne jamais couper une idée en deux pages au milieu d'une phrase : regrouper dans un
  bloc `.keep` ce qui doit rester d'un seul tenant.

---

## Structure type d'un document

```
Couverture  →  Sommaire  →  [Bandeau volet]  →  Sections numérotées  →  Page de fin
```

Adapter le nombre de sections au besoin. Les bandeaux de volet sont optionnels
(utiles quand il y a 2+ grandes parties).

---

## CSS complet (à coller tel quel dans `<style>`)

```css
:root{
  --green-50:#EAF1E9; --green-100:#D8E8D6; --green-200:#B7D4B4; --green-400:#6FA86D;
  --green-500:#3F8A3D; --green-600:#2F6E2E; --green-700:#2A5C29; --green-900:#1F4620;
  --blue:#1B5F8C;
  --success:#10B981; --success-soft:#D1FAE5; --danger:#EF4444; --danger-soft:#FEE2E2;
  --warning:#F59E0B; --warning-soft:#FEF3C7; --info:#3B82F6; --info-soft:#DBEAFE;
  --text:#0E1A24; --text-muted:#5A6B7A; --text-light:#8A95A0;
  --bg-soft:#FAF8F4; --bg-medium:#F2EFE8; --border:#E6E2D8; --border-strong:#D2CCBF;
}
@page{
  size:A4; margin:18mm 16mm 20mm 16mm;
  @bottom-left{content:"<Votre marque>";font-family:'Inter',sans-serif;font-size:8pt;color:#94A3B8;}
  @bottom-center{content:counter(page)" / "counter(pages);font-family:'Inter',sans-serif;font-size:8pt;color:#64748B;font-weight:600;}
  @bottom-right{content:"DOC-REF";font-family:'JetBrains Mono',monospace;font-size:7pt;color:#94A3B8;}
}
@page :first{margin:0;@bottom-left{content:none;}@bottom-center{content:none;}@bottom-right{content:none;}}
@page closing{margin:0;@bottom-left{content:none;}@bottom-center{content:none;}@bottom-right{content:none;}}
*{box-sizing:border-box;}
html,body{margin:0;padding:0;font-family:'Inter','Segoe UI',Helvetica,Arial,sans-serif;font-size:10.5pt;line-height:1.5;color:var(--text);}
.mono{font-family:'JetBrains Mono','Consolas','Courier New',monospace;letter-spacing:.2px;}
h1,h2,h3{margin:0;}
p{margin:0 0 3.5mm;}
.lead{font-size:12pt;color:var(--text-muted);line-height:1.55;}
strong{color:var(--text);}

/* COUVERTURE */
.cover{page-break-after:always;height:297mm;width:210mm;margin:0;position:relative;background:#fff;}
.cover-band{height:78mm;background:linear-gradient(135deg,var(--green-700) 0%,var(--green-500) 55%,var(--green-400) 100%);position:relative;}
.cover-band::after{content:"";position:absolute;bottom:0;left:0;right:0;height:8px;background:linear-gradient(90deg,var(--green-900),var(--green-500),var(--green-900));}
.cover-logo-zone{position:absolute;top:20mm;left:0;right:0;display:flex;flex-direction:column;align-items:center;gap:10px;}
.cover-logo{height:30mm;max-width:100mm;object-fit:contain;background:#fff;padding:5mm 11mm;border-radius:8px;box-shadow:0 12px 32px rgba(31,70,32,.25);}
.cover-brand{color:#fff;font-size:13pt;font-weight:800;letter-spacing:.18em;text-transform:uppercase;margin-top:6mm;}
.cover-tagline{color:#fff;font-size:9.5pt;font-style:italic;opacity:.92;margin-top:3px;}
.cover-title-zone{margin-top:16mm;padding:0 20mm;text-align:center;}
.cover-eyebrow{font-size:9.5pt;font-weight:700;letter-spacing:.4em;color:var(--green-500);margin-bottom:8px;}
.cover-title{font-size:30pt;font-weight:800;color:var(--text);line-height:1.15;letter-spacing:-.01em;}
.cover-divider{width:60mm;height:3px;background:linear-gradient(90deg,var(--green-500),var(--green-700));margin:16px auto;border-radius:2px;}
.cover-sub{font-size:13pt;font-weight:600;color:var(--green-700);margin-top:6px;}
.cover-meta{margin:16mm 26mm 0 26mm;background:#fff;border:2px solid var(--green-100);border-radius:14px;box-shadow:0 18px 40px -16px rgba(63,138,61,.30);padding:10mm 13mm;position:relative;}
.cover-meta::before{content:"";position:absolute;top:0;left:0;bottom:0;width:4px;background:linear-gradient(180deg,var(--green-500),var(--green-700));}
.cover-meta-row{display:flex;gap:14px;padding:8px 0;border-bottom:1px solid var(--bg-medium);}
.cover-meta-row:last-child{border-bottom:none;padding-bottom:0;}
.cover-meta-row:first-child{padding-top:0;}
.cover-meta-icon{font-size:15pt;width:26px;flex-shrink:0;}
.cover-meta-label{font-size:7.5pt;font-weight:800;letter-spacing:.16em;color:var(--green-600);text-transform:uppercase;}
.cover-meta-value{font-size:11pt;font-weight:700;color:var(--text);}
.cover-legal{position:absolute;bottom:16mm;left:18mm;right:18mm;text-align:center;font-size:8pt;color:var(--text-light);font-style:italic;}
.cover-band-bottom{position:absolute;bottom:0;left:0;right:0;height:12mm;background:linear-gradient(135deg,var(--green-700),var(--green-500));}

/* SOMMAIRE */
.toc{page-break-after:always;padding-top:4mm;}
.toc h1{font-size:22pt;font-weight:800;margin-bottom:4mm;}
.toc-divider{width:40mm;height:3px;background:linear-gradient(90deg,var(--green-500),var(--green-700));border-radius:2px;margin-bottom:8mm;}
.toc-group{font-size:9pt;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--green-600);margin:6mm 0 2mm;}
.toc-item{display:flex;align-items:baseline;gap:8px;padding:3px 0;font-size:11pt;}
.toc-num{font-family:'JetBrains Mono',monospace;font-weight:700;color:var(--green-500);min-width:22px;}

/* SECTIONS */
.section{page-break-before:always;}
.section-head{display:flex;align-items:center;gap:14px;margin-bottom:6mm;padding-bottom:4mm;border-bottom:2px solid var(--green-100);}
.section-num{font-family:'JetBrains Mono',monospace;font-size:24pt;font-weight:800;color:var(--green-200);line-height:1;}
.section-eyebrow{font-size:8.5pt;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--green-500);}
.section-title{font-size:19pt;font-weight:800;color:var(--text);letter-spacing:-.01em;}

/* BANDEAU DE VOLET */
.volet{page-break-before:always;height:80mm;display:flex;flex-direction:column;justify-content:center;padding:0 22mm;}
.volet-a{background:linear-gradient(135deg,var(--green-700),var(--green-500));}
.volet-b{background:linear-gradient(135deg,var(--blue),#2E7FB0);}
.volet-kicker{color:#fff;font-size:10pt;font-weight:700;letter-spacing:.3em;opacity:.85;text-transform:uppercase;}
.volet-title{color:#fff;font-size:30pt;font-weight:800;line-height:1.1;margin-top:6px;}
.volet-desc{color:#fff;font-size:12pt;opacity:.95;margin-top:10px;max-width:130mm;}

/* BLOCS DE CONTENU */
.block{margin:0 0 5mm;}
.block-title{font-size:12.5pt;font-weight:800;color:var(--green-700);margin-bottom:2.5mm;display:flex;align-items:center;gap:8px;}
.block-title .ic{font-size:13pt;}
ul.clean{margin:0 0 4mm;padding-left:5mm;} ul.clean li{margin-bottom:2mm;}
.keep{page-break-inside:avoid;}

.card{background:#fff;border:1px solid var(--border);border-left:4px solid var(--green-500);border-radius:10px;padding:5mm 6mm;margin:0 0 4mm;box-shadow:0 4px 14px -8px rgba(0,0,0,.15);page-break-inside:avoid;}
.card-blue{border-left-color:var(--blue);}
.card h4{font-size:11pt;font-weight:800;color:var(--text);margin-bottom:2mm;}
.callout{background:var(--green-50);border:1px solid var(--green-100);border-radius:10px;padding:4mm 5mm;margin:0 0 4mm;font-size:10pt;page-break-inside:avoid;}
.callout-blue{background:var(--info-soft);border-color:#BFDBFE;}
.example{background:var(--bg-soft);border:1px dashed var(--border-strong);border-radius:10px;padding:4mm 5mm;margin:0 0 4mm;page-break-inside:avoid;}
.example .tag{font-size:8pt;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--green-600);}

table.grid{width:100%;border-collapse:collapse;margin:0 0 4mm;font-size:9.7pt;}
table.grid th{background:var(--green-600);color:#fff;text-align:left;padding:5px 8px;font-weight:700;}
table.grid td{border:1px solid var(--border);padding:5px 8px;vertical-align:top;}
table.grid tr:nth-child(even) td{background:var(--bg-soft);}

.pill{display:inline-block;padding:1px 8px;border-radius:999px;font-size:8.5pt;font-weight:800;}
.pill-ok{background:var(--success-soft);color:#065F46;}
.pill-ko{background:var(--danger-soft);color:#991B1B;}
.pill-wait{background:var(--warning-soft);color:#92400E;}

/* Liste numérotée à pastilles (centrage fiable WeasyPrint via line-height) */
.steps{margin:0;padding-left:5mm;counter-reset:step;list-style:none;}
.steps li{position:relative;padding:5px 0 5px 8mm;counter-increment:step;font-size:10pt;line-height:1.5;}
.steps li::before{content:counter(step);position:absolute;left:0;top:4px;width:6mm;height:6mm;border-radius:50%;background:var(--green-500);color:#fff;font-size:8.5pt;font-weight:800;display:block;text-align:center;line-height:6mm;}

/* SCHÉMA (boîtes reliées) */
.arch{background:var(--bg-soft);border:1px solid var(--border);border-radius:12px;padding:6mm;margin:0 0 4mm;}
.arch-row{display:flex;gap:8px;justify-content:center;margin:3mm 0;}
.node{flex:1;max-width:55mm;background:#fff;border:1.5px solid var(--green-200);border-radius:8px;padding:3.5mm;text-align:center;}
.node-strong{border-color:var(--green-500);background:var(--green-50);}
.node-title{font-weight:800;font-size:10pt;color:var(--green-700);}
.node-sub{font-size:8.5pt;color:var(--text-muted);margin-top:2px;}
.arch-caddy{background:linear-gradient(135deg,var(--green-700),var(--green-500));border:none;}
.arch-caddy .node-title,.arch-caddy .node-sub{color:#fff;}
.arch-arrow{text-align:center;color:var(--green-400);font-size:13pt;margin:1mm 0;}

/* PAGE DE FIN */
.closing{page:closing;page-break-before:always;height:297mm;width:210mm;position:relative;background:#fff;display:flex;flex-direction:column;}
.closing-band{height:60mm;background:linear-gradient(135deg,var(--green-700),var(--green-500),var(--green-400));}
.closing-body{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 24mm;}
.closing-eyebrow{font-size:9pt;font-weight:700;letter-spacing:.4em;color:var(--green-500);text-transform:uppercase;}
.closing-title{font-size:24pt;font-weight:800;color:var(--text);margin-top:8px;}
.closing-sub{font-size:12pt;color:var(--text-muted);margin-top:10px;max-width:120mm;}
.closing-foot{padding:0 24mm 22mm;text-align:center;font-size:8.5pt;color:var(--text-light);font-style:italic;}
```

> **Règle de pagination importante** (retours d'expérience) : ne JAMAIS mettre
> `page-break-inside:avoid` sur un grand bloc conteneur (il serait rejeté entier sur la
> page suivante → grosse page blanche). Mettre `avoid` sur les **petits** sous-blocs
> (`.card`, `.callout`, `.example`, `.keep`) pour que la coupure tombe **entre** eux.

---

## Briques HTML (à assembler)

### Couverture

```html
<div class="cover">
  <div class="cover-band">
    <div class="cover-logo-zone">
      <!-- Si le logo est dispo : <img src="logo.jpg" class="cover-logo" alt="Logo"> -->
      <div class="cover-brand">&lt;Votre marque&gt;</div>
      <div class="cover-tagline">— &lt;accroche&gt; —</div>
    </div>
  </div>
  <div class="cover-title-zone">
    <div class="cover-eyebrow">FICHE TECHNIQUE</div>
    <div class="cover-title">Titre du document</div>
    <div class="cover-divider"></div>
    <div class="cover-sub">Sous-titre explicatif en une ligne</div>
  </div>
  <div class="cover-meta">
    <div class="cover-meta-row"><div class="cover-meta-icon">🎯</div><div><div class="cover-meta-label">Objet</div><div class="cover-meta-value">…</div></div></div>
    <div class="cover-meta-row"><div class="cover-meta-icon">📅</div><div><div class="cover-meta-label">Référence</div><div class="cover-meta-value mono">DOC-REF</div></div></div>
  </div>
  <div class="cover-legal">Document de présentation — &lt;Votre marque&gt;.</div>
  <div class="cover-band-bottom"></div>
</div>
```

### Sommaire

```html
<div class="toc">
  <h1>Sommaire</h1><div class="toc-divider"></div>
  <p class="lead">Phrase d'accroche du document.</p>
  <div class="toc-group">Partie</div>
  <div class="toc-item"><span class="toc-num">1</span><span>Titre de section</span></div>
</div>
```

### Bandeau de volet (optionnel)

```html
<div class="volet volet-a">  <!-- volet-a = vert, volet-b = bleu -->
  <div class="volet-kicker">Volet 1</div>
  <div class="volet-title">Nom du volet</div>
  <div class="volet-desc">Une phrase qui annonce ce que couvre ce volet.</div>
</div>
```

### Section + blocs

```html
<div class="section">
  <div class="section-head">
    <div class="section-num">01</div>
    <div><div class="section-eyebrow">Partie</div><div class="section-title">Titre de section</div></div>
  </div>

  <p class="lead">Paragraphe d'accroche.</p>

  <div class="block">
    <div class="block-title"><span class="ic">⚙️</span>Sous-titre</div>
    <ul class="clean"><li>Point…</li></ul>
  </div>

  <table class="grid">
    <tr><th>Colonne A</th><th>Colonne B</th></tr>
    <tr><td>…</td><td><span class="pill pill-ok">OK</span></td></tr>
  </table>

  <div class="card"><h4>Titre de carte</h4><p>…</p></div>
  <div class="callout"><strong>À retenir :</strong> …</div>
  <div class="example"><div class="tag">Exemple</div><p>…</p></div>

  <ol class="steps"><li>Étape une.</li><li>Étape deux.</li></ol>
</div>
```

### Page de fin

```html
<div class="closing">
  <div class="closing-band"></div>
  <div class="closing-body">
    <div class="closing-eyebrow">&lt;Votre marque&gt;</div>
    <div class="closing-title">Phrase de clôture.</div>
    <div class="closing-sub">Une ou deux phrases de conclusion.</div>
  </div>
  <div class="closing-foot">Référence du document · &lt;Votre marque&gt;</div>
</div>
```

---

## Rendu PDF (WeasyPrint)

```python
from pathlib import Path
from weasyprint import HTML

src = Path("mon-document.html")
out = Path("Mon-Document.pdf")
# base_url = dossier du HTML, pour résoudre le logo et les assets relatifs.
HTML(filename=str(src), base_url=str(src.parent)).write_pdf(str(out))
print("PDF généré :", out, out.stat().st_size, "octets")
```

- **Installation** : `pip install weasyprint`. Sous Windows, WeasyPrint a besoin du
  **runtime GTK3** (sinon erreur `libgobster`/`libgobject`). Les avertissements
  `GLib-GIO-WARNING` au rendu sont inoffensifs.
- **Polices** : Inter et JetBrains Mono si présentes ; sinon WeasyPrint retombe sur
  les polices système (le rendu reste propre).
- **Logo** : déposer `logo.jpg` à côté du HTML et décommenter la balise `<img>`
  de la couverture. Sans logo, le bloc `.cover-brand` (texte) suffit.

---

## Checklist qualité avant livraison

- [ ] Couverture + sommaire + page de fin présents.
- [ ] Chaque grande section a un paragraphe `.lead`.
- [ ] Au moins un `.callout` (point à retenir) et un `.example` (cas concret) là où c'est utile.
- [ ] Aucune donnée inventée ; chiffres et faits vérifiés.
- [ ] Aucune capture d'écran.
- [ ] Orthographe et accents corrects (français soigné).
- [ ] Le PDF se génère sans erreur ; pas de page blanche injustifiée ; numéros centrés.
- [ ] Livrer le `.html` ET le `.pdf`.
```

---
name: guide-utilisateur
description: Use when the user wants a "guide d'utilisation" / user manual / mode d'emploi of an application as a premium PDF WITH annotated screenshots — reproduces the premium Forêt look of the reference user guide (cover, quick-reference cheat sheet, 5-minute quickstart, feature-by-feature sections with figures, badges Niveau/Temps, permissions matrix, troubleshooting decision tree, FAQ, glossary, closing page). Adapt the content and screenshots to each project. Self-contained: charte, canonical structure, full CSS, HTML blocks and render command are all in this file. NOT for a technical datasheet (use fiche-technique) nor a generic report (use pdf-premium).
---

# Skill — Guide utilisateur premium

## Ce que produit cette skill

Un **guide d'utilisation** PDF A4 complet, identique en charte et en style au
**guide de référence** : couverture, sommaire à plusieurs groupes, page de **référence rapide**
(cheat sheet), **démarrage en 5 minutes**, puis les fonctionnalités **écran par écran
avec captures d'écran annotées**, badges Niveau / Temps, matrice des permissions, arbre
de dépannage, FAQ, glossaire, page de fin. Charte **Forêt** (vert
sapin + papier crème, polices Inter / JetBrains Mono). Optimisé **WeasyPrint**.

C'est un **manuel end-user** : on montre l'application telle que l'utilisateur la voit
et on explique comment s'en servir, pas à pas. **Les captures d'écran font partie du
livrable.**

**Règle d'or :** on n'invente **jamais** de faits, de chiffres ni d'écrans. Chaque
capture doit être une vraie image de l'application. Français soigné, orthographe vérifiée.

## À quoi ça sert, et ce que ce n'est pas

| Livrable | Cette skill ? |
|---|---|
| Guide d'utilisation / manuel / mode d'emploi, avec captures | ✅ Oui |
| Fiche technique (présentation technique & métier, sans captures) | ❌ Non → `fiche-technique` |
| Rapport / note / livrable générique premium | ❌ Non → `pdf-premium` |

Base commune de la charte : `pdf-premium`. Cette skill en est la **déclinaison
« guide utilisateur »** : même CSS de base + composants spécifiques (cadres de captures,
cheat sheet, badges Niveau/Temps, arbre de dépannage) et la méthode de rédaction pas à pas.

---

## Workflow en 5 étapes

1. **Collecter le contenu ET les captures** (section suivante).
2. **Choisir l'ossature** parmi la structure type (6 groupes), adaptée au projet.
3. **Placer les captures** : une figure = un paragraphe d'intro + l'image + une légende.
4. **Monter le HTML** : `<style>` complet, puis briques (couverture → sommaire →
   référence rapide → démarrage → sections fonctionnalité → annexes → page de fin).
5. **Rendre le PDF** avec WeasyPrint.

Livrer **les deux** fichiers : le `.html` source + le `.pdf`, plus le dossier `img-guide/`.

---

## Étape 0 — Collecter le contenu et les captures (lecture auto + questions)

### Le contenu (jamais inventer)
1. **Demander le dossier du projet** si tu ne l'as pas.
2. **Lire** : `README.md`, `CLAUDE.md`, `docs/`, le code de l'interface (composants,
   pages, routes), les libellés de boutons/menus, les rôles et permissions, les statuts.
3. **En extraire** le parcours utilisateur réel : écrans, actions possibles, vocabulaire
   métier, badges/statuts, raccourcis.
4. **Poser des questions** pour les manques (rôles exacts, règles, valeurs réelles).

### Les captures d'écran (indispensables)
- **Demander à l'utilisateur de fournir les captures** de son application (il les prend
  lui-même à l'écran, ou avec un outil de capture pas à pas comme Scribe).
- Les déposer dans un dossier **`img-guide/`** à côté du HTML.
- **Nommer** chaque image par son écran : `login.png`, `dashboard.png`,
  `creer-projet.png`, `schema-1.png` (schémas de parcours). Tenir un petit
  `img-guide/_mapping.md` qui associe chaque image à sa section.
- **Une capture manquante n'est jamais inventée** : laisser un repère
  `[[capture à fournir : …]]` dans le texte et le signaler à l'utilisateur.

---

## Structure type (l'ossature à adapter, 6 groupes)

Reprend l'ossature validée du guide de référence. **Garde les sections utiles, supprime les
autres, renomme selon le projet.** Numéros spéciaux : `★` référence rapide, `▶` démarrage.

```
Couverture
Sommaire  (groupes ci-dessous)

── Pour démarrer ──
★  Référence rapide (cheat sheet : couleurs, statuts, raccourcis)
▶  Démarrage rapide en 5 minutes (parcours complet condensé + 1 schéma)

── Découvrir l'application ──
0  Vue d'ensemble : à quoi sert l'app, ses grandes parties
1  Premiers pas — connexion & navigation
2  L'écran d'accueil / tableau de bord

── Le cœur du métier ──
3..n  Une section PAR fonctionnalité principale (créer, gérer, consulter, calculer…)
      chacune avec ses captures et ses étapes

── Aller plus loin ──
Fonctions avancées, assistant / recherche, exports, sécurité & garde-fous

── Pilotage & administration ──  (si l'app en a)
Administration, paramétrage, moteurs de calcul, pilotage d'équipe

── Référence & support ──
Légende des badges & statuts · Matrice des permissions (rôles) ·
Bonnes pratiques · Dépannage (arbre de décision) · FAQ · Glossaire ·
Historique des versions & contact
Page de fin
```

Viser un manuel réellement complet : autant de sections « fonctionnalité » que l'app en
a d'écrans importants. Chaque groupe peut être précédé d'un **bandeau de partie** (`.part`).

---

## Règles d'écriture (le « joli » texte)

- **`.lead`** en tête de chaque section (2-3 phrases qui posent l'objectif).
- **Sous-titres `.sub`** pour découper une section en gestes (« Se connecter »,
  « La navigation »…).
- **Listes `.steps`** (pastilles numérotées) pour les actions à faire dans l'ordre.
- **Badges `.sec-meta`** (Niveau + Temps estimé) juste sous le titre des sections « faire ».
- **Tableaux `.grid`** pour le vocabulaire, les rôles, les statuts ; **`.mini`** en
  colonnes pour la référence rapide.
- **Callouts** : `.callout` (à savoir), `.callout-blue` (info), `.callout-warn` (piège /
  attention), `.callout-danger` (erreur à éviter). Utiliser `<span class="lbl">` pour
  le mot d'accroche en tête.
- **Ton** : on s'adresse à l'utilisateur, phrases courtes, verbes d'action, zéro jargon
  gratuit. Renvoyer entre sections avec des repères « (§3) ».

### La règle des captures (figures)
Chaque capture suit **toujours** ce trio, dans cet ordre :
1. un paragraphe `.fig-intro` **avant** l'image, qui dit quoi regarder ;
2. l'image dans `<figure class="figure"><img …></figure>` ;
3. une `<figcaption>` avec un `.fig-tag` numéroté (**Fig. X.Y** pour un écran,
   **Schéma N** pour un schéma de parcours).

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
  @bottom-left{content:"Guide d'utilisation · <Votre marque>";font-family:'Inter',sans-serif;font-size:8pt;color:#94A3B8;}
  @bottom-center{content:counter(page)" / "counter(pages);font-family:'Inter',sans-serif;font-size:8pt;color:#64748B;font-weight:600;}
  @bottom-right{content:"GUIDE-UTILISATEUR";font-family:'JetBrains Mono',monospace;font-size:7pt;color:#94A3B8;}
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
.sub{font-size:12.5pt;font-weight:800;color:var(--green-700);margin:5mm 0 2.5mm;}

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
.callout-warn{background:var(--warning-soft);border-color:#FCD34D;}
.callout-danger{background:var(--danger-soft);border-color:#FCA5A5;}
.callout .lbl{font-weight:800;letter-spacing:.04em;}
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

.steps{margin:0;padding-left:5mm;counter-reset:step;list-style:none;}
.steps li{position:relative;padding:5px 0 5px 8mm;counter-increment:step;font-size:10pt;line-height:1.5;}
.steps li::before{content:counter(step);position:absolute;left:0;top:4px;width:6mm;height:6mm;border-radius:50%;background:var(--green-500);color:#fff;font-size:8.5pt;font-weight:800;display:block;text-align:center;line-height:6mm;}

/* SCHÉMA */
.arch{background:var(--bg-soft);border:1px solid var(--border);border-radius:12px;padding:6mm;margin:0 0 4mm;}
.arch-row{display:flex;gap:8px;justify-content:center;margin:3mm 0;}
.node{flex:1;max-width:60mm;background:#fff;border:1.5px solid var(--green-200);border-radius:8px;padding:3.5mm;text-align:center;}
.node-strong{border-color:var(--green-500);background:var(--green-50);}
.node-title{font-weight:800;font-size:10pt;color:var(--green-700);}
.node-sub{font-size:8.5pt;color:var(--text-muted);margin-top:2px;}
.arch-arrow{text-align:center;color:var(--green-400);font-size:13pt;margin:1mm 0;}

/* FIGURE / CAPTURE D'ÉCRAN */
.figure{margin:1mm 0 5mm;page-break-inside:avoid;}
.figure img{display:block;margin:0 auto;max-width:100%;max-height:172mm;width:auto;height:auto;border:1px solid var(--border-strong);border-radius:8px;box-shadow:0 6px 18px -10px rgba(0,0,0,.3);}
figcaption{font-size:9pt;color:var(--text-muted);margin-top:2.5mm;padding-left:3mm;border-left:3px solid var(--green-200);line-height:1.45;}
.fig-tag{font-family:'JetBrains Mono',monospace;font-weight:800;color:var(--green-600);margin-right:5px;}
.fig-intro{font-size:10.2pt;line-height:1.5;margin:0 0 1.5mm;color:var(--text);}

/* Pagination des tableaux : en-tête répété + lignes non coupées */
table.grid thead, table.mini thead{display:table-header-group;}
table.grid tr, table.mini tr{break-inside:avoid;page-break-inside:avoid;}
table.grid thead tr, table.mini thead tr{break-after:avoid;page-break-after:avoid;}

/* Badges Niveau / Temps sous le titre de section */
.sec-meta{display:flex;gap:6px;margin:3mm 0 2mm;flex-wrap:wrap;}
.tag-lvl,.tag-time{font-size:7.5pt;font-weight:800;letter-spacing:.06em;text-transform:uppercase;padding:1.5px 8px;border-radius:999px;}
.tag-lvl{background:var(--green-100);color:var(--green-700);}
.tag-time{background:var(--info-soft);color:#1E40AF;}

/* Cheat sheet — grille compacte 2 colonnes */
.cheat{display:flex;gap:6mm;}
.cheat-col{flex:1;}
table.mini{width:100%;border-collapse:collapse;margin:0 0 3mm;font-size:8.8pt;}
table.mini th{background:var(--green-600);color:#fff;text-align:left;padding:3px 6px;font-weight:700;font-size:8pt;}
table.mini td{border:1px solid var(--border);padding:3px 6px;vertical-align:top;}
table.mini tr:nth-child(even) td{background:var(--bg-soft);}

/* Arbre de décision (dépannage) */
.tree{background:var(--bg-soft);border:1px solid var(--border);border-radius:10px;padding:5mm 6mm;margin:0 0 4mm;font-size:9.5pt;}
.tree .q{font-weight:800;color:var(--green-700);margin-bottom:1.5mm;}
.tree .branch{padding:1.5mm 0 1.5mm 6mm;border-left:2px solid var(--green-200);margin:1mm 0 1mm 2mm;}

/* Bandeau de partie (séparateur) */
.part{page-break-before:always;height:70mm;display:flex;flex-direction:column;justify-content:center;padding:0 22mm;background:linear-gradient(135deg,var(--green-700),var(--green-500));}
.part-kicker{color:#fff;font-size:10pt;font-weight:700;letter-spacing:.3em;opacity:.85;text-transform:uppercase;}
.part-title{color:#fff;font-size:28pt;font-weight:800;line-height:1.1;margin-top:6px;}
.part-desc{color:#fff;font-size:11.5pt;opacity:.95;margin-top:8px;max-width:130mm;}

/* PAGE DE FIN */
.closing{page:closing;page-break-before:always;height:297mm;width:210mm;position:relative;background:#fff;display:flex;flex-direction:column;}
.closing-band{height:60mm;background:linear-gradient(135deg,var(--green-700),var(--green-500),var(--green-400));}
.closing-body{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 24mm;}
.closing-eyebrow{font-size:9pt;font-weight:700;letter-spacing:.4em;color:var(--green-500);text-transform:uppercase;}
.closing-title{font-size:24pt;font-weight:800;color:var(--text);margin-top:8px;}
.closing-sub{font-size:12pt;color:var(--text-muted);margin-top:10px;max-width:120mm;}
.closing-foot{padding:0 24mm 22mm;text-align:center;font-size:8.5pt;color:var(--text-light);font-style:italic;}
```

> **Règle de pagination :** ne JAMAIS mettre `page-break-inside:avoid` sur un grand
> conteneur (grosse page blanche). Le mettre sur les petits blocs (`.card`, `.callout`,
> `.example`, `.figure`, lignes de tableau). Les captures trop hautes sont plafonnées par
> `max-height:172mm` — c'est voulu, ne pas l'enlever.

---

## Briques HTML (à assembler)

### Couverture

```html
<div class="cover">
  <div class="cover-band">
    <div class="cover-logo-zone">
      <img src="logo.jpg" class="cover-logo" alt="Logo">
      <div class="cover-brand">&lt;Votre marque&gt;</div>
      <div class="cover-tagline">— accompagnement clé en main —</div>
    </div>
  </div>
  <div class="cover-title-zone">
    <div class="cover-eyebrow">GUIDE D'UTILISATION</div>
    <div class="cover-title">Nom de l'application</div>
    <div class="cover-divider"></div>
    <div class="cover-sub">Ce que l'utilisateur va apprendre à faire, en une ligne</div>
  </div>
  <div class="cover-meta">
    <div class="cover-meta-row"><div class="cover-meta-icon">🎯</div><div><div class="cover-meta-label">Objet</div><div class="cover-meta-value">Prise en main complète de l'application</div></div></div>
    <div class="cover-meta-row"><div class="cover-meta-icon">👥</div><div><div class="cover-meta-label">Destinataires</div><div class="cover-meta-value">Équipes, encadrement &amp; clients</div></div></div>
    <div class="cover-meta-row"><div class="cover-meta-icon">📅</div><div><div class="cover-meta-label">Version</div><div class="cover-meta-value mono">V1 — 2026</div></div></div>
  </div>
  <div class="cover-legal">Document d'utilisation — &lt;Votre marque&gt;.</div>
  <div class="cover-band-bottom"></div>
</div>
```

### Sommaire (multi-groupes)

```html
<div class="toc">
  <h1>Sommaire</h1><div class="toc-divider"></div>
  <p class="lead">Phrase d'accroche du guide.</p>

  <div class="toc-group">Pour démarrer</div>
  <div class="toc-item"><span class="toc-num">★</span><span>Référence rapide</span></div>
  <div class="toc-item"><span class="toc-num">▶</span><span>Démarrage rapide en 5 minutes</span></div>

  <div class="toc-group">Découvrir l'application</div>
  <div class="toc-item"><span class="toc-num">1</span><span>Premiers pas — connexion &amp; navigation</span></div>

  <div class="toc-group">Référence &amp; support</div>
  <div class="toc-item"><span class="toc-num">FAQ</span><span>Questions fréquentes</span></div>
</div>
```

### Référence rapide (cheat sheet)

```html
<div class="section">
  <div class="section-head">
    <div class="section-num">★</div>
    <div><div class="section-eyebrow">Pour démarrer</div><div class="section-title">Référence rapide</div></div>
  </div>
  <p class="lead">Une page à garder sous la main : codes couleur, statuts et raccourcis.</p>
  <div class="cheat">
    <div class="cheat-col">
      <table class="mini">
        <thead><tr><th colspan="2">Statuts</th></tr></thead>
        <tr><td>Vert</td><td>OK / valide</td></tr>
        <tr><td>Rouge</td><td>bloquant</td></tr>
      </table>
    </div>
    <div class="cheat-col">
      <table class="mini">
        <thead><tr><th colspan="2">Raccourcis</th></tr></thead>
        <tr><td>Échap</td><td>annuler</td></tr>
        <tr><td>Entrée</td><td>confirmer</td></tr>
      </table>
    </div>
  </div>
  <div class="callout callout-blue"><span class="lbl">À SAVOIR :</span> le réglage le plus important du parcours.</div>
</div>
```

### Section « fonctionnalité » (avec badges, sous-titres, étapes et capture)

```html
<div class="section">
  <div class="section-head">
    <div class="section-num">01</div>
    <div><div class="section-eyebrow">Découvrir l'application</div><div class="section-title">Premiers pas — connexion &amp; navigation</div></div>
  </div>
  <div class="sec-meta"><span class="tag-lvl">Niveau : Débutant</span><span class="tag-time">Temps estimé : 5 min</span></div>

  <p class="lead">Se connecter, comprendre la navigation, et le vocabulaire de base.</p>

  <div class="sub">Se connecter</div>
  <ol class="steps">
    <li>Cliquez sur votre <strong>carte utilisateur</strong>.</li>
    <li>Saisissez votre mot de passe.</li>
  </ol>

  <p class="fig-intro">Sur l'écran de connexion, cliquez sur votre carte : le champ mot de passe apparaît (Fig. 1.1).</p>
  <figure class="figure">
    <img src="img-guide/login.png" alt="Écran de connexion">
    <figcaption><span class="fig-tag">Fig. 1.1</span> L'écran de connexion.</figcaption>
  </figure>

  <div class="callout callout-warn"><span class="lbl">PIÈGE :</span> ne partagez pas votre mot de passe.</div>
</div>
```

### Bandeau de partie

```html
<div class="part">
  <div class="part-kicker">Partie</div>
  <div class="part-title">Le cœur du métier</div>
  <div class="part-desc">Ce que couvre cette partie.</div>
</div>
```

### Arbre de dépannage

```html
<div class="tree">
  <div class="q">Le calcul ne se lance pas ?</div>
  <div class="branch">Vérifiez que la fiche est éligible (verdict vert).</div>
  <div class="branch">Sinon, contrôlez la date d'engagement.</div>
</div>
```

### FAQ / Glossaire / Permissions (tableaux `.grid`)

```html
<table class="grid">
  <thead><tr><th>Question</th><th>Réponse</th></tr></thead>
  <tr><td>Comment créer un dossier ?</td><td>Bouton Import, puis suivez les étapes.</td></tr>
</table>
```

### Page de fin

```html
<div class="closing">
  <div class="closing-band"></div>
  <div class="closing-body">
    <div class="closing-eyebrow">&lt;Votre marque&gt;</div>
    <div class="closing-title">Vous êtes prêt.</div>
    <div class="closing-sub">Gardez la référence rapide à portée de main.</div>
  </div>
  <div class="closing-foot">Guide d'utilisation · &lt;Votre marque&gt;</div>
</div>
```

---

## Rendu PDF (WeasyPrint)

```python
from pathlib import Path
from weasyprint import HTML

src = Path("guide-utilisation-projet.html")
out = Path("Guide-Utilisation-Projet.pdf")
# base_url = dossier du HTML, pour résoudre logo.jpg ET le dossier img-guide/.
HTML(filename=str(src), base_url=str(src.parent)).write_pdf(str(out))
print("PDF généré :", out, out.stat().st_size, "octets")
```

- **Installation** : `pip install weasyprint`. Sous Windows, runtime **GTK3** requis.
- **Assets** : `logo.jpg` et le dossier `img-guide/` doivent être **à côté** du HTML.
  Le PDF sera lourd si les captures sont nombreuses (normal).

---

## Checklist qualité avant livraison

- [ ] Couverture (eyebrow « GUIDE D'UTILISATION ») + sommaire multi-groupes + page de fin.
- [ ] Page de **référence rapide** (cheat sheet) et **démarrage en 5 minutes** présents.
- [ ] Une section par fonctionnalité importante ; chaque section « faire » a ses badges
      `.sec-meta` (Niveau + Temps).
- [ ] **Chaque capture** suit le trio : `.fig-intro` → `figure/img` → `figcaption`
      numérotée (Fig. X.Y ou Schéma N). Toutes les images existent dans `img-guide/`.
- [ ] Aucune capture inventée ; repères `[[capture à fournir]]` signalés à l'utilisateur.
- [ ] Annexes utiles : légende des statuts, permissions, dépannage, FAQ, glossaire.
- [ ] Orthographe et accents corrects (français soigné).
- [ ] Le PDF se génère sans erreur ; captures nettes et non coupées (max-height respecté).
- [ ] Livrer le `.html`, le `.pdf` ET le dossier `img-guide/`.

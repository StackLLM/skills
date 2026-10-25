---
name: fiche-technique
description: Use when the user wants a "fiche technique" / technical reference / "documentation technique de référence" of an application — a real map of how the project is built (frontend, backend, API, database, RAG, AI, anonymisation, security, multi-tenant, infrastructure), feature by feature, with file paths, flows and the reasons behind each choice, never a commercial sheet. Produces (1) a Markdown reference in the repo (docs/fiche-technique/), (2) a draw.io schema (data + infrastructure), (3) a premium PDF (charte Forêt), marked internal, with a shareable part for clients. Self-contained: analysis method, exact 18-part structure, writing rules, full CSS, SVG schema renderer and Markdown→PDF converter are all in this file. NOT for user manuals with screenshots (guide-utilisateur) nor generic reports (pdf-premium).
---

# Skill — Fiche technique de référence

## Ce que produit cette skill

Une **carte technique** d'un projet logiciel. En la lisant, quelqu'un qui n'est pas
développeur expert doit comprendre :

> **sur quoi le projet est construit, comment les données circulent, comment chaque
> fonctionnalité marche, où elle est codée, quelles technologies sont utilisées, pourquoi
> elles ont été choisies et quelles protections existent.**

Trois livrables, toujours dans cet ordre :

| # | Livrable | Où | Format |
|---|---|---|---|
| 1 | **Fiche de référence** | dans le dépôt : `docs/fiche-technique/fiche-technique-<projet>.md` | Markdown + Mermaid |
| 2 | **Schéma** des données et de l'infrastructure | `docs/fiche-technique/schema-<projet>.drawio` | draw.io, charte `diagram-premium` |
| 3 | **PDF premium** | dossier de livrables demandé (ex. `…\<Client>\Livrables\`) | PDF A4, charte Forêt, **document interne** |

Modèle de référence : une fiche de 59 pages validée en production. La reproduire
**à l'identique** en structure, précision et rendu.

**Ce n'est pas une fiche commerciale.** Interdit : « architecture moderne et sécurisée ».
Attendu : « Le frontend X appelle l'endpoint Y. Celui-ci vérifie Z puis appelle le service A.
Les données sont lues dans B. Le contrôle d'organisation est fait dans C. »

| Demande | Cette skill ? |
|---|---|
| Documentation technique de référence, carte du projet, revue technique | ✅ Oui |
| Fiche de présentation commerciale à deux volets pour un client | ⚠️ Seulement la partie « Version partageable » (§16) ; sinon `pdf-premium` |
| Manuel utilisateur avec captures | ❌ `guide-utilisateur` |

---

## Règles absolues

1. **Ne jamais inventer** une technologie, une base, un modèle, une API, une architecture, un
   mécanisme de sécurité, un script, une capacité ou un fournisseur.
2. **Trois marques**, utilisées partout :

   | Marque | Sens |
   |---|---|
   | (aucune) | **Fait** : lu dans le code ou la configuration, fichier cité. |
   | **Déduction** | Conclusion raisonnable tirée du code, pas écrite telle quelle. |
   | **À confirmer dans le projet** | Introuvable ou contradictoire dans le dépôt. |
   | **Raison historique non identifiable dans le projet** | Le choix existe, aucune trace de sa raison. |

3. **Aucun secret.** Jamais de valeur lue dans un `.env`, une clé, un mot de passe, une URL
   privée de tunnel. Seulement `VARIABLE=...` et son rôle.
4. **Fichier + fonction**, pas de numéros de ligne dans le livrable (ils bougent).
5. **Ne pas présenter une démo comme une production.** Si rien n'est déployé : écrire
   « **Production non déployée actuellement.** » Distinguer modèle **actuel / prévu / testé**.
6. **Interne / partageable.** Le document entier est **interne**. Seule la partie 16
   « Version partageable » peut aller à un client : ni chemin, ni port, ni nom de variable,
   ni **fournisseur intermédiaire** (proxy d'API, routeur de modèles…). Respecter les
   consignes du client sur les noms à ne jamais citer.
7. **Ne rien corriger dans le projet.** Les écarts trouvés vont dans « Limites » (§15).
8. Français simple, phrases courtes, gras sur le mot qui porte l'information.

---

## Workflow

```
00  Cadrer          projet, livrables, dossier de sortie, nom du PDF (ne jamais écraser une version)
01  Analyser        6 analyses en parallèle, lecture seule (section « Analyse »)
02  Vérifier        contrôler soi-même les points sensibles et les contradictions
03  Rédiger         la fiche Markdown, structure exacte (section « Structure »)
04  Contrôler       chemins cités existants, aucun secret, partie 16 propre
05  Schéma draw.io  2 onglets : données + infrastructure (skill diagram-premium)
06  PDF             convertisseur Markdown → HTML premium → WeasyPrint
07  Relire le PDF   planches de pages, zoom des schémas, détection des débordements
08  Livrer          chemins, ce qui est interne, points « à confirmer », libellé de commit
```

**Ne pas commencer par rédiger.** Un existant (fiche, docs) s'analyse et s'améliore plutôt
que de créer un doublon.

---

## 01 — Analyse : six analyses en parallèle

Lancer **six agents d'exploration en lecture seule, en même temps** (outil Agent, type
Explore, `run_in_background`), chacun avec cette consigne commune :

> Lecture seule, très complète. Chaque affirmation cite son fichier (+ ligne). Ne rien
> deviner : marquer « À confirmer ». Jamais de valeur secrète (noms de variables seulement).
> Rapport structuré, sans gros extraits de code.

| Agent | Périmètre et questions |
|---|---|
| **Frontend** | `package.json` (versions), config du bundler (ports, proxy), variables `import.meta.env`, builds par espace ; arborescence ; **toutes les routes** (chemin → page → qui y accède) et gardes ; client API (URL de base, jeton, stockage, délais, 401, erreurs) ; connexion et session ; **le bot côté écran** (page, composants, fonction d'envoi, endpoint, charge utile, réponse, polling/streaming, sources, attente de validation) ; validation ; centre de connaissances ; administration ; tableaux de bord ; protections côté écran. |
| **Backend / routes** | `requirements` (versions), version du langage ; `main` (routeurs et préfixes, middlewares, CORS, en-têtes, démarrage, tâches) ; structure des modules (rôle en une ligne) ; **catalogue complet des endpoints** (méthode, chemin, rôle, permission, service, tables) ; dépendances de permission ; cloisonnement ; erreurs ; journaux. |
| **Base de données** | moteur, version, conteneur, port, connexion, ORM, sessions ; **chaque table** (rôle, champs, PK, FK, index, JSON) ; relations ; tables avec `organisation_id` ; migrations dans l'ordre et la dernière ; seeds ; sauvegardes ; où sont les données personnelles. |
| **RAG / sources** | sources réelles du corpus (origine, format, ingestion, stockage, mise à jour, statut) ; pipeline (extraction, nettoyage, découpage, métadonnées, embeddings, stockage, index) ; recherche (lexicale, vectorielle, fusion, top-k, filtres, reranking) ; **versionnement** ; formatage du contexte et citations ; API externes (ex. Légifrance) ; veille ; centre de connaissances. |
| **Bot / IA / anonymisation** | la route de question **pas à pas** ; couche IA (modèles, paramètres, délais, secours, choix par organisation, incidents) ; prompts et règles ; **contrôles après génération** ; workflow de validation humaine ; **anonymisation** (fichier, technique, catégories, repères, correspondance, restitution, ce qui est en base, journaux) ; ce qui part au modèle et ce qui reste local. |
| **Sécurité / infra** | connexion, hachage, jeton, durée, révocation, anti-abus ; rôles et matrice ; isolation multi-organisation et tests qui la prouvent ; espaces et accès publics ; CORS, HTTPS, en-têtes, proxy ; secrets ; scripts de démarrage, conteneurs, ports, tunnels, hébergeurs ; tâches planifiées ; production réelle ou non ; audit, incidents, journaux ; nombre de tests. |

Attendre les six rapports. Puis **vérifier soi-même** (étape 02) :
- les points où deux rapports se contredisent ;
- ce qui touche la sécurité et les données personnelles (ce qui part au modèle, ce qui est
  journalisé, ce que l'API renvoie au client) ;
- la configuration réelle d'exécution (variable d'environnement de production posée ou non) ;
- les écarts entre la documentation existante et le code (ports, noms de conteneurs…).

---

## 03 — Structure exacte de la fiche Markdown

### En-tête (avant la partie 1)

```markdown
# Fiche technique de <Produit> — <sous-titre>

> **Carte technique de référence du projet.** Elle décrit le code réel du dépôt
> `<dépôt>` (branche `<branche>`), analysé le **JJ/MM/AAAA** (commit `<sha>`).
> Ce n'est pas une fiche commerciale : la version partageable avec un client est au §16.

## Comment lire cette fiche
<tableau des marques> + 5 puces : chemins relatifs, fichier+fonction, aucun secret,
la grille commune, le lien vers le schéma draw.io.

## Sommaire
<liste numérotée avec ancres, 8.1 à 8.6 en sous-liste>
```

### Les 18 parties (titres de niveau `#`, numérotés `# N. Titre`)

| # | Titre | Contenu obligatoire |
|---|---|---|
| 1 | **Vue d'ensemble** | ce que c'est ; tableau des **briques** (brique, technologie, où elle tourne) ; **schéma Mermaid `flowchart`** d'ensemble ; **état réel des environnements** (production / démo / dev) ; résumé des communications |
| 2 | **Frontend** | grille commune ; tableau des technologies (versions) ; structure des dossiers ; **tableau des routes** (chemin, page, qui) ; appels API ; espaces/builds ; **exemple détaillé du bot côté écran** (tableau étape → où) |
| 3 | **Backend** | grille commune ; ordre du démarrage ; middlewares ; tableau des technologies ; structure des modules ; **fiches de routes importantes** (`####` par route : Rôle, Entrées, Traitement, Services, Données, Réponse, Permissions, Fichier) ; gestion des erreurs |
| 4 | **API et communications** | 4.1 tableau de **toutes les communications** (de → vers, protocole, adresse, authentification, données, délai/erreurs, fichier) ; 4.2 **catalogue des endpoints** par domaine (endpoint, accès, rôle) |
| 5 | **Base de données** | tableau technique (image, conteneur, port, connexion, ORM, migrations, repli, seeds, sauvegarde) ; **tableau des entités** (table, rôle, champs, relations, qui accède) ; données hors base ; **schéma Mermaid `erDiagram`** ; puces sur liens logiques, contenu partagé, tables avec `organisation_id` |
| 6 | **RAG — Retrieval-Augmented Generation** | qu'est-ce qu'un RAG (simple) ; pourquoi ce projet en utilise un ; **schéma Mermaid `flowchart LR`** du parcours ; **tableau étape par étape** (étape, ce qui se passe, technologie, fichier) ; commandes ; 6.1 **sources** (origine, format, ingestion, stockage, mise à jour, utilisée par l'IA) + « d'où vient l'information donnée au modèle ? » ; 6.2 **versionnement** (pourquoi, comment, à surveiller) — ou « ce mécanisme n'existe pas » |
| 7 | **IA — modèle et fonctionnement du bot** | 7.1 tableau des modèles (**actuel, secours, prévu, testés, retirés, tests**), paramètres (température, sortie max, délai, contexte, format, nouvel essai), chaîne de secours ; 7.2 **pourquoi ce modèle ?** (tableau critère / ce que dit le projet / source ; limites ; ou « Décision en cours — benchmark nécessaire ») ; 7.3 **cadrage** : avant la génération (prompts, règles), après (tableau des contrôles), validation humaine, ce qui reste une limite ; 7.4 **le bot du clic à la réponse** (**schéma Mermaid `flowchart TD`** + tableau étape → détail → fichier + ce qui part au modèle / ce qui reste local) |
| 8 | **Fonctionnalités** | 8.1 **Anonymisation** (quand ; schéma texte ; technologie et fichier exact ; catégories exactes ; repères ; correspondance ; restitution ; autres sorties ; où restent les données d'origine ; journaux ; limites) · 8.2 **Authentification et sécurité** (tableau auth, sessions, autorisation, accès public, protections transverses : CORS, en-têtes, HTTPS, secrets, erreurs, audit, IA, tests) · 8.3 **Isolation des organisations** (arbre texte, tableau des mécanismes, matrice des rôles, tests) · 8.4 **Fonctionnalités métier, fiche par fiche** (`###` par fonction : Objectif, Utilisateur, Frontend, Backend/API, Base, RAG/IA, Sécurité, Flux, Pourquoi, À surveiller) · 8.5 **Administration** (accès, tableau page → rôle → API, garde-fous) · 8.6 **Sources externes / veille** (tableau source, rôle, API/auth, fréquence, stockage, usage RAG, erreurs, fichiers) |
| 9 | **Infrastructure et déploiement** | **schéma ASCII** de l'infrastructure réelle ; environnements (local, démo, hébergeur, tunnel, **production**) ; tâches planifiées ; journaux ; CI ; tableau des **services utilisés** (rôle, statut) |
| 10 | **Environnement et configuration** | tableau des **ports et adresses** (exposition) ; tableau des **variables** par groupe (noms seulement) ; dépendances humaines |
| 11 | **Flux complets** | 5 **diagrammes Mermaid `sequenceDiagram`** : connexion, question au bot, validation, centre de connaissances (ou fonction de consultation), administration |
| 12 | **Tableau de traçabilité technique** | Fonctionnalité · Frontend · Backend · API · Base · RAG · IA · Sécurité · Fichiers principaux |
| 13 | **Tableau des technologies** | Couche · Technologie · Version · Rôle · Pourquoi ce choix · Fichiers |
| 14 | **Pourquoi cette architecture ?** | Décision · Choix actuel · Pourquoi · Alternative possible · Impact |
| 15 | **Limites actuelles et points à surveiller** | tableau numéroté · Point · Gravité (haute/moyenne/faible) · Où |
| 16 | **Version partageable** | encadré d'avertissement ; Architecture, Technologies, Fonctionnement du RAG, IA, Contrôle des réponses, Données et anonymisation, Sécurité, Hébergement — **sans chemin, port, variable ni fournisseur intermédiaire** |
| 17 | **Glossaire** | Terme · Définition (1-2 phrases) · Rôle dans le projet |
| 18 | **Contrôle final : où trouver chaque réponse** | Question → section |

Adapter les intitulés au domaine (ex. « Centre de connaissances » → la fonction de
consultation du projet), **jamais l'ordre ni la séparation** Frontend / Backend / Base /
RAG / IA / Sécurité / Infrastructure. Pas de RAG ou pas d'IA : garder la partie et écrire
clairement « absent du projet ».

### La grille commune (parties 2, 3, 5, 6 et chaque grand volet)

```markdown
### Ce que c'est
### À quoi ça sert
### Comment ça fonctionne
### Technologies          (tableau avec versions)
### Fichiers concernés    (ou tableau « Structure »)
### Données manipulées
### Communications
### Pourquoi ce choix     (raison documentée, Déduction, ou « Raison historique non identifiable »)
### Sécurité
### À surveiller
```

### Fiche d'une fonctionnalité (§8.4)

```markdown
### <Nom>
- **Objectif** : …
- **Utilisateur** : …
- **Frontend** : route, page, composants (fichiers).
- **Backend / API** : routes, fichiers.
- **Base** : tables lues / écrites.
- **RAG / IA** : oui / non, comment.
- **Sécurité** : permissions, protections.
- **Flux** : Utilisateur → Page → API → service → base/RAG/IA → réponse → écran.
- **Pourquoi** : …
- **À surveiller** : …
```

### Contrôle final (avant de passer au schéma)

Pouvoir répondre, avec la fiche seule, à : grandes briques et communications ; technologie
et pages du frontend, comment une page appelle le backend ; routes, services, logique
métier ; base, entités, relations ; RAG, sources, traitement des documents, contexte
envoyé au modèle ; modèle et sa raison, cadrage ; anonymisation (technologie, script,
moment, données protégées, ce que reçoit le modèle) ; authentification, permissions,
isolation d'un client, protections backend ; lancement, services, environnements,
déploiement ; pour chaque fonction : écran, API, backend, données, sécurité.
**Une réponse manque → reprendre l'analyse.**

Puis vérifier par script : **chaque chemin cité existe** dans le dépôt, aucun motif de
secret (`sk-`, `password=`, URL de tunnel), la partie 16 ne contient ni chemin, ni port,
ni `.env`, ni fournisseur intermédiaire.

---

## 05 — Schéma draw.io (skill `diagram-premium`)

Fichier `docs/fiche-technique/schema-<projet>.drawio`, **deux onglets**, généré par script
Python (jamais à la main) puis validé (`xml.dom.minidom`) :

1. **Schéma des données** : 6 panneaux-colonnes (Clients et comptes · Conversations ·
   Validation et suivi · Questions validées · Corpus (RAG) · Transverse), chaque table en
   CARTE (nom en gras, `PK`, `FK … → table`, champs clés), flèches vertes « 1-n » entre
   en-têtes de panneaux, flèche bleue pointillée pour les liens logiques ; encadrés
   « Comment lire le schéma » et « Données gardées en fichiers ».
2. **Infrastructure réelle** : entrées (bleu) → interfaces (vert) → API (or) → ressources
   locales (vert) ; services externes à droite (émeraude = actif, rouge = coupé ou non
   configuré) ; encadré « À retenir ».

Si draw.io n'est pas installé, **ne pas** envoyer le fichier sur un site externe pour le
voir : valider le XML et le dire.

---

## 06 — PDF premium

Le PDF est **produit à partir du Markdown** par un convertisseur. Charte de la fiche
technique Forêt (couverture verte, sommaire groupé, sections numérotées `00`…`18`,
tableaux verts, page de fin). Moteur : **WeasyPrint**.

### Fichiers nécessaires

- `_style-fiche.css` (CSS ci-dessous) et `logo.jpg`.
- La classe `Schema` (ci-dessous) pour dessiner les schémas en SVG.
- Le convertisseur (ci-dessous). Le placer dans un dossier de travail, **pas** dans les
  outils de l'utilisateur ; n'écrire dans le dossier de livrables que le PDF.

### Correspondance Markdown → PDF

| Markdown | PDF |
|---|---|
| `# N. Titre` | nouvelle page, `section-head` : numéro `NN`, surtitre de groupe, titre |
| `## …` / `### …` / `#### …` | `.h2` vert / `.h3` encre / `.h4` bleu |
| tableau | `table.grid` ; 5-6 colonnes → `grid-moyen` ; ≥ 7 colonnes → `grid-large` (`table-layout:fixed`) |
| liste `-` / `1.` | `ul.clean` / `ol.num` (imbrication par indentation) |
| `> …` | `.callout` |
| `` `code` `` | `.code` avec **espaces de largeur nulle** après `/ _ . , |` (coupures propres) |
| ```` ```mermaid ```` | **schéma SVG** charte Forêt (`flowchart`, `erDiagram`) ou **étapes numérotées** dans une `.card` (`sequenceDiagram`) |
| bloc de code texte | `pre.ascii` ; le schéma ASCII d'infrastructure → schéma SVG |
| « Comment lire cette fiche » | section `00 · Mode d'emploi` |
| « Sommaire » Markdown | remplacé par le sommaire premium groupé |

Groupes du sommaire : **Présentation** (1) · **Les couches** (2-7) · **Fonctionnalités et
sécurité** (8) · **Exploitation** (9-11) · **Références** (12-18).

Couverture : surtitre « FICHE TECHNIQUE DE RÉFÉRENCE », titre « <Produit><br><sous-titre> »,
sous-titre « Comment <Produit> est construit, couche par couche, et comment chaque fonction
marche », pastille **« Document interne »**, encadré méta (Destinée à · Contenu ·
Référence `FT-<PRODUIT>-AAAA V<n> · état au JJ/MM/AAAA`), mention légale : « Document interne
<Votre marque> : il cite des fichiers, des ports et des fournisseurs. Pour <client>, utiliser seulement
la partie 16 « Version partageable ». »

Nom du PDF : `<Produit>-Fiche-techniqueV<n>-interne.pdf` — **ne jamais écraser** une version
existante.

### CSS (`_style-fiche.css`, à coller tel quel)

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
  @bottom-left{content:"<Produit> — <sous-titre> · Fiche technique · <Votre marque>";font-family:'Inter',sans-serif;font-size:8pt;color:#94A3B8;}
  @bottom-right{content:counter(page)" / "counter(pages)"   ·   FT-<PRODUIT>-AAAA";font-family:'JetBrains Mono',monospace;font-size:7pt;color:#94A3B8;}
}
@page :first{margin:0;@bottom-left{content:none;}@bottom-center{content:none;}@bottom-right{content:none;}}
@page closing{margin:0;@bottom-left{content:none;}@bottom-center{content:none;}@bottom-right{content:none;}}
*{box-sizing:border-box;}
html,body{margin:0;padding:0;font-family:'Inter','Segoe UI',Helvetica,Arial,sans-serif;font-size:10pt;line-height:1.48;color:var(--text);}
.mono{font-family:'JetBrains Mono','Consolas','Courier New',monospace;letter-spacing:.2px;}
h1,h2,h3{margin:0;}
p{margin:0 0 3.5mm;}
.lead{font-size:12pt;color:var(--text-muted);line-height:1.55;}
strong{color:var(--text);}
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
.cover-meta-label{font-size:7.5pt;font-weight:800;letter-spacing:.16em;color:var(--green-600);text-transform:uppercase;}
.cover-meta-value{font-size:11pt;font-weight:700;color:var(--text);}
.cover-legal{position:absolute;bottom:16mm;left:18mm;right:18mm;text-align:center;font-size:8pt;color:var(--text-light);font-style:italic;}
.cover-band-bottom{position:absolute;bottom:0;left:0;right:0;height:12mm;background:linear-gradient(135deg,var(--green-700),var(--green-500));}
.toc{page-break-after:always;padding-top:4mm;}
.toc h1{font-size:22pt;font-weight:800;margin-bottom:4mm;}
.toc-divider{width:40mm;height:3px;background:linear-gradient(90deg,var(--green-500),var(--green-700));border-radius:2px;margin-bottom:8mm;}
.toc-group{font-size:9pt;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--green-600);margin:6mm 0 2mm;}
.toc-item{display:flex;align-items:baseline;gap:8px;padding:3px 0;font-size:11pt;}
.toc-num{font-family:'JetBrains Mono',monospace;font-weight:700;color:var(--green-500);min-width:22px;}
.section{page-break-before:always;}
.section-head{display:flex;align-items:center;gap:14px;margin-bottom:6mm;padding-bottom:4mm;border-bottom:2px solid var(--green-100);}
.section-num{font-family:'JetBrains Mono',monospace;font-size:24pt;font-weight:800;color:var(--green-200);line-height:1;}
.section-eyebrow{font-size:8.5pt;font-weight:700;letter-spacing:.22em;text-transform:uppercase;color:var(--green-500);}
.section-head > div:last-child{flex:1;}
.section-title{font-size:19pt;font-weight:800;color:var(--text);letter-spacing:-.01em;}
.keep{page-break-inside:avoid;}
ul.clean{margin:0 0 4mm;padding-left:5mm;} ul.clean li{margin-bottom:2mm;}
.card{background:#fff;border:1px solid var(--border);border-left:4px solid var(--green-500);border-radius:10px;padding:5mm 6mm;margin:0 0 4mm;box-shadow:0 4px 14px -8px rgba(0,0,0,.15);page-break-inside:avoid;}
.card h4{font-size:9.5pt;font-weight:800;color:var(--green-700);margin-bottom:2mm;}
.callout{background:var(--green-50);border:1px solid var(--green-100);border-radius:10px;padding:4mm 5mm;margin:0 0 4mm;font-size:10pt;page-break-inside:avoid;}
table.grid{width:100%;border-collapse:collapse;margin:0 0 4mm;font-size:9.2pt;}
table.grid th{background:var(--green-600);color:#fff;text-align:left;padding:5px 8px;font-weight:700;}
table.grid td{border:1px solid var(--border);padding:5px 8px;vertical-align:top;overflow-wrap:break-word;}
table.grid tr:nth-child(even) td{background:var(--bg-soft);}
table.grid thead{display:table-header-group;}
table.grid tr{break-inside:avoid;page-break-inside:avoid;}
table.grid-moyen{font-size:8.4pt;}
table.grid-large{font-size:7.2pt;table-layout:fixed;}
table.grid-large td{overflow-wrap:anywhere;}
table.grid-large td,table.grid-large th{padding:3px 4px;}
table.grid-large .code{font-size:6.6pt;}
.steps{margin:0;padding-left:5mm;counter-reset:step;list-style:none;}
.steps li{position:relative;padding:5px 0 5px 8mm;counter-increment:step;font-size:10pt;line-height:1.5;}
.steps li::before{content:counter(step);position:absolute;left:0;top:4px;width:6mm;height:6mm;border-radius:50%;background:var(--green-500);color:#fff;font-size:8.5pt;font-weight:800;display:block;text-align:center;line-height:6mm;}
.h2{font-size:13.5pt;font-weight:800;color:var(--green-700);margin:6mm 0 2.5mm;page-break-after:avoid;}
.h3{font-size:11pt;font-weight:800;color:var(--text);margin:4.5mm 0 2mm;page-break-after:avoid;}
.h4{font-size:10pt;font-weight:800;color:var(--blue);margin:4mm 0 1.5mm;page-break-after:avoid;}
.code{font-family:'JetBrains Mono','Consolas',monospace;font-size:8.4pt;background:var(--bg-medium);color:var(--green-900);padding:0 3px;border-radius:3px;}
ol.num{margin:0 0 4mm;padding-left:6mm;} ol.num li{margin-bottom:1.5mm;}
ul.clean ul.clean{margin:1mm 0 1mm;}
pre.ascii{font-family:'JetBrains Mono','Consolas',monospace;font-size:7.6pt;line-height:1.35;background:var(--bg-soft);border:1px solid var(--border);border-left:4px solid var(--green-500);border-radius:8px;padding:4mm 5mm;white-space:pre;margin:0 0 4mm;}
.figure{margin:2mm 0 5mm;text-align:center;}
.figure img{width:100%;border:1px solid var(--border);border-radius:10px;}
.figure-legende{font-size:8.5pt;color:var(--text-muted);font-style:italic;margin-top:1.5mm;}
.cover-interne{display:inline-block;margin-top:5mm;padding:2px 12px;border-radius:999px;background:var(--warning-soft);color:#92400E;font-size:9pt;font-weight:800;letter-spacing:.12em;text-transform:uppercase;}
.closing{page:closing;page-break-before:always;height:297mm;width:210mm;position:relative;background:#fff;display:flex;flex-direction:column;}
.closing-band{height:60mm;background:linear-gradient(135deg,var(--green-700),var(--green-500),var(--green-400));}
.closing-body{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 24mm;}
.closing-eyebrow{font-size:9pt;font-weight:700;letter-spacing:.4em;color:var(--green-500);text-transform:uppercase;}
.closing-title{font-size:24pt;font-weight:800;color:var(--text);margin-top:8px;}
.closing-sub{font-size:12pt;color:var(--text-muted);margin-top:10px;max-width:120mm;}
.closing-foot{padding:0 24mm 22mm;text-align:center;font-size:8.5pt;color:var(--text-light);font-style:italic;}
```

### Classe `Schema` (schémas SVG, charte Forêt)

Les textes des cases ne passent **pas** à la ligne seuls : une ligne ≈ 26 caractères pour
une case de 170 px. Titre en gras + 1 à 3 lignes.

```python
import html

TONS = {  # fond, dégradé, bordure, texte, sous-texte
    'bleu':   ('#1B5F8C', '#2A74A6', '#13476A', '#FFFFFF', '#E6F0F7'),
    'vert':   ('#3F8A3D', '#4FA34C', '#2C6A2A', '#FFFFFF', '#EAF4E9'),
    'or':     ('#B8860B', '#D4A017', '#8A6608', '#FFFFFF', '#FFF4D6'),
    'eme':    ('#10B981', '#34D399', '#0B7A5E', '#0E1A24', '#0E1A24'),
    'rouge':  ('#EF4444', '#F87171', '#B91C1C', '#FFFFFF', '#FFE4E4'),
    'carte':  ('#FFFFFF', None, '#3F8A3D', '#0E1A24', '#475569'),
    'exemple': ('#FCF6E8', None, '#B8860B', '#0E1A24', '#475569'),
}
FLECHES = {'vert': '#3F8A3D', 'bleu': '#1B5F8C', 'rouge': '#B91C1C', 'or': '#8A6608', 'gris': '#64748B'}


class Schema:
    def __init__(self, num, nom, largeur, hauteur):
        self.num, self.nom, self.l, self.h = num, nom, largeur, hauteur
        self.noeuds, self.fleches = {}, []

    def noeud(self, nid, x, y, w, h, ton, titre, lignes=(), losange=False, align='left'):
        self.noeuds[nid] = dict(x=x, y=y, w=w, h=h, ton=ton, titre=titre, lignes=list(lignes),
                                losange=losange, align=align)

    def fleche(self, a, b, sa='r', sb='l', ton='vert', libelle='', pointille=False, via=None):
        self.fleches.append(dict(a=a, b=b, sa=sa, sb=sb, ton=ton, libelle=libelle,
                                 pointille=pointille, via=via))

    def ancre(self, nid, cote):
        n = self.noeuds[nid]
        x, y, w, h = n['x'], n['y'], n['w'], n['h']
        return {'r': (x + w, y + h / 2), 'l': (x, y + h / 2), 't': (x + w / 2, y), 'b': (x + w / 2, y + h)}[cote]

    def chemin(self, f):
        (x1, y1), (x2, y2) = self.ancre(f['a'], f['sa']), self.ancre(f['b'], f['sb'])
        if f['via']:
            return [(x1, y1)] + list(f['via']) + [(x2, y2)]
        if f['sa'] in 'rl' and f['sb'] in 'rl':
            mx = (x1 + x2) / 2
            return [(x1, y1), (mx, y1), (mx, y2), (x2, y2)] if y1 != y2 else [(x1, y1), (x2, y2)]
        if f['sa'] in 'tb' and f['sb'] in 'tb':
            my = (y1 + y2) / 2
            return [(x1, y1), (x1, my), (x2, my), (x2, y2)] if x1 != x2 else [(x1, y1), (x2, y2)]
        if f['sa'] in 'tb':
            return [(x1, y1), (x1, y2), (x2, y2)]
        return [(x1, y1), (x2, y1), (x2, y2)]

    def svg(self):
        p = 's%d' % self.num
        o = ['<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg">' % (self.l, self.h), '<defs>']
        for ton, (a, b, *_r) in TONS.items():
            if b:
                o.append('<linearGradient id="%s%s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/>'
                         '<stop offset="1" stop-color="%s"/></linearGradient>' % (p, ton, a, b))
        for nom, coul in FLECHES.items():
            o.append('<marker id="%sf%s" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">'
                     '<path d="M0,0 L9,4.5 L0,9 z" fill="%s"/></marker>' % (p, nom, coul))
        o.append('</defs><rect width="%d" height="%d" fill="#FAF8F4"/>' % (self.l, self.h))
        for n in self.noeuds.values():
            fond, deg, bord, txt, sous = TONS[n['ton']]
            remp = 'url(#%s%s)' % (p, n['ton']) if deg else fond
            trait = ' stroke="%s"' % bord if bord else ''
            x, y, w, h = n['x'], n['y'], n['w'], n['h']
            if n['losange']:
                o.append('<polygon points="%s,%s %s,%s %s,%s %s,%s" fill="%s"%s/>' % (
                    x + w / 2, y, x + w, y + h / 2, x + w / 2, y + h, x, y + h / 2, remp, trait))
            else:
                o.append('<rect x="%s" y="%s" width="%s" height="%s" rx="10" fill="%s"%s/>' % (x, y, w, h, remp, trait))
            nb = 1 + len(n['lignes'])
            ty = y + (h - (17 + 15 * (nb - 1))) / 2 + 13
            centre = n['align'] == 'center' or n['losange']
            tx = x + w / 2 if centre else x + 13
            ancre = ' text-anchor="middle"' if centre else ''
            o.append('<text x="%s" y="%s" font-family="Helvetica" font-size="13.5" font-weight="bold" fill="%s"%s>%s</text>'
                     % (tx, ty, txt, ancre, html.escape(n['titre'])))
            for i, l in enumerate(n['lignes']):
                o.append('<text x="%s" y="%s" font-family="Helvetica" font-size="11" fill="%s"%s>%s</text>'
                         % (tx, ty + 17 + 15 * i, sous, ancre, html.escape(l)))
        for f in self.fleches:
            pts = self.chemin(f)
            coul = FLECHES[f['ton']]
            d = 'M' + ' L'.join('%s,%s' % pt for pt in pts)
            tiret = ' stroke-dasharray="6 4"' if f['pointille'] else ''
            o.append('<path d="%s" fill="none" stroke="%s" stroke-width="2.2"%s marker-end="url(#%sf%s)"/>'
                     % (d, coul, tiret, p, f['ton']))
            if f['libelle']:
                i = len(pts) // 2
                (ax, ay), (bx, by) = pts[i - 1], pts[i]
                lx, ly = (ax + bx) / 2, (ay + by) / 2
                lw = 6.2 * len(f['libelle']) + 12
                o.append('<rect x="%s" y="%s" width="%s" height="18" rx="5" fill="#FAF8F4"/>' % (lx - lw / 2, ly - 10, lw))
                o.append('<text x="%s" y="%s" font-family="Helvetica" font-size="10.5" font-weight="bold" fill="%s" '
                         'text-anchor="middle">%s</text>' % (lx, ly + 3.5, coul, html.escape(f['libelle'])))
        o.append('</svg>')
        return '\n'.join(o)
```

**Les quatre schémas du modèle** (largeur 760, pas de 190 entre colonnes de 170) :

| Schéma | Disposition |
|---|---|
| **Vue d'ensemble** (760×470) | Utilisateur (bleu, centré) → 3 interfaces (vert) ; tunnel sous l'hébergeur ; API (or) au centre ; à droite de l'API : modèle externe (émeraude) et services coupés (rouge, pointillé) ; en bas : 4 ressources locales (vert). Réutilisé pour la partie 9. |
| **Données** (760×500) | rangée 1 : organisation → user → conversation → message (« 1-n ») ; rangée 2 : questions validées (or) ← « crée (option) », versions, carte « Rattachés au message » ; rangée 3 : document → chunk ; rangée 4 : cartes transverses. Lien logique message → chunk en bleu pointillé, **libellé posé sur un segment horizontal dans un espace vide** (`via` à 4 points). |
| **RAG** (760×330) | rangée 1, gauche → droite : corpus → extraction → découpage → embeddings ; descente vers stockage ; rangée 2, droite → gauche : stockage → recherche (or) → prompt + modèle → réponse citée (émeraude) ; question (bleu) sous la recherche ; « bonne version » en pointillé or. |
| **Bot** (760×640) | serpentin numéroté : 1-4 en rangée 1 ; 5 analyse → losange « Il manque une information ? » (non → recherche, oui → cadrage, en dessous) → 6 recherche → 7 rédaction ; 8 contrôles → 9 en attente → 10 consultant → 11 réponse publiée (émeraude) ; encadré « Chemins courts » en bas. |

Les `sequenceDiagram` deviennent des **étapes numérotées** dans une `.card` :
`<h4>Acteurs : …</h4><ol class="steps">…</ol>`, 5 à 8 étapes, chacune avec le fichier ou
l'endpoint en `code`.

### Convertisseur Markdown → PDF (gabarit à adapter)

Adapter seulement le bloc **CONFIGURATION**, les schémas et les flux. Le reste est stable.

```python
# -*- coding: utf-8 -*-
"""Fiche technique de référence (Markdown du dépôt) → PDF premium (charte Forêt)."""
from __future__ import annotations
import html, re
from pathlib import Path
from weasyprint import HTML
# from schema_foret import Schema     # la classe ci-dessus, dans un fichier voisin

# ── CONFIGURATION ──────────────────────────────────────────────────────────────
ICI = Path(__file__).resolve().parent
MD = Path(r"<dépôt>\docs\fiche-technique\fiche-technique-<projet>.md")
CSS = ICI / "_style-fiche.css"
LOGO = ICI / "logo.jpg"
SORTIE_PDF = Path(r"<dossier livrables>\<Produit>-Fiche-techniqueV<n>-interne.pdf")
PRODUIT, SOUS_TITRE, REF, DATE = "<Produit>", "<sous-titre>", "FT-<PRODUIT>-AAAA V<n>", "JJ/MM/AAAA"
CLIENT = "<client>"
MARQUE, ACCROCHE = "<Votre marque>", "<accroche>"
VOLETS = {1: "Présentation", 2: "Volet technique", 3: "Volet technique", 4: "Volet technique",
          5: "Volet technique", 6: "Connaissances", 7: "Intelligence artificielle", 8: "Fonctionnalités",
          9: "Exploitation", 10: "Exploitation", 11: "Flux", 12: "Références", 13: "Références",
          14: "Références", 15: "Références", 16: "Partageable", 17: "Références", 18: "Références"}
GROUPES = [("Présentation", [1]), ("Les couches", [2, 3, 4, 5, 6, 7]), ("Fonctionnalités et sécurité", [8]),
           ("Exploitation", [9, 10, 11]), ("Références", [12, 13, 14, 15, 16, 17, 18])]
MARQUEUR_INFRA = "<texte présent dans le schéma ASCII de la partie 9>"
SVG = ICI / "svg"; SVG.mkdir(exist_ok=True)


def inline(t: str) -> str:
    t = html.escape(t, quote=False)
    # code : coupures propres après / _ . , |  (r"\1" — jamais "\1", qui donne le caractère 0x01)
    t = re.sub(r"`([^`]+)`", lambda m: '<span class="code">' + re.sub(r"([/_.,|])", r"\1" + "\u200b", m.group(1)) + "</span>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", t)
    return t


# ── SCHÉMAS (une fonction par schéma, voir le tableau des dispositions) ──────────
def s_ensemble(num): ...     # Schema(num, "Vue d'ensemble", 760, 470) + noeuds + flèches
def s_donnees(num): ...
def s_rag(num): ...
def s_bot(num): ...
def s_infra(num): return s_ensemble(num)

SCHEMAS = {}
for i, fab in enumerate((s_ensemble, s_donnees, s_rag, s_bot, s_infra), start=11):
    chemin = SVG / f"fiche-{i}.svg"; chemin.write_text(fab(i).svg(), encoding="utf-8")
    SCHEMAS[fab.__name__] = chemin

def figure(nom, legende):
    return (f'<div class="figure keep"><img src="{SCHEMAS[nom].as_uri()}" alt="{html.escape(legende)}">'
            f'<div class="figure-legende">{html.escape(legende)}</div></div>')

def etapes(acteurs, lignes):
    li = "".join(f"<li>{inline(l)}</li>" for l in lignes)
    return f'<div class="card keep"><h4>{html.escape(acteurs)}</h4><ol class="steps">{li}</ol></div>'

FLUX = [etapes("Acteurs : …", ["…"]) for _ in range(5)]   # connexion, question, validation, consultation, administration
# Dans l'ordre d'apparition des blocs ```mermaid du Markdown :
MERMAID = [figure("s_ensemble", "…"), figure("s_donnees", "…"), figure("s_rag", "…"), figure("s_bot", "…"), *FLUX]


# ── MARKDOWN → HTML ───────────────────────────────────────────────────────────
def table(lignes):
    rangs = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lignes
             if not re.match(r"^\s*\|[\s:\-|]+\|\s*$", l)]
    ent, corps = rangs[0], rangs[1:]
    cl = "grid" + (" grid-large" if len(ent) >= 7 else " grid-moyen" if len(ent) >= 5 else "")
    th = "".join(f"<th>{inline(c)}</th>" for c in ent)
    tr = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in corps)
    return f'<table class="{cl}"><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table>'

def liste(lignes):
    items = []
    for l in lignes:   # réunir d'abord le texte complet de chaque élément (le gras peut couper une ligne)
        m = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", l)
        if m: items.append([len(m.group(1)) // 2, "ol" if m.group(2)[0].isdigit() else "ul", m.group(3)])
        else: items[-1][2] += " " + l.strip()
    out, pile = [], []
    for niveau, tag, contenu in items:
        while len(pile) > niveau + 1 or (pile and len(pile) == niveau + 1 and pile[-1] != tag):
            out.append(f"</{pile.pop()}>")
        while len(pile) < niveau + 1:
            pile.append(tag); out.append('<ol class="num">' if tag == "ol" else '<ul class="clean">')
        out.append(f"<li>{inline(contenu)}</li>")
    while pile: out.append(f"</{pile.pop()}>")
    return "".join(out)

def convertir(md, attendu):
    L, out, som, i, n, ouverte = md.split("\n"), [], [], 0, 0, False
    debut_liste = r"^\s*([-*]|\d+\.)\s+"
    while i < len(L):
        l = L[i]
        if l.startswith("```"):
            langue, bloc = l[3:].strip(), []; i += 1
            while not L[i].startswith("```"): bloc.append(L[i]); i += 1
            i += 1
            if langue == "mermaid": out.append(MERMAID[n]); n += 1
            elif any(MARQUEUR_INFRA in b for b in bloc): out.append(figure("s_infra", f"Infrastructure réelle au {DATE}"))
            else: out.append('<pre class="ascii keep">' + html.escape("\n".join(bloc)) + "</pre>")
            continue
        m = re.match(r"^# (\d+)\. (.*)$", l)
        if m:
            num, titre = int(m.group(1)), m.group(2).strip()
            if ouverte: out.append("</div>")
            out.append(f'<div class="section"><div class="section-head"><div class="section-num">{num:02d}</div>'
                       f'<div><div class="section-eyebrow">{VOLETS.get(num, "")}</div>'
                       f'<div class="section-title">{inline(titre)}</div></div></div>')
            ouverte = True; som.append((num, titre)); i += 1; continue
        for pre, cl in (("#### ", "h4"), ("### ", "h3"), ("## ", "h2")):
            if l.startswith(pre):
                out.append(f'<{cl} class="{cl}">{inline(l[len(pre):])}</{cl}>'); i += 1; break
        else:
            if l.startswith("|"):
                bloc = []
                while i < len(L) and L[i].startswith("|"): bloc.append(L[i]); i += 1
                out.append(table(bloc)); continue
            if re.match(debut_liste, l):
                bloc = []
                while i < len(L) and (re.match(debut_liste, L[i]) or (L[i].startswith("  ") and L[i].strip())):
                    bloc.append(L[i]); i += 1
                out.append(liste(bloc)); continue
            if l.startswith(">"):
                bloc = []
                while i < len(L) and L[i].startswith(">"): bloc.append(L[i].lstrip("> ").rstrip()); i += 1
                out.append(f'<div class="callout">{inline(" ".join(bloc))}</div>'); continue
            if l.strip() in ("", "---"): i += 1; continue
            bloc = [l]; i += 1
            while i < len(L) and L[i].strip() and not re.match(r"^(#|\||>|```|\s*([-*]|\d+\.)\s)", L[i]):
                bloc.append(L[i]); i += 1
            out.append(f"<p>{inline(' '.join(x.strip() for x in bloc))}</p>")
    if ouverte: out.append("</div>")
    assert n == attendu, (n, attendu)      # autant de blocs mermaid que de rendus prévus
    return "\n".join(out), som

texte = MD.read_text(encoding="utf-8")
avant, _, corps = texte.partition("\n# 1. ")
corps = "# 1. " + corps
lecture = avant.split("## Comment lire cette fiche")[1].split("## Sommaire")[0]
corps_html, som = convertir(corps, len(MERMAID))
lecture_html, _ = convertir(lecture, 0)
titres = dict(som)
toc = "".join(f'<div class="toc-group">{g}</div>' + "".join(
    f'<div class="toc-item"><span class="toc-num">{n}</span><span>{inline(titres[n])}</span></div>' for n in nums)
    for g, nums in GROUPES)

page = f"""<!DOCTYPE html><html lang="fr"><head><meta charset="utf-8">
<title>{PRODUIT} — {SOUS_TITRE} · Fiche technique de référence</title>
<style>{CSS.read_text(encoding="utf-8")}</style></head><body>
<div class="cover">
  <div class="cover-band"><div class="cover-logo-zone"><img src="{LOGO.as_uri()}" class="cover-logo" alt="Logo">
    <div class="cover-brand">{MARQUE}</div><div class="cover-tagline">— {ACCROCHE} —</div></div></div>
  <div class="cover-title-zone"><div class="cover-eyebrow">FICHE TECHNIQUE DE RÉFÉRENCE</div>
    <div class="cover-title">{PRODUIT}<br>{SOUS_TITRE}</div><div class="cover-divider"></div>
    <div class="cover-sub">Comment {PRODUIT} est construit, couche par couche,<br>et comment chaque fonction marche</div>
    <div class="cover-interne">Document interne</div></div>
  <div class="cover-meta">
    <div class="cover-meta-row"><div><div class="cover-meta-label">Destinée à</div><div class="cover-meta-value">{MARQUE} — direction, équipe technique, revue technique</div></div></div>
    <div class="cover-meta-row"><div><div class="cover-meta-label">Contenu</div><div class="cover-meta-value">Architecture · Données · RAG · IA · Sécurité · Infrastructure</div></div></div>
    <div class="cover-meta-row"><div><div class="cover-meta-label">Référence</div><div class="cover-meta-value mono">{REF} · état au {DATE}</div></div></div></div>
  <div class="cover-legal">Document interne {MARQUE} : il cite des fichiers, des ports et des fournisseurs. Pour {CLIENT}, utiliser seulement la partie 16 « Version partageable ».</div>
  <div class="cover-band-bottom"></div></div>
<div class="toc"><h1>Sommaire</h1><div class="toc-divider"></div>
  <p class="lead">Cette fiche décrit le code réel de {PRODUIT}, analysé le {DATE}. Elle répond à trois questions : sur quoi le projet est construit, comment les données circulent, et quelles protections existent.</p>{toc}</div>
<div class="section"><div class="section-head"><div class="section-num">00</div>
  <div><div class="section-eyebrow">Mode d'emploi</div><div class="section-title">Comment lire cette fiche</div></div></div>{lecture_html}</div>
{corps_html}
<div class="closing"><div class="closing-band"></div><div class="closing-body">
  <div class="closing-eyebrow">{MARQUE}</div><div class="closing-title">{PRODUIT} — {SOUS_TITRE}</div>
  <div class="closing-sub">Une phrase de clôture fidèle au projet (aucune promesse).</div></div>
  <div class="closing-foot">{REF} · état au {DATE} · document interne · {MARQUE}</div></div>
</body></html>"""

sortie_html = ICI / "fiche-technique.html"
sortie_html.write_text(page, encoding="utf-8")
doc = HTML(filename=str(sortie_html), base_url=str(ICI)).render()
doc.write_pdf(str(SORTIE_PDF))
print("pages :", len(doc.pages), "·", SORTIE_PDF.name, SORTIE_PDF.stat().st_size // 1024, "Ko")
```

`pip install weasyprint` ; sous Windows il faut le runtime GTK3. Les avertissements
`GLib-GIO-WARNING` sont inoffensifs.

---

## 07 — Relire le PDF (obligatoire)

Générer n'est pas vérifier.

```python
import fitz                      # PyMuPDF
from PIL import Image
from pathlib import Path
d = fitz.open(PDF)
Path("pages").mkdir(exist_ok=True)
for i, p in enumerate(d): p.get_pixmap(dpi=60).save(f"pages/p{i+1:02d}.png")
ims = sorted(Path("pages").glob("p*.png"))
for k in range(0, len(ims), 12):                       # planches de 12 pages
    grp = [Image.open(x) for x in ims[k:k + 12]]; w, h = grp[0].size
    W = Image.new("RGB", (w * 6, h * 2), "white")
    for j, im in enumerate(grp): W.paste(im, ((j % 6) * w, (j // 6) * h))
    W.save(f"planche{k // 12 + 1}.png")
# texte qui sort de la marge droite (A4 = 595 pt, marge 16 mm)
lim = 595 - 16 * 72 / 25.4 + 2
for i, p in enumerate(d):
    if 0 < i < len(d) - 1 and any(b[2] > lim for b in p.get_text("blocks")): print("débordement page", i + 1)
```

Regarder **toutes** les planches, puis zoomer (`dpi=90-110`, `clip=`) sur les schémas et le
tableau de traçabilité. Défauts déjà rencontrés et leur correction :

| Défaut | Cause | Correction |
|---|---|---|
| `**texte**` affiché avec ses astérisques | gras coupé entre deux lignes d'une puce | réunir le texte complet de l'élément **avant** `inline()` |
| `####` affiché brut | niveau de titre non géré | gérer `####` → `.h4` |
| mots coupés lettre par lettre dans une colonne | `overflow-wrap:anywhere` sur toutes les cellules | `break-word` partout ; `anywhere` seulement pour `grid-large` |
| colonne de droite coupée hors de la page | tableau ≥ 7 colonnes en largeur automatique | `table-layout:fixed` + police 7,2 pt |
| chemins longs qui ne se coupent pas | aucun point de coupure | espace de largeur nulle après `/ _ . , |` |
| caractère invisible `\x01` dans le HTML | `"\1"` dans une chaîne normale | `r"\1" + "\u200b"` |
| libellé de flèche coupé au bord du schéma | libellé sur un segment vertical collé au bord | router la flèche (`via`) pour poser le libellé sur un segment horizontal dans un espace vide |

---

## 08 — Livrer

Réponse courte, sections `##`, en français simple :
- ce qui est livré (chemins des 3 fichiers, nombre de pages) ;
- ce qui a été vérifié (analyse en six volets, chemins existants, aucun secret, relecture
  visuelle) ;
- ce qui est marqué honnêtement (production, modèle actuel/prévu, raisons inconnues) ;
- **le caractère interne du PDF** et la partie 16 pour le client (proposer un PDF client
  séparé, sans le faire sans accord) ;
- les points « à confirmer » et les écarts trouvés (sans les avoir corrigés) ;
- `## Zone technique concernée` puis `## Libellé de commit` (convention du projet ; ne
  jamais commiter à la place de l'utilisateur ; rien à commiter si seul un fichier hors
  dépôt a changé).

---

## Checklist qualité

- [ ] Six analyses faites avant d'écrire ; contradictions vérifiées à la main.
- [ ] Les 18 parties, dans l'ordre, avec les tableaux obligatoires ; grille commune appliquée.
- [ ] Bot suivi du clic à l'affichage (page, composant, fonction, route, service,
      anonymisation, RAG, sources, prompt, modèle, contrôles, validation, stockage, affichage).
- [ ] Anonymisation : fichier exact, moment, catégories exactes, repères, correspondance,
      restitution, base, journaux, limites.
- [ ] Modèle **actuel / prévu / testé** distingués ; « Production non déployée » si c'est le cas.
- [ ] Chaque choix : raison documentée, **Déduction**, ou « Raison historique non identifiable ».
- [ ] Chemins cités existants ; aucun secret ; partie 16 sans chemin, port, variable ni
      fournisseur intermédiaire.
- [ ] Schéma draw.io à 2 onglets, XML valide.
- [ ] PDF : couverture « Document interne », sommaire groupé, sections `00`-`18`, 4 schémas
      SVG + 5 flux en étapes, page de fin ; relu sur planches ; aucun débordement.
- [ ] Aucune version existante écrasée ; rien corrigé dans le projet sans demande.

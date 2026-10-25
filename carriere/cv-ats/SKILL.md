---
name: cv-ats
description: Reconstruit un CV professionnel compatible ATS à partir d'un fichier Markdown ou d'un ancien CV (PDF, texte, image), détecte le domaine et le niveau du candidat, adapte la structure, et livre 3 PDF premium d'une page (bleu, émeraude, bordeaux) contrôlés automatiquement (lecture ATS, mise en page, cohérence). Utiliser pour toute demande de création, refonte, reconstruction ou mise en forme de CV / résumé, y compris en anglais.
---

# cv-ats — reconstruction de CV ATS en trois couleurs

Une source (Markdown ou ancien CV) donne **3 PDF A4** prêts à envoyer. Ils ont le même contenu et la même
mise en page, avec trois identités de couleur. Le design reprend la version de référence **V4**
(mesures dans [references/design.md](references/design.md)).

Le travail se partage en deux :

- **toi (le modèle)** : comprendre la source, structurer, réécrire, juger ;
- **les scripts** : mise en page, ajustement à la page, PDF, contrôles, aperçus.

## Prérequis

macOS avec `python3` et `swiftc` (Xcode Command Line Tools). Rien d'autre à installer.
L'outil natif `scripts/cvtool.swift` se compile tout seul au premier lancement.

## Règle absolue

**Ne jamais inventer** une expérience, une entreprise, une date, un chiffre, une compétence, une
certification ou une information personnelle. Une information manquante ou ambiguë va dans
`a_confirmer`. Elle n'est pas comblée par une supposition. Reformuler est permis ; ajouter un fait,
non.

## Déroulé

### 1. Lire la source

- **Markdown / texte** : c'est la source principale des données.
- **Ancien CV en PDF** : `scripts/.bin/cvtool texte ancien.pdf` (texte tel qu'un ATS le lit). Regarder
  aussi le PDF lui-même : l'ordre extrait peut être mélangé.
- **Image ou scan** : le lire visuellement.
- **Photo** : noter son chemin. Elle sera recadrée automatiquement sur le visage.

### 2. Détecter domaine et niveau

```bash
python3 scripts/cv.py detecter source.md
```

C'est un second avis par mots-clés, le poste visé compte triple. Tu décides : si le domaine
renvoyé est faux, écris le bon dans `domaine`. Domaines : `tech`, `ingenierie`, `finance`,
`marketing`, `commercial`, `management`, `design`, `sante`, `juridique`, `autre`.
Niveaux : `junior` (< 2 ans hors stages), `confirme`, `senior` (≥ 8 ans).
Le plan de sections de chaque domaine est dans [references/domaines.md](references/domaines.md).

### 3. Écrire `cv.json`

Format complet et exemple : [references/schema.md](references/schema.md).

- **Titre** : le poste visé, précis (« Développeur Full-Stack React / Node.js », pas « Développeur »).
- **Profil** : 2 à 3 phrases. Qui, combien d'années, spécialité, ce qu'on apporte. Pas de « dynamique
  et motivé ».
- **Missions** : un verbe d'action au début, une idée par ligne, le résultat chiffré s'il existe dans la
  source. 2 à 6 lignes par poste ; les postes anciens sont plus courts.
- **Corriger** : orthographe, accents, majuscules des noms propres, format des dates (`MM/AAAA` ou
  `AAAA`), intitulés incohérents. Supprimer les répétitions.
- **Compétences** : groupées par thème (3 à 10 groupes), sans doublon avec le titre du groupe.
- **Réalisations** (`realisations`) : 2 à 4 résultats marquants, **uniquement s'ils sont dans la source**.
  Utile en finance, marketing, commercial, management.
- **Langue du CV** (`langue`) : celle de la source ou celle demandée (`fr` / `en`). Les titres de
  sections suivent automatiquement.
- **Marché** (`marche`) : pays visé. Il décide de la photo (voir ci-dessous).

### 4. Photo

Une photo n'est incluse que si elle est **fournie** et **d'usage sur le marché** visé (Maroc, France,
Belgique, Suisse, Allemagne, Moyen-Orient : oui ; USA, UK, Canada, Irlande, Australie : non, sauf
`photo_forcee`). Le recadrage est automatique : visage détecté, cadrage de la V4. On ne crée jamais
de photo.

### 5. Générer

```bash
python3 scripts/cv.py construire cv.json --sortie DOSSIER_CLIENT
```

Environ 5 s pour les 3 PDF. Options : `--themes bleu` (une seule couleur), `--garder-html` (source
HTML éditable, seulement si le client veut retoucher la mise en page à la main).

La page s'ajuste seule : équilibre des colonnes, espacements et taille de texte dans des bornes
fixes, deux pages seulement si une page ne suffit pas.

### 6. Contrôler — obligatoire avant de livrer

1. Lire `DOSSIER_CLIENT/_controle/rapport.md`.
2. **Erreurs** : corriger `cv.json` puis régénérer. Ne jamais livrer avec une erreur.
3. **Avertissements** :
   - « mot isolé en fin de ligne » : reformuler la ligne citée, sans changer le sens ;
   - « page remplie à X % » (moins de 75 %) : demander au client plus de détails, sans rien inventer ;
   - « à confirmer » : à transmettre au client.
4. **Regarder chaque aperçu** (`_controle/apercus/*.png`, avec l'outil Read). Suivre la grille de
   [references/controle-qualite.md](references/controle-qualite.md).
5. Régénérer après chaque correction et recontrôler.

### 7. Livrer

- Les 3 PDF : `CV-Nom-Prenom-Bleu.pdf`, `-Emeraude.pdf`, `-Bordeaux.pdf`.
- `cv.json` est la source éditable : une correction = modifier le JSON et régénérer.
- Le dossier `_controle/` est interne : ne pas l'envoyer au client.
- Message au client : la liste des points `a_confirmer`, en questions courtes (oui / non, A ou B).

Pas de DOCX, PNG ou autre format, sauf demande explicite.

## Fichiers

| Fichier | Rôle |
|---|---|
| `scripts/cv.py` | commandes `construire`, `detecter`, `photo` |
| `scripts/domaines.py` | détection domaine / niveau, plans de sections, règle photo |
| `scripts/rendu.py` | JSON → HTML, 3 thèmes de couleur |
| `scripts/verifications.py` | contrôles données, lecture ATS, variantes |
| `scripts/cvtool.swift` | WebKit → PDF A4, recadrage photo (Vision), extraction texte, aperçus |
| `assets/cv.css` | gabarit V4 en variables |
| `assets/ajustement.js` | ajustement automatique de la page |
| `assets/profil-modele.md` | modèle à remplir par le client |
| `assets/fonts/` | police Geist (licence OFL) |
| `tests/` | 6 profils de test et `lancer_tests.py` |

## Tests

```bash
python3 tests/lancer_tests.py
```

Six profils fictifs : développeur, ingénieure, DAF senior, marketing UK en anglais, data analyst
junior, directeur avec un parcours très long (deux pages). Chaque profil passe par toute la chaîne
(source → domaine → PDF → ATS → mise en page → comparaison des trois couleurs). Regarder ensuite les
aperçus listés.

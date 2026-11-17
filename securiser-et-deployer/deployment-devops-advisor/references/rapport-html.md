# Le rapport HTML

Charte reprise de `powerpoint-premium` : mêmes couleurs, mêmes polices, mêmes
formes. Le deck est fait pour être projeté, le rapport pour être lu à 50 cm —
seule **l'échelle de taille** change.

**Le même rendu que `security-auditor`**, au mot près : le script est le même,
les deux rapports se lisent de la même façon. Ce qui change, c'est ce qu'on
met dedans.

**Fonds clairs uniquement. Un seul accent. Aucun dégradé.**

---

## 1. Ce qu'on ne fait pas à la main

Le HTML n'est **pas** écrit à la main. On écrit un fichier JSON de constats, et
le script le rend.

```bash
python scripts/rapport.py constats.json -o "Audit-deploiement-<Projet>.html"
```

Trois raisons :

1. La charte est toujours respectée, sans recopier 400 lignes de CSS.
2. Les deux agents rendent **exactement** la même mise en page.
3. Le script **masque les secrets** avant de les écrire. Un oubli humain ne
   peut pas faire fuiter une clé dans le rapport.

La forme du JSON est décrite plus bas, et un modèle complet est dans
[constats.exemple.json](../scripts/constats.exemple.json).

---

## 2. Les jetons

### Fonds et surfaces

| Rôle | Valeur |
|---|---|
| Fond de page | `#F2EDE1` |
| Bandeau, zone alternée | `#FAF7F0` |
| Carte | `#FFFFFF` |
| Bordure | `#E4DCCB` |
| Aplat sable | `#EFE7D6` |

### Texte

| Rôle | Valeur |
|---|---|
| Encre — titres, chiffres | `#1E2C38` |
| Gris — texte courant | `#5C6873` |
| Gris éteint | `#96A1AB` |

### Accent — un seul

| Rôle | Valeur |
|---|---|
| Accent | `#3E88B5` |
| Accent foncé | `#215C80` |
| Accent très pâle | `#E6F0F7` |
| Accent bordure | `#C3DCEB` |

### Formes

```
ombre : 0 2px 6px rgba(30,44,56,0.06)   ← une seule, partout
rayon : 20px cartes · 14px petits blocs · 999px badges
filet : 1px solid #E4DCCB
```

---

## 3. L'échelle de criticité

Ce ne sont **pas** des accents décoratifs. Ce sont des couleurs de fonction.
Elles ne servent que dans le badge et la barre de gauche d'un constat — jamais
en fond plein, jamais sur du texte courant.

| Niveau | Trait | Fond | Texte du badge |
|---|---|---|---|
| CRITIQUE | `#9E2B20` | `#FBF2F0` | `#7E2118` |
| ÉLEVÉ | `#B26A00` | `#FDF8F0` | `#8A5200` |
| MOYEN | `#A08200` | `#FBF8EA` | `#7A6300` |
| FAIBLE | `#3E88B5` | `#E6F0F7` | `#215C80` |
| INFORMATION | `#5C6873` | `#F4F1EA` | `#5C6873` |

Un niveau **n'est jamais seul**. Il est toujours accompagné de la phrase qui
dit pourquoi ce niveau-là.

---

## 4. Le niveau de confiance

Obligatoire sur chaque constat. Petite pastille en police machine, à côté du
niveau de criticité.

| Valeur | Ce que ça veut dire |
|---|---|
| **Confirmé** | lu dans le code, reproductible, montré |
| **Probable** | le code le laisse fortement penser, pas encore prouvé |
| **À vérifier** | une piste, il manque une information |
| **Non vérifiable** | impossible à trancher avec ce qui est accessible |

Un constat « Probable » ne s'écrit **jamais** comme un fait. La phrase le dit :
« le code semble… », pas « le code permet… ».

---

## 5. La typographie

| Famille | Usage |
|---|---|
| `'Source Serif 4', Georgia, serif` | titres, grands chiffres |
| `'IBM Plex Sans', Arial, sans-serif` | tout le texte |
| `'JetBrains Mono', Consolas, monospace` | code, chemins, identifiants |

Échelle **document** (le deck est à une autre échelle, ne pas la reprendre) :

| Élément | Taille | Graisse |
|---|---|---|
| Titre de couverture | 46 px | 600 |
| Titre de section | 30 px | 600 |
| Titre de constat | 19 px | 600 |
| Texte courant | 15.5 px | 400 |
| Sur-titre, badge | 11.5 px | 600, majuscules, `letter-spacing:.1em` |
| Code | 13 px | 400 |

Deux graisses : 400 et 600. Les polices viennent de Google Fonts ; sans
réseau, les polices de repli prennent le relais et le rapport reste propre.

---

## 6. La structure du rapport

Dans cet ordre. Une section vide ne s'affiche pas.

```text
Couverture            projet, date, dépôts analysés, niveau de risque global
Résumé exécutif       cinq lignes, lisibles par quelqu'un qui n'ouvrira rien d'autre
Compte des constats   le tableau par niveau
Architecture          ce qui a été compris du projet, en mots simples
Sections de constats  une par domaine, triées du plus grave au moins grave
Plan de correction    à faire avant / pendant / après le déploiement
Checklists            avant déploiement, après déploiement, retour arrière
Ce qui n'a pas pu être vérifié
```

La dernière section n'est pas optionnelle. Un audit qui ne dit pas ses limites
laisse croire que tout a été regardé.

---

## 7. La forme d'un constat

Le script rend ces champs. Tous sont attendus, sauf `chemin` et `norme`.

| Champ | Contenu |
|---|---|
| `titre` | le problème en une phrase, sans jargon |
| `criticite` | CRITIQUE · ÉLEVÉ · MOYEN · FAIBLE · INFORMATION |
| `confiance` | Confirmé · Probable · À vérifier · Non vérifiable |
| `pourquoi` | pourquoi c'est dangereux, en mots simples |
| `impact` | ce qui peut arriver concrètement |
| `ou` | le fichier et la ligne |
| `verifier` | comment le constater soi-même |
| `corriger` | la liste des étapes, dans l'ordre |
| `prouver` | comment savoir que c'est réparé |
| `chemin` | le scénario de panne, étape par étape |
| `norme` | la référence, si elle apporte quelque chose |

`chemin` s'affiche en escalier :

```text
Déploiement lancé
   ↓
Variable d'environnement absente
   ↓
Valeur par défaut « localhost » utilisée
   ↓
Le backend ne joint pas la base
   ↓
Le service démarre puis s'arrête en boucle
```

---

## 8. Ce que le script refuse

- Un constat sans `confiance` → erreur, pas de rapport.
- Une valeur qui ressemble à un secret → masquée, toujours.
- Un niveau de criticité inconnu → erreur.

Le rapport ne se génère pas tant que ces trois points ne passent pas.

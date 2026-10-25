# Design — référence V4

Le gabarit (`assets/cv.css`) reprend au millimètre la version V4 validée par le client. À
`--air = 1` et `--txt = 1`, la page est identique à la V4.

## Mesures

| Élément | Valeur |
|---|---|
| Page | A4, marges 10 mm (haut), 13 mm (côtés), 9 mm (bas) |
| Police | Geist Sans 400 / 500 / 600 / 700, intégrée, **ligatures désactivées** |
| Texte courant | 8,95 pt, interligne 1,38, couleur `#334155` |
| Nom | 19 pt, gras 700, `#0f172a` |
| Titre (poste) | 10,5 pt, 500, couleur du thème |
| Filet sous le titre | 14 mm × 2 px, couleur du thème |
| Coordonnées | 8,2 pt, sur une ligne (deux si trop long), séparées par « · » |
| Photo | 28 × 28 mm, coins 5 mm, filet 1 px `#e2e8f0` |
| Colonnes | principale souple, latérale 64 mm, écart 6 mm |
| Encadré latéral | fond `#f8fafc`, filet `#e2e8f0`, coins 3 mm, marges internes 3,2 × 3,8 mm |
| Titres de section | 8,2 pt majuscules, interlettrage 0,1 em, **point noir** de 1,6 mm, filet à droite |
| Écart entre sections | 5 mm (principale), 4 mm (latérale) |
| Écart entre postes | 2,4 mm |
| Compétences | intitulé du groupe en couleur du thème, filet fin entre groupes |

## Ajustement automatique (`assets/ajustement.js`)

1. **Équilibrage** : une section mobile change de colonne si cela améliore la colonne la plus serrée.
2. **Densité** : si le contenu déborde, l'espacement descend jusqu'à 72 %, puis le texte jusqu'à
   94 % (8,4 pt minimum).
3. **Aération** : si la page est trop vide, l'espacement monte jusqu'à 170 %, puis le texte jusqu'à
   108 %.
4. **Deux pages** : seulement si une page ne suffit pas à densité minimale. Aucun bloc n'est coupé ;
   un titre n'est jamais laissé seul en bas de page ; l'encadré latéral s'arrête avec son contenu.
5. **Typographie** : les chiffres et leur unité restent ensemble (« 18 MDH ») ; les deux derniers
   mots d'un paragraphe sont liés pour éviter un mot isolé, sauf si cela perturbe l'ordre de lecture
   ATS (le script régénère alors sans cette liaison).

Jamais d'espace insécable U+00A0 dans le texte : certains lecteurs PDF perdent alors la fin de ligne.
On utilise `white-space: nowrap`.

## Les trois couleurs

Seules `--accent` et `--accent-texte` changent. Contraste mesuré (WCAG) sur blanc et sur l'encadré :

| Version | Couleur | Sur blanc | Sur encadré | Caractère |
|---|---|---|---|---|
| Bleu | `#00478c` | 9,2:1 | 8,8:1 | corporate, confiance (couleur de la V4) |
| Émeraude | `#0b6655` | 6,9:1 | 6,6:1 | moderne, calme |
| Bordeaux | `#7a1f3d` | 10,0:1 | 9,6:1 | élégant, affirmé |

Minimum exigé par les contrôles : 4,5:1.

## Ce qui reste fixe

- Points des titres de section en noir (pas en couleur).
- Pas de dégradé, d'ombre, de flou, d'icône ni d'image décorative.
- Liens affichés par leur libellé, en couleur, sans soulignement.

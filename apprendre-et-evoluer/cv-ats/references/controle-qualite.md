# Contrôle qualité

Un CV n'est livré que si les deux contrôles sont bons : automatique **et** visuel.

## Contrôles automatiques (`_controle/rapport.md`)

| Contrôle | Bloquant |
|---|---|
| Nom, email valides ; téléphone complet | oui |
| Dates cohérentes (fin après début, pas de début futur) | oui |
| Chaque poste, entreprise, date, mission, diplôme, compétence, certification, langue, projet et réalisation se retrouve dans le texte extrait du PDF | oui |
| Ordre de lecture des expériences respecté | oui |
| Aucune ligature (lettres perdues par les ATS) ; polices intégrées | oui |
| Liens email et profils cliquables | oui |
| Format A4, rien ne dépasse à droite, rien ne déborde en bas | oui |
| Contraste de la couleur ≥ 4,5:1 | oui |
| Photo non vide (si présente) | oui |
| Les 3 variantes ont exactement le même texte | oui |
| Mot isolé en fin de ligne | non : reformuler |
| Page remplie à moins de 75 % | non : demander plus de détails au client |
| Deux pages pour un profil non senior | non : condenser |
| Texte réduit sous 8,4 pt | non : condenser |
| Points `a_confirmer` | non : à transmettre au client |

## Contrôle visuel (aperçus PNG)

Ouvrir chaque aperçu avec l'outil Read et vérifier :

1. **Photo** : visage net et centré, cadrage comme la V4, pas de déformation.
2. **En-tête** : nom sur une ligne, titre lisible, coordonnées alignées, pas de « · » en début de ligne.
3. **Colonnes** : bas des colonnes équilibré, encadré latéral sans grand vide.
4. **Sections** : titres bien séparés, espacements réguliers, rien de collé.
5. **Lignes** : pas de mot seul en fin de paragraphe, pas de date qui passe à la ligne.
6. **Couleurs** : la couleur reste une touche (titre, filet, entreprises, intitulés), jamais un aplat.
7. **Deux pages** : aucun bloc coupé, pas de titre seul en bas de page 1.
8. **Comparer les trois couleurs** : mise en page identique.

## Corriger

Toute correction passe par `cv.json`, puis on régénère et on recontrôle. On ne retouche jamais un
PDF à la main.

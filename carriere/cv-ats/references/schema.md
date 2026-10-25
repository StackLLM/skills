# Format de `cv.json`

Tous les champs sont facultatifs sauf `identite.nom` et `identite.email`, plus au moins une
expérience ou une formation. Un champ vide ou absent fait disparaître la section correspondante.

## Réglages

| Champ | Valeurs | Défaut |
|---|---|---|
| `langue` | `fr`, `en` | `fr` |
| `marche` | pays visé : `maroc`, `france`, `uk`, `usa`, `canada`… | `maroc` |
| `domaine` | `auto`, `tech`, `ingenierie`, `finance`, `marketing`, `commercial`, `management`, `design`, `sante`, `juridique`, `autre` | `auto` |
| `niveau` | `auto`, `junior`, `confirme`, `senior` | `auto` |
| `photo` | chemin de la photo, relatif au JSON | aucune |
| `photo_forcee` | `true` pour garder la photo sur un marché qui ne l'utilise pas | `false` |
| `titre_competences` | titre de la section compétences, s'il faut remplacer celui du domaine | selon domaine |

## Contenu

```json
{
  "identite": {
    "nom": "Prénom Nom",
    "titre": "Poste visé, précis",
    "telephone": "+212 6 00 00 00 00",
    "email": "prenom.nom@example.com",
    "liens": [
      {"type": "linkedin", "url": "https://linkedin.com/in/…"},
      {"type": "github", "url": "https://github.com/…"},
      {"type": "portfolio", "url": "https://…", "libelle": "Portfolio"}
    ],
    "ville": "Casablanca",
    "age": 27,
    "autres": ["Permis B", "Disponible immédiatement"]
  },
  "profil": "2 à 3 phrases.",
  "experiences": [
    {
      "poste": "Intitulé du poste",
      "entreprise": "Entreprise",
      "lieu": "Ville",
      "debut": "03/2022",
      "fin": "Présent",
      "points": ["Verbe d'action + mission + résultat chiffré si connu."]
    }
  ],
  "realisations": ["Résultat marquant, présent dans la source."],
  "projets": [
    {"nom": "Nom", "description": "ce que c'est, en une phrase.", "technologies": ["…"], "lien": "https://…"}
  ],
  "formation": [
    {"diplome": "Diplôme", "etablissement": "École", "lieu": "Ville", "debut": "2018", "fin": "2021",
     "mention": "Mention Bien", "detail": "Spécialité ou sujet de mémoire"}
  ],
  "notes_formation": ["Sigle : signification en toutes lettres."],
  "competences": [
    {"groupe": "Thème", "elements": ["outil", "méthode"]}
  ],
  "certifications": ["Nom simple", {"nom": "Nom", "organisme": "Organisme", "annee": "2024"}],
  "langues": [{"langue": "Français", "niveau": "courant"}],
  "soft_skills": ["rigueur", "travail en équipe"],
  "interets": ["course à pied"],
  "a_confirmer": ["Question à poser au client, avec ce que dit la source."]
}
```

## Règles de remplissage

- **Dates** : `MM/AAAA` ou `AAAA`. `fin` vide ou « Présent » / « Present » = poste en cours.
  Le script signale les fins avant les débuts et les débuts dans le futur.
- **Ordre** : expériences et formations de la plus récente à la plus ancienne.
- **Stages** : « Stage » ou « internship » dans l'intitulé. Ils ne comptent pas dans les années
  d'expérience, et un profil junior affiche « Expériences et stages ».
- **Liens** : affichés par leur libellé (LinkedIn, GitHub…) et cliquables. Le téléphone ouvre l'appel,
  l'email ouvre un message.
- **Chiffres** : en finance, ingénierie, marketing, commercial et management, les résultats chiffrés
  (%, montants, ×N) passent en gras automatiquement. Ne jamais en ajouter un absent de la source.
- **`a_confirmer`** : tout ce qui est déduit, ambigu ou manquant. Ces points apparaissent dans le
  rapport, jamais dans le CV.

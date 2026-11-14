# Format du fichier carte.json

Exemple complet : `scripts/exemple-projet.json`.

Le script refuse tout champ qui n'est pas dans ces tableaux.

## La carte

| Champ | Obligatoire | Limite | Contenu |
|---|---|---|---|
| `type` | oui | | `projet` ou `orga` |
| `nom` | oui | | nom du projet ou de l'orga |
| `sous_titre` | non | | ce que c'est, en quelques mots |
| `date` | oui | | date de l'état, `AAAA-MM-JJ` |
| `verdict` | oui | 150 | la situation réelle, en une phrase |
| `prochaine_action` | oui | 110 | la seule chose à faire ensuite |
| `volets` | si `projet` | | la liste des volets |
| `projets` | si `orga` | | la liste des projets |
| `depots_total` | non, orga | | nombre de dépôts de l'orga, affiché à côté du nombre de projets |
| `hors_carte` | non | | ce qui n'est pas sur la map : « 12 dépôts dormants, 3 forks ». Affiché dans le bandeau |

## Un volet ou un projet

| Champ | Obligatoire | Limite | Contenu |
|---|---|---|---|
| `nom` | oui | 34 | |
| `sous_titre` | non | 48 | à quoi sert ce volet, en mots simples. Jamais un chemin de fichier ni une liste de technos. Vide si rien d'utile à dire |
| `resume` | oui | 170 | ce qui existe aujourd'hui, en une ou deux phrases |
| `derniere_activite` | oui sur une orga | | voir ci-dessous |
| `etiquettes` | non | 20 | texte d'une case de la matrice : `{"Construction": "lots 1–7"}` |
| `lots` | oui | | la liste des lots, 14 au plus conseillé |
| `phase_estimee` | si aucun lot | | une des cinq phases |
| `source_phase` | si aucun lot | | d'où vient cette estimation |

Sans `etiquettes`, la case affiche le compte de lots.

`derniere_activite` est la date du dernier commit, toutes branches poussées
comprises. Pour un volet : le dernier commit de ses dossiers. Un volet sans dossier
propre n'a pas ce champ. Un commit qui n'existe qu'en local se signale dans `resume`.

## Un lot

| Champ | Obligatoire | Limite | Contenu |
|---|---|---|---|
| `titre` | oui | 44 | |
| `detail` | non | 46 | précision courte |
| `phase` | oui | | `Cadrage`, `Construction`, `Pré-production`, `Bêta`, `Lancement` |
| `statut` | oui | | voir ci-dessous |
| `source` | oui, sauf `a_confirmer` | | fichier, commit, ticket, ou la demande de l'utilisateur avec sa date |
| `cause` | non | | nom court d'une cause partagée par plusieurs lots : `hebergeur` |

Le `titre` s'affiche nu dans la carte du volet : sans le statut, sans le
`detail`. Il doit se lire seul. Le `detail` et le statut en mots restent sur
la map par lot. La source s'affiche au survol dans les deux HTML.

## Les statuts

| Statut | Quand | Couleur |
|---|---|---|
| `fait` | livré, et prouvé | vert |
| `en_cours` | du travail réel a commencé | bleu |
| `a_faire` | à faire maintenant, rien n'empêche de commencer | bleu |
| `a_fournir` | on attend un élément : photo, accès, données | bleu |
| `a_trancher` | on attend une décision | bleu |
| `bloquant` | empêche de passer à la phase suivante | rouge |
| `a_venir` | prévu plus tard | gris |
| `a_confirmer` | aucune preuve trouvée | pointillé |

## Ce que le script calcule seul

Ces valeurs ne s'écrivent jamais dans le fichier.

| Valeur | Règle |
|---|---|
| Case de la matrice | tout fait : vert. Un bloquant : rouge. Tout à venir : gris. Seulement à confirmer ou à venir : pointillé. Sinon : bleu. Aucun lot : tiret |
| Phase d'un volet ou d'un projet d'orga | la dernière phase avec un lot `fait` ou `en_cours`. Un lot `a_faire`, `a_fournir`, `a_trancher` ou `bloquant` y fait entrer seulement si la phase d'avant est finie. `a_confirmer` et `a_venir` ne font jamais avancer |
| Phase d'un projet | la médiane basse de ses volets |
| Ligne d'avancement | lots faits divisés par le total de lots |
| Verdict d'une carte | le premier qui s'applique : Terminé, Bloqué, À l'arrêt, À trancher, À confirmer, Pas commencé, En bonne voie |
| À l'arrêt | plus de 45 jours sans commit, avec des lots restants. Le nombre de jours s'affiche aussi sur une carte Bloqué ou À trancher |
| Verdict du bandeau | le plus urgent, avec son compte : « Bloqué : 1 volet sur 7 » |
| Ordre des projets d'orga | ce qui demande une action d'abord |
| Contenu d'une carte de volet | les lots en titres, derrière une case à cocher, rangés en deux paquets : « Fait », puis « Reste ». Sur une orga, seul « Reste » est listé, coupé à 7 titres suivis de « + N autres » |
| Bloquants et décisions du compteur | un même `cause` compte une fois |

Deux règles bloquent la génération sur une orga :

- `derniere_activite` manque sur un projet.
- Tous les lots d'un projet sont faits, mais aucun n'est en Lancement.

Les 90 jours de l'inventaire et les 45 jours de la map sont deux choses :
90 jours décide quels dépôts lire, 45 jours décide du verdict « À l'arrêt ».

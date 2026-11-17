# Domaines, niveaux et plans de CV

## Détection

`python3 scripts/cv.py detecter source` compte des mots-clés par domaine. Le poste visé compte
triple. En dessous de 3 signaux, le domaine retenu est `autre`. Le résultat est un **second avis** :
le modèle tranche, surtout sur les profils mixtes (ex. data analyst en banque → `tech`, contrôleur de
gestion industriel → `finance`).

Le niveau vient des années d'expérience **hors stages**, les périodes qui se chevauchent étant
fusionnées : moins de 2 ans = `junior`, moins de 8 ans = `confirme`, sinon `senior`.

## Plans de sections

Colonne principale à gauche (lue en premier par les ATS), colonne latérale à droite dans un encadré.
Une section vide disparaît. Une section présente dans les données mais absente du plan est ajoutée en
fin de colonne : rien n'est perdu.

| Domaine | Colonne principale | Colonne latérale | Titre compétences | Chiffres en gras |
|---|---|---|---|---|
| tech | profil, expériences, projets, certifications | formation, compétences, langues, qualités | Compétences techniques | non |
| ingenierie | profil, expériences, projets, certifications | formation, compétences, langues, qualités | Expertise technique | oui |
| finance | profil, réalisations, expériences, certifications | formation, compétences, langues, qualités | Compétences clés | oui |
| marketing | profil, réalisations, expériences, projets | compétences, formation, certifications, langues, qualités | Compétences | oui |
| commercial | profil, réalisations, expériences | compétences, formation, certifications, langues, qualités | Compétences commerciales | oui |
| management | profil, réalisations, expériences | compétences, formation, certifications, langues, qualités | Compétences de direction | oui |
| design | profil, expériences, projets | compétences, formation, certifications, langues, qualités | Expertise et outils | non |
| sante | profil, expériences, formation | compétences, certifications, langues, qualités | Compétences cliniques | non |
| juridique | profil, expériences, formation | compétences, certifications, langues, qualités | Domaines d'expertise | non |
| autre | profil, expériences, réalisations, projets | formation, compétences, certifications, langues, qualités | Compétences | non |

**Profil junior** : la formation passe en colonne principale, juste après le profil, et les projets
remontent juste après les expériences.

**Sections mobiles** : certifications, langues et qualités peuvent changer de colonne pendant
l'ajustement si cela évite un débordement.

## Photo selon le marché

| Marché | Photo |
|---|---|
| Maroc, France, Belgique, Suisse, Allemagne, Espagne, Moyen-Orient, Afrique | oui si fournie |
| USA, UK, Canada, Irlande, Australie | non (risque de discrimination, refus fréquent) ; `photo_forcee` pour l'imposer |

## Conseils de rédaction par domaine

- **Tech** : stack précise et versions utiles ; projets avec technologies et lien GitHub ; résultats
  techniques (performance, utilisateurs, disponibilité).
- **Ingénierie** : normes et outils (ISO, AMDEC, CAO) ; indicateurs industriels (TRS, disponibilité,
  coûts, sécurité).
- **Finance** : périmètre (CA, budget, nombre d'entités) ; délais de clôture ; économies ; normes
  (IFRS) ; certifications (CFA, ACCA, DNEC).
- **Marketing / commercial** : résultats d'abord (CA, croissance, coût d'acquisition, conversion) ;
  budgets gérés ; outils (CRM, Ads, analytics).
- **Management** : taille des équipes et des budgets ; transformations menées ; résultats d'ensemble.
- **Design** : lien portfolio dans `identite.liens` ; outils ; types de projets et clients.
- **Santé / juridique** : diplômes, inscriptions et habilitations en évidence ; services ou matières.

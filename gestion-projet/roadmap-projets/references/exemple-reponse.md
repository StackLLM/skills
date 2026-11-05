# Exemple de réponse — mode organisation

La réponse réelle que l'utilisateur a choisie comme modèle (StackLLM, 30 octobre
2026). Imiter l'ordre, la longueur et le ton. Le widget se place à l'endroit
marqué ; son code est `gabarit-orga.html`.

---

MySalary et LucidNews sont les plus avancés : ils sont construits et préparent
leur mise en production. Les Skills attendent une décision sur la licence et les
prix. TeachMe en est au cadrage. L'e-commerce n'a pas encore de repository dans
StackLLM.

J'ai construit ce roadmap à partir des repositories et de leurs documents de
suivi : `docs/lots.md` et `docs/prod.md` pour MySalary, `docs/roadmap.md` pour
LucidNews, `Plan.md` pour TeachMe.

**[widget : roadmap]**

## Ce qui avance

- **MySalary** : c'est le projet le plus actif. Son dernier commit date d'hier
  (correction du cumul de fin de mois). Toutes les fonctions sont faites. Ce qui
  reste, c'est la mise en ligne : PostgreSQL, Netlify, puis une bêta fermée.
- **LucidNews** : il est techniquement prêt, mais aucun commit depuis le
  18 octobre. Il manque l'e-mail en production, les sauvegardes et le suivi des
  erreurs (lots 33 à 35).

## Ce qui attend une action de votre part

- **MySalary** : 6 lots sont livrés mais pas validés (23 à 27, et 35). Les
  valider ferait avancer le projet tout de suite.
- **LucidNews** : le lot 12 bis demande d'annoter 100 news à la main. Sans ça,
  pas de preuve que la veille est fiable.
- **TeachMe** : avant de coder, il faut faire relire le plan et réunir un comité
  pédagogique (enseignants, inspecteur).
- **Skills** : avant toute vente, il faut vérifier que vous en êtes propriétaire
  et faire valider la licence.

## Décalages à corriger

- Le README de LucidNews indique encore « Phase 1 — fondations ». Sa feuille de
  route montre pourtant 33 lots terminés, à la date du 18 octobre.
- Le profil public StackLLM présente l'e-commerce comme « In development ». Or
  il n'existe encore aucun repository : seulement des études dans
  `PERSO/ECOMMERCE`.

---

# Adapter au mode projet

Même ordre, mêmes sections. Le sujet devient les **volets** au lieu des projets.

- Verdict : la phase du projet, le volet le plus avancé, celui qui bloque.
  « Le projet X est en construction, 8 lots sur 16. La base est finie, l'API est
  livrée mais pas validée, le front en est à la page Commandes. Le déploiement
  est bloqué par le choix de l'hébergeur. »
- Sources : « J'ai construit ce roadmap à partir de `Plan.md`, `docs/lots.md`
  et des 30 derniers jours de commits. »
- Widget : `gabarit-projet.html`.
- `## Ce qui avance` : une puce par volet actif, avec sa preuve.
- `## Ce qui attend une action de votre part` : lots à valider, décisions
  ouvertes, accès à fournir.
- `## Décalages à corriger` : plan en retard sur le code, lot « fait » sans
  trace, README périmé.

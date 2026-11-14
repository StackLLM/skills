# 0001 — Pile technique de {{NOM}}

- **Date** : {{DATE}}
- **État** : acceptée

## Contexte

{{NOM}} est un projet de type **{{TYPE}}**. <!-- Résumer ici le besoin tiré du plan : utilisateurs, données, intégrations. -->

## Décision

- `frontend/` : Vite + React + TypeScript strict, testé avec Vitest.
- `backend/` : **{{PILE_LIBELLE}}**.
- Livraison : image Docker, branches `feature/…` → `dev` → `main`, livraison vers `main` après une CI verte.
- Hébergement : pas encore choisi. Le socle respecte le contrat de `references/hebergement.md` (skill adviser-dev).

## Conséquences

<!-- Ce que ce choix facilite, ce qu'il coûte, ce qui obligerait à le revoir. -->

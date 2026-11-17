# D'où vient cette skill

`security-auditor` est une skill maison. Le 10 novembre 2026, elle a été
fusionnée avec la skill **`security-audit` de Cloudflare**, publiée sous
licence MIT :

<https://github.com/cloudflare/security-audit-skill>

> MIT License — Copyright (c) 2025-2026 Cloudflare, Inc.

## Ce qui vient de Cloudflare

| Ce qui a été repris | Où c'est |
|---|---|
| La règle de la frontière franchie et du résultat concret | `SKILL.md`, règle 1 |
| La séparation entre criticité et certitude | `SKILL.md`, règle 3 |
| Les ancrages de criticité, et le départage ÉLEVÉ / MOYEN | `SKILL.md`, temps 5 |
| Le plus petit correctif efficace, au dernier point de décision | `SKILL.md`, temps 6 |
| Les deux modes : conseil et audit complet | `SKILL.md`, en tête |
| Le registre de couverture, les profils, la relecture indépendante | `references/couverture.md` |
| Les règles d'exécution : jamais de test en ligne ou partagé | `references/execution-sure.md` |
| Les classes d'attaque, et les domaines spécialisés | `references/classes-attaque.md` |
| Plusieurs pièges connus | `SKILL.md`, dernier tableau |

Le fichier `references/classes-attaque.md` condense en français les onze
fichiers de domaine de la skill d'origine : `ATTACK-CLASSES`,
`WEB-PROTOCOL-AND-AUTH`, `CLIENT-SIDE`, `CLOUD-AND-DEPLOYMENT`,
`SUPPLY-CHAIN-AND-RELEASE`, `AI-AND-LLM`, `DATA-ISOLATION-AND-LIFECYCLE`,
`RESOURCE-EXHAUSTION-AND-AVAILABILITY`, `PROTOCOLS-RPC-AND-MESSAGING`,
`MEMORY-SAFETY-AND-BINARY`, `DESKTOP-MOBILE-AND-LOCAL-IPC`.

## Ce qui reste maison

| Ce qui n'a pas changé | Pourquoi |
|---|---|
| Le français simple, et la table « à ne pas écrire / à écrire » | Le lecteur n'est pas expert en sécurité |
| Les quatre niveaux de confiance | Plus lisibles que `confirmed` / `needs_validation` |
| Les profils d'attaquant | On part de qui attaque, pas d'une liste de failles |
| Le chemin d'attaque en escalier | C'est ce qui fait comprendre le problème |
| Le masquage systématique des secrets | Règle maison, jamais une valeur entière |
| Les étapes de correction et la preuve de réparation | Signaler sans guider ne sert à rien |
| Le rapport HTML premium | Le livrable de l'équipe |
| Les quatre groupes de priorité | Ils disent quand corriger, pas seulement quoi |

## Ce qui a été écarté

L'orchestration multi-agents de Cloudflare — identifiants d'agents, isolation
d'écriture, promotion de fichiers depuis un bac à sable, budget d'invocations,
validateurs `.cjs` — n'a pas été reprise. Elle vise une plateforme d'audit
industrielle. Ici, la relecture indépendante et le registre de couverture
donnent le même gain sans la machinerie.

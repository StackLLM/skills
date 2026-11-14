# Ce qu'on a le droit de lancer

Un audit **observe**. Il ne casse rien, il ne touche à rien en ligne, il ne
consomme pas de quota payant.

> Adapté de la skill `security-audit` de Cloudflare (MIT). Voir `ORIGINES.md`.

---

## La règle

**La lecture du code est toujours autorisée. L'exécution ne l'est presque
jamais.**

| Action | Autorisée ? |
|---|---|
| Lire le code, la configuration, l'historique Git | Oui |
| Lancer les scripts de sonde de cette skill | Oui |
| Lancer un test unitaire déjà présent, en local, hors réseau | Oui, sous les conditions ci-dessous |
| Écrire un petit harnais qui appelle **une** fonction | Oui, sous les conditions ci-dessous |
| Lancer l'application complète du projet | Non, sauf demande explicite |
| Appeler une adresse en ligne du projet | **Non** |
| Tester un service partagé, une recette, une production | **Non** |
| Tester la charge ou la disponibilité | **Non** |
| Se connecter avec un vrai compte | **Non** |
| Installer une dépendance pour faire tourner un test | **Non** |
| Dépenser un quota payant | **Non** |

Un fichier `.env` ne s'ouvre jamais, même pour vérifier qu'une clé est vide.

---

## Les conditions, quand on exécute quelque chose

Les cinq doivent tenir en même temps. S'il en manque une, **on n'exécute pas** :
le point passe en « Non vérifiable », avec le contrôle manquant écrit noir sur
blanc, et le moyen sûr de le trancher.

1. **Pas de réseau extérieur.** Seulement la boucle locale, et seulement si le
   test a besoin d'un client et d'un serveur.
2. **Environnement vide**, rempli uniquement avec ce qu'on a choisi, avec des
   valeurs factices. Jamais l'environnement de la machine.
3. **Source en lecture seule.** Si la construction doit écrire, on travaille sur
   une copie jetable.
4. **Limites explicites** de processeur, de mémoire, de processus, de taille de
   fichier et de durée.
5. **Données factices.** Faux comptes, faux secrets, faux fichiers. Jamais de
   vraies données, jamais une vraie identité.

---

## S'arrêter au premier effet

On s'arrête dès que le défaut est établi :

- une valeur de retour fausse,
- un enregistrement d'un faux client lu alors qu'il ne devrait pas l'être,
- une différence entre la règle écrite et le comportement réel.

**On ne va pas plus loin.** Pas de chaîne d'exploitation, pas de persistance,
pas de contournement de trace. L'audit prouve qu'une porte s'ouvre ; il
n'entre pas.

---

## Quand le fait décisif est hors du code

C'est fréquent : un réglage de proxy, une variable de production, une règle du
pare-feu, un en-tête ajouté par l'hébergeur.

Dans ce cas, on **n'invente rien**, ni dans un sens ni dans l'autre. On écrit :

```text
Confiance : Non vérifiable
Ce qui manque : la valeur de ALLOWED_ORIGINS en production.
Comment le trancher sans risque : la lire dans le tableau de bord de
l'hébergeur, ou lancer `curl -I https://…` et regarder l'en-tête renvoyé.
```

Un contrôle absent du dépôt n'est **pas** un contrôle absent en production.

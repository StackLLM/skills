# Les secrets

Un secret trouvé dans un dépôt est **déjà compromis**. Le retirer du code ne
le décompromet pas : il est resté dans l'historique, il a pu être cloné, copié
ou indexé.

La seule réponse qui compte est la **révocation**.

---

## 1. Ce qu'on cherche

| Famille | Forme reconnaissable |
|---|---|
| Fournisseurs d'IA | `sk-…`, `sk-or-v1-…`, `sk-ant-…` |
| Stripe | `sk_live_…`, `rk_live_…` |
| GitHub | `ghp_…`, `gho_…`, `ghs_…`, `ghr_…` |
| AWS | `AKIA…`, `ASIA…`, plus la clé secrète associée |
| Google, Firebase | `AIza…`, fichier de compte de service JSON |
| Slack | `xoxb-…`, `xoxp-…` |
| Jetons JWT | `eyJ….eyJ….…` |
| Clés privées | bloc `-----BEGIN … PRIVATE KEY-----` |
| Chaînes de connexion | `postgres://user:motdepasse@…`, `mongodb+srv://…` |
| Secrets en dur | `password=`, `secret=`, `api_key=`, `token=` suivis d'une vraie valeur |
| Chaînes à forte entropie | longues, aléatoires, posées dans le code |

Et les endroits, pas seulement les motifs :

- le code envoyé au **navigateur** — le pire cas, lisible par tous ;
- les fichiers `.env` commités ;
- l'**historique Git**, même si le fichier a été supprimé depuis ;
- les fichiers de workflow de CI ;
- les journaux et les messages d'erreur ;
- les fichiers de configuration d'exemple, quand ils ont été remplis ;
- les captures d'écran et les fichiers de documentation.

```bash
python ../scripts/chercher_secrets.py <projet> --historique -o secrets.md
```

---

## 2. Vrai secret ou exemple ?

La moitié des alertes brutes sont des exemples. Trier avant d'alarmer.

| Probablement un exemple | Probablement un vrai secret |
|---|---|
| dans `.env.example`, `.env.sample` | dans `.env`, dans le code, dans un workflow |
| `your-api-key-here`, `xxx`, `changeme`, `TODO` | une valeur qui a la bonne forme et la bonne longueur |
| `sk-xxxxxxxx` | `sk-` suivi de caractères aléatoires |
| dans un bloc de documentation | à côté d'un appel réseau réel |
| valeur répétée à l'identique partout | valeur unique |

**Dans le doute, on alerte.** Le coût d'une révocation inutile est d'une heure.
Le coût d'une clé laissée publique n'a pas de plafond.

---

## 3. Le masquage — règle absolue

Un secret ne s'affiche **jamais** en entier. Ni dans la réponse, ni dans le
rapport, ni dans un message, ni dans un exemple.

```text
OPENROUTER_API_KEY=sk-o••••••••98
```

On garde les **quatre premiers** caractères — ils disent quel fournisseur — et
les **deux derniers** — ils permettent de reconnaître la bonne clé dans le
tableau de bord du fournisseur. Rien d'autre.

Le script de rapport masque automatiquement. C'est un **filet**, pas une
autorisation de coller une valeur entière.

---

## 4. La procédure, dans l'ordre

Une clé exposée est toujours « à corriger immédiatement ». Les étapes ne se
réordonnent pas : la révocation vient **avant** le nettoyage du code.

```text
 1. Identifier la clé : quel fournisseur, quel compte, quels droits.
 2. Révoquer la clé actuelle, sur le tableau de bord du fournisseur.
    C'est la seule étape qui arrête vraiment le risque.
 3. Créer une nouvelle clé, avec les droits minimum nécessaires.
 4. La ranger dans les variables d'environnement du serveur,
    ou dans le gestionnaire de secrets de l'hébergeur.
 5. Retirer la valeur du code, et la lire depuis l'environnement.
 6. Si la clé était côté navigateur : créer une adresse sur le backend
    qui appelle le service à la place du frontend.
 7. Vérifier que le fichier est bien dans .gitignore.
 8. Vérifier l'historique Git. S'il contient la clé, la considérer
    comme publique pour toujours — c'est pourquoi l'étape 2 existe.
 9. Redéployer.
10. Vérifier que l'ancienne clé renvoie une erreur d'authentification.
11. Regarder la consommation et les journaux d'accès du compte
    sur les jours qui suivent.
```

### Faut-il réécrire l'historique Git ?

| Situation | Réponse |
|---|---|
| Dépôt public, ou cloné par d'autres | **Non, ça ne sert à rien.** La clé est dehors. Révoquer suffit. |
| Dépôt privé, peu de clones, secret très sensible | Possible, mais ça casse les copies de tout le monde. |
| Dans tous les cas | Révoquer d'abord. La réécriture est un nettoyage, pas une protection. |

Ne jamais proposer une réécriture d'historique comme **la** solution. C'est
une opération risquée qui donne un faux sentiment de sécurité.

---

## 5. Les bonnes pratiques à recommander

| Pratique | Pourquoi |
|---|---|
| Aucun secret dans le code, jamais | le code se partage, se clone, s'indexe |
| Un `.env.example` avec des valeurs factices | documenter sans exposer |
| `.env`, `*.pem`, `credentials.json` dans `.gitignore` | dès le premier commit |
| Les secrets de CI dans le coffre du fournisseur | pas dans les fichiers de workflow |
| Une clé par environnement | une fuite en recette ne touche pas la production |
| Droits minimum sur chaque clé | limiter ce qu'une fuite permet |
| Rotation périodique | même sans incident |
| Aucun secret côté navigateur | tout ce qui est téléchargé est lisible |

**La règle qui résume tout :** si le navigateur peut le télécharger, ce n'est
pas un secret. Une clé qui doit rester privée vit côté serveur, point.

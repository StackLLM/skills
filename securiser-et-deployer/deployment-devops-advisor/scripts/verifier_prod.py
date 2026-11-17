#!/usr/bin/env python3
"""
verifier_prod.py — les motifs qui cassent au déploiement.

    python verifier_prod.py <projet> -o deploiement.md

Le script cherche ce qui fait tomber une application qui tourne bien en local :
adresses locales en dur, ports figés, chemins Windows, variables utilisées mais
déclarées nulle part, écritures sur le disque du serveur, dépendances non
verrouillées, version de langage non fixée, conteneur en root, base exposée,
secrets dans les fichiers de CI, absence de page de santé.

**Des pistes, pas des verdicts.** Un `localhost` dans un fichier de test ne
pose aucun problème. Chaque ligne se confirme en ouvrant le fichier.

Aucune dépendance : bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

IGNORES = {"node_modules", ".git", "dist", "build", "out", ".next", ".nuxt",
           ".venv", "venv", "__pycache__", "vendor", "target", "coverage",
           ".turbo", ".cache", "site-packages", ".pytest_cache", "obj"}
CODE = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rb", ".php", ".java",
        ".env", ".yml", ".yaml", ".toml", ".json", ".ini", ".conf", ".ps1",
        ".sh", ".bat", ".cmd", ".cs"}
TAILLE_MAX = 600_000

LOCALE = re.compile(r"(?i)(https?://(?:localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])(?::\d+)?)")
PORT_FIGE = re.compile(r"""(?i)(?:\.listen\(\s*(\d{4,5})|port\s*[=:]\s*(\d{4,5}))""")
PORT_ENV = re.compile(r"""(?i)(process\.env\.PORT|os\.getenv\(\s*["']PORT|environ\[?\s*["']PORT)""")
ECOUTE_LOCALE = re.compile(r"""(?i)(host\s*[=:]\s*["']127\.0\.0\.1|["']127\.0\.0\.1["']\s*,\s*\d|--host[= ]127\.0\.0\.1)""")
CHEMIN_WINDOWS = re.compile(r"""["'][A-Za-z]:[\\/]{1,2}[^"'\n]{3,}["']|["'][^"'\n]*\\\\[^"'\n]*["']""")
ECRITURE = re.compile(r"""(?i)(open\s*\([^)]*["']w|writeFileSync|createWriteStream|
    \.save\(|shutil\.copy|os\.makedirs|mkdirSync)""", re.VERBOSE)
CORS_OUVERT = re.compile(r"""(?i)(allow_origins\s*=\s*\[\s*["']\*|
    Access-Control-Allow-Origin["']?\s*[:,]\s*["']\*|origin\s*:\s*["']\*)""", re.VERBOSE)
SANTE = re.compile(r"""(?i)["'](/(?:health|healthz|sante|ping|status|ready|live)[a-z/_-]*)["']""")
ENV_UTILISEE = re.compile(r"""(?:os\.environ(?:\.get)?\[?\s*["']([A-Z0-9_]{3,})["']|"""
                          r"""os\.getenv\(\s*["']([A-Z0-9_]{3,})["']|"""
                          r"""process\.env\.([A-Z0-9_]{3,})|"""
                          r"""import\.meta\.env\.([A-Z0-9_]{3,}))""")
REPLI_DANGEREUX = re.compile(
    r"""(?i)(?:getenv|environ\.get)\(\s*["'][A-Z0-9_]+["']\s*,\s*["']"""
    r"""([^"']*(?:localhost|127\.0\.0\.1|changeme|secret|sqlite|admin|password)[^"']*)["']""")
PORTS_BASE = {"5432": "PostgreSQL", "3306": "MySQL", "27017": "MongoDB",
              "6379": "Redis", "9200": "Elasticsearch", "1433": "SQL Server"}


def est_un_test(rel: str) -> bool:
    bas = rel.lower()
    return ("test" in bas or "spec" in bas or "__mocks__" in bas
            or ".example" in bas or ".sample" in bas or "/docs/" in bas)


def parcourir(racine: Path, extensions: set[str] | None = None):
    for chemin in racine.rglob("*"):
        if not chemin.is_file() or any(p in IGNORES for p in chemin.parts):
            continue
        if extensions is not None and chemin.suffix.lower() not in extensions:
            continue
        try:
            if chemin.stat().st_size > TAILLE_MAX:
                continue
        except OSError:
            continue
        yield chemin


def lire(chemin: Path) -> str:
    try:
        return chemin.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def sonder_code(racine: Path) -> dict:
    r = {k: [] for k in ("locale", "port", "ecoute", "windows", "ecriture",
                         "cors", "repli")}
    variables: dict[str, str] = {}
    sante, port_env = [], False

    for chemin in parcourir(racine, CODE):
        rel = chemin.relative_to(racine).as_posix()
        texte = lire(chemin)
        if PORT_ENV.search(texte):
            port_env = True
        for i, ligne in enumerate(texte.splitlines(), 1):
            if len(ligne) > 3000:
                ligne = ligne[:3000]
            ou, extrait = f"{rel}:{i}", ligne.strip()[:120]
            test = est_un_test(rel)

            for m in LOCALE.finditer(ligne):
                r["locale"].append({"ou": ou, "extrait": m.group(1), "test": test})
            m = PORT_FIGE.search(ligne)
            if m and not PORT_ENV.search(ligne):
                r["port"].append({"ou": ou, "extrait": extrait,
                                  "port": m.group(1) or m.group(2), "test": test})
            if ECOUTE_LOCALE.search(ligne):
                r["ecoute"].append({"ou": ou, "extrait": extrait, "test": test})
            if CHEMIN_WINDOWS.search(ligne):
                r["windows"].append({"ou": ou, "extrait": extrait, "test": test})
            if ECRITURE.search(ligne) and not test:
                r["ecriture"].append({"ou": ou, "extrait": extrait, "test": False})
            if CORS_OUVERT.search(ligne):
                r["cors"].append({"ou": ou, "extrait": extrait, "test": test})
            for m in REPLI_DANGEREUX.finditer(ligne):
                r["repli"].append({"ou": ou, "extrait": extrait,
                                   "valeur": m.group(1), "test": test})
            for m in ENV_UTILISEE.finditer(ligne):
                variables.setdefault(next(g for g in m.groups() if g), ou)
            for m in SANTE.finditer(ligne):
                sante.append({"adresse": m.group(1), "ou": ou})

    r["variables"] = variables
    r["sante"] = sante
    r["port_env"] = port_env
    return r


def variables_declarees(racine: Path) -> set[str]:
    noms = set()
    for chemin in parcourir(racine):
        nom = chemin.name.lower()
        if not (nom.startswith(".env") or nom.startswith("docker-compose")
                or nom.startswith("compose.") or nom in ("app.yaml", "fly.toml",
                                                         "render.yaml")):
            continue
        for ligne in lire(chemin).splitlines():
            m = re.match(r"\s*(?:-\s*)?([A-Z][A-Z0-9_]{2,})\s*[=:]", ligne)
            if m:
                noms.add(m.group(1))
    return noms


def sonder_livraison(racine: Path) -> list[dict]:
    """Verrouillage, versions, conteneur, base exposée, secrets de CI."""
    faits = []

    def ajouter(gravite: str, quoi: str, detail: str, ou: str = "") -> None:
        faits.append({"gravite": gravite, "quoi": quoi, "detail": detail, "ou": ou})

    # --- Verrouillage des dépendances ---
    if (racine / "package.json").exists():
        verrous = [f for f in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock",
                               "bun.lockb") if (racine / f).exists()]
        if verrous:
            ajouter("ok", "Dépendances verrouillées", ", ".join(verrous))
        else:
            ajouter("alerte", "Aucun fichier de verrouillage Node",
                    "Le build peut passer aujourd'hui et casser demain sans "
                    "changement de code. Commiter le fichier de verrouillage, "
                    "et installer avec `npm ci`.", "package.json")
        try:
            pkg = json.loads(lire(racine / "package.json"))
            if pkg.get("engines", {}).get("node"):
                ajouter("ok", "Version de Node fixée", pkg["engines"]["node"])
            elif not (racine / ".nvmrc").exists():
                ajouter("alerte", "Version de Node non fixée",
                        "Le serveur peut installer une autre version que le "
                        "poste. Ajouter `engines.node` ou un fichier `.nvmrc`.",
                        "package.json")
        except json.JSONDecodeError:
            ajouter("alerte", "package.json illisible", "À vérifier.", "package.json")

    py = [f for f in ("requirements.txt", "pyproject.toml", "Pipfile") if (racine / f).exists()]
    if py:
        fige = any("==" in lire(racine / f) for f in py)
        verrou = any((racine / f).exists() for f in ("poetry.lock", "Pipfile.lock",
                                                    "requirements.lock", "uv.lock"))
        if fige or verrou:
            ajouter("ok", "Dépendances Python figées", ", ".join(py))
        else:
            ajouter("alerte", "Dépendances Python non figées",
                    "Sans version exacte, l'installation change d'un jour à "
                    "l'autre. Figer avec `==`, ou commiter un fichier de "
                    "verrouillage.", py[0])
        if not (racine / ".python-version").exists() and not any(
                "python_requires" in lire(racine / f) or "requires-python" in lire(racine / f)
                for f in py):
            ajouter("alerte", "Version de Python non fixée",
                    "Ajouter `requires-python`, ou un fichier "
                    "`.python-version`.", py[0])

    # --- Conteneur ---
    for chemin in parcourir(racine):
        if chemin.name != "Dockerfile":
            continue
        rel = chemin.relative_to(racine).as_posix()
        texte = lire(chemin)
        if re.search(r"(?im)^\s*FROM\s+\S+:latest", texte) or \
           re.search(r"(?im)^\s*FROM\s+[^\s:]+\s*$", texte):
            ajouter("alerte", "Image de base non figée",
                    "`latest` change sans prévenir : le build n'est pas "
                    "reproductible. Mettre une version précise.", rel)
        if not re.search(r"(?im)^\s*USER\s+", texte):
            ajouter("alerte", "Le conteneur tourne en root",
                    "Une faille dans l'application donne alors les pleins "
                    "droits dans le conteneur. Créer un utilisateur et ajouter "
                    "une instruction `USER`.", rel)
        if not re.search(r"(?im)^\s*HEALTHCHECK", texte):
            ajouter("info", "Pas de vérification de santé dans l'image",
                    "Sans elle, l'orchestrateur ne sait pas si l'application "
                    "est vivante.", rel)

    # --- Composition : base exposée ---
    for chemin in parcourir(racine):
        if not (chemin.name.startswith("docker-compose") or
                chemin.name.startswith("compose.")):
            continue
        rel = chemin.relative_to(racine).as_posix()
        for i, ligne in enumerate(lire(chemin).splitlines(), 1):
            m = re.search(r"""["']?(\d{1,5}):(\d{4,5})["']?""", ligne)
            if m and m.group(2) in PORTS_BASE:
                ajouter("alerte", f"{PORTS_BASE[m.group(2)]} exposé hors du réseau",
                        "La base devient joignable depuis l'extérieur. Retirer "
                        "la publication du port : les autres services "
                        "l'atteignent par le réseau interne.", f"{rel}:{i}")

    # --- Secrets dans la CI ---
    for chemin in parcourir(racine, {".yml", ".yaml"}):
        rel = chemin.relative_to(racine).as_posix()
        if ".github/workflows" not in rel and "gitlab-ci" not in rel:
            continue
        for i, ligne in enumerate(lire(chemin).splitlines(), 1):
            if re.search(r"""(?i)(api[_-]?key|token|password|secret)\s*:\s*["']?[A-Za-z0-9_\-]{12,}""", ligne) \
               and "secrets." not in ligne and "${{" not in ligne:
                ajouter("alerte", "Secret probablement en clair dans la CI",
                        "Le déplacer dans le coffre à secrets du fournisseur "
                        "et le référencer, puis **révoquer la valeur "
                        "actuelle**.", f"{rel}:{i}")

    # --- Migrations ---
    migrations = [c for c in parcourir(racine)
                  if "migration" in c.as_posix().lower() or "/alembic/" in c.as_posix().lower()]
    if migrations:
        ajouter("info", "Le projet a des migrations",
                f"{len(migrations)} fichiers. Vérifier qu'elles sont jouées "
                "dans l'étape de déploiement, **avant** le démarrage de la "
                "nouvelle version, et qu'elles sont réversibles.")
    return faits


def tableau(items: list[dict], colonnes: list[str], cles: list[str],
            plafond: int = 40) -> list[str]:
    out = ["| " + " | ".join(colonnes) + " |",
           "|" + "|".join(["---"] * len(colonnes)) + "|"]
    for t in items[:plafond]:
        cellules = []
        for c in cles:
            v = str(t.get(c, "")).replace("|", "\\|")
            cellules.append(f"`{v}`" if c in ("ou", "extrait", "valeur") and v else v)
        out.append("| " + " | ".join(cellules) + " |")
    if len(items) > plafond:
        out.append(f"| … | {len(items) - plafond} autres |" +
                   " |" * (len(colonnes) - 2))
    return out + [""]


def rendre(r: dict, declarees: set[str], livraison: list[dict], racine: Path) -> str:
    l = [f"# Prêt pour la production ? — {racine.name}", "",
         "> **Des pistes, pas des verdicts.** Un `localhost` dans un fichier de "
         "test ne pose aucun problème. Chaque ligne se confirme en ouvrant le "
         "fichier.", ""]

    def bloc(titre: str, cle: str, note: str, colonne: str, valeur: str):
        """Un domaine, groupé par fichier.

        Le groupement n'est pas cosmétique : sur un vrai projet, un même motif
        revient des centaines de fois dans quelques fichiers. Une ligne par
        occurrence noie le signal ; une ligne par fichier se lit.
        """
        nonlocal l                       # sinon `l += …` ferait de `l` une locale
        items = r[cle]
        hors_test = [t for t in items if not t.get("test")]
        dans_test = [t for t in items if t.get("test")]
        l += [f"## {titre}", ""]
        if not hors_test:
            l += ["*Rien hors des fichiers de test et d'exemple.*"
                  if dans_test else "*Rien trouvé.*", ""]
            return

        par_fichier: dict[str, dict] = {}
        for t in hors_test:
            fichier, _, ligne = t["ou"].rpartition(":")
            g = par_fichier.setdefault(fichier, {"n": 0, "premiere": ligne,
                                                 "exemple": t.get(valeur, "")})
            g["n"] += 1
        ordonnes = sorted(par_fichier.items(), key=lambda x: -x[1]["n"])

        l += [f"{len(hors_test)} occurrences dans {len(par_fichier)} fichiers. "
              f"{note}", "",
              f"| Fichier | Occurrences | Première ligne | {colonne} |",
              "|---|---|---|---|"]
        for fichier, g in ordonnes[:40]:
            exemple = str(g["exemple"]).replace("|", "\\|")[:80]
            l.append(f"| `{fichier}` | {g['n']} | {g['premiere']} | "
                     f"{'`' + exemple + '`' if exemple else '—'} |")
        if len(ordonnes) > 40:
            l.append(f"| … | | | {len(ordonnes) - 40} autres fichiers |")
        l.append("")
        if dans_test:
            l += [f"*Plus {len(dans_test)} occurrences dans des fichiers de "
                  f"test, d'exemple ou de documentation — sans conséquence.*", ""]

    bloc("Adresses locales en dur", "locale",
         "Une adresse `localhost` dans le code applicatif ne marchera pas "
         "depuis le navigateur d'un visiteur. **Pour un frontend, la valeur "
         "est figée au moment du build.**",
         "Exemple", "extrait")

    l.append("## Port d'écoute")
    l.append("")
    if r["port_env"]:
        l += ["*Le port est lu depuis l'environnement quelque part. Vérifier "
              "que c'est bien le cas au point de démarrage.*", ""]
    ports = [t for t in r["port"] if not t.get("test")]
    if ports:
        l += [f"{len(ports)} port(s) écrits en dur. Beaucoup de plateformes "
              "imposent leur propre port par une variable `PORT` : un port "
              "figé fait échouer la vérification de santé.", ""]
        l += tableau(ports, ["Où", "Port", "Extrait"], ["ou", "port", "extrait"])
    elif not r["port_env"]:
        l += ["*Aucun port trouvé. À vérifier à la main.*", ""]

    bloc("Écoute sur 127.0.0.1", "ecoute",
         "Dans un conteneur, `127.0.0.1` n'est joignable que de l'intérieur. "
         "Il faut écouter sur `0.0.0.0`.",
         "Extrait", "extrait")

    bloc("Valeurs de repli dangereuses", "repli",
         "Quand la variable manque, le code prend cette valeur — et "
         "l'application tourne sur la mauvaise cible **sans erreur**. C'est le "
         "pire cas : tout semble marcher.",
         "Valeur de repli", "valeur")

    bloc("Chemins Windows", "windows",
         "Un antislash ou une lettre de lecteur ne passe pas sur un serveur "
         "Linux. Construire les chemins avec l'outil du langage.",
         "Extrait", "extrait")

    bloc("CORS ouvert à toutes les origines", "cors",
         "`*` est un trou de sécurité, et ne fonctionne de toute façon pas "
         "avec des cookies. Mettre la liste des origines en variable "
         "d'environnement.",
         "Extrait", "extrait")

    bloc("Écritures sur le disque du serveur", "ecriture",
         "Sur beaucoup d'hébergeurs, le disque du conteneur est remis à zéro à "
         "chaque redémarrage. Vérifier ce qui est écrit : un cache est sans "
         "conséquence, un fichier envoyé par un utilisateur est perdu.",
         "Extrait", "extrait")

    l += ["## Page de santé", ""]
    if r["sante"]:
        l += ["Adresses trouvées :", ""]
        l += [f"- `{t['adresse']}` — `{t['ou']}`" for t in r["sante"][:10]] + [""]
        l += ["**Vérifier qu'elle teste vraiment quelque chose.** Une page qui "
              "renvoie toujours « tout va bien » laisse l'hébergeur croire le "
              "service sain alors que la base ne répond plus.", ""]
    else:
        l += ["**Aucune page de santé trouvée.** Sans elle, l'hébergeur n'a "
              "aucun moyen de savoir si l'application est vivante, et ne la "
              "redémarrera jamais quand elle sera bloquée.", ""]

    manquantes = sorted(set(r["variables"]) - declarees)
    l += ["## Variables d'environnement", "",
          f"{len(r['variables'])} utilisées dans le code, "
          f"{len(declarees)} déclarées quelque part.", ""]
    if manquantes:
        l += [f"### Utilisées mais déclarées nulle part ({len(manquantes)})", "",
              "Au déploiement, elles seront vides. Les déclarer dans un "
              "`.env.example`, puis les saisir sur l'hébergeur.", ""]
        l += tableau([{"nom": f"`{n}`", "ou": r["variables"][n]} for n in manquantes],
                     ["Variable", "Première utilisation"], ["nom", "ou"], 60)
    else:
        l += ["*Toutes les variables utilisées sont déclarées quelque part.*", ""]

    l += ["## Livraison et infrastructure", ""]
    if livraison:
        etiquettes = {"ok": "OK", "alerte": "À corriger", "info": "À vérifier"}
        l += ["| État | Quoi | Où | Détail |", "|---|---|---|---|"]
        rang = {"alerte": 0, "info": 1, "ok": 2}
        for f in sorted(livraison, key=lambda x: rang[x["gravite"]]):
            ou = f"`{f['ou']}`" if f["ou"] else "—"
            l.append(f"| {etiquettes[f['gravite']]} | {f['quoi']} | {ou} | "
                     f"{f['detail'].replace('|', chr(92) + '|')} |")
        l.append("")
    else:
        l += ["*Aucun fichier de livraison trouvé.*", ""]

    l += ["## Ce que le script ne voit pas", "",
          "À vérifier à la main :", "",
          "- les réglages réellement saisis sur l'hébergeur ;",
          "- les adresses de retour enregistrées chez les services externes ;",
          "- la persistance du disque chez l'hébergeur choisi ;",
          "- les migrations jouées, et leur réversibilité ;",
          "- la sauvegarde de la base, et une **restauration déjà testée** ;",
          "- le plan de retour arrière, et sa durée en minutes.", ""]
    return "\n".join(l)


def main():
    p = argparse.ArgumentParser(description="Cherche les pièges du déploiement.")
    p.add_argument("projet")
    p.add_argument("--sortie", "-o")
    args = p.parse_args()

    racine = Path(args.projet).resolve()
    if not racine.is_dir():
        print(f"Dossier introuvable : {racine}", file=sys.stderr)
        raise SystemExit(1)

    r = sonder_code(racine)
    declarees = variables_declarees(racine)
    livraison = sonder_livraison(racine)

    hors_test = lambda cle: sum(1 for t in r[cle] if not t.get("test"))
    print(f"Adresses locales : {hors_test('locale')} · "
          f"ports figés : {hors_test('port')} · "
          f"replis dangereux : {hors_test('repli')} · "
          f"variables non déclarées : {len(set(r['variables']) - declarees)} · "
          f"alertes de livraison : {sum(1 for f in livraison if f['gravite'] == 'alerte')}",
          file=sys.stderr)

    markdown = rendre(r, declarees, livraison, racine)
    if args.sortie:
        chemin = Path(args.sortie)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(markdown, encoding="utf-8")
        print(f"Écrit : {chemin}", file=sys.stderr)
    else:
        sys.stdout.write(markdown)


if __name__ == "__main__":
    main()

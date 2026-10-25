#!/usr/bin/env python3
"""
sonder_projet.py — les portes d'entrée d'un projet, et ce qui s'y passe.

    python sonder_projet.py <projet> -o surface.md
    python sonder_projet.py <projet> --dependances -o surface.md

Ce que le script relève :

- les adresses de l'API, et si un contrôle d'accès est visible à côté ;
- la configuration CORS ;
- les points d'envoi de fichiers ;
- les appels dangereux (exécution de code, commandes système, HTML brut) ;
- les requêtes SQL construites par collage de chaînes ;
- les variables d'environnement utilisées, et celles qui ne sont déclarées
  nulle part ;
- avec `--dependances`, les alertes connues des paquets installés.

**Des pistes, pas des verdicts.** Un script ne voit pas un contrôle posé trois
lignes plus haut, ni un middleware monté ailleurs. Chaque ligne se confirme en
ouvrant le fichier.

Aucune dépendance : bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

IGNORES = {"node_modules", ".git", "dist", "build", "out", ".next", ".nuxt",
           ".venv", "venv", "__pycache__", "vendor", "target", "coverage",
           ".turbo", ".cache", "site-packages", ".pytest_cache", "obj"}
CODE = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rb", ".php", ".java"}
TAILLE_MAX = 600_000

ADRESSE = re.compile(r"""@?\w+\.(get|post|put|patch|delete|route)\s*\(\s*["'`]([^"'`]+)""",
                     re.IGNORECASE)
# Ce qui, à proximité, ressemble à un contrôle d'accès.
CONTROLE = re.compile(r"""(?i)\b(depends|current_user|get_current|require|auth|
    authenticate|authorize|permission|is_admin|login_required|guard|verify_token|
    jwt_required|ensure|protect|can_|policy)""", re.VERBOSE)
PROPRIETE = re.compile(r"""(?i)(user_id|utilisateur_id|owner|proprietaire|
    current_user|tenant|organisation_id|account_id)""", re.VERBOSE)

DANGERS = [
    ("Exécution de code", re.compile(r"\b(eval|exec)\s*\(")),
    ("Commande système", re.compile(r"\b(os\.system|subprocess\.\w+\([^)]*shell\s*=\s*True|child_process|execSync)")),
    ("HTML inséré sans échappement", re.compile(r"(dangerouslySetInnerHTML|\.innerHTML\s*=|v-html)")),
    ("Désérialisation non sûre", re.compile(r"\b(pickle\.loads|yaml\.load\s*\((?![^)]*Loader)|unserialize)\b")),
    ("Vérification TLS désactivée", re.compile(r"(?i)(verify\s*=\s*False|rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED)")),
    ("Mode debug", re.compile(r"(?i)\b(debug\s*=\s*True|DEBUG\s*:\s*true|app\.debug)")),
    ("Aléatoire non cryptographique pour un secret", re.compile(r"(?i)(Math\.random|random\.random)\s*\(\)[^\n]{0,40}(token|secret|password|cle|key)")),
]
# Le drapeau d'insensibilité à la casse se pose à la compilation : au milieu
# d'une alternance, Python le refuse.
SQL_COLLE = re.compile(
    r"""(select|insert|update|delete)\s[^\n"']{0,120}["']\s*\+"""
    r"""|f["'][^"'\n]*\b(?:select|insert|update|delete)\b[^"'\n]*\{""",
    re.IGNORECASE)
CORS = re.compile(r"(?i)(allow_origins|Access-Control-Allow-Origin|cors\s*\(|origin\s*:)")
UPLOAD = re.compile(r"(?i)(UploadFile|multer|FormData|multipart|\.save\(|save_file|request\.files)")
ENV = re.compile(r"""(?:os\.environ(?:\.get)?\[?\s*["']([A-Z0-9_]{3,})["']|"""
                 r"""os\.getenv\(\s*["']([A-Z0-9_]{3,})["']|"""
                 r"""process\.env\.([A-Z0-9_]{3,})|"""
                 r"""import\.meta\.env\.([A-Z0-9_]{3,}))""")


def parcourir(racine: Path, extensions: set[str] | None = None):
    for chemin in racine.rglob("*"):
        if not chemin.is_file() or any(p in IGNORES for p in chemin.parts):
            continue
        if extensions and chemin.suffix.lower() not in extensions:
            continue
        try:
            if chemin.stat().st_size > TAILLE_MAX:
                continue
        except OSError:
            continue
        yield chemin


def lire(chemin: Path) -> list[str]:
    try:
        return chemin.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []


def est_un_test(rel: str) -> bool:
    bas = rel.lower()
    return "test" in bas or "spec" in bas or "__mocks__" in bas


def sonder(racine: Path) -> dict:
    adresses, dangers, sql, cors, uploads = [], [], [], [], []
    variables: dict[str, str] = {}

    for chemin in parcourir(racine, CODE):
        rel = chemin.relative_to(racine).as_posix()
        lignes = lire(chemin)
        for i, ligne in enumerate(lignes):
            numero = i + 1

            for m in ADRESSE.finditer(ligne):
                methode, adresse = m.group(1).upper(), m.group(2)
                if not adresse.startswith("/") or est_un_test(rel):
                    continue
                # Un contrôle se pose sur la ligne de l'adresse, sur la
                # signature juste en dessous, ou juste au-dessus.
                voisinage = "\n".join(lignes[max(0, i - 2):i + 6])
                adresses.append({
                    "methode": methode, "adresse": adresse,
                    "ou": f"{rel}:{numero}",
                    "controle": bool(CONTROLE.search(voisinage)),
                    "propriete": bool(PROPRIETE.search(voisinage)),
                })

            for nom, motif in DANGERS:
                if motif.search(ligne):
                    dangers.append({"quoi": nom, "ou": f"{rel}:{numero}",
                                    "extrait": ligne.strip()[:110]})
            if SQL_COLLE.search(ligne):
                sql.append({"ou": f"{rel}:{numero}", "extrait": ligne.strip()[:110]})
            if CORS.search(ligne):
                cors.append({"ou": f"{rel}:{numero}", "extrait": ligne.strip()[:110]})
            if UPLOAD.search(ligne) and not est_un_test(rel):
                uploads.append({"ou": f"{rel}:{numero}", "extrait": ligne.strip()[:110]})
            for m in ENV.finditer(ligne):
                nom = next(g for g in m.groups() if g)
                variables.setdefault(nom, f"{rel}:{numero}")

    return {"adresses": adresses, "dangers": dangers, "sql": sql,
            "cors": cors, "uploads": uploads, "variables": variables}


def variables_declarees(racine: Path) -> set[str]:
    """Les variables listées dans un fichier d'exemple ou de configuration."""
    noms = set()
    for chemin in parcourir(racine):
        nom = chemin.name.lower()
        if not (nom.startswith(".env") or nom in ("docker-compose.yml",
                                                  "docker-compose.yaml")):
            continue
        for ligne in lire(chemin):
            m = re.match(r"\s*(?:-\s*)?([A-Z][A-Z0-9_]{2,})\s*[=:]", ligne)
            if m:
                noms.add(m.group(1))
    return noms


def audit_dependances(racine: Path) -> list[str]:
    """Lance les outils d'audit du projet, s'ils sont disponibles.

    Lecture seule : aucun de ces outils ne modifie le projet. Une alerte n'est
    pas un constat — il faut vérifier que le code appelle la partie touchée.
    """
    lignes = []
    if (racine / "package.json").exists():
        try:
            r = subprocess.run(["npm", "audit", "--json"], cwd=racine,
                               capture_output=True, text=True, timeout=300,
                               encoding="utf-8", errors="replace", shell=True)
            data = json.loads(r.stdout or "{}")
            compte = (data.get("metadata", {}).get("vulnerabilities")
                      or data.get("vulnerabilities") or {})
            if isinstance(compte, dict) and compte:
                resume = ", ".join(f"{k} : {v}" for k, v in compte.items()
                                   if isinstance(v, int) and v)
                lignes.append(f"- **npm audit** — {resume or 'aucune alerte'}")
            else:
                lignes.append("- **npm audit** — aucune alerte.")
        except Exception as erreur:
            lignes.append(f"- **npm audit** non exécuté : {type(erreur).__name__}.")
    for outil, cible in (("pip-audit", "requirements.txt"),
                         ("pip-audit", "pyproject.toml")):
        if not (racine / cible).exists():
            continue
        try:
            r = subprocess.run([outil, "--progress-spinner", "off"], cwd=racine,
                               capture_output=True, text=True, timeout=300,
                               encoding="utf-8", errors="replace", shell=True)
            tete = (r.stdout or r.stderr or "").strip().splitlines()[:12]
            lignes.append(f"- **{outil}** ({cible}) :\n\n```\n" +
                          "\n".join(tete) + "\n```")
        except Exception as erreur:
            lignes.append(f"- **{outil}** non exécuté : {type(erreur).__name__}. "
                          f"Installer avec `pip install pip-audit`.")
        break
    return lignes or ["- Aucun outil d'audit applicable trouvé."]


def rendre(r: dict, declarees: set[str], deps: list[str], racine: Path) -> str:
    l = [f"# Surface d'attaque — {racine.name}", "",
         "> **Des pistes, pas des verdicts.** Le script ne voit pas un contrôle "
         "posé ailleurs dans le fichier, ni un middleware monté au niveau du "
         "routeur. Ouvrir chaque fichier avant de conclure.", ""]

    adresses = r["adresses"]
    sans = [a for a in adresses if not a["controle"]]
    sans_propriete = [a for a in adresses
                      if a["controle"] and not a["propriete"]
                      and re.search(r"\{|\:", a["adresse"])]

    l += ["## Adresses de l'API", "",
          f"{len(adresses)} adresses déclarées. "
          f"{len(sans)} sans contrôle d'accès visible.", ""]
    if sans:
        l += ["### Aucun contrôle d'accès visible", "",
              "Normal pour une page publique ou la connexion. Anormal partout "
              "ailleurs.", "",
              "| Méthode | Adresse | Où |", "|---|---|---|"]
        l += [f"| `{a['methode']}` | `{a['adresse']}` | `{a['ou']}` |"
              for a in sans[:60]] + [""]
    if sans_propriete:
        l += ["### Contrôle présent, mais aucun filtre sur le propriétaire", "",
              "L'adresse porte un identifiant et vérifie la connexion, sans "
              "qu'on voie de filtre sur l'utilisateur. **C'est le motif le plus "
              "fréquent d'accès aux données d'autrui.** À confirmer en lisant "
              "la fonction.", "",
              "| Méthode | Adresse | Où |", "|---|---|---|"]
        l += [f"| `{a['methode']}` | `{a['adresse']}` | `{a['ou']}` |"
              for a in sans_propriete[:60]] + [""]

    for titre, items, note in (
        ("Appels dangereux", r["dangers"],
         "Chaque ligne demande une vérification : d'où vient la valeur ?"),
        ("Requêtes SQL construites par collage", r["sql"],
         "Dangereux seulement si la valeur vient de l'utilisateur. À vérifier."),
        ("Configuration CORS", r["cors"],
         "Vérifier qu'aucune origine n'est ouverte à tous avec des identifiants."),
        ("Envois de fichiers", r["uploads"],
         "Vérifier : type réel, taille, nom nettoyé, dossier non exécutable."),
    ):
        l += [f"## {titre}", ""]
        if not items:
            l += ["*Rien trouvé.*", ""]
            continue
        l += [note, "", "| Où | Extrait |", "|---|---|"]
        for t in items[:50]:
            extrait = t["extrait"].replace("|", "\\|")
            quoi = f"**{t['quoi']}** — " if "quoi" in t else ""
            l.append(f"| `{t['ou']}` | {quoi}`{extrait}` |")
        if len(items) > 50:
            l.append(f"| … | {len(items) - 50} autres |")
        l.append("")

    manquantes = sorted(set(r["variables"]) - declarees)
    l += ["## Variables d'environnement", "",
          f"{len(r['variables'])} variables utilisées dans le code.", ""]
    if manquantes:
        l += [f"### Utilisées mais déclarées nulle part ({len(manquantes)})", "",
              "Ni dans un `.env.example`, ni dans un fichier de composition. "
              "Au déploiement, elles seront vides.", "",
              "| Variable | Première utilisation |", "|---|---|"]
        l += [f"| `{n}` | `{r['variables'][n]}` |" for n in manquantes[:60]] + [""]
    else:
        l += ["*Toutes les variables utilisées sont déclarées quelque part.*", ""]

    l += ["## Dépendances", ""] + deps + [""]
    l += ["> Une alerte d'outil n'est pas un constat. Vérifier que le code "
          "appelle vraiment la partie vulnérable avant de monter le niveau.", ""]
    return "\n".join(l)


def main():
    p = argparse.ArgumentParser(description="Relève les portes d'entrée d'un projet.")
    p.add_argument("projet")
    p.add_argument("--dependances", action="store_true",
                   help="Lancer aussi les outils d'audit de dépendances.")
    p.add_argument("--sortie", "-o")
    args = p.parse_args()

    racine = Path(args.projet).resolve()
    if not racine.is_dir():
        print(f"Dossier introuvable : {racine}", file=sys.stderr)
        raise SystemExit(1)

    resultat = sonder(racine)
    declarees = variables_declarees(racine)
    deps = audit_dependances(racine) if args.dependances else \
        ["- Non demandé. Relancer avec `--dependances`."]

    print(f"{len(resultat['adresses'])} adresses, "
          f"{len(resultat['dangers'])} appels à vérifier, "
          f"{len(resultat['variables'])} variables.", file=sys.stderr)

    markdown = rendre(resultat, declarees, deps, racine)
    if args.sortie:
        chemin = Path(args.sortie)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(markdown, encoding="utf-8")
        print(f"Écrit : {chemin}", file=sys.stderr)
    else:
        sys.stdout.write(markdown)


if __name__ == "__main__":
    main()

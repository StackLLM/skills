#!/usr/bin/env python3
"""
collecter_projet.py — fait l'inventaire d'un projet local, pour bâtir sa map.

    python3 collecter_projet.py chemin/du/projet -o inventaire.json

Ce script ne juge rien. Il dit où chercher :
- l'activité git (dernier commit, tags, branches) ;
- les documents qui parlent de plan, de lots, de décisions, avec le nombre de
  cases cochées et les titres de lots trouvés ;
- les preuves techniques (tests, CI, déploiement) ;
- les dossiers de premier niveau, pour repérer les volets ;
- les tickets et jalons GitHub, si le dépôt est sur GitHub et `gh` connecté.

Le contenu des fichiers .env n'est jamais lu : on note seulement leur nom.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

DOSSIERS_IGNORES = {
    ".git", "node_modules", "venv", ".venv", "env", "dist", "build", "out",
    "__pycache__", ".next", ".nuxt", ".cache", "coverage", "vendor", "target",
    ".idea", ".vscode", "worktrees", "site-packages", "backups", "logs",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
}

MOTS_PLAN = re.compile(
    r"(plan|roadmap|feuille|lot|suivi|todo|avancement|etat|état|cdc|cahier|"
    r"cadrage|spec|adr|decision|décision|backlog|projet|changelog|release|"
    r"livraison|mise.?en.?ligne|deploiement|déploiement|readme|correction|"
    r"demarche|démarche|etude|étude|audit|vision|analyse|bug|map)", re.I)

TITRE_LOT = re.compile(
    r"^#{1,5}\s+.*\b(lot|phase|étape|etape|sprint|jalon|milestone|chantier)\b.*$",
    re.I | re.M)

FICHIERS_DEPLOIEMENT = re.compile(
    r"^(dockerfile.*|docker-compose.*\.ya?ml|compose.*\.ya?ml|netlify\.toml|"
    r"vercel\.json|fly\.toml|render\.yaml|railway\.json|caddyfile.*|"
    r"nginx.*\.conf|procfile|deploy\.(bat|sh|ps1))$", re.I)

FICHIER_TEST = re.compile(
    r"(^test_.*\.py$|.*_test\.(py|go)$|.*\.(test|spec)\.[jt]sx?$)", re.I)

MAX_DOCUMENTS = 60
MAX_TITRES = 30


def executer(commande: list[str], dossier: Path | None = None) -> str | None:
    try:
        sortie = subprocess.run(commande, cwd=dossier, capture_output=True,
                                timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if sortie.returncode != 0:
        return None
    try:
        return sortie.stdout.decode("utf-8").strip()
    except UnicodeDecodeError:
        # Certains commits faits sous Windows ne sont pas en UTF-8.
        return sortie.stdout.decode("cp1252", errors="replace").strip()


def fichiers(racine: Path):
    for chemin in racine.rglob("*"):
        relatif = chemin.relative_to(racine)
        if any(partie in DOSSIERS_IGNORES for partie in relatif.parts[:-1]):
            continue
        if chemin.is_file():
            yield chemin, relatif


def est_document_plan(relatif: Path) -> bool:
    """Tout document à la racine compte : le nom d'un suivi est imprévisible."""
    suffixe = relatif.suffix.lower()
    if suffixe in (".md", ".mdx", ".txt", ".rst"):
        return len(relatif.parts) == 1 or bool(MOTS_PLAN.search(relatif.as_posix()))
    return (suffixe == ".html" and relatif.parts[0] == "docs"
            and bool(MOTS_PLAN.search(relatif.name)))


def lire_document(chemin: Path, relatif: Path, racine: Path) -> dict:
    try:
        texte = chemin.read_text(encoding="utf-8", errors="replace")
    except OSError:
        texte = ""
    date = executer(["git", "log", "-1", "--format=%ad", "--date=short", "--",
                     relatif.as_posix()], racine)
    return {
        "chemin": relatif.as_posix(),
        "derniere_modif": date or None,
        "lignes": texte.count("\n") + 1,
        "cases_cochees": len(re.findall(r"^\s*[-*] \[[xX]\]", texte, re.M)),
        "cases_vides": len(re.findall(r"^\s*[-*] \[ \]", texte, re.M)),
        "titres_de_lots": [m.group(0).strip()
                           for m in TITRE_LOT.finditer(texte)][:MAX_TITRES],
    }


def poids(document: dict) -> tuple:
    """Les documents de suivi les plus riches et les plus récents d'abord."""
    return (len(document["titres_de_lots"])
            + document["cases_cochees"] + document["cases_vides"],
            document["derniere_modif"] or "")


def inventaire_git(racine: Path) -> dict:
    def git(*arguments):
        # Sur Windows, git sort parfois les accents dans un autre encodage.
        return executer(["git", "-c", "i18n.logOutputEncoding=utf-8", *arguments],
                        racine)

    if git("rev-parse", "--is-inside-work-tree") != "true":
        return {"depot_git": False}
    tags = git("tag", "--sort=-creatordate") or ""
    branches = git("branch", "-a", "--format=%(refname:short)") or ""
    return {
        "depot_git": True,
        "remote": git("remote", "get-url", "origin"),
        "branche": git("branch", "--show-current"),
        "dernier_commit": git("log", "-1", "--format=%ad %s", "--date=short"),
        "premier_commit": (git("log", "--reverse", "--format=%ad", "--date=short")
                           or "\n").split("\n")[0] or None,
        "commits_30_jours": int(git("rev-list", "--count", "--since=30.days",
                                    "HEAD") or 0),
        "commits_total": int(git("rev-list", "--count", "HEAD") or 0),
        "tags": tags.split("\n")[:10] if tags else [],
        "branches": branches.split("\n")[:30] if branches else [],
        "derniers_commits": (git("log", "-40", "--format=%ad %s", "--date=short")
                             or "").split("\n"),
    }


def inventaire_github(remote: str | None) -> dict:
    trouve = re.search(r"github\.com[:/]([^/]+/[^/.]+)", remote or "")
    if not trouve:
        return {"disponible": False}
    depot = trouve.group(1)
    issues = executer(["gh", "issue", "list", "-R", depot, "--state", "open",
                       "--limit", "50", "--json", "number,title,labels,milestone"])
    jalons = executer(["gh", "api", f"repos/{depot}/milestones?state=all"])
    deploiements = executer(["gh", "api", f"repos/{depot}/deployments?per_page=5"])
    if issues is None and jalons is None:
        return {"disponible": False, "depot": depot}
    return {
        "disponible": True,
        "depot": depot,
        "tickets_ouverts": json.loads(issues or "[]"),
        "jalons": [{"titre": j["title"], "ouverts": j["open_issues"],
                    "fermes": j["closed_issues"], "etat": j["state"]}
                   for j in json.loads(jalons or "[]")],
        "deploiements": [{"environnement": d["environment"],
                          "date": d["created_at"][:10]}
                         for d in json.loads(deploiements or "[]")],
    }


def inventorier(racine: Path) -> dict:
    documents, deploiement, ci, env = [], [], [], []
    nombre_tests = 0
    for chemin, relatif in fichiers(racine):
        nom = relatif.name
        if est_document_plan(relatif):
            documents.append((chemin, relatif))
        if FICHIERS_DEPLOIEMENT.match(nom):
            deploiement.append(relatif.as_posix())
        if FICHIER_TEST.match(nom):
            nombre_tests += 1
        if ".github/workflows" in relatif.as_posix():
            ci.append(relatif.as_posix())
        if nom.startswith(".env"):
            env.append(relatif.as_posix())

    lus = [lire_document(c, r, racine) for c, r in documents]
    lus.sort(key=poids, reverse=True)
    git = inventaire_git(racine)
    return {
        "nom": racine.name,
        "chemin": str(racine),
        "git": git,
        "github": inventaire_github(git.get("remote")),
        "dossiers_premier_niveau": sorted(
            p.name for p in racine.iterdir()
            if p.is_dir() and p.name not in DOSSIERS_IGNORES
            and not p.name.startswith(".")),
        "documents": lus[:MAX_DOCUMENTS],
        "documents_non_listes": max(0, len(lus) - MAX_DOCUMENTS),
        "preuves": {
            "fichiers_de_test": nombre_tests,
            "ci": ci,
            "deploiement": deploiement,
            "fichiers_env_noms_seulement": env,
        },
    }


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parseur = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parseur.add_argument("projet", type=Path)
    parseur.add_argument("-o", "--sortie", type=Path)
    options = parseur.parse_args()

    racine = options.projet.resolve()
    if not racine.is_dir():
        print(f"Dossier introuvable : {racine}", file=sys.stderr)
        return 2
    texte = json.dumps(inventorier(racine), ensure_ascii=False, indent=2)
    if options.sortie:
        options.sortie.write_text(texte, encoding="utf-8")
        print(options.sortie)
    else:
        print(texte)
    return 0


if __name__ == "__main__":
    sys.exit(main())

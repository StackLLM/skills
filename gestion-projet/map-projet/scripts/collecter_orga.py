#!/usr/bin/env python3
"""
collecter_orga.py — fait l'inventaire de tous les dépôts d'une organisation GitHub.

    python collecter_orga.py StackLLM -o inventaire-orga.json
    python collecter_orga.py StackLLM --racine ~/Documents/Developer

Pour chaque dépôt, sans rien cloner : dernière activité, tickets, jalons,
dernière version publiée, documents de suivi, fichiers de test et de déploiement.
Avec --racine, il indique aussi le clone local quand il existe, pour lire le
projet en détail avec collecter_projet.py.

Chaque dépôt est classé :
- actif : un push depuis moins de 90 jours, donc à lire pour la map ;
- dormant : plus ancien ;
- archive, fork, gabarit : selon GitHub.

Pour chaque clone local, `clone_a_jour` dit s'il contient le dernier commit de la
branche principale. `dernier_push_branche` dit où a eu lieu le dernier push :
ce n'est pas toujours la branche principale.

Ce script ne juge rien. Il dit où chercher. Prérequis : `gh` connecté.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path, PurePosixPath

from collecter_projet import (DOSSIERS_IGNORES, FICHIER_TEST,
                              FICHIERS_DEPLOIEMENT, est_document_plan, executer)

JOURS_ACTIF = 90
MAX_DOCUMENTS = 25


def gh_json(*arguments: str):
    sortie = executer(["gh", *arguments])
    if not sortie:
        return None
    try:
        return json.loads(sortie)
    except json.JSONDecodeError:
        return None


def clones_locaux(racine: Path | None) -> dict[str, str]:
    """Associe « orga/depot » en minuscules au dossier local qui le clone."""
    if not racine or not racine.is_dir():
        return {}
    clones = {}
    for dossier in racine.iterdir():
        config = dossier / ".git" / "config"
        if not config.is_file():
            continue
        texte = config.read_text(encoding="utf-8", errors="replace")
        for depot in re.findall(r"github\.com[:/]([^/\s]+/[^/\s]+?)(?:\.git)?\s", texte):
            clones.setdefault(depot.lower(), str(dossier))
        # Certains clones n'ont pas l'orga en remote : on garde aussi le nom.
        clones.setdefault(f"nom:{normaliser(dossier.name)}", str(dossier))
    return clones


def normaliser(nom: str) -> str:
    return re.sub(r"[-_ ]", "", nom).lower()


def trouver_clone(orga: str, nom: str, clones: dict[str, str]) -> tuple[str | None, bool]:
    """Renvoie le dossier et si le lien n'est qu'une ressemblance de nom."""
    exact = clones.get(f"{orga}/{nom}".lower())
    if exact:
        return exact, False
    probable = clones.get(f"nom:{normaliser(nom)}")
    return probable, bool(probable)


def etat_branches(orga: str, nom: str, branche: str, clone: str | None) -> dict:
    tete = gh_json("api", f"repos/{orga}/{nom}/commits/{branche}") or {}
    evenements = gh_json("api", f"repos/{orga}/{nom}/events?per_page=30") or []
    pushes = [ev for ev in evenements if ev.get("type") == "PushEvent"]
    sha = tete.get("sha")
    a_jour = None
    if clone and sha:
        a_jour = executer(["git", "cat-file", "-e", f"{sha}^{{commit}}"],
                          Path(clone)) is not None
    return {
        "branche_principale": branche,
        "dernier_commit_principal": (((tete.get("commit") or {}).get("committer")
                                      or {}).get("date") or "")[:10] or None,
        "dernier_push_branche": ((pushes[0].get("payload") or {}).get("ref", "")
                                 .replace("refs/heads/", "") if pushes else None),
        "clone_a_jour": a_jour,
    }


def lire_arbre(orga: str, nom: str, branche: str) -> dict:
    arbre = gh_json("api", f"repos/{orga}/{nom}/git/trees/{branche}?recursive=1")
    chemins = [n["path"] for n in (arbre or {}).get("tree", [])
               if n.get("type") == "blob"]
    gardes = [c for c in chemins
              if not DOSSIERS_IGNORES.intersection(c.split("/")[:-1])]
    documents = [c for c in gardes if est_document_plan(PurePosixPath(c))]
    documents.sort(key=lambda c: (c.count("/"), c))
    return {
        "documents": documents[:MAX_DOCUMENTS],
        "documents_non_listes": max(0, len(documents) - MAX_DOCUMENTS),
        "fichiers_de_test": sum(bool(FICHIER_TEST.match(c.rsplit("/", 1)[-1]))
                                for c in gardes),
        "deploiement": [c for c in gardes
                        if FICHIERS_DEPLOIEMENT.match(c.rsplit("/", 1)[-1])][:10],
        "ci": [c for c in gardes if c.startswith(".github/workflows/")],
        "dossiers_premier_niveau": sorted({c.split("/")[0] for c in gardes
                                           if "/" in c and not c.startswith(".")}),
    }


def lire_depot(orga: str, depot: dict, clones: dict[str, str]) -> dict:
    nom = depot["name"]
    pousse = (depot.get("pushedAt") or "")[:10]
    jours = None
    if pousse:
        jours = (dt.date.today() - dt.date.fromisoformat(pousse)).days
    if depot.get("isArchived"):
        classe = "archive"
    elif depot.get("isTemplate"):
        classe = "gabarit"
    elif depot.get("isFork"):
        classe = "fork"
    elif jours is not None and jours <= JOURS_ACTIF:
        classe = "actif"
    else:
        classe = "dormant"

    clone, par_nom = trouver_clone(orga, nom, clones)
    fiche = {
        "nom": nom,
        "classe": classe,
        "description": depot.get("description") or "",
        "dernier_push": pousse or None,
        "jours_sans_push": jours,
        "fork": depot.get("isFork", False),
        "site": depot.get("homepageUrl") or None,
        "clone_local": clone,
        "clone_trouve_par_le_nom": par_nom,
    }
    if classe in ("archive", "gabarit", "fork"):
        return fiche

    branche = (depot.get("defaultBranchRef") or {}).get("name") or "main"
    fiche.update(etat_branches(orga, nom, branche, clone))
    fiche.update(lire_arbre(orga, nom, branche))
    tickets = gh_json("issue", "list", "-R", f"{orga}/{nom}", "--state", "open",
                      "--limit", "30", "--json", "number,title,labels,milestone")
    jalons = gh_json("api", f"repos/{orga}/{nom}/milestones?state=all")
    version = gh_json("api", f"repos/{orga}/{nom}/releases/latest")
    fiche["tickets_ouverts"] = tickets or []
    fiche["jalons"] = [{"titre": j["title"], "ouverts": j["open_issues"],
                        "fermes": j["closed_issues"], "etat": j["state"]}
                       for j in jalons or []]
    fiche["derniere_version"] = (
        {"nom": version.get("tag_name"),
         "date": (version.get("published_at") or "")[:10]} if version else None)
    return fiche


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parseur = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parseur.add_argument("orga")
    parseur.add_argument("-o", "--sortie", type=Path)
    parseur.add_argument("--racine", type=Path,
                         help="dossier qui contient les clones locaux")
    options = parseur.parse_args()

    depots = gh_json("repo", "list", options.orga, "--limit", "300", "--json",
                     "name,description,pushedAt,isArchived,isFork,isTemplate,"
                     "homepageUrl,defaultBranchRef")
    if depots is None:
        print(f"Impossible de lister {options.orga}. Vérifier `gh auth status`.",
              file=sys.stderr)
        return 2

    clones = clones_locaux(options.racine.expanduser() if options.racine else None)
    with ThreadPoolExecutor(max_workers=6) as groupe:
        fiches = list(groupe.map(lambda d: lire_depot(options.orga, d, clones), depots))
    fiches.sort(key=lambda f: f["dernier_push"] or "", reverse=True)

    resultat = {
        "orga": options.orga,
        "date": dt.date.today().isoformat(),
        "compte": {c: sum(f["classe"] == c for f in fiches)
                   for c in ("actif", "dormant", "archive", "fork", "gabarit")},
        "depots": fiches,
    }
    texte = json.dumps(resultat, ensure_ascii=False, indent=2)
    if options.sortie:
        options.sortie.write_text(texte, encoding="utf-8")
        print(options.sortie)
    else:
        print(texte)
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reconstruit l'index des fiches Technical Mentor, et tient la charte à jour.

Sans option : relit toutes les fiches HTML du dossier de sortie, lit leurs
métadonnées (`mentor-domaine`, `mentor-date`, `mentor-resume`) et réécrit
`index.html`. Aucune fiche n'est modifiée.

Avec `--maj-charte` : réinjecte en plus le contenu de `CSS.css` dans chaque
fiche, entre les marques `/* CHARTE:DEBUT */` et `/* CHARTE:FIN */`.
C'est ce qui permet aux fiches d'être autonomes — déplaçables, partageables —
tout en gardant `CSS.css` comme source unique de la charte.

    python indexer.py
    python indexer.py --maj-charte
    python indexer.py --dossier "D:/autre/chemin" --maj-charte
"""

from __future__ import annotations

import argparse
import html
import re
import sys
from datetime import date
from pathlib import Path

# Le dossier des fiches, sous le dossier personnel de la machine.
# Ecrit relativement : un chemin en dur avec un nom d'utilisateur ne
# marche que sur une seule machine.
DOSSIER_DEFAUT = Path.home() / "Documents" / "REVISION-TECHNIQUE" / "Technical-words"

ORDRE_DOMAINES = [
    "Développement",
    "DevOps",
    "Cloud",
    "IA",
    "Sécurité",
]

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin",
        "juillet", "août", "septembre", "octobre", "novembre", "décembre"]


MARQUE_DEBUT = "/* CHARTE:DEBUT */"
MARQUE_FIN = "/* CHARTE:FIN */"
BLOC_CHARTE = re.compile(
    re.escape(MARQUE_DEBUT) + r".*?" + re.escape(MARQUE_FIN), re.S
)


def injecter_charte(dossier: Path) -> tuple[int, int]:
    """Réinjecte la charte et les composants dans chaque fiche, entre les marques.

    Deux sources, dans cet ordre :
      1. `CSS.css`, à côté du dossier des fiches — la charte de la maison ;
      2. `references/mentor.css`, dans cette skill — les composants pédagogiques.

    Renvoie (fiches mises à jour, fiches sans marques).
    """
    charte_src = dossier.parent / "CSS.css"
    mentor_src = Path(__file__).resolve().parent.parent / "references" / "mentor.css"

    morceaux = []
    for source, nom in ((charte_src, "charte"), (mentor_src, "composants")):
        if not source.is_file():
            print(f"{nom.capitalize()} introuvable : {source}")
            return (0, 0)
        morceaux.append(source.read_text(encoding="utf-8").strip())

    remplacement = MARQUE_DEBUT + "\n" + "\n\n".join(morceaux) + "\n" + MARQUE_FIN
    faites, sans_marque = 0, 0

    for chemin in sorted(dossier.glob("*.html")):
        if chemin.name == "index.html":
            continue
        avant = chemin.read_text(encoding="utf-8")
        if MARQUE_DEBUT not in avant or MARQUE_FIN not in avant:
            sans_marque += 1
            print(f"  ! {chemin.name} : marques de charte absentes, fiche ignorée")
            continue
        apres = BLOC_CHARTE.sub(lambda _: remplacement, avant, count=1)
        if apres != avant:
            chemin.write_text(apres, encoding="utf-8")
            faites += 1

    return (faites, sans_marque)


def meta(contenu: str, nom: str) -> str:
    """Lit une balise <meta name="..." content="..."> quel que soit l'ordre des attributs.

    Le délimiteur ouvrant est capturé et doit refermer : sans ça, une apostrophe
    dans un résumé en français coupe la valeur au milieu.
    """
    for motif, groupe in (
        (rf'<meta\s+name=["\']{nom}["\']\s+content=(["\'])(.*?)\1', 2),
        (rf'<meta\s+content=(["\'])(.*?)\1\s+name=["\']{nom}["\']', 2),
    ):
        trouve = re.search(motif, contenu, re.I | re.S)
        if trouve:
            return html.unescape(trouve.group(groupe)).strip()
    return ""


def titre(contenu: str, repli: str) -> str:
    trouve = re.search(r"<title>(.*?)</title>", contenu, re.I | re.S)
    if not trouve:
        return repli
    brut = html.unescape(trouve.group(1)).strip()
    return brut.split("—")[0].strip() or repli


def date_lisible(brut: str) -> str:
    trouve = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", brut.strip())
    if not trouve:
        return brut
    a, m, j = (int(x) for x in trouve.groups())
    return f"{j} {MOIS[m - 1]} {a}"


def lire_fiches(dossier: Path) -> list[dict]:
    fiches = []
    for chemin in sorted(dossier.glob("*.html")):
        if chemin.name == "index.html":
            continue
        contenu = chemin.read_text(encoding="utf-8", errors="replace")
        fiches.append({
            "fichier": chemin.name,
            "titre": titre(contenu, chemin.stem.replace("-", " ")),
            "domaine": meta(contenu, "mentor-domaine") or "Non classé",
            "date": meta(contenu, "mentor-date"),
            "resume": meta(contenu, "mentor-resume"),
        })
    return fiches


def rang(domaine: str) -> int:
    return ORDRE_DOMAINES.index(domaine) if domaine in ORDRE_DOMAINES else len(ORDRE_DOMAINES)


def lire_styles(dossier: Path) -> str:
    """La charte et les composants, pour les coller dans l'index."""
    morceaux = []
    for source in (
        dossier.parent / "CSS.css",
        Path(__file__).resolve().parent.parent / "references" / "mentor.css",
    ):
        if source.is_file():
            morceaux.append(source.read_text(encoding="utf-8").strip())
    return "\n\n".join(morceaux)


def construire(fiches: list[dict], styles: str) -> str:
    groupes: dict[str, list[dict]] = {}
    for f in fiches:
        groupes.setdefault(f["domaine"], []).append(f)

    blocs = []
    for domaine in sorted(groupes, key=lambda d: (rang(d), d)):
        lignes = []
        for f in sorted(groupes[domaine], key=lambda x: x["titre"].lower()):
            resume = html.escape(f["resume"]) if f["resume"] else ""
            quand = date_lisible(f["date"]) if f["date"] else ""
            lignes.append(
                '<div class="card">'
                f'<h3><a href="{html.escape(f["fichier"])}">{html.escape(f["titre"])}</a></h3>'
                + (f"<p>{resume}</p>" if resume else "")
                + (f'<span class="source">{html.escape(quand)}</span>' if quand else "")
                + "</div>"
            )
        blocs.append(
            f'<h2 class="anchor" id="{html.escape(domaine.lower())}">{html.escape(domaine)}'
            f' <span class="source">{len(groupes[domaine])}</span></h2>'
            '<div class="grid-3">' + "".join(lignes) + "</div>"
        )

    total = len(fiches)
    aujourdhui = date_lisible(date.today().isoformat())

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Technical Mentor — index des fiches</title>
<style>{styles}

  .grid-3 {{ gap: 1.2rem; }}
  .card h3 {{ margin-bottom: .4rem; font-size: 1.05rem; }}
  .card p {{ font-size: .88rem; margin-bottom: .6rem; }}
  h2 .source {{ vertical-align: middle; margin-left: .5rem; }}
  @media (max-width: 1000px) {{ .grid-3 {{ grid-template-columns: 1fr 1fr; }} }}
  @media (max-width: 700px) {{ .grid-3 {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<div class="container">
  <header class="hero">
    <span class="badge">Technical Mentor</span>
    <h1>Les fiches techniques</h1>
    <p>Une fiche par notion : le problème qu'elle résout, son mécanisme réel,
    sa mise en œuvre, ses compromis, et comment la défendre devant un expert.</p>
    <p class="source">{total} fiche{"s" if total > 1 else ""} · index reconstruit le {aujourdhui}</p>
  </header>
  {"".join(blocs) if blocs else "<p>Aucune fiche pour l'instant.</p>"}
  <footer class="footer">
    Index généré par <code>technical-mentor/scripts/indexer.py</code>.<br>
    Relancer le script après chaque nouvelle fiche.
  </footer>
</div>
</body>
</html>
"""


def main() -> int:
    # La console Windows est en cp1252 : sans ça, un accent ou une flèche
    # fait planter le script au moment de l'affichage.
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8", errors="replace")

    parseur = argparse.ArgumentParser(description="Reconstruit l'index des fiches.")
    parseur.add_argument("--dossier", default=str(DOSSIER_DEFAUT))
    parseur.add_argument(
        "--maj-charte",
        action="store_true",
        help="réinjecte CSS.css dans chaque fiche, entre les marques CHARTE",
    )
    args = parseur.parse_args()

    dossier = Path(args.dossier)
    if not dossier.is_dir():
        print(f"Dossier introuvable : {dossier}")
        return 1

    if args.maj_charte:
        faites, sans_marque = injecter_charte(dossier)
        print(f"Charte réinjectée dans {faites} fiche(s)"
              + (f", {sans_marque} ignorée(s)" if sans_marque else ""))

    fiches = lire_fiches(dossier)
    sortie = dossier / "index.html"
    sortie.write_text(construire(fiches, lire_styles(dossier)), encoding="utf-8")

    print(f"{len(fiches)} fiche(s) indexée(s) → {sortie}")
    for f in fiches:
        marque = "" if f["domaine"] != "Non classé" else "  (métadonnée mentor-domaine absente)"
        print(f"  · {f['domaine']:<16} {f['fichier']}{marque}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

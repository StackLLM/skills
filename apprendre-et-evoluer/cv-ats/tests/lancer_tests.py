#!/usr/bin/env python3
"""Tests de bout en bout de la skill cv-ats.

Pour chaque profil : source → détection du domaine → génération des 3 variantes
→ PDF → contrôle ATS → contrôle de mise en page → comparaison des variantes.

  python3 tests/lancer_tests.py            # tous les profils
  python3 tests/lancer_tests.py 3 5       # profils dont le nom commence par 3 ou 5

Les aperçus PNG à inspecter visuellement sont listés en fin de sortie.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ICI = Path(__file__).resolve().parent
CV = ICI.parent / "scripts" / "cv.py"
PROFILS = ICI / "profils"
RESULTATS = ICI / "resultats"

# profil : (domaine attendu, niveau attendu, pages attendues)
ATTENDUS = {
    "1-dev-fullstack": ("tech", "confirme", 1),
    "2-ingenieur-maintenance": ("ingenierie", "confirme", 1),
    "3-finance-senior": ("finance", "senior", 1),
    "4-marketing-uk": ("marketing", "confirme", 1),
    "5-junior-data": ("tech", "junior", 1),
    "6-senior-long": ("management", "senior", 2),
}


def lancer(*args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(CV), *args], capture_output=True, text=True, timeout=600)
    return r.returncode, r.stdout


def main() -> int:
    filtres = sys.argv[1:]
    echecs, apercus = [], []
    for nom, (domaine, niveau, pages) in ATTENDUS.items():
        if filtres and not any(nom.startswith(f) for f in filtres):
            continue
        problemes = []

        # 1. Détection depuis la source brute (Markdown) quand elle existe.
        md = PROFILS / f"{nom}.md"
        if md.exists() and "stress" not in md.read_text(encoding="utf-8"):
            _, sortie = lancer("detecter", str(md))
            detecte = json.loads(sortie)["domaine"]
            if detecte != domaine:
                problemes.append(f"source md détectée « {detecte} » au lieu de « {domaine} »")

        # 2. Génération complète.
        code, sortie = lancer("construire", str(PROFILS / f"{nom}.json"), "--sortie", str(RESULTATS / nom))
        if not sortie.strip():
            echecs.append(f"{nom} : aucune sortie (code {code})")
            continue
        res = json.loads(sortie)
        rapport = json.loads((RESULTATS / nom / "_controle" / "rapport.json").read_text(encoding="utf-8"))
        plan = rapport["plan"]

        if code != 0:
            problemes.append(f"erreurs bloquantes : {res['erreurs']}")
        if plan["domaine"] != domaine:
            problemes.append(f"domaine {plan['domaine']} ≠ {domaine}")
        if plan["niveau"] != niveau:
            problemes.append(f"niveau {plan['niveau']} ≠ {niveau}")
        if len(res["pdf"]) != 3:
            problemes.append(f"{len(res['pdf'])} PDF au lieu de 3")
        for theme, r in rapport["resultats"].items():
            a = r["ajustement"]
            if r["pages"] != pages:
                problemes.append(f"{theme} : {r['pages']} page(s) au lieu de {pages}")
            if a["debordement"] or a["debordements_horizontaux"]:
                problemes.append(f"{theme} : débordement")
            if r["taille_ko"] > 400:
                problemes.append(f"{theme} : PDF trop lourd ({r['taille_ko']} Ko)")
        # Les trois variantes : même texte, même mise en page (seule la couleur change).
        if not any("texte strictement identique" in ok for ok in rapport["ok"]):
            problemes.append("les variantes n'ont pas le même texte")
        mises_en_page = {json.dumps({k: v for k, v in r["ajustement"].items()}, sort_keys=True)
                         for r in rapport["resultats"].values()}
        if len(mises_en_page) > 1:
            problemes.append("les variantes n'ont pas la même mise en page")

        a = next(iter(rapport["resultats"].values()))["ajustement"]
        etat = "OK " if not problemes else "ÉCHEC"
        print(f"{etat} {nom:26} {plan['libelle_domaine']:26} {plan['niveau']:9} "
              f"{a['pages']} p. · texte {a['corps_texte_pt']} pt · air ×{a['air']} · "
              f"rempli {round((1 - a['part_vide']) * 100)} % · {len(rapport['avertissements'])} avert.")
        for p in problemes:
            print(f"     ↳ {p}")
        if problemes:
            echecs.append(nom)
        apercus += res["apercus"]

    print("\nAperçus à contrôler visuellement :")
    for p in apercus:
        print(f"  {p}")
    print(f"\n{'TOUS LES TESTS PASSENT' if not echecs else 'ÉCHECS : ' + ', '.join(echecs)}")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())

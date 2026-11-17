#!/usr/bin/env python3
"""cv-ats — génération de CV ATS en trois identités visuelles.

  python3 cv.py construire cv.json [--sortie DOSSIER] [--themes bleu,emeraude,bordeaux] [--garder-html]
  python3 cv.py detecter fichier.(md|json|txt)
  python3 cv.py photo entree.jpg sortie.jpg

« construire » : photo recadrée → HTML (gabarit V4) → PDF ajusté (WebKit) →
contrôles ATS et visuels → aperçus PNG → rapport. Code de sortie 1 si une
erreur bloquante est détectée.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

ICI = Path(__file__).resolve().parent
sys.path.insert(0, str(ICI))

from domaines import detecter_domaine, detecter_niveau, annees_experience, plan_pour, photo_autorisee, texte_du_cv  # noqa: E402
from rendu import ASSETS, THEMES, Rendu  # noqa: E402
from verifications import Rapport, verifier_donnees, verifier_pdf, verifier_variantes  # noqa: E402

BINAIRE = ICI / ".bin" / "cvtool"
SOURCE_SWIFT = ICI / "cvtool.swift"


def cvtool() -> Path:
    """Compile l'outil natif au premier usage (ou après modification de la source)."""
    if not BINAIRE.exists() or BINAIRE.stat().st_mtime < SOURCE_SWIFT.stat().st_mtime:
        if sys.platform != "darwin" or not shutil.which("swiftc"):
            sys.exit("cv-ats a besoin de macOS et de swiftc (Xcode Command Line Tools) pour générer les PDF.")
        BINAIRE.parent.mkdir(exist_ok=True)
        print("Compilation de cvtool (une seule fois)…", file=sys.stderr)
        subprocess.run(["swiftc", "-O", str(SOURCE_SWIFT), "-o", str(BINAIRE)], check=True,
                       stderr=subprocess.DEVNULL)
    return BINAIRE


def lancer(*args: str) -> str:
    res = subprocess.run([str(cvtool()), *args], capture_output=True, text=True, timeout=120)
    if res.returncode != 0:
        raise RuntimeError(f"cvtool {args[0]} : {res.stderr.strip()}")
    return res.stdout.strip().splitlines()[-1] if res.stdout.strip() else "{}"


def slug(nom: str) -> str:
    ascii_ = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode()
    return "-".join(m.capitalize() for m in re.findall(r"[A-Za-z0-9]+", ascii_)) or "CV"


def charger(chemin: Path) -> dict:
    cv = json.loads(chemin.read_text(encoding="utf-8"))
    cv.setdefault("identite", {})
    return cv


# ---------------------------------------------------------------------------
def construire(args) -> int:
    source = Path(args.cv).resolve()
    cv = charger(source)
    sortie = Path(args.sortie or source.parent / f"CV-{slug(cv['identite'].get('nom', 'CV'))}").resolve()
    controle = sortie / "_controle"
    travail = controle / "html"
    if controle.exists():
        shutil.rmtree(controle)
    travail.mkdir(parents=True)
    shutil.copytree(ASSETS / "fonts", travail / "fonts")

    r = Rapport()
    verifier_donnees(cv, r)
    plan = plan_pour(cv)
    r.valide(f"domaine : {plan['libelle_domaine']} ({plan['domaine']}), niveau : {plan['niveau']} "
             f"({plan['annees_experience']} an(s) hors stages)")

    # Photo : recadrage automatique sur le visage, si d'usage sur le marché visé.
    photo = None
    avec_photo, raison = photo_autorisee(cv)
    if avec_photo:
        chemin_photo = (source.parent / cv["photo"]).resolve()
        if not chemin_photo.exists():
            r.erreur(f"photo introuvable : {chemin_photo}")
        else:
            # 300 px pour un cadre de 28 mm ≈ 270 dpi à l'impression ; au-delà, WebKit
            # intègre l'image sans perte et le PDF grossit pour rien.
            infos = json.loads(lancer("photo", str(chemin_photo), str(travail / "photo.jpg"), "300"))
            photo = "photo.jpg"
            if not infos.get("visages"):
                r.avert("aucun visage détecté sur la photo : recadrage centré, à vérifier visuellement")
            if infos.get("contraste_ecart_type", 0) < 8:
                r.erreur("photo recadrée vide ou uniforme (noire/blanche) : vérifier le fichier source")
            if infos.get("cote_px", 0) < 250:
                r.avert(f"photo de faible résolution ({infos.get('cote_px')} px) : flou possible à l'impression")
    if "retirée" in raison:
        r.avert(raison)
    else:
        r.valide(raison)

    if r.erreurs:
        return terminer(sortie, controle, r, plan, {}, args)

    rendu = Rendu(cv, plan, photo)
    themes = [t.strip() for t in args.themes.split(",") if t.strip()]
    avant = (len(r.erreurs), len(r.avertissements), len(r.ok))

    # 1er essai avec la liaison des derniers mots (meilleure typographie). Si la
    # lecture ATS en souffre (ordre des lignes), on régénère sans : l'ATS prime.
    for liaison in (True, False):
        del r.erreurs[avant[0]:], r.avertissements[avant[1]:], r.ok[avant[2]:]
        textes, resultats = generer(cv, plan, rendu, themes, travail, controle, sortie, r, liaison, args)
        if liaison and any("illisibles par un ATS" in x or "ordre de lecture ATS" in x for x in r.erreurs):
            continue
        break
    if not liaison:
        r.avert("liaison des derniers mots désactivée : elle perturbait l'ordre de lecture ATS")

    if args.garder_html:
        shutil.copytree(travail, sortie / "source-html", dirs_exist_ok=True)
    return terminer(sortie, controle, r, plan, resultats, args)


def generer(cv, plan, rendu, themes, travail, controle, sortie, r, liaison, args):
    """Produit et contrôle les PDF des thèmes demandés."""
    nom = cv["identite"]["nom"]
    textes, resultats = {}, {}
    shutil.rmtree(controle / "apercus", ignore_errors=True)
    for cle in themes:
        theme = THEMES[cle]
        html_fichier = travail / f"cv-{cle}.html"
        html_fichier.write_text(rendu.page(theme, liaison), encoding="utf-8")
        pdf = sortie / f"CV-{slug(nom)}-{theme['nom']}.pdf"
        ajust = json.loads(lancer("render", str(html_fichier), str(pdf), f"CV — {nom}", nom))
        extrait = json.loads(lancer("texte", str(pdf)))
        textes[cle] = verifier_pdf(cv, plan, pdf, extrait, ajust, theme, r)
        apercus = [] if args.sans_apercus else json.loads(
            lancer("apercu", str(pdf), str(controle / "apercus"), "1400"))["apercus"]
        resultats[cle] = {"pdf": str(pdf), "ajustement": ajust, "pages": extrait["pages"],
                          "taille_ko": round(pdf.stat().st_size / 1024), "apercus": apercus}
    verifier_variantes(textes, r)
    return textes, resultats


def terminer(sortie: Path, controle: Path, r: Rapport, plan: dict, resultats: dict, args) -> int:
    shutil.rmtree(controle / "html", ignore_errors=True)
    rapport = {"plan": {k: v for k, v in plan.items() if k != "titres"}, "resultats": resultats, **r.dict()}
    (controle / "rapport.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")

    lignes = ["# Rapport de contrôle", "",
              f"Domaine : **{plan.get('libelle_domaine', '?')}** · niveau : **{plan.get('niveau', '?')}**", ""]
    for cle, res in resultats.items():
        a = res["ajustement"]
        lignes.append(f"- `{Path(res['pdf']).name}` — {res['pages']} page(s), {res['taille_ko']} Ko, "
                      f"texte {a.get('corps_texte_pt')} pt, espacement ×{a.get('air')}, "
                      f"marges {a.get('marges_px')}, sections déplacées {a.get('deplacees') or 'aucune'}")
    for titre, liste in (("Erreurs (bloquantes)", r.erreurs), ("Avertissements", r.avertissements), ("Validé", r.ok)):
        lignes += ["", f"## {titre}", ""] + ([f"- {x}" for x in liste] or ["- aucun"])
    (controle / "rapport.md").write_text("\n".join(lignes) + "\n", encoding="utf-8")

    print(json.dumps({"sortie": str(sortie), "pdf": [v["pdf"] for v in resultats.values()],
                      "apercus": [p for v in resultats.values() for p in v["apercus"]],
                      "rapport": str(controle / "rapport.md"),
                      "erreurs": r.erreurs, "avertissements": r.avertissements}, ensure_ascii=False, indent=2))
    return 1 if r.erreurs else 0


def detecter(args) -> int:
    chemin = Path(args.fichier)
    brut = chemin.read_text(encoding="utf-8")
    if chemin.suffix == ".json":
        cv = json.loads(brut)
        texte, titre = texte_du_cv(cv), cv.get("identite", {}).get("titre", "")
        niveau, annees = detecter_niveau(cv), annees_experience(cv)
    else:
        # Source libre : les premières lignes portent en général le nom et le poste visé.
        texte, titre = brut, "\n".join(brut.strip().splitlines()[:3])
        niveau, annees = None, None
    res = detecter_domaine(texte, titre)
    res.update({"niveau": niveau, "annees_experience": annees})
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


def photo(args) -> int:
    print(lancer("photo", args.entree, args.sortie, str(args.cote)))
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="cv-ats : CV ATS premium en trois couleurs")
    sp = p.add_subparsers(dest="commande", required=True)

    c = sp.add_parser("construire", help="génère les PDF à partir du JSON")
    c.add_argument("cv")
    c.add_argument("--sortie")
    c.add_argument("--themes", default="bleu,emeraude,bordeaux")
    c.add_argument("--garder-html", action="store_true", help="conserver le HTML source (modifications manuelles)")
    c.add_argument("--sans-apercus", action="store_true")
    c.set_defaults(f=construire)

    d = sp.add_parser("detecter", help="suggère domaine et niveau")
    d.add_argument("fichier")
    d.set_defaults(f=detecter)

    ph = sp.add_parser("photo", help="recadre une photo sur le visage")
    ph.add_argument("entree")
    ph.add_argument("sortie")
    ph.add_argument("--cote", type=int, default=480)
    ph.set_defaults(f=photo)

    args = p.parse_args()
    return args.f(args)


if __name__ == "__main__":
    sys.exit(main())

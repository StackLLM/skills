#!/usr/bin/env python3
"""
carte-des-skills.py — la carte du dossier SKILLS, au rendu de map-projet.

    python3 outils/carte-des-skills.py                 # CARTE-DES-SKILLS.html à la racine
    python3 outils/carte-des-skills.py --colonnes 2    # cartes plus larges

Les données sont dans outils/skills.json. Quand une skill arrive, part ou change
de place : modifier sa ligne là, puis relancer.

La représentation est celle de map-projet : bandeau, frise, compteurs, matrice,
légende, puis une carte par volet. Les cinq phases deviennent ici la maturité de
chaque skill (A, B+, B, sans note). Une skill marquée "plugin": false n'est que
sur ce poste.

Tout se calcule depuis le fichier. Le script vérifie aussi que chaque dossier
existe et que son SKILL.md déclare bien le nom attendu ; les versions viennent
du marketplace du dépôt ~/stackllm/skills quand il est là : un plugin par volet,
et une skill s'appelle <volet>:<skill>.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
MAP_PROJET = RACINE / "piloter-les-projets" / "map-projet" / "scripts"
MARKETPLACE = Path.home() / "stackllm" / "skills" / ".claude-plugin" / "marketplace.json"

sys.path.insert(0, str(MAP_PROJET))
try:
    from generer_maps import CSS  # le style de map-projet, sans copie
except ImportError:
    sys.exit(f"Introuvable : {MAP_PROJET / 'generer_maps.py'} (le style vient de map-projet)")

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
        "septembre", "octobre", "novembre", "décembre"]

# Ce que la carte ajoute au style de map-projet : le chemin du dossier, et une
# skill sur deux lignes (son nom derrière la case, puis ce à quoi elle sert).
CSS_CARTE = """
.titre .sous.chemin, .ligne .chemin { font-family: ui-monospace, Menlo,
  Consolas, monospace; font-size: 12.5px; color: var(--pale); }
.ligne .chemin { display: block; margin-top: 2px; }
.titres li { display: block; padding: 6px 0 7px; }
.titres .haut { display: flex; align-items: flex-start; gap: 10px; }
.titres .haut i { flex: none; box-sizing: border-box; width: 14px; height: 14px;
  margin-top: 2px; border: 1px solid var(--pale); border-radius: 4px;
  position: relative; }
.titres li.partagee .haut i { background: var(--doux); border-color: var(--doux); }
.titres li.partagee .haut i::after { content: ""; position: absolute; left: 4.5px;
  top: 1.8px; width: 3.2px; height: 6.6px; border: solid var(--carte);
  border-width: 0 1.7px 1.7px 0; transform: rotate(45deg); }
.titres .nom { font-family: ui-monospace, Menlo, Consolas, monospace;
  font-size: 13px; font-weight: 650; line-height: 1.32; flex: 1; min-width: 0;
  overflow-wrap: anywhere; }
.titres .sert-a { color: var(--doux); font-size: 13.2px; line-height: 1.42;
  margin: 3px 0 0 24px; }
.titres .appel { font-family: ui-monospace, Menlo, Consolas, monospace;
  font-size: 11.5px; color: var(--pale); margin: 3px 0 0 24px;
  overflow-wrap: anywhere; }
.titres li:not(.partagee) .nom { color: var(--doux); }
.mini-noms span { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.case.poste { background: var(--gris-fond); color: var(--gris-texte);
  box-shadow: inset 0 0 0 1px var(--bord); }
.page { max-width: 1400px; }
"""


def e(texte) -> str:
    return html.escape(str(texte), quote=True)


def pluriel(n: int, mot: str) -> str:
    return f"{n} {mot}{'s' if n > 1 else ''}"


def date_fr(jour: dt.date) -> str:
    return f"{jour.day} {MOIS[jour.month - 1]} {jour.year}"


def versions() -> dict[str, str]:
    if not MARKETPLACE.exists():
        return {}
    return {p["name"]: p.get("version", "") for p in
            json.loads(MARKETPLACE.read_text("utf-8"))["plugins"]}


def verifier(donnees: dict) -> list[str]:
    """Chaque dossier existe, et son SKILL.md déclare le nom de la carte."""
    erreurs = []
    colonnes = {c["id"] for c in donnees["colonnes"]}
    for volet in donnees["volets"]:
        for s in volet["skills"]:
            if s["maturite"] not in colonnes:
                erreurs.append(f"{s['nom']} : maturité inconnue « {s['maturite']} »")
            skill_md = RACINE / s["dossier"] / "SKILL.md"
            if not skill_md.exists():
                erreurs.append(f"{s['nom']} : {s['dossier']}SKILL.md introuvable")
                continue
            nom = re.search(r"^name:\s*(.+)$", skill_md.read_text("utf-8"), re.M)
            if not nom or nom.group(1).strip() != s["nom"]:
                erreurs.append(f"{s['nom']} : le SKILL.md déclare « {nom.group(1).strip() if nom else '?'} »")
    return erreurs


def rendre(donnees: dict, colonnes: int) -> str:
    lieux = donnees["colonnes"]
    volets = donnees["volets"]
    plugin = donnees["plugin"]
    vers = versions()
    toutes = [s for v in volets for s in v["skills"]]
    poste = [s for s in toutes if s.get("plugin") is False]
    partagees = len(toutes) - len(poste)
    par_lieu = {l["id"]: sum(s["maturite"] == l["id"] for s in toutes) for l in lieux}
    fourni = max(volets, key=lambda v: len(v["skills"]))

    tete = (f'<header class="entete"><div><h1>{e(donnees["nom"])}</h1>'
            f'<div class="soustitre">{e(donnees["sous_titre"])}</div></div>'
            f'<div class="date">État au {date_fr(dt.date.today())}</div></header>')

    etiquette = (f'<span class="tag bleu">{pluriel(len(poste), "skill")} sur ce poste</span>'
                 if poste else '<span class="tag vert">Tout dans le plugin</span>')
    bandeau = (f'<section class="verdict"><div class="verdict-haut">'
               f'<span class="verdict-mot">Le dossier</span>{etiquette}'
               f'<span class="tag gris">{pluriel(len(volets), "volet")}</span></div>'
               f'<div class="verdict-phrase">{len(toutes)} skills vivantes, rangées en '
               f'{len(volets)} volets. Un volet = un besoin.</div>'
               f'<div class="action"><b>Le plus fourni :</b> {e(fourni["nom"])}, '
               f'{pluriel(len(fourni["skills"]), "skill")}.</div>'
               f'<div class="hors"><b>Hors carte :</b> {e(donnees["hors_carte"])}</div></section>')

    frise = (f'<section class="frise" style="grid-template-columns:repeat({len(lieux)},1fr)">'
             + "".join(f'<div class="etape passee" title="{e(l.get("aide", ""))}">'
                       f'{e(l["nom"])}<small>{pluriel(par_lieu[l["id"]], "skill")}</small></div>'
                       for l in lieux) + '</section>')

    pct = round(100 * partagees / len(toutes)) if toutes else 0
    chiffres = (f'<section class="chiffres">'
                f'<div class="chiffre"><b>{len(toutes)}</b><span>skills vivantes</span></div>'
                f'<div class="chiffre"><b>{len(volets)}</b><span>volets</span></div>'
                f'<div class="chiffre"><b>{partagees} / {len(toutes)}</b><span>dans le plugin ({pct} %)</span></div>'
                f'<div class="chiffre"><b>{len(poste)}</b><span>sur ce poste seulement</span></div></section>')

    lignes = []
    for v in volets:
        cases = []
        for l in lieux:
            n = sum(s["maturite"] == l["id"] for s in v["skills"])
            classe = "vide" if not n else "fait"
            cases.append(f'<td class="case {classe}">{n or "—"}</td>')
        chemin = v.get("dossier") or " · ".join(s["dossier"] for s in v["skills"])
        lignes.append(f'<tr><td class="ligne"><b>{e(v["nom"])}</b>'
                      f'<span class="chemin">{e(chemin)}</span></td>{"".join(cases)}</tr>')
    matrice = (f'<div class="defile"><table class="matrice"><colgroup><col class="tete">'
               + "<col>" * len(lieux) + '</colgroup><thead><tr><th></th>'
               + "".join(f'<th>{e(l["nom"])}</th>' for l in lieux)
               + f'</tr></thead><tbody>{"".join(lignes)}</tbody></table></div>')

    legende = ('<div class="legende">'
               + "".join(f'<span><b>{e(l["court"])}</b>&nbsp; {e(l["aide"])}</span>' for l in lieux)
               + '<span>—&nbsp;&nbsp;dans une case : aucune skill de ce niveau</span></div>')

    cartes = []
    for v in sorted(volets, key=lambda v: -len(v["skills"])):
        n = len(v["skills"])
        p = sum(s.get("plugin") is not False for s in v["skills"])
        etat = ('<span class="tag vert">Partagé</span>' if p == n else
                '<span class="tag bleu">En partie</span>' if p else
                '<span class="tag gris">Sur ce poste</span>')
        chemin = v.get("dossier") or "à la racine"
        mini = "".join(
            f'<i class="{"fait" if any(s["maturite"] == l["id"] for s in v["skills"]) else ""}"></i>'
            for l in lieux)
        items = []
        for s in v["skills"]:
            dans = s.get("plugin") is not False
            appel = ""
            if dans:
                maturite = f" · maturité {s['maturite']}" if s.get("maturite", "—") != "—" else ""
                volet_id = v["dossier"].strip("/")
                version = vers.get(volet_id, "")
                appel = (f'<div class="appel">{e(volet_id)}:{e(s["nom"])}'
                         f'{e(maturite)}{" · plugin " + e(volet_id) + " " + e(version) if version else ""}</div>')
            items.append(f'<li class="{"partagee" if dans else ""}"><div class="haut"><i></i>'
                         f'<span class="nom">{e(s["nom"])}</span></div>'
                         f'<div class="sert-a">{e(s["sert_a"])}</div>{appel}</li>')
        cartes.append((
            f'<article class="bloc"><div class="titre">'
            f'<div class="case-cocher {"pleine" if p == n else ""}"></div>'
            f'<h2>{e(v["nom"])}<span class="sous chemin">{e(chemin)}</span></h2></div>'
            f'<div class="tags">{etat}<span class="tag gris">{pluriel(n, "skill")}</span></div>'
            f'<p class="resume">{e(v["resume"])}</p>'
            f'<div class="barre"><i style="width:{round(100 * p / n)}%"></i></div>'
            f'<div class="mesure"><span><b>{p} / {n}</b> dans le plugin</span>'
            f'<span><b>{round(100 * p / n)} %</b></span></div>'
            f'<div class="mini" style="grid-template-columns:repeat({len(lieux)},1fr)">{mini}</div>'
            f'<div class="mini-noms" style="grid-template-columns:repeat({len(lieux)},1fr)">'
            + "".join(f'<span title="{e(l["nom"])}">{e(l.get("court", l["nom"]))}</span>' for l in lieux) + '</div>'
            f'<div class="paquet"><div class="paquet-tete"><span>Les skills</span><span>{n}</span></div>'
            f'<ul class="titres">{"".join(items)}</ul></div></article>', n))

    # Chaque carte dans la colonne la plus courte, dans l'ordre : comme map-projet.
    cols: list[list[str]] = [[] for _ in range(colonnes)]
    hauteurs = [0] * colonnes
    for contenu, poids in cartes:
        i = hauteurs.index(min(hauteurs))
        cols[i].append(contenu)
        hauteurs[i] += poids + 3
    corps_cartes = ('<section class="colonnes">'
                    + "".join(f'<div class="colonne">{"".join(c)}</div>' for c in cols)
                    + '</section>')

    corps = tete + bandeau + frise + chiffres + matrice + legende + corps_cartes
    return (f'<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{e(donnees["nom"])} — la carte des skills</title>'
            f'<style>{CSS}{CSS_CARTE}</style></head>'
            f'<body><main class="page">{corps}</main></body></html>')


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parseur.add_argument("--colonnes", type=int, choices=(1, 2, 3, 4), default=3)
    parseur.add_argument("-o", "--sortie", type=Path, default=RACINE / "CARTE-DES-SKILLS.html")
    options = parseur.parse_args()

    donnees = json.loads((RACINE / "outils" / "skills.json").read_text("utf-8"))
    erreurs = verifier(donnees)
    if erreurs:
        print("skills.json ne correspond pas au dossier :", file=sys.stderr)
        for erreur in erreurs:
            print(f"  - {erreur}", file=sys.stderr)
        return 1
    options.sortie.write_text(rendre(donnees, options.colonnes), encoding="utf-8")
    print(options.sortie)
    return 0


if __name__ == "__main__":
    sys.exit(main())

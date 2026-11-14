#!/usr/bin/env python3
"""
generer_widget.py — transforme un carte.json en deux maps à afficher DANS la réponse.

    python generer_widget.py carte.json --verifier   # contrôle, sans rien écrire
    python generer_widget.py carte.json              # écrit les deux fragments
    python generer_widget.py carte.json -o dossier/  # ailleurs

Sortie : deux fragments HTML, à passer tels quels à l'outil d'affichage de la
conversation (`show_widget`). Ce ne sont pas des pages : pas de doctype, pas de
<html>, pas de fond. Le chat fournit le cadre, le fond et le mode sombre.

Un seul fichier : map.widget.html. Une seule map, qu'on affiche. Deux images
dans une réponse, on en regarde une — et celle-ci porte déjà les lots.

Deux contraintes viennent du chat, et expliquent tout le reste :

1. La largeur est de 680 px. Une seule colonne de cartes, jamais trois.
2. Les couleurs sont celles de l'interface, en variables CSS. Aucune couleur
   écrite en dur : sinon la map devient illisible en mode sombre.

Les calculs — phase, verdict, couleurs, avancement — sont dans moteur.py, le
même que la skill `map-projet`. Une carte valide ici l'est là-bas.

Aucune dépendance Python, et aucun navigateur : il n'y a pas d'image à produire.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from moteur import (  # noqa: E402
    COULEUR_VERDICT, LOTS_CONSEILLES, LOTS_EN_TITRES, NOM_COURT, ORDRE_VERDICT,
    PHASES, STATUTS, CarteInvalide, cases, charger, cle_elements, compte,
    date_fr, e, jours_sans_activite, phase_projet, pluriel, position, totaux,
    trier, verdict_element, verifier, JOURS_ARRET,
)

# Les familles de couleur du moteur deviennent des classes, ecrites une seule
# fois. Repeter le style en ligne sur chaque case et chaque point gonflait le
# fragment d'un tiers, pour rien.
#
# Aucune couleur n'est ecrite en dur : ce sont les jetons de l'interface du
# chat, qui basculent seuls entre le mode clair et le mode sombre.
TEINTES = """
.mp .f-vert{background:var(--bg-success);color:var(--text-success);border-color:var(--border-success)}
.mp .f-bleu{background:var(--bg-accent);color:var(--text-accent);border-color:var(--border-accent)}
.mp .f-rouge{background:var(--bg-danger);color:var(--text-danger);border-color:var(--border-danger)}
.mp .f-gris{background:var(--surface-1);color:var(--text-muted)}
.mp .f-pointille{color:var(--text-secondary);border-color:var(--border-strong)}
"""

# Tout est serré d'un cran par rapport à la version en fichiers : la map doit
# tenir dans la conversation sans qu'on la fasse défiler dix fois. On la lit
# de loin, et on l'agrandit pour lire une ligne.
CSS = TEINTES + """
.mp{font-size:13px;line-height:1.4;color:var(--text-primary);padding:.5rem 0}
.mp .sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0)}
.mp h1{font-size:19px;font-weight:500;margin:0}
.mp h2{font-size:14.5px;font-weight:500;margin:0}
.mp .doux{color:var(--text-secondary)}
.mp .pale{color:var(--text-muted)}
.mp .tete{display:flex;justify-content:space-between;align-items:baseline;gap:12px;margin-bottom:10px}
.mp .bloc{background:var(--surface-2);border:0.5px solid var(--border);border-radius:11px;padding:.7rem .85rem}
.mp .verdict{margin-bottom:10px}
.mp .mot{font-size:11px;color:var(--text-muted)}
.mp .phrase{font-size:14.5px;font-weight:500;margin:6px 0 0}
.mp .etiq{display:flex;gap:6px;flex-wrap:wrap;align-items:center}
.mp .tag{font-size:11px;border-radius:var(--radius);padding:2px 7px;border:0.5px solid}
.mp .frise{display:grid;grid-template-columns:repeat(5,1fr);gap:5px;margin-bottom:10px}
.mp .etape{border-radius:var(--radius);padding:6px 3px;text-align:center;font-size:11px;border:0.5px solid transparent}
.mp .etape b{display:block;font-weight:500;font-size:12px}
.mp .ici{border-color:var(--border-accent)}
.mp .nombres{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin-bottom:13px}
.mp .nombre{background:var(--surface-1);border-radius:var(--radius);padding:9px 10px}
.mp .nombre b{display:block;font-size:18px;font-weight:500;line-height:1.2}
.mp .nombre span{font-size:11px;color:var(--text-secondary)}
.mp table{width:100%;border-collapse:separate;border-spacing:5px 5px;table-layout:fixed}
.mp th{font-weight:400;font-size:11px;color:var(--text-secondary);padding:0}
.mp td.nom{width:150px;font-size:12px;padding-right:12px;line-height:1.3}
.mp td.nom b{display:block;font-weight:500}
.mp td.nom span{display:block;margin-top:1px}
.mp .case{height:30px;border-radius:var(--radius);text-align:center;font-size:11px;border:0.5px solid transparent;overflow:hidden}
.mp .legende{display:flex;gap:13px;flex-wrap:wrap;font-size:11px;color:var(--text-secondary)}
.mp .barre{display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;margin:8px 0 13px}
.mp .reglage{display:flex;align-items:center;gap:5px;font-size:11px;color:var(--text-muted);white-space:nowrap}
.mp .reglage button{font-size:11px;padding:1px 8px;min-height:0;line-height:1.5;border-radius:var(--radius)}
.mp .reglage button.actif{background:var(--bg-accent);color:var(--text-accent);border-color:var(--border-accent)}
.mp .legende i{display:inline-block;width:10px;height:10px;border-radius:3px;margin-right:6px;vertical-align:-1px;border:0.5px solid transparent}
.mp .cartes{column-count:3;column-gap:10px}
.mp .cartes.c1{column-count:1}
.mp .cartes.c2{column-count:2;column-gap:12px}
.mp .cartes.c3{column-count:3;column-gap:10px}
.mp .carte{break-inside:avoid;margin-bottom:10px}
.mp .resume{margin:7px 0 0;color:var(--text-secondary);font-size:12.5px}
.mp .piste{height:6px;background:var(--surface-1);border-radius:3px;overflow:hidden;margin-top:9px}
.mp .piste i{display:block;height:100%;background:var(--text-success)}
.mp .mesure{display:flex;justify-content:space-between;font-size:11px;color:var(--text-secondary);margin-top:4px}
.mp .mesure b{color:var(--text-primary);font-weight:500}
.mp .paquet{margin-top:12px}
.mp .paquet+.paquet{margin-top:14px}
.mp .paquet-tete{display:flex;justify-content:space-between;align-items:center;font-size:11px;color:var(--text-muted);padding-bottom:5px;border-bottom:0.5px solid var(--border)}
.mp .paquet-tete span{font-variant-numeric:tabular-nums}
.mp ul{list-style:none;margin:5px 0 0;padding:0}
.mp li{display:flex;align-items:flex-start;gap:9px;font-size:12.5px;padding:3px 0}
.mp li i{flex:none;box-sizing:border-box;width:13px;height:13px;margin-top:2px;border:1px solid var(--border-strong);border-radius:4px;position:relative}
.mp li.fait{color:var(--text-muted)}
.mp li.fait i{background:var(--text-secondary);border-color:var(--text-secondary)}
.mp li.fait i::after{content:"";position:absolute;left:4.2px;top:1.6px;width:3px;height:6.2px;border:solid var(--surface-2);border-width:0 1.6px 1.6px 0;transform:rotate(45deg)}
.mp li.encours i::after{content:"";position:absolute;left:2px;top:4.5px;width:7px;height:2px;border-radius:1px;background:var(--text-secondary)}
.mp li.aconfirmer{color:var(--text-muted)}
.mp li.aconfirmer i{border-style:dashed}
.mp li.autres{color:var(--text-muted);padding-left:22px}
.mp .rien{color:var(--text-secondary);font-size:12px;margin-top:8px}
"""


def etiquette(verdict: str, texte: str | None = None) -> str:
    return (f'<span class="tag f-{COULEUR_VERDICT[verdict]}">'
            f'{e(texte or verdict)}</span>')


# --------------------------------------------------------------------- en-tête

def entete(carte: dict, sous_titre: str) -> str:
    return (f'<div class="tete"><div><h1>{e(carte["nom"])}</h1>'
            f'<div class="doux">{e(sous_titre)}</div></div>'
            f'<div class="pale">État au {date_fr(carte["date"])}</div></div>')


def bandeau(carte: dict, verdict: str, mesure: str, texte: str) -> str:
    hors = (f'<div class="doux" style="margin-top:6px">Hors map : '
            f'{e(carte["hors_carte"])}</div>') if carte.get("hors_carte") else ""
    return (f'<div class="bloc verdict"><div class="etiq">'
            f'<span class="mot">Verdict</span>{etiquette(verdict, texte)}'
            f'<span class="tag f-gris">{e(mesure)}</span></div>'
            f'<p class="phrase">{e(carte["verdict"])}</p>'
            f'<div class="doux" style="margin-top:6px">Prochaine étape : '
            f'{e(carte["prochaine_action"])}</div>{hors}</div>')


def frise(elements: list[dict], rang: int | None) -> str:
    """Les cinq phases, avec le nombre de lots faits dans chacune."""
    etapes = []
    for i, phase in enumerate(PHASES):
        lots = [l for el in elements for l in (el.get("lots") or [])
                if l["phase"] == phase]
        faits = sum(l["statut"] == "fait" for l in lots)
        if not lots or not faits:
            famille = "gris"      # rien n'a commencé : la case reste neutre
        elif faits == len(lots):
            famille = "vert"
        else:
            famille = "bleu"
        ici = " ici" if rang is not None and i == rang else ""
        compte_txt = (f'{faits} / {len(lots)} lot{"s" if len(lots) > 1 else ""}'
                      if lots else "aucun lot")
        etapes.append(f'<div class="etape f-{famille}{ici}">'
                      f'<b>{e(NOM_COURT.get(phase, phase))}</b>{e(compte_txt)}</div>')
    return f'<div class="frise">{"".join(etapes)}</div>'


def nombres(t: dict, nom_elements: str) -> str:
    pourcent = round(100 * t["faits"] / t["total"]) if t["total"] else 0
    tuiles = [
        (t["elements"], nom_elements),
        (f'{t["faits"]} / {t["total"]}', f'lots faits ({pourcent} %)'),
        (t["bloquants"], pluriel(t["bloquants"], "bloquant")),
        (t["a_trancher"], f'{pluriel(t["a_trancher"], "décision")} à trancher'),
    ]
    corps = "".join(f'<div class="nombre"><b>{e(v)}</b><span>{e(l)}</span></div>'
                    for v, l in tuiles)
    return f'<div class="nombres">{corps}</div>'


# ---------------------------------------------------------------- la matrice

ETAT_FAMILLE = {"fait": "vert", "ouvert": "bleu", "bloque": "rouge",
                "confirmer": "pointille", "avenir": "gris", "vide": "gris"}


def matrice(elements: list[dict]) -> str:
    entetes = "".join(f'<th>{e(NOM_COURT.get(p, p))}</th>' for p in PHASES)
    lignes = []
    for el in elements:
        cellules = ""
        for phase in PHASES:
            c = cases(el)[phase]
            famille = ETAT_FAMILLE[c["etat"]]
            cellules += (f'<td class="case f-{famille}">'
                         f'{e(c["texte"])}</td>')
        sous = (f'<span class="doux">{e(el["sous_titre"])}</span>'
                if el.get("sous_titre") else "")
        lignes.append(f'<tr><td class="nom"><b>{e(el["nom"])}</b>{sous}</td>'
                      f'{cellules}</tr>')
    return (f'<table><colgroup><col style="width:150px"><col><col><col><col><col>'
            f'</colgroup><thead><tr><th></th>{entetes}</tr></thead>'
            f'<tbody>{"".join(lignes)}</tbody></table>')


# Le lecteur règle la largeur des cartes lui-même : trois colonnes pour voir
# tout d'un coup, une seule pour lire une ligne sans la couper. Le bouton ne
# fait que changer une classe, donc rien n'est reconstruit et rien ne bouge.
REGLAGE = (
    '<div class="reglage"><span>Colonnes</span>'
    '<button type="button" data-c="1" aria-label="Afficher sur une colonne">1</button>'
    '<button type="button" data-c="2" aria-label="Afficher sur deux colonnes">2</button>'
    '<button type="button" data-c="3" class="actif" '
    'aria-label="Afficher sur trois colonnes">3</button></div>'
)

SCRIPT = (
    '<script>(function(){'
    'var g=document.querySelector(".mp .cartes"),'
    'b=document.querySelectorAll(".mp .reglage button");'
    'b.forEach(function(x){x.addEventListener("click",function(){'
    'g.className="cartes c"+x.dataset.c;'
    'b.forEach(function(y){y.classList.remove("actif")});'
    'x.classList.add("actif");});});})();</script>'
)


def legende() -> str:
    paires = [("vert", "Terminé"), ("bleu", "En cours ou à trancher"),
              ("rouge", "Bloquant"), ("pointille", "À confirmer"),
              ("gris", "À venir")]
    corps = "".join(f'<span><i class="f-{f}"></i>{e(mot)}</span>'
                    for f, mot in paires)
    return (f'<div class="barre"><div class="legende">{corps}</div>'
            f'{REGLAGE}</div>')


# ------------------------------------------------------------------ les cartes

def titre_carte(el: dict, date_carte: str) -> str:
    verdict = verdict_element(el, date_carte)
    sous = (f'<div class="doux" style="font-size:12px">{e(el["sous_titre"])}</div>'
            if el.get("sous_titre") else "")
    tags = etiquette(verdict) + (f'<span class="tag f-gris">'
                                 f'{e(PHASES[position(el)])}</span>')
    jours = jours_sans_activite(el, date_carte)
    if jours is not None and jours > JOURS_ARRET and verdict != "Terminé":
        tags += (f'<span class="tag f-gris">'
                 f'{jours} j sans commit</span>')
    return (f'<h2>{e(el["nom"])}</h2>{sous}'
            f'<div class="etiq" style="margin-top:7px">{tags}</div>')


def avancement(el: dict) -> str:
    c = compte(el)
    if not c["total"]:
        return ('<p class="rien">Aucun lot écrit dans ce projet. '
                'Phase estimée, à confirmer.</p>')
    return (f'<div class="piste"><i style="width:{c["pourcent"]}%"></i></div>'
            f'<div class="mesure"><span><b>{c["faits"]} / {c["total"]}</b> lots '
            f'faits</span><span><b>{c["pourcent"]} %</b></span></div>')


# Dans la carte, un lot ne porte pas son statut : il est fait, ou il ne l'est
# pas. Une case à cocher le dit sans couleur. Cinq couleurs sur quarante lignes
# fatiguaient l'œil pour une information qui tient en une coche.
#
# Trois cases seulement. Le reste du statut vit sur la map par lot.
CASE = {
    "fait": "fait",               # cochée
    "en_cours": "encours",        # un trait : commencé, pas fini
    "a_confirmer": "aconfirmer",  # bord en pointillés : on ne sait pas
}

# Dans « Reste », ce qui bouge passe devant, ce qui est flou ferme la marche.
# À statut égal, l'ordre des phases, qui est l'ordre du travail.
ORDRE_RESTE = ("en_cours", "bloquant", "a_trancher", "a_fournir", "a_faire",
               "a_venir", "a_confirmer")


def ligne_titre(lot: dict) -> str:
    """Une case, un titre. Le statut exact et la preuve restent au survol."""
    etat = CASE.get(lot["statut"])
    classe = f' class="{etat}"' if etat else ""
    # Tout ce qui ne tient pas sur la ligne part au survol : le statut en
    # toutes lettres, la précision, et la preuve.
    bulle = " — ".join(x for x in (STATUTS[lot["statut"]][0], lot.get("detail"),
                                   lot.get("source")) if x)
    return f'<li{classe} title="{e(bulle)}"><i></i>{e(lot["titre"])}</li>'


def paquet(titre: str, lots: list[dict], autres: int = 0) -> str:
    if not lots:
        return ""
    corps = "".join(ligne_titre(l) for l in lots)
    if autres:
        corps += f'<li class="autres">+ {autres} autres</li>'
    return (f'<div class="paquet"><div class="paquet-tete">{e(titre)}'
            f'<span>{len(lots) + autres}</span></div><ul>{corps}</ul></div>')


def lots_titres(el: dict, maximum: int | None = None) -> str:
    """Les lots du volet, rangés en deux paquets : ce qui est clôturé, puis
    ce qui reste.

    Mélangés, deux cochés entre trois vides, la liste ne dit plus rien : ni
    où on en est, ni ce qui attend. Séparés, les deux se lisent d'un coup.

    `maximum` sert aux cartes d'une map d'orga, où la place manque : on n'y
    montre que ce qui reste, coupé. Le compte des lots faits est déjà sur la
    ligne d'avancement, juste au-dessus."""
    lots = el.get("lots") or []
    if not lots:
        return ""
    faits = sorted((l for l in lots if l["statut"] == "fait"),
                   key=lambda l: PHASES.index(l["phase"]))
    reste = sorted((l for l in lots if l["statut"] != "fait"),
                   key=lambda l: (ORDRE_RESTE.index(l["statut"]),
                                  PHASES.index(l["phase"])))
    if maximum is None:
        return paquet("Fait", faits) + paquet("Reste", reste)
    coupe = reste[:maximum]
    return paquet("Reste", coupe, len(reste) - len(coupe))


def carte_volet(el: dict, date_carte: str, maximum: int | None = None) -> str:
    return (f'<div class="bloc carte">{titre_carte(el, date_carte)}'
            f'<p class="resume">{e(el["resume"])}</p>'
            f'{avancement(el)}{lots_titres(el, maximum)}</div>')


# ------------------------------------------------------------------ la page

def colonnes(cartes) -> str:
    """Les cartes sur deux colonnes, équilibrées par le navigateur.

    `column-count` coupe le flux en deux hauteurs égales tout seul, et
    `break-inside:avoid` empêche une carte d'être coupée en deux. Sur une
    seule colonne, 680 px de large donnaient une image deux fois trop haute :
    on passait son temps à la faire défiler au lieu de la lire."""
    return f'<div class="cartes">{"".join(cartes)}</div>'


def verdict_global(carte: dict, elements: list[dict]) -> str:
    verdicts = {verdict_element(el, carte["date"]) for el in elements}
    return next(mot for mot in ORDRE_VERDICT if mot in verdicts)


def texte_verdict(carte: dict, elements: list[dict], global_: str, nom: str) -> str:
    nombre = sum(verdict_element(el, carte["date"]) == global_ for el in elements)
    return f"{global_} : {nombre} {nom}{'s' if nombre > 1 else ''} sur {len(elements)}"


def envelopper(resume: str, corps: str) -> str:
    """Le fragment prêt pour la conversation. Pas de page, pas de fond."""
    return (f'<style>{CSS}</style><div class="mp">'
            f'<h2 class="sr">{e(resume)}</h2>{corps}</div>{SCRIPT}')


def rendu_projet(carte: dict) -> dict[str, str]:
    """Une seule map, et c'est volontaire.

    Deux images dans une réponse, on en regarde une. Celle-ci porte déjà les
    lots, rangés en cases à cocher : le détail de chaque lot n'a plus besoin
    d'une image à lui, il tient dans l'infobulle. La map par lot reste dans la
    skill `map-projet`, qui livre des fichiers qu'on garde."""
    volets = trier(carte)
    date_carte = carte["date"]
    rang = phase_projet(volets)
    tete = (entete(carte, carte.get("sous_titre") or "Map du projet")
            + bandeau(carte, verdict_global(carte, volets),
                      f"Phase : {PHASES[rang]}",
                      texte_verdict(carte, volets,
                                    verdict_global(carte, volets), "volet"))
            + frise(volets, rang))
    t = totaux(volets)
    resume = (f'Map du projet {carte["nom"]} : {len(volets)} volets, '
              f'{t["faits"]} lots faits sur {t["total"]}, phase {PHASES[rang]}.')
    corps = (tete + nombres(t, "volets") + matrice(volets) + legende()
             + colonnes(carte_volet(v, date_carte) for v in volets))
    return {"map": envelopper(resume + " Une carte par volet, avec ses lots "
                              "en cases à cocher.", corps)}


def rendu_orga(carte: dict) -> dict[str, str]:
    projets = trier(carte)
    date_carte = carte["date"]
    couverture = f"{len(projets)} projets"
    if carte.get("depots_total"):
        couverture += f" sur {carte['depots_total']} dépôts"
    global_ = verdict_global(carte, projets)
    tete = (entete(carte, carte.get("sous_titre") or "Map de l'organisation")
            + bandeau(carte, global_, couverture,
                      texte_verdict(carte, projets, global_, "projet"))
            + frise(projets, None))
    t = totaux(projets)
    resume = (f'Map de {carte["nom"]} : {len(projets)} projets, '
              f'{t["faits"]} lots faits sur {t["total"]}.')
    corps = (tete + nombres(t, "projets") + matrice(projets) + legende()
             + colonnes(carte_volet(p, date_carte, LOTS_EN_TITRES)
                        for p in projets))
    return {"map": envelopper(resume + " Une carte par projet, avec ce qui "
                              "reste en cases à cocher.", corps)}


# ------------------------------------------------------------------- entrée

def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("carte", type=Path)
    p.add_argument("-o", "--sortie", type=Path)
    p.add_argument("--verifier", action="store_true")
    options = p.parse_args()

    try:
        carte = charger(options.carte)
    except (OSError, CarteInvalide) as erreur:
        print(f"Erreur : {erreur}", file=sys.stderr)
        return 2

    erreurs = verifier(carte)
    if erreurs:
        print(f"Carte refusée, {len(erreurs)} problème(s) :", file=sys.stderr)
        for erreur in erreurs:
            print(f"  - {erreur}", file=sys.stderr)
        return 1
    for element in carte[cle_elements(carte)]:
        nombre = len(element.get("lots") or [])
        if nombre > LOTS_CONSEILLES:
            print(f"Attention : « {element['nom']} » a {nombre} lots (conseillé : "
                  f"{LOTS_CONSEILLES} au plus). Regrouper les plus petits.",
                  file=sys.stderr)
    if options.verifier:
        print("Carte valide.")
        return 0

    dossier = options.sortie or options.carte.resolve().parent
    dossier.mkdir(parents=True, exist_ok=True)
    pages = rendu_projet(carte) if carte["type"] == "projet" else rendu_orga(carte)
    for nom, fragment in pages.items():
        chemin = dossier / f"{nom}.widget.html"
        chemin.write_text(fragment, encoding="utf-8")
        print(f"{chemin}  ({len(fragment) // 1024} Ko)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

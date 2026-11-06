#!/usr/bin/env python3
"""
generer_maps.py — transforme un fichier carte.json en deux maps visuelles.

    python3 generer_maps.py carte.json                 # widgets + HTML à côté du JSON
    python3 generer_maps.py carte.json -o dossier/     # ailleurs
    python3 generer_maps.py carte.json --colonnes 3    # cartes sur 3 colonnes
    python3 generer_maps.py carte.json --png           # en plus, PNG (Chrome ou Edge)
    python3 generer_maps.py carte.json --verifier      # contrôle, sans rien écrire

Les fichiers vont là où est le carte.json. Les maps se dessinent dans la
conversation, pas dans un dossier du projet : écrire le carte.json dans le
dossier de travail temporaire de la session.

Chaque map sort en deux fichiers :
- <nom>.widget.html : fragment à passer tel quel à show_widget, pour dessiner
  la map dans la conversation. Couleurs du thème de l'hôte, clair et sombre.
- <nom>.html : page complète, à télécharger.

Type « projet » : par-volet et par-lot.
Type « orga »   : par-projet et lots-restants.

Ce script ne décide d'aucun état à la main. Il calcule tout depuis les lots :
la couleur de chaque case, la phase, la barre, le verdict, le reste à faire.
Un même lot ne peut donc pas dire deux choses différentes sur les deux maps.

Il refuse un fichier qui ne respecte pas les règles : lot sans source, phase
inconnue, texte trop long. Le format complet est dans references/format-carte.md.

Aucune dépendance Python. Le PNG, optionnel, passe par Chrome ou Edge, sans fenêtre.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PHASES = ["Cadrage", "Construction", "Pré-production", "Bêta", "Lancement"]

# statut du lot -> (texte de la pastille, famille de couleur)
STATUTS = {
    "fait": ("fait", "vert"),
    "en_cours": ("en cours", "bleu"),
    "a_faire": ("à faire", "bleu"),
    "a_fournir": ("à fournir", "bleu"),
    "a_trancher": ("à trancher", "bleu"),
    "bloquant": ("bloquant", "rouge"),
    "a_venir": ("à venir", "gris"),
    "a_confirmer": ("à confirmer", "pointille"),
}

# Lots montrés en titres dans la carte d'un projet, sur une map d'orga. Un
# volet montre tous les siens : la map d'un seul projet a la place.
LOTS_EN_TITRES = 7

# Limites de longueur : la map se lit d'un coup d'œil, pas phrase par phrase.
LIMITES = {
    "verdict": 150,
    "prochaine_action": 110,
    "resume": 170,
    "nom": 34,
    "sous_titre": 48,
    "titre": 44,
    "detail": 46,
    "etiquette": 20,
}

# Sans commit depuis ce nombre de jours, un projet ouvert est dit à l'arrêt.
JOURS_ARRET = 45

# Au-delà, une carte de lots ne se lit plus d'un coup d'œil.
LOTS_CONSEILLES = 14

# Un lot ouvert : on sait que le travail est là, mais il n'a pas commencé.
OUVERTS = ("a_faire", "a_fournir", "a_trancher", "bloquant")

CHAMPS_CARTE = {"type", "nom", "sous_titre", "date", "verdict", "prochaine_action",
                "volets", "projets", "hors_carte", "depots_total"}
CHAMPS_ELEMENT = {"nom", "sous_titre", "resume", "derniere_activite", "etiquettes",
                  "lots", "phase_estimee", "source_phase"}
CHAMPS_LOT = {"titre", "detail", "phase", "statut", "source", "cause"}

# Ordre de lecture de la map d'orga : ce qui demande une action passe d'abord.
ORDRE_VERDICT = ["Bloqué", "À l'arrêt", "À trancher", "À confirmer",
                 "En bonne voie", "Pas commencé", "Terminé"]

NOM_COURT = {"Pré-production": "Pré-prod"}

COULEUR_VERDICT = {
    "Bloqué": "rouge", "À trancher": "bleu", "À confirmer": "pointille",
    "En bonne voie": "vert", "À l'arrêt": "gris", "Pas commencé": "gris",
    "Terminé": "vert",
}


class CarteInvalide(Exception):
    """Le fichier carte.json ne respecte pas le format."""


# --------------------------------------------------------------------------
# Contrôle du fichier
# --------------------------------------------------------------------------

def cle_elements(carte: dict) -> str:
    return "volets" if carte.get("type") == "projet" else "projets"


def verifier(carte: dict) -> list[str]:
    """Renvoie la liste de tous les problèmes, pour tout corriger en une fois."""
    erreurs: list[str] = []

    def longueur(valeur, champ, ou):
        if isinstance(valeur, str) and len(valeur) > LIMITES[champ]:
            erreurs.append(f"{ou} : « {champ} » fait {len(valeur)} caractères "
                           f"(maximum {LIMITES[champ]}). À raccourcir.")

    def date_valide(valeur, champ, ou):
        try:
            dt.date.fromisoformat(str(valeur))
        except ValueError:
            erreurs.append(f"{ou} : « {champ} » doit être une date AAAA-MM-JJ "
                           f"(reçu : {valeur!r}).")

    def champs(objet, permis, ou):
        for champ in sorted(set(objet) - permis):
            erreurs.append(f"{ou} : champ inconnu « {champ} ». Les valeurs "
                           f"calculées ne s'écrivent pas dans la carte.")

    if not isinstance(carte, dict) or carte.get("type") not in ("projet", "orga"):
        return ["« type » doit valoir projet ou orga."]
    champs(carte, CHAMPS_CARTE, "Carte")

    for champ in ("nom", "date", "verdict", "prochaine_action"):
        if not str(carte.get(champ) or "").strip():
            erreurs.append(f"Carte : le champ « {champ} » est obligatoire.")
    if carte.get("date"):
        date_valide(carte["date"], "date", "Carte")
    longueur(carte.get("verdict"), "verdict", "Carte")
    longueur(carte.get("prochaine_action"), "prochaine_action", "Carte")

    cle = cle_elements(carte)
    elements = carte.get(cle)
    if not isinstance(elements, list) or not elements:
        erreurs.append(f"Carte : la liste « {cle} » est obligatoire et non vide.")
        return erreurs

    if not all(isinstance(x, dict) for x in elements):
        erreurs.append(f"Carte : chaque élément de « {cle} » doit être un objet.")
        return erreurs

    noms_vus: set[str] = set()
    for element in elements:
        nom = str(element.get("nom") or "").strip()
        ou = f"« {nom or '?'} »"
        if not nom:
            erreurs.append(f"{cle} : un élément n'a pas de nom.")
        if nom in noms_vus:
            erreurs.append(f"{ou} : ce nom apparaît deux fois.")
        noms_vus.add(nom)
        champs(element, CHAMPS_ELEMENT, ou)
        if carte["type"] == "orga" and not element.get("derniere_activite"):
            erreurs.append(f"{ou} : « derniere_activite » est obligatoire sur une "
                           f"orga. Sans elle, un projet à l'arrêt ne se voit pas.")
        if not str(element.get("resume") or "").strip():
            erreurs.append(f"{ou} : « resume » est obligatoire.")
        for champ in ("nom", "sous_titre", "resume"):
            longueur(element.get(champ), champ, ou)
        if element.get("derniere_activite"):
            date_valide(element["derniere_activite"], "derniere_activite", ou)

        for phase, texte in (element.get("etiquettes") or {}).items():
            if phase not in PHASES:
                erreurs.append(f"{ou} : étiquette sur une phase inconnue "
                               f"« {phase} ».")
            longueur(texte, "etiquette", f"{ou}, phase {phase}")

        lots = element.get("lots") or []
        estimee = element.get("phase_estimee")
        if not lots:
            if estimee not in PHASES:
                erreurs.append(f"{ou} : sans lot, « phase_estimee » est "
                               f"obligatoire ({', '.join(PHASES)}).")
            if not str(element.get("source_phase") or "").strip():
                erreurs.append(f"{ou} : sans lot, « source_phase » doit dire "
                               f"d'où vient la phase estimée.")
        elif estimee:
            erreurs.append(f"{ou} : « phase_estimee » est réservée aux éléments "
                           f"sans lot. Avec des lots, la phase se calcule.")

        for lot in lots:
            if not isinstance(lot, dict):
                erreurs.append(f"{ou} : chaque lot doit être un objet.")
                continue
            titre = str(lot.get("titre") or "").strip()
            ou_lot = f"{ou}, lot « {titre or '?'} »"
            champs(lot, CHAMPS_LOT, ou_lot)
            if not titre:
                erreurs.append(f"{ou} : un lot n'a pas de titre.")
            longueur(titre, "titre", ou_lot)
            longueur(lot.get("detail"), "detail", ou_lot)
            if lot.get("phase") not in PHASES:
                erreurs.append(f"{ou_lot} : phase inconnue {lot.get('phase')!r} "
                               f"({', '.join(PHASES)}).")
            statut = lot.get("statut")
            if statut not in STATUTS:
                erreurs.append(f"{ou_lot} : statut inconnu {statut!r} "
                               f"({', '.join(STATUTS)}).")
            elif statut != "a_confirmer" and not str(lot.get("source") or "").strip():
                erreurs.append(f"{ou_lot} : pas de source. Mettre le fichier, "
                               f"le commit ou le ticket qui le prouve, ou "
                               f"passer le statut à a_confirmer.")
    if not erreurs and carte["type"] == "orga":
        for projet in elements:
            lots = projet.get("lots") or []
            if (lots and all(l["statut"] == "fait" for l in lots)
                    and position(projet) < len(PHASES) - 1):
                erreurs.append(f"« {projet['nom']} » : tous les lots sont faits "
                               f"mais rien en Lancement. Ajouter les lots qui "
                               f"restent jusqu'au lancement.")
    return erreurs


# --------------------------------------------------------------------------
# Calculs : tout ce qu'on affiche vient d'ici
# --------------------------------------------------------------------------

def etat_case(lots: list[dict]) -> str:
    """État d'une case phase : vide, fait, bloque, ouvert, confirmer ou avenir."""
    if not lots:
        return "vide"
    statuts = {l["statut"] for l in lots}
    if statuts == {"fait"}:
        return "fait"
    if "bloquant" in statuts:
        return "bloque"
    if statuts == {"a_venir"}:
        return "avenir"
    if statuts <= {"a_confirmer", "a_venir"}:
        return "confirmer"
    return "ouvert"


def cases(element: dict) -> dict[str, dict]:
    resultat = {}
    etiquettes = element.get("etiquettes") or {}
    for phase in PHASES:
        lots = [l for l in element.get("lots") or [] if l["phase"] == phase]
        faits = sum(l["statut"] == "fait" for l in lots)
        etat = etat_case(lots)
        if etiquettes.get(phase):
            texte = etiquettes[phase]
        elif etat == "vide":
            texte = "—"
        elif etat == "fait":
            texte = "fait" if len(lots) == 1 else f"{faits} lots"
        elif etat == "avenir":
            texte = "à venir"
        else:
            texte = f'{faits} / {len(lots)} {pluriel(len(lots), "lot")}'
        resultat[phase] = {"etat": etat, "texte": texte}
    return resultat


def position(element: dict) -> int:
    """Rang de la phase atteinte. 0 si rien n'a démarré.

    Une phase est atteinte par un lot fait ou en cours. Un lot seulement ouvert
    (à faire, bloquant…) y fait entrer si la phase d'avant est finie : on est
    alors bien arrivé là. Un lot à confirmer ou à venir ne fait jamais avancer.
    """
    if not element.get("lots"):
        return PHASES.index(element["phase_estimee"])
    rang = 0
    precedente_finie = False
    for i, phase in enumerate(PHASES):
        lots = [l for l in element["lots"] if l["phase"] == phase]
        if not lots:
            continue
        statuts = {l["statut"] for l in lots}
        if statuts & {"fait", "en_cours"}:
            rang = i
        elif statuts & set(OUVERTS) and precedente_finie:
            rang = i
        precedente_finie = statuts == {"fait"}
    return rang


def phase_projet(volets: list[dict]) -> int:
    """Médiane basse des volets : un volet en avance ne tire pas tout le projet."""
    rangs = sorted(position(v) for v in volets)
    return rangs[(len(rangs) - 1) // 2]


def compte(element: dict) -> dict:
    lots = element.get("lots") or []
    total = len(lots)
    faits = sum(l["statut"] == "fait" for l in lots)
    return {
        "total": total,
        "faits": faits,
        "restants": total - faits,
        "pourcent": round(100 * faits / total) if total else 0,
    }


def titres(element: dict, *statuts: str) -> list[str]:
    return [l["titre"] for l in element.get("lots") or [] if l["statut"] in statuts]


def jours_sans_activite(element: dict, date_carte: str) -> int | None:
    valeur = element.get("derniere_activite")
    if not valeur:
        return None
    return (dt.date.fromisoformat(date_carte) - dt.date.fromisoformat(valeur)).days


def verdict_element(element: dict, date_carte: str) -> str:
    c = compte(element)
    if not c["total"]:
        return "À confirmer"
    if c["faits"] == c["total"]:
        return "Terminé"
    if titres(element, "bloquant"):
        return "Bloqué"
    jours = jours_sans_activite(element, date_carte)
    if jours is not None and jours > JOURS_ARRET:
        return "À l'arrêt"
    if titres(element, "a_trancher"):
        return "À trancher"
    if titres(element, "a_confirmer"):
        return "À confirmer"
    if not c["faits"] and not titres(element, "en_cours"):
        return "Pas commencé"
    return "En bonne voie"


def totaux(elements: list[dict]) -> dict:
    lots = [l for e in elements for l in e.get("lots") or []]

    def distincts(statut):
        retenus = [l for l in lots if l["statut"] == statut]
        causes = {l["cause"] for l in retenus if l.get("cause")}
        return len(causes) + sum(not l.get("cause") for l in retenus)

    return {
        "elements": len(elements),
        "total": len(lots),
        "faits": sum(l["statut"] == "fait" for l in lots),
        "bloquants": distincts("bloquant"),
        "a_trancher": distincts("a_trancher"),
    }


def trier(carte: dict) -> list[dict]:
    """Projet : l'ordre du fichier. Orga : ce qui demande une action d'abord."""
    elements = carte[cle_elements(carte)]
    if carte["type"] == "projet":
        return list(elements)
    return sorted(elements, key=lambda e: (
        ORDRE_VERDICT.index(verdict_element(e, carte["date"])), -position(e)))


# --------------------------------------------------------------------------
# Rendu HTML
# --------------------------------------------------------------------------

CSS = """
:root {
  --fond: #fafafa; --carte: #ffffff; --bord: #e4e4e4; --encre: #111111;
  --doux: #5c5c5c; --pale: #8c8c8c; --piste: #f1f1f1;
  --vert: #099309; --vert-fond: #cdeacb; --vert-texte: #17691a;
  --bleu-fond: #cfe2fb; --bleu-bord: #7db2ee; --bleu-texte: #174a86;
  --rouge-fond: #fbdcd9; --rouge-bord: #e8958c; --rouge-texte: #9c2015;
  --gris-fond: #f5f5f5; --gris-texte: #8c8c8c;
}
* { box-sizing: border-box; }
html { background: var(--fond); }
body {
  margin: 0; padding: 32px; background: var(--fond); color: var(--encre);
  font-family: Inter, "Segoe UI", -apple-system, BlinkMacSystemFont, Roboto,
    "Helvetica Neue", Arial, sans-serif;
  font-size: 15px; line-height: 1.42; -webkit-font-smoothing: antialiased;
}
.page { max-width: 1216px; margin: 0 auto; }
.etroite { max-width: 1216px; }

/* En-tête */
.entete { display: flex; justify-content: space-between; align-items: flex-start;
  gap: 24px; margin-bottom: 18px; }
h1 { font-size: 27px; line-height: 1.15; margin: 0; letter-spacing: -.01em; }
.soustitre { color: var(--doux); margin-top: 3px; }
.date { color: var(--pale); white-space: nowrap; padding-top: 6px; }

/* Bandeau verdict */
.verdict { background: var(--carte); border: 1px solid var(--bord);
  border-radius: 16px; padding: 18px 22px; margin-bottom: 14px; }
.verdict-haut { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.verdict-mot { font-size: 12px; font-weight: 700; letter-spacing: .08em;
  text-transform: uppercase; color: var(--pale); }
.verdict-phrase { font-size: 19px; font-weight: 650; line-height: 1.3;
  margin-top: 8px; }
.action { color: var(--doux); margin-top: 6px; }
.action b { color: var(--encre); font-weight: 600; }

/* Frise des phases */
.frise { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px;
  margin-bottom: 14px; }
.etape { background: var(--gris-fond); color: var(--gris-texte);
  border-radius: 10px; padding: 9px 8px; text-align: center; font-size: 14px;
  border: 1px solid transparent; }
.etape.passee { background: var(--vert-fond); color: var(--vert-texte); }
.etape.actuelle { background: var(--bleu-fond); color: var(--bleu-texte);
  border-color: var(--bleu-bord); font-weight: 700; }
.etape.ouverte { background: var(--bleu-fond); color: var(--bleu-texte); }
.etape small { display: block; font-size: 12.5px; font-weight: 400; opacity: .85; }
.etape .nombre { display: block; font-size: 21px; font-weight: 700;
  line-height: 1.15; }

/* Chiffres clés */
.chiffres { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
  margin-bottom: 22px; }
.chiffre { background: var(--carte); border: 1px solid var(--bord);
  border-radius: 14px; padding: 12px 16px; }
.chiffre b { display: block; font-size: 24px; line-height: 1.15; }
.chiffre span { color: var(--doux); font-size: 13.5px; }
.chiffre.alerte b { color: var(--rouge-texte); }

/* Matrice phases */
.matrice { width: 100%; border-collapse: separate; border-spacing: 10px 8px;
  table-layout: fixed; margin: 0 -10px 4px; width: calc(100% + 20px); }
.matrice th { font-weight: 400; color: var(--doux); font-size: 15px;
  padding-bottom: 4px; }
.matrice td.ligne { width: 216px; vertical-align: middle; }
.matrice col.tete { width: 216px; }
.ligne b { display: block; font-weight: 600; font-size: 16.5px; line-height: 1.2; }
.ligne span { color: var(--doux); font-size: 14px; }
.case { height: 42px; border-radius: 11px; text-align: center; font-size: 14.5px;
  padding: 0 6px; vertical-align: middle; overflow: hidden; }
.case.fait { background: var(--vert-fond); color: var(--vert-texte); }
.case.ouvert { background: var(--bleu-fond); color: var(--bleu-texte);
  box-shadow: inset 0 0 0 1px var(--bleu-bord); }
.case.bloque { background: var(--rouge-fond); color: var(--rouge-texte);
  box-shadow: inset 0 0 0 1px var(--rouge-bord); }
.case.confirmer { color: var(--doux); outline: 1px dashed var(--pale);
  outline-offset: -1px; }
.case.avenir { color: var(--gris-texte); }
.case.vide { color: var(--gris-texte); }

/* Légende */
.legende { display: flex; gap: 22px; flex-wrap: wrap; color: var(--doux);
  font-size: 14px; margin: 8px 0 20px; }
.legende i { display: inline-block; width: 13px; height: 13px; border-radius: 3px;
  margin-right: 7px; vertical-align: -1px; }
.legende .l-vert { background: var(--vert-fond); }
.legende .l-bleu { background: var(--bleu-fond);
  box-shadow: inset 0 0 0 1px var(--bleu-bord); }
.legende .l-rouge { background: var(--rouge-fond);
  box-shadow: inset 0 0 0 1px var(--rouge-bord); }
.legende .l-pointille { border: 1px dashed var(--pale); }
.legende .l-gris { background: var(--gris-fond);
  box-shadow: inset 0 0 0 1px var(--bord); }

/* Cartes */
.colonnes { display: flex; gap: 20px; align-items: flex-start; }
.colonne { flex: 1 1 0; min-width: 0; }
.bloc {
  background: var(--carte); border: 1px solid var(--bord); border-radius: 16px;
  padding: 20px 22px; margin-bottom: 20px; }
.titre { display: flex; align-items: flex-start; gap: 12px; }
.case-cocher { flex: none; width: 14px; height: 14px; margin-top: 5px;
  border: 2px solid var(--encre); border-radius: 2px; }
.case-cocher.pleine { background: var(--vert); border-color: var(--vert); }
.titre h2 { font-size: 18.5px; line-height: 1.25; margin: 0; flex: 1; }
.titre .sous { display: block; font-weight: 400; font-size: 14px;
  color: var(--doux); margin-top: 2px; }
.tags { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 11px; }
.tag { font-size: 12.5px; font-weight: 600; border-radius: 7px; padding: 3px 9px;
  border: 1px solid transparent; white-space: nowrap; }
.resume { margin: 11px 0 0; }

/* Ligne d'avancement */
.barre { height: 9px; background: var(--piste); border-radius: 5px;
  overflow: hidden; margin-top: 13px; }
.barre i { display: block; height: 100%; background: var(--vert); border-radius: 5px; }
.mesure { display: flex; justify-content: space-between; color: var(--doux);
  font-size: 13.5px; margin-top: 5px; }
.mesure b { color: var(--encre); font-weight: 650; }
.mini { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px;
  margin-top: 10px; }
.mini i { display: block; height: 6px; border-radius: 3px; background: var(--piste); }
.mini i.fait { background: var(--vert); }
.mini i.ouvert { background: var(--bleu-bord); }
.mini i.bloque { background: var(--rouge-bord); }
.mini i.confirmer { background: repeating-linear-gradient(90deg, var(--pale) 0 4px,
  transparent 4px 7px); }
.mini-noms { display: grid; grid-template-columns: repeat(5, 1fr); gap: 3px;
  color: var(--pale); font-size: 10.5px; margin-top: 3px; }
.mini-noms span.ici { color: var(--bleu-texte); font-weight: 700; }

/* Les lots de la carte : deux paquets, une case à cocher par lot */
.paquet { margin-top: 13px; }
.paquet + .paquet { margin-top: 15px; }
.paquet-tete { display: flex; justify-content: space-between;
  align-items: center; font-size: 12px; color: var(--pale);
  padding-bottom: 5px; border-bottom: 1px solid var(--bord); }
.titres { list-style: none; margin: 6px 0 0; padding: 0; }
.titres li { display: flex; align-items: flex-start; gap: 10px; font-size: 14px;
  line-height: 1.3; padding: 3px 0; }
.titres i { flex: none; box-sizing: border-box; width: 14px; height: 14px;
  margin-top: 2px; border: 1px solid var(--pale); border-radius: 4px;
  position: relative; }
.titres li.fait { color: var(--pale); }
.titres li.fait i { background: var(--doux); border-color: var(--doux); }
.titres li.fait i::after { content: ""; position: absolute; left: 4.5px;
  top: 1.8px; width: 3.2px; height: 6.6px; border: solid var(--carte);
  border-width: 0 1.7px 1.7px 0; transform: rotate(45deg); }
.titres li.encours i::after { content: ""; position: absolute; left: 2.2px;
  top: 5px; width: 7.6px; height: 2px; border-radius: 1px;
  background: var(--doux); }
.titres li.aconfirmer { color: var(--pale); }
.titres li.aconfirmer i { border-style: dashed; }
.titres li.autres { color: var(--pale); font-size: 13px; padding-left: 24px; }

/* Liste des lots */
.lot { display: flex; align-items: center; justify-content: space-between;
  gap: 12px; padding: 5px 0; }
.lot-texte { min-width: 0; }
.lot-titre { font-weight: 550; font-size: 14.5px; line-height: 1.25; }
.lot-detail { color: var(--doux); font-size: 13px; line-height: 1.25; }
.lots { margin-top: 10px; }
.pastille { flex: none; width: 92px; text-align: center; font-size: 13px;
  border-radius: 9px; padding: 4px 4px; border: 1px solid transparent; }
.vert { background: var(--vert-fond); color: var(--vert-texte); }
.bleu { background: var(--bleu-fond); color: var(--bleu-texte);
  border-color: var(--bleu-bord); }
.rouge { background: var(--rouge-fond); color: var(--rouge-texte);
  border-color: var(--rouge-bord); }
.gris { background: var(--gris-fond); color: var(--gris-texte); }
.pointille { background: transparent; color: var(--doux);
  border: 1px dashed var(--pale); }
.groupe { color: var(--pale); font-size: 12px; font-weight: 600;
  letter-spacing: .04em; margin-top: 10px; text-transform: uppercase; }
.sans-lot { color: var(--doux); font-size: 14px; margin-top: 12px; }
.hors { color: var(--doux); font-size: 14px; margin-top: 6px; }
.hors b { color: var(--encre); font-weight: 600; }

@media (max-width: 900px) {
  body { padding: 16px; }
  .colonnes { display: block; }
  .chiffres { grid-template-columns: repeat(2, 1fr); }
  .defile { overflow-x: auto; }
  .matrice { min-width: 760px; }
}
"""


def e(texte) -> str:
    return html.escape(str(texte), quote=True)


def tag(verdict: str, texte: str | None = None) -> str:
    return f'<span class="tag {COULEUR_VERDICT[verdict]}">{e(texte or verdict)}</span>'


def date_fr(valeur: str) -> str:
    d = dt.date.fromisoformat(valeur)
    return d.strftime("%d/%m/%Y")


def repartir(cartes: list[tuple[str, float]], nombre: int) -> str:
    """Pose chaque carte dans la colonne la plus courte, sans changer l'ordre.

    Le résultat se lit de gauche à droite, et les colonnes finissent à peu près
    à la même hauteur.
    """
    colonnes: list[list[str]] = [[] for _ in range(nombre)]
    hauteurs = [0.0] * nombre
    for rang, (contenu, poids) in enumerate(cartes):
        # data-i garde l'ordre de lecture : le widget s'en sert pour
        # redistribuer les cartes quand on change le nombre de colonnes.
        contenu = contenu.replace('<article class="bloc"',
                                  f'<article class="bloc" data-i="{rang}"', 1)
        i = hauteurs.index(min(hauteurs))
        colonnes[i].append(contenu)
        hauteurs[i] += poids
    corps = "".join(f'<div class="colonne">{"".join(c)}</div>' for c in colonnes)
    return f'<section class="colonnes" data-n="{nombre}">{corps}</section>'


def page(titre: str, corps: str) -> str:
    return (f'<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{e(titre)}</title><style>{CSS}</style></head>'
            f'<body><main class="page">{corps}</main></body></html>')


# --------------------------------------------------------------------------
# Widget : la même map, dessinée dans la conversation par show_widget
# --------------------------------------------------------------------------

# Les couleurs de la page complète, rebranchées sur celles de l'hôte : la map
# suit le thème clair ou sombre de la conversation.
VARIABLES_WIDGET = """.mp {
  --fond: transparent; --carte: var(--surface-2); --bord: var(--border);
  --encre: var(--text-primary); --doux: var(--text-secondary);
  --pale: var(--text-muted); --piste: var(--surface-1);
  --vert: var(--fill-success); --vert-fond: var(--bg-success);
  --vert-texte: var(--text-success);
  --bleu-fond: var(--bg-accent); --bleu-bord: var(--border-accent);
  --bleu-texte: var(--text-accent);
  --rouge-fond: var(--bg-danger); --rouge-bord: var(--border-danger);
  --rouge-texte: var(--text-danger);
  --gris-fond: var(--surface-1); --gris-texte: var(--text-muted);
  color: var(--encre); font-size: 14px; line-height: 1.42; padding: 4px 0;
}
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden;
  clip: rect(0 0 0 0); white-space: nowrap; }"""


def css_widget() -> str:
    """Le CSS de la page, adapté aux règles du widget.

    Pas de commentaire, pas de règle sur html ou body, deux graisses (400 et
    500), rien sous 11 px, pas de défilement interne : le widget fait 680 px.
    """
    css = re.sub(r"/\*.*?\*/", "", CSS, flags=re.S)
    css = re.sub(r":root\s*\{.*?\}", "", css, flags=re.S)
    css = re.sub(r"(?m)^(\*|html|body|\.page|\.etroite)\s*\{.*?\}", "", css, flags=re.S)
    css = re.sub(r"@media[^{]*\{.*\}\s*$", "", css, flags=re.S)
    css = re.sub(r"font-weight:\s*(5[5-9]0|[6-9]\d\d)", "font-weight: 500", css)
    css = re.sub(r"font-size:\s*10(\.\d+)?px", "font-size: 11px", css)
    css = css.replace("h1 { font-size: 27px;", "h1 { font-size: 22px; font-weight: 500;")
    css = css.replace(".titre h2 { font-size: 18.5px;",
                      ".titre h2 { font-size: 16px; font-weight: 500;")
    css += """
.mp .reglage { display: flex; align-items: center; gap: 6px; margin: 0 0 12px;
  font-size: 13px; color: var(--doux); }
.mp .reglage button { min-width: 34px; padding: 2px 10px; font-size: 13px; }
.mp .reglage button[aria-pressed="true"] { border-color: var(--border-accent);
  color: var(--text-accent); background: var(--bg-accent); }
.mp .chiffres { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.mp .matrice { margin: 0 0 4px; width: 100%; border-spacing: 6px 8px; }
.mp .matrice td.ligne, .mp .matrice col.tete { width: 150px; }
.mp .case { font-size: 12px; }
.mp .etroit { gap: 12px; }
.mp .etroit .bloc { padding: 14px 14px; margin-bottom: 12px; }
.mp .etroit .mini-noms span { overflow: hidden; text-overflow: ellipsis;
  white-space: nowrap; }
.mp .etroit .lot { flex-direction: column; align-items: flex-start; gap: 4px; }
.mp .etroit .pastille { width: auto; padding: 2px 8px; font-size: 12px; }
.mp .etroit .tag { white-space: normal; }
@media (max-width: 560px) {
  .mp .defile { overflow-x: auto; }
  .mp .matrice { min-width: 560px; }
  .mp .frise { grid-template-columns: repeat(5, minmax(0, 1fr)); font-size: 12px; }
  .mp .etape { font-size: 12px; padding: 8px 4px; }
  .mp .entete { flex-direction: column; gap: 4px; }
}
"""
    return VARIABLES_WIDGET + re.sub(r"\n\s*\n+", "\n", css)


# Redistribue les cartes dans 1, 2 ou 3 colonnes, dans l'ordre de lecture,
# chaque carte dans la colonne la plus courte : même règle que repartir().
# Une colonne fait au moins 200 px : sur un écran étroit
# (téléphone), la map prend moins de colonnes que demandé.
SCRIPT_COLONNES = """<script>
(function () {
  var sec = document.querySelector('.mp .colonnes');
  if (!sec) return;
  var cartes = Array.prototype.slice.call(sec.querySelectorAll('.bloc'))
    .sort(function (a, b) { return a.dataset.i - b.dataset.i; });
  var boutons = document.querySelectorAll('.mp .reglage button');
  function poser(n) {
    n = Math.max(1, Math.min(n, Math.floor((sec.clientWidth + 20) / 220)));
    sec.innerHTML = '';
    sec.classList.toggle('etroit', sec.clientWidth / n < 300);
    var cols = [];
    for (var k = 0; k < n; k++) {
      var c = document.createElement('div');
      c.className = 'colonne';
      sec.appendChild(c);
      cols.push(c);
    }
    cartes.forEach(function (carte) {
      var courte = cols.reduce(function (a, b) {
        return b.offsetHeight < a.offsetHeight ? b : a;
      });
      courte.appendChild(carte);
    });
    boutons.forEach(function (b) {
      b.setAttribute('aria-pressed', String(Number(b.dataset.n) === n));
    });
  }
  boutons.forEach(function (b) {
    b.addEventListener('click', function () { poser(Number(b.dataset.n)); });
  });
  poser(Number(sec.dataset.n));
})();
</script>"""


def widget(page_html: str, resume: str, colonnes: int = 2) -> str:
    """Fragment pour show_widget : un titre caché, le style, le contenu.

    Pas de DOCTYPE, pas de html, head ou body : show_widget les refuse.
    Au-dessus des cartes, trois boutons pour passer en 1, 2 ou 3 colonnes.
    """
    corps = re.search(r'<main class="page">(.*)</main>', page_html, flags=re.S).group(1)
    reglage = ('<div class="reglage">Colonnes'
               + "".join(f'<button type="button" data-n="{n}" aria-pressed="false">'
                         f'{n}</button>' for n in (1, 2, 3))
               + '</div>')
    corps = re.sub(r'<section class="colonnes" data-n="\d+">',
                   f'{reglage}<section class="colonnes" data-n="{colonnes}">', corps, count=1)
    return (f'<h2 class="sr-only">{e(resume)}</h2>'
            f'<style>{css_widget()}</style><div class="mp">{corps}</div>'
            f'{SCRIPT_COLONNES}')


def legende() -> str:
    return ('<div class="legende">'
            '<span><i class="l-vert"></i>Terminé</span>'
            '<span><i class="l-bleu"></i>En cours ou à trancher</span>'
            '<span><i class="l-rouge"></i>Bloquant</span>'
            '<span><i class="l-pointille"></i>À confirmer</span>'
            '<span><i class="l-gris"></i>À venir</span></div>')


def entete(carte: dict, sous_titre: str) -> str:
    return (f'<header class="entete"><div><h1>{e(carte["nom"])}</h1>'
            f'<div class="soustitre">{e(sous_titre)}</div></div>'
            f'<div class="date">État au {date_fr(carte["date"])}</div></header>')


def bandeau_verdict(carte: dict, verdict: str, etiquette: str,
                    texte: str | None = None) -> str:
    hors = ""
    if carte.get("hors_carte"):
        hors = f'<div class="hors"><b>Hors map :</b> {e(carte["hors_carte"])}</div>'
    return (f'<section class="verdict"><div class="verdict-haut">'
            f'<span class="verdict-mot">Verdict</span>{tag(verdict, texte)}'
            f'<span class="tag gris">{e(etiquette)}</span></div>'
            f'<div class="verdict-phrase">{e(carte["verdict"])}</div>'
            f'<div class="action"><b>Prochaine étape :</b> '
            f'{e(carte["prochaine_action"])}</div>{hors}</section>')


def pluriel(nombre: int, mot: str) -> str:
    return mot if nombre <= 1 else " ".join(
        m if m == "à" else f"{m}s" for m in mot.split(" "))


def chiffres(t: dict, nom_elements: str) -> str:
    pourcent = round(100 * t["faits"] / t["total"]) if t["total"] else 0
    tuiles = [
        (t["elements"], nom_elements, False),
        (f'{t["faits"]} / {t["total"]}', f"lots faits ({pourcent} %)", False),
        (t["bloquants"], pluriel(t["bloquants"], "bloquant"), t["bloquants"] > 0),
        (t["a_trancher"], f'{pluriel(t["a_trancher"], "décision")} à trancher', False),
    ]
    contenu = "".join(
        f'<div class="chiffre{" alerte" if alerte else ""}"><b>{e(v)}</b>'
        f'<span>{e(l)}</span></div>' for v, l, alerte in tuiles)
    return f'<section class="chiffres">{contenu}</section>'


def frise_projet(volets: list[dict], rang: int) -> str:
    etapes = []
    for i, phase in enumerate(PHASES):
        lots = [l for v in volets for l in v.get("lots") or [] if l["phase"] == phase]
        faits = sum(l["statut"] == "fait" for l in lots)
        if i == rang:
            classe = "actuelle"
        elif i < rang:
            classe = "passee" if faits == len(lots) else "ouverte"
        else:
            classe = ""
        mesure = f'{faits} / {len(lots)} {pluriel(len(lots), "lot")}' if lots else "aucun lot"
        etapes.append(f'<div class="etape {classe}">{e(phase)}'
                      f'<small>{mesure}</small></div>')
    return f'<section class="frise">{"".join(etapes)}</section>'


def frise_orga(elements: list[dict]) -> str:
    etapes = []
    for i, phase in enumerate(PHASES):
        nombre = sum(position(p) == i for p in elements)
        classe = "actuelle" if nombre else ""
        etapes.append(f'<div class="etape {classe}"><span class="nombre">{nombre}'
                      f'</span>{e(phase)}</div>')
    return f'<section class="frise">{"".join(etapes)}</section>'


def matrice(elements: list[dict]) -> str:
    entetes = "".join(f"<th>{e(p)}</th>" for p in PHASES)
    lignes = []
    for el in elements:
        etats = cases(el)
        sous = f'<span>{e(el["sous_titre"])}</span>' if el.get("sous_titre") else ""
        cellules = "".join(
            f'<td class="case {etats[p]["etat"]}">{e(etats[p]["texte"])}</td>'
            for p in PHASES)
        lignes.append(f'<tr><td class="ligne"><b>{e(el["nom"])}</b>{sous}</td>'
                      f'{cellules}</tr>')
    return (f'<div class="defile"><table class="matrice"><colgroup>'
            f'<col class="tete"><col><col><col><col><col></colgroup>'
            f'<thead><tr><th></th>{entetes}</tr></thead>'
            f'<tbody>{"".join(lignes)}</tbody></table></div>')


def ligne_avancement(el: dict) -> str:
    c = compte(el)
    if not c["total"]:
        return ('<p class="sans-lot">Aucun lot écrit dans ce projet. '
                'Phase estimée, à confirmer.</p>')
    return (f'<div class="barre"><i style="width:{c["pourcent"]}%"></i></div>'
            f'<div class="mesure"><span><b>{c["faits"]} / {c["total"]}</b> lots '
            f'faits</span><span><b>{c["pourcent"]} %</b></span></div>')


def mini_phases(el: dict) -> str:
    etats = cases(el)
    rang = position(el)
    barres = "".join(f'<i class="{etats[p]["etat"]}"></i>' for p in PHASES)
    noms = "".join(
        f'<span class="{"ici" if i == rang else ""}">{e(NOM_COURT.get(p, p))}</span>'
        for i, p in enumerate(PHASES))
    return f'<div class="mini">{barres}</div><div class="mini-noms">{noms}</div>'


def titre_carte(el: dict, date_carte: str) -> str:
    verdict = verdict_element(el, date_carte)
    pleine = " pleine" if verdict == "Terminé" else ""
    sous = f'<span class="sous">{e(el["sous_titre"])}</span>' if el.get("sous_titre") else ""
    phase = f'<span class="tag gris">{e(PHASES[position(el)])}</span>'
    jours = jours_sans_activite(el, date_carte)
    if jours is not None and jours > JOURS_ARRET and verdict != "Terminé":
        phase += f'<span class="tag gris">{jours} j sans commit</span>'
    return (f'<div class="titre"><span class="case-cocher{pleine}"></span>'
            f'<h2>{e(el["nom"])}{sous}</h2></div>'
            f'<div class="tags">{tag(verdict)}{phase}</div>')


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
    mot = STATUTS[lot["statut"]][0]
    etat = CASE.get(lot["statut"])
    classe = f' class="{etat}"' if etat else ""
    bulle = f'{mot} — {lot["source"]}' if lot.get("source") else mot
    return f'<li{classe} title="{e(bulle)}"><i></i>{e(lot["titre"])}</li>'


def paquet(titre: str, lots: list[dict], autres: int = 0) -> str:
    if not lots:
        return ""
    corps = "".join(ligne_titre(l) for l in lots)
    if autres:
        corps += f'<li class="autres">+ {autres} autres</li>'
    return (f'<div class="paquet"><div class="paquet-tete">{e(titre)}'
            f'<span>{len(lots) + autres}</span></div>'
            f'<ul class="titres">{corps}</ul></div>')


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


def carte_synthese(el: dict, date_carte: str, maximum: int | None = None) -> str:
    return (f'<article class="bloc">{titre_carte(el, date_carte)}'
            f'<p class="resume">{e(el["resume"])}</p>'
            f'{ligne_avancement(el)}{mini_phases(el)}'
            f'{lots_titres(el, maximum)}</article>')


def ligne_lot(lot: dict) -> str:
    texte, couleur = STATUTS[lot["statut"]]
    detail = f'<div class="lot-detail">{e(lot["detail"])}</div>' if lot.get("detail") else ""
    source = f' title="Source : {e(lot["source"])}"' if lot.get("source") else ""
    return (f'<div class="lot"{source}><div class="lot-texte">'
            f'<div class="lot-titre">{e(lot["titre"])}</div>{detail}</div>'
            f'<span class="pastille {couleur}">{e(texte)}</span></div>')


def carte_lots(el: dict, date_carte: str, restants_seuls: bool) -> str:
    lots = el.get("lots") or []
    if restants_seuls:
        lots = [l for l in lots if l["statut"] != "fait"]
    # Dans une même carte, on garde l'ordre des phases : c'est l'ordre du travail.
    lots = sorted(lots, key=lambda l: PHASES.index(l["phase"]))
    corps = []
    phase_courante = None
    for lot in lots:
        if lot["phase"] != phase_courante:
            phase_courante = lot["phase"]
            corps.append(f'<div class="groupe">{e(phase_courante)}</div>')
        corps.append(ligne_lot(lot))
    c = compte(el)
    if not c["total"]:
        corps = ['<p class="sans-lot">Aucun lot écrit dans ce projet.</p>']
    elif restants_seuls and not lots:
        corps = ['<p class="sans-lot">Plus aucun lot à faire.</p>']
    return (f'<article class="bloc">{titre_carte(el, date_carte)}'
            f'{ligne_avancement(el) if c["total"] else ""}'
            f'<div class="lots">{"".join(corps)}</div></article>')


def verdict_global(carte: dict, elements: list[dict]) -> str:
    verdicts = {verdict_element(el, carte["date"]) for el in elements}
    return next(mot for mot in ORDRE_VERDICT if mot in verdicts)


def texte_verdict(carte: dict, elements: list[dict], global_: str, nom: str) -> str:
    """« Bloqué : 1 volet sur 7 ». Un seul mot exagérerait un souci localisé."""
    nombre = sum(verdict_element(el, carte["date"]) == global_ for el in elements)
    return f"{global_} : {nombre} {nom}{'s' if nombre > 1 else ''} sur {len(elements)}"


def poids_synthese(el: dict, maximum: int | None = None) -> float:
    """Hauteur approchée de la carte, pour équilibrer les colonnes.

    Une ligne par lot montré, plus l'en-tête de chaque paquet."""
    lots = el.get("lots") or []
    faits = [l for l in lots if l["statut"] == "fait"]
    reste = [l for l in lots if l["statut"] != "fait"]
    if maximum is None:
        lignes = len(lots)
        entetes = bool(faits) + bool(reste)
    else:
        # Carte d'orga : seul « Reste » est listé, coupé, avec sa ligne « + N ».
        lignes = min(len(reste), maximum + 1)
        entetes = 1 if reste else 0
    return 10 + len(el["resume"]) / 45 + 1.45 * lignes + 1.8 * entetes


def poids_lots(el: dict, restants_seuls: bool) -> float:
    lots = [l for l in el.get("lots") or []
            if not restants_seuls or l["statut"] != "fait"]
    groupes = len({l["phase"] for l in lots})
    return 7 + 1.8 * len(lots) + 1.4 * groupes


def rendu_projet(carte: dict, colonnes: int | None = None) -> dict[str, str]:
    volets = trier(carte)
    date_carte = carte["date"]
    rang = phase_projet(volets)
    sous_titre = carte.get("sous_titre") or "Map du projet"
    global_ = verdict_global(carte, volets)
    tete = (entete(carte, sous_titre)
            + bandeau_verdict(carte, global_, f"Phase : {PHASES[rang]}",
                              texte_verdict(carte, volets, global_, "volet"))
            + frise_projet(volets, rang))
    t = totaux(volets)
    par_volet = (tete + chiffres(t, "volets") + matrice(volets) + legende()
                 + repartir([(carte_synthese(v, date_carte), poids_synthese(v))
                             for v in volets], colonnes or 3))
    par_lot = (tete + legende()
               + repartir([(carte_lots(v, date_carte, False), poids_lots(v, False))
                           for v in volets], colonnes or 2))
    return {
        "par-volet": page(f'{carte["nom"]} — par volet', par_volet),
        "par-lot": page(f'{carte["nom"]} — par lot', par_lot),
    }


def rendu_orga(carte: dict, colonnes: int | None = None) -> dict[str, str]:
    projets = trier(carte)
    date_carte = carte["date"]
    sous_titre = carte.get("sous_titre") or "Map de l'organisation"
    global_ = verdict_global(carte, projets)
    couverture = f"{len(projets)} projets"
    if carte.get("depots_total"):
        couverture += f" sur {carte['depots_total']} dépôts"
    tete = (entete(carte, sous_titre)
            + bandeau_verdict(carte, global_, couverture,
                              texte_verdict(carte, projets, global_, "projet"))
            + frise_orga(projets))
    t = totaux(projets)
    # Sur une orga, la liste de lots se coupe : dix projets de quatorze lots
    # donnent une image qu'on ne lit plus.
    par_projet = (tete + chiffres(t, "projets") + matrice(projets) + legende()
                  + repartir([(carte_synthese(p, date_carte, LOTS_EN_TITRES),
                               poids_synthese(p, LOTS_EN_TITRES))
                              for p in projets], colonnes or 3))
    restants = (tete + legende()
                + repartir([(carte_lots(p, date_carte, True), poids_lots(p, True))
                            for p in projets], colonnes or 3))
    return {
        "par-projet": page(f'{carte["nom"]} — par projet', par_projet),
        "lots-restants": page(f'{carte["nom"]} — lots restants', restants),
    }


# --------------------------------------------------------------------------
# PNG : Chrome ou Edge sans fenêtre
# --------------------------------------------------------------------------

LARGEUR_PNG = 1280


def trouver_navigateur() -> str | None:
    candidats = [os.environ.get("CHROME")]
    for nom in ("chrome", "google-chrome", "chromium", "chromium-browser", "msedge"):
        candidats.append(shutil.which(nom))
    for racine in (os.environ.get("PROGRAMFILES"), os.environ.get("PROGRAMFILES(X86)"),
                   os.environ.get("LOCALAPPDATA")):
        if racine:
            candidats.append(str(Path(racine) / "Google/Chrome/Application/chrome.exe"))
            candidats.append(str(Path(racine) / "Microsoft/Edge/Application/msedge.exe"))
    candidats.append("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
    return next((c for c in candidats if c and Path(c).exists()), None)


def lancer(navigateur: str, profil: str, *arguments: str) -> str:
    commande = [navigateur, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                "--no-first-run", "--no-default-browser-check",
                f"--user-data-dir={profil}", *arguments]
    sortie = subprocess.run(commande, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=120)
    return sortie.stdout


def hauteur_page(navigateur: str, profil: str, source: Path) -> int:
    """Mesure la vraie hauteur : le script ajouté l'écrit dans le DOM."""
    contenu = source.read_text(encoding="utf-8").replace(
        "</body>",
        "<script>document.title='H'+Math.ceil("
        "document.documentElement.getBoundingClientRect().height);"
        "document.body.dataset.h=document.title</script></body>")
    mesure = Path(profil) / "mesure.html"
    mesure.write_text(contenu, encoding="utf-8")
    dom = lancer(navigateur, profil, f"--window-size={LARGEUR_PNG},1000",
                 "--virtual-time-budget=2000", "--dump-dom", mesure.as_uri())
    trouve = re.search(r'data-h="H(\d+)"', dom)
    if not trouve:
        raise RuntimeError("hauteur de page introuvable")
    return int(trouve.group(1))


def capturer(navigateur: str, source: Path, cible: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="map-projet-") as profil:
        hauteur = hauteur_page(navigateur, profil, source)
        lancer(navigateur, profil, f"--window-size={LARGEUR_PNG},{hauteur}",
               "--force-device-scale-factor=2", f"--screenshot={cible}",
               "--virtual-time-budget=2000", source.as_uri())
    if not cible.exists():
        raise RuntimeError(f"capture non produite : {cible.name}")


# --------------------------------------------------------------------------
# Entrée
# --------------------------------------------------------------------------

def charger(chemin: Path) -> dict:
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erreur:
        raise CarteInvalide(f"JSON illisible : {erreur}") from erreur


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    parseur = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parseur.add_argument("carte", type=Path)
    parseur.add_argument("-o", "--sortie", type=Path)
    parseur.add_argument("--colonnes", type=int, choices=(1, 2, 3),
                         help="nombre de colonnes de cartes (défaut : 2 dans la "
                              "conversation ; 3 par volet et 2 par lot en HTML)")
    parseur.add_argument("--png", action="store_true",
                         help="ajoute une image PNG de chaque map (Chrome ou Edge)")
    parseur.add_argument("--verifier", action="store_true")
    options = parseur.parse_args()

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
    rendu = rendu_projet if carte["type"] == "projet" else rendu_orga
    pages = rendu(carte, options.colonnes)

    navigateur = trouver_navigateur() if options.png else None
    if options.png and not navigateur:
        print("Attention : ni Chrome ni Edge trouvé, pas de PNG. "
              "Indiquer le chemin dans la variable CHROME.", file=sys.stderr)

    resume = f'{carte["nom"]} : {carte["verdict"]}'
    for nom, contenu in pages.items():
        fragment = dossier / f"{nom}.widget.html"
        fragment.write_text(widget(contenu, resume, options.colonnes or 2),
                            encoding="utf-8")
        print(fragment)
        chemin = dossier / f"{nom}.html"
        chemin.write_text(contenu, encoding="utf-8")
        print(chemin)
        if navigateur:
            png = dossier / f"{nom}.png"
            capturer(navigateur, chemin.resolve(), png.resolve())
            print(png)
    return 0


if __name__ == "__main__":
    sys.exit(main())

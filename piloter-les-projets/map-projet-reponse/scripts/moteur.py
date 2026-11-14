#!/usr/bin/env python3
"""
moteur.py — contrôles et calculs d'un carte.json. Aucun rendu.

Ce fichier ne dessine rien. Il répond aux questions :
le fichier est-il valide, quelle est la phase d'un volet, quel est son verdict,
combien de lots sont faits, dans quel ordre lire les cartes.

`generer_widget.py` s'en sert pour fabriquer les deux maps de la réponse.
C'est le même moteur que la skill `map-projet`, qui, elle, écrit des fichiers :
une carte valide ici l'est là-bas, et donne les mêmes couleurs.

Le format complet du fichier est dans references/format-carte.md.
Aucune dépendance Python.
"""

from __future__ import annotations

import datetime as dt
import html
import json
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


def pluriel(nombre: int, mot: str) -> str:
    """« 1 lot », « 3 lots ». Les mots liés par « à » ne prennent pas de s."""
    return mot if nombre <= 1 else " ".join(
        m if m == "à" else f"{m}s" for m in mot.split(" "))


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

def e(texte) -> str:
    return html.escape(str(texte), quote=True)


def date_fr(valeur: str) -> str:
    d = dt.date.fromisoformat(valeur)
    return d.strftime("%d/%m/%Y")


def charger(chemin: Path) -> dict:
    try:
        return json.loads(chemin.read_text(encoding="utf-8"))
    except json.JSONDecodeError as erreur:
        raise CarteInvalide(f"JSON illisible : {erreur}") from erreur

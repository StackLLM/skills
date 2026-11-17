"""Contrôles qualité : données d'entrée, PDF (lecture ATS), cohérence des variantes."""

from __future__ import annotations

import re
import unicodedata
import zlib
from datetime import date
from pathlib import Path

from domaines import parse_date

EMAIL = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")


class Rapport:
    def __init__(self):
        self.erreurs: list[str] = []
        self.avertissements: list[str] = []
        self.ok: list[str] = []

    def erreur(self, m):
        if m not in self.erreurs:
            self.erreurs.append(m)

    def avert(self, m):
        if m not in self.avertissements:
            self.avertissements.append(m)
    def valide(self, m): self.ok.append(m)

    def dict(self):
        return {"erreurs": self.erreurs, "avertissements": self.avertissements, "ok": self.ok}


# ---------------------------------------------------------------------------
# 1. Données d'entrée
# ---------------------------------------------------------------------------
def verifier_donnees(cv: dict, r: Rapport, aujourd_hui: date | None = None) -> None:
    aujourd_hui = aujourd_hui or date.today()
    ident = cv.get("identite", {})
    if not ident.get("nom"):
        r.erreur("identite.nom manquant")
    if not ident.get("titre"):
        r.avert("identite.titre manquant : le poste visé aide fortement les ATS")
    if not ident.get("email"):
        r.erreur("identite.email manquant : un recruteur doit pouvoir répondre")
    elif not EMAIL.match(ident["email"]):
        r.erreur(f"email invalide : {ident['email']}")
    if not ident.get("telephone"):
        r.avert("identite.telephone manquant")
    elif len(re.sub(r"\D", "", ident["telephone"])) < 8:
        r.erreur(f"téléphone incomplet : {ident['telephone']}")
    if not cv.get("experiences") and not cv.get("formation"):
        r.erreur("ni expérience ni formation : contenu insuffisant pour un CV")

    for x in cv.get("experiences", []):
        nom = f"{x.get('poste', '?')} / {x.get('entreprise', '?')}"
        for champ in ("poste", "entreprise"):
            if not x.get(champ):
                r.erreur(f"expérience sans {champ} : {nom}")
        d, f = parse_date(x.get("debut")), parse_date(x.get("fin") or "present", aujourd_hui)
        if x.get("debut") and not d:
            r.avert(f"date de début illisible ({x.get('debut')}) : {nom}")
        if not x.get("debut"):
            r.avert(f"date de début manquante : {nom}")
        if d and f and f < d:
            r.erreur(f"dates incohérentes (fin avant début) : {nom}")
        if d and d > aujourd_hui:
            r.erreur(f"date de début dans le futur : {nom}")
        if not x.get("points"):
            r.avert(f"aucune mission décrite : {nom}")

    for fo in cv.get("formation", []):
        if not fo.get("diplome"):
            r.erreur("formation sans intitulé de diplôme")
        d, f = parse_date(fo.get("debut")), parse_date(fo.get("fin"))
        if d and f and f < d:
            r.erreur(f"dates de formation incohérentes : {fo.get('diplome')}")

    for point in cv.get("a_confirmer", []):
        r.avert(f"à confirmer avec le client : {point}")


# ---------------------------------------------------------------------------
# 2. PDF
# ---------------------------------------------------------------------------
def normaliser(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"[‐-―−]", "-", s)
    # Coupure de fin de ligne sur un trait d'union (« expert-⏎comptable ») : on recolle.
    s = re.sub(r"-[ \t]*\n\s*", "-", s)
    s = re.sub(r"[​­]", "", s)
    s = s.replace("’", "'")
    return re.sub(r"\s+", " ", s).strip()


def attendus(cv: dict) -> list[tuple[str, str]]:
    """Tout ce qui doit être lisible par un ATS, avec une étiquette."""
    out = []
    ident = cv["identite"]
    for champ in ("nom", "titre", "email", "ville"):
        if ident.get(champ):
            out.append((f"identité : {champ}", ident[champ]))
    for x in cv.get("experiences", []):
        out += [("poste", x.get("poste", "")), ("entreprise", x.get("entreprise", "")),
                ("date", x.get("debut", "")), ("date", x.get("fin", ""))]
        out += [("mission", p) for p in x.get("points", [])]
    for f in cv.get("formation", []):
        out += [("diplôme", f.get("diplome", "")), ("établissement", f.get("etablissement", ""))]
    for g in cv.get("competences", []):
        if isinstance(g, dict):
            out += [("compétence", el) for el in g.get("elements", [])]
        else:
            out.append(("compétence", g))
    for c in cv.get("certifications", []):
        out.append(("certification", c["nom"] if isinstance(c, dict) else c))
    for l in cv.get("langues", []):
        out.append(("langue", l["langue"] if isinstance(l, dict) else l))
    for p in cv.get("projets", []):
        # Le point final est replacé après les technologies : on compare sans lui.
        out += [("projet", p.get("nom", "")), ("projet", p.get("description", "").strip().rstrip("."))]
    out += [("réalisation", x) for x in cv.get("realisations", [])]
    if cv.get("profil"):
        out.append(("profil", cv["profil"]))
    return [(k, v) for k, v in out if v and str(v).strip()]


def ligatures_et_polices(pdf: Path) -> tuple[int, bool]:
    """Compte les glyphes « multi-lettres » (ligatures) et vérifie l'intégration des polices."""
    data = pdf.read_bytes()
    blobs = [data]
    for m in re.finditer(rb"stream\r?\n", data):
        fin = data.find(b"endstream", m.end())
        try:
            blobs.append(zlib.decompress(data[m.end():fin]))
        except Exception:
            pass
    tout = b"".join(blobs)
    ligatures = 0
    for b in blobs:
        if b"begincmap" in b:
            ligatures += len(re.findall(rb"<[0-9a-fA-F]+>\s*<[0-9a-fA-F]{4}\s?[0-9a-fA-F]{4}>", b))
    polices = b"/FontFile" in tout
    return ligatures, polices


def contraste(hex_a: str, hex_b: str) -> float:
    def lum(h):
        h = h.lstrip("#")
        c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
        return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
    a, b = sorted((lum(hex_a), lum(hex_b)), reverse=True)
    return (a + 0.05) / (b + 0.05)


def verifier_pdf(cv: dict, plan: dict, pdf: Path, extrait: dict, ajust: dict, theme: dict, r: Rapport) -> str:
    """Contrôle un PDF ; renvoie son texte normalisé (pour comparer les variantes)."""
    nom = pdf.name
    texte = normaliser("\n".join(extrait["textes"]))

    # Pagination
    if ajust.get("debordement"):
        r.erreur(f"{nom} : le contenu ne tient pas sur 2 pages, il faut condenser")
    pages = extrait["pages"]
    if pages == 2 and plan["niveau"] != "senior":
        r.avert(f"2 pages pour un profil {plan['niveau']} — condenser si possible")
    if any(abs(w - 595.28) > 1 or abs(h - 841.89) > 1 for w, h in extrait["formats"]):
        r.erreur(f"{nom} : format de page différent de l'A4")
    if ajust.get("debordements_horizontaux"):
        r.erreur(f"{nom} : texte qui dépasse à droite : {ajust['debordements_horizontaux'][:3]}")
    if ajust.get("part_vide", 0) > 0.25 and pages == 1:
        r.avert(f"page remplie à {round((1 - ajust['part_vide']) * 100)} % — demander au client "
                f"plus de détails (missions, résultats, projets), sans rien inventer")
    if ajust.get("corps_texte_pt", 9) < 8.4:
        r.avert(f"{nom} : texte réduit à {ajust['corps_texte_pt']} pt")

    # Lecture ATS : rien ne doit manquer, et chaque phrase doit se lire dans l'ordre.
    mots = set(re.findall(r"\w+", texte))
    manquants, desordre = [], []
    for k, v in attendus(cv):
        cible = normaliser(str(v))
        if cible in texte:
            continue
        # Tous les mots sont là mais pas dans l'ordre : une ligne très courte a été lue
        # à part par le lecteur PDF. Reformuler la phrase pour supprimer cette ligne.
        (desordre if set(re.findall(r"\w+", cible)) <= mots else manquants).append(f"{k} « {v[:60]} »")
    tel = cv["identite"].get("telephone")
    if tel and re.sub(r"\D", "", tel) not in re.sub(r"\D", "", texte):
        manquants.append(f"téléphone « {tel} »")
    if manquants:
        r.erreur(f"{nom} : {len(manquants)} élément(s) illisibles par un ATS : {manquants[:5]}")
    for x in desordre:
        r.erreur(f"ordre de lecture ATS perturbé (ligne finale trop courte) — reformuler : {x}")

    # Ordre de lecture : les postes dans l'ordre donné
    positions = [texte.find(normaliser(x["poste"])) for x in cv.get("experiences", []) if x.get("poste")]
    if positions and positions != sorted(positions):
        r.erreur(f"{nom} : ordre de lecture des expériences incorrect")

    # Ligatures, polices, liens
    ligatures, polices = ligatures_et_polices(pdf)
    if ligatures:
        r.erreur(f"{nom} : {ligatures} ligature(s) — un ATS perdrait des lettres")
    if not polices:
        r.erreur(f"{nom} : polices non intégrées")
    liens_attendus = []
    ident = cv["identite"]
    if ident.get("email"):
        liens_attendus.append("mailto:" + ident["email"])
    liens_attendus += [l["url"] for l in ident.get("liens", [])]
    absents = [u for u in liens_attendus if not any(x.rstrip("/") == u.rstrip("/") for x in extrait["liens"])]
    if absents:
        r.erreur(f"{nom} : liens non cliquables : {absents}")

    # Couleurs
    for fond, nom_fond in (("#ffffff", "blanc"), ("#f8fafc", "colonne latérale")):
        c = contraste(theme["accent_texte"], fond)
        if c < 4.5:
            r.erreur(f"{nom} : contraste insuffisant sur {nom_fond} ({c:.1f}:1)")

    # Mise en page identique pour les 3 couleurs : un seul message par ligne concernée.
    for ligne in ajust.get("lignes_courtes", []):
        r.avert(f"mot isolé en fin de ligne, reformuler : « …{ligne} »")

    if not r.erreurs:
        r.valide(f"{nom} : {pages} page(s), texte {ajust.get('corps_texte_pt')} pt, espacement ×{ajust.get('air')}, "
                 f"{len(attendus(cv))} éléments lus, {len(extrait['liens'])} liens")
    return texte


def verifier_variantes(textes: dict[str, str], r: Rapport) -> None:
    noms = list(textes)
    reference = textes[noms[0]]
    for n in noms[1:]:
        if textes[n] != reference:
            r.erreur(f"les variantes {noms[0]} et {n} n'ont pas exactement le même texte")
    if len(noms) > 1 and all(textes[n] == reference for n in noms[1:]):
        r.valide(f"{len(noms)} variantes : texte strictement identique")

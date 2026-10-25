"""Rendu HTML du CV à partir du JSON structuré et du plan de domaine."""

from __future__ import annotations

import html
import re
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# Trois identités visuelles. Seules ces deux couleurs changent d'une version à l'autre.
THEMES = {
    "bleu": {"nom": "Bleu", "accent": "#00478c", "accent_texte": "#00478c"},
    "emeraude": {"nom": "Emeraude", "accent": "#0b6655", "accent_texte": "#0b6655"},
    "bordeaux": {"nom": "Bordeaux", "accent": "#7a1f3d", "accent_texte": "#7a1f3d"},
}

LIBELLES_LIENS = {
    "linkedin": "LinkedIn", "github": "GitHub", "gitlab": "GitLab", "portfolio": "Portfolio",
    "behance": "Behance", "dribbble": "Dribbble", "site": "Site web", "website": "Website",
}

e = html.escape

# Résultats chiffrés mis en gras : pourcentages, montants, multiplicateurs, hausses/baisses.
_CHIFFRE = re.compile(
    r"(?<![\w/.])("
    r"[£$€]\s?\d[\d.,]*\s?(?:[kKMB]|bn|million|millions)?"
    r"|\d[\d  .,]*\s?(?:milliards?|millions?|billions?)\s?(?:de\s)?(?:MAD|DH|dirhams|€|euros|\$|USD|EUR)"
    r"|[+\-−]\s?\d[\d  .,]*(?:\s?(?:%|€|k€|K€|M€|MAD|DH|MDH|KDH|k|K|M|\$|pts?))?"
    r"|\d[\d  .,]*\s?(?:%|€|k€|K€|M€|MAD|DH|MDH|KDH|M\$|k\$|\$|pts?)"
    r"|[x×]\s?\d+(?:[.,]\d+)?|\d+(?:[.,]\d+)?\s?[x×]"
    r")(?![\w])"
)


def texte_html(brut: str) -> str:
    """Échappe un texte de contenu (les apostrophes restent des apostrophes)."""
    return html.escape(brut, quote=False)


def gras_chiffres(brut: str) -> str:
    """Met en gras les résultats chiffrés. Travaille sur le texte BRUT, puis échappe
    chaque morceau : appliquer la regex sur du HTML casserait les entités (&#x27;)."""
    morceaux, debut = [], 0
    for m in _CHIFFRE.finditer(brut):
        chiffre = m.group(1).strip()
        if not chiffre:
            continue
        fin_chiffre = m.start(1) + len(m.group(1).rstrip())
        morceaux.append(texte_html(brut[debut:m.start(1)]))
        # « 70 MDH » ou « 14 % » ne se coupent jamais (white-space: nowrap, pas d'espace
        # insécable : certains lecteurs PDF perdent la fin de ligne qui en contient une).
        morceaux.append(f'<strong class="chiffre">{texte_html(chiffre)}</strong>')
        debut = fin_chiffre
    morceaux.append(texte_html(brut[debut:]))
    return "".join(morceaux)


def lien_tel(numero: str) -> str:
    return "tel:" + re.sub(r"[^\d+]", "", numero)


def url_courte(url: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", url).rstrip("/")


class Rendu:
    def __init__(self, cv: dict, plan: dict, photo_fichier: str | None):
        self.cv, self.plan, self.photo = cv, plan, photo_fichier
        self.t = plan["titres"]
        # Deux-points : espace avant en français, pas en anglais.
        self.dp = " : " if plan["langue"] == "fr" else ": "

    # ---------- utilitaires ----------
    def texte(self, valeur: str, chiffres: bool = False) -> str:
        brut = str(valeur).strip()
        return gras_chiffres(brut) if chiffres and self.plan["chiffres_en_gras"] else texte_html(brut)

    def periode(self, debut: str | None, fin: str | None) -> str:
        debut, fin = (debut or "").strip(), (fin or "").strip()
        if not fin and debut:
            fin = self.t["present"]
        if debut and fin:
            return f"{e(debut)} – {e(fin)}"
        return e(debut or fin)

    def titre(self, cle: str) -> str:
        return f"<h2>{e(self.t[cle])}</h2>"

    # ---------- en-tête ----------
    def entete(self) -> str:
        ident = self.cv["identite"]
        items = []
        if ident.get("telephone"):
            items.append(f'<li><a href="{e(lien_tel(ident["telephone"]))}">{e(ident["telephone"])}</a></li>')
        if ident.get("email"):
            items.append(f'<li><a href="mailto:{e(ident["email"])}">{e(ident["email"])}</a></li>')
        for lien in ident.get("liens", []):
            libelle = lien.get("libelle") or LIBELLES_LIENS.get(lien.get("type", "").lower()) or url_courte(lien["url"])
            items.append(f'<li><a href="{e(lien["url"])}">{e(libelle)}</a></li>')
        if ident.get("ville"):
            items.append(f"<li>{e(ident['ville'])}</li>")
        if ident.get("age"):
            items.append(f"<li>{e(str(ident['age']))} {e(self.t['ans'])}</li>")
        for autre in ident.get("autres", []):
            items.append(f"<li>{e(autre)}</li>")

        photo = ""
        if self.photo:
            photo = f'<img class="photo" src="{e(self.photo)}" alt="Photo de {e(ident["nom"])}">\n    '
        classe = "" if self.photo else ' class="sans-photo"'
        titre = f'<p class="titre">{e(ident["titre"])}</p>' if ident.get("titre") else ""
        return f"""  <header{classe}>
    {photo}<div>
      <h1>{e(ident["nom"])}</h1>
      {titre}
      <div class="filet"></div>
      <ul class="coordonnees">
        {chr(10).join("        " + i for i in items).strip()}
      </ul>
    </div>
  </header>"""

    # ---------- sections ----------
    def s_profil(self, colonne: str) -> str:
        if not self.cv.get("profil"):
            return ""
        return f'<section data-section="profil">\n{self.titre("profil")}\n<p>{self.texte(self.cv["profil"])}</p>\n</section>'

    def s_experiences(self, colonne: str) -> str:
        exps = self.cv.get("experiences", [])
        if not exps:
            return ""
        cle = "experiences_junior" if self.plan["niveau"] == "junior" and any(
            "stage" in (x.get("poste", "") + x.get("type", "")).lower() for x in exps) else "experiences"
        blocs = []
        for x in exps:
            lieu = f' <span class="lieu">· {e(x["lieu"])}</span>' if x.get("lieu") else ""
            points = "".join(f"<li>{self.texte(p, chiffres=True)}</li>" for p in x.get("points", []))
            ul = f'<ul class="points">{points}</ul>' if points else ""
            blocs.append(
                f'<div class="bloc"><div class="tete"><div class="entete"><h3>{e(x["poste"])}</h3>'
                f'<span class="date">{self.periode(x.get("debut"), x.get("fin"))}</span></div>'
                f'<p class="role">{e(x.get("entreprise", ""))}{lieu}</p></div>{ul}</div>'
            )
        return f'<section data-section="experiences">\n{self.titre(cle)}\n' + "\n".join(blocs) + "\n</section>"

    def s_projets(self, colonne: str) -> str:
        projets = self.cv.get("projets", [])
        if not projets:
            return ""
        items = []
        for p in projets:
            brut = p.get("description", "").strip()
            techno = ""
            if p.get("technologies"):
                fin = "." if brut.endswith(".") else ""
                brut = brut.rstrip(".")
                techno = f" ({texte_html(', '.join(p['technologies']))}){fin}"
            desc = self.texte(brut, chiffres=True)
            lien = f' — <a href="{e(p["lien"])}">{e(url_courte(p["lien"]))}</a>' if p.get("lien") else ""
            sep = self.dp if desc else ""
            items.append(f"<li><strong>{e(p['nom'])}</strong>{sep}{desc}{techno}{lien}</li>")
        return f'<section data-section="projets">\n{self.titre("projets")}\n<ul class="points">{"".join(items)}</ul>\n</section>'

    def s_realisations(self, colonne: str) -> str:
        r = self.cv.get("realisations", [])
        if not r:
            return ""
        items = "".join(f"<li>{self.texte(x, chiffres=True)}</li>" for x in r)
        return f'<section data-section="realisations">\n{self.titre("realisations")}\n<ul class="points">{items}</ul>\n</section>'

    def s_formation(self, colonne: str) -> str:
        f = self.cv.get("formation", [])
        if not f:
            return ""
        blocs = []
        for d in f:
            mention = d.get("mention", "")
            if colonne == "laterale":
                ecole = ", ".join(x for x in (d.get("etablissement", ""), d.get("lieu", "")) if x)
                date_txt = self.periode(d.get("debut"), d.get("fin"))
                if mention:
                    date_txt = f"{date_txt} · {e(mention)}" if date_txt else e(mention)
                detail = f'<p class="ecole">{e(d["detail"])}</p>' if d.get("detail") else ""
                blocs.append(f'<div class="bloc"><h3>{e(d["diplome"])}</h3><p class="ecole">{e(ecole)}</p>{detail}'
                             f'<p class="date">{date_txt}</p></div>')
            else:
                infos = " · ".join(e(x) for x in (d.get("etablissement", ""), d.get("lieu", ""), mention) if x)
                detail = f" — {e(d['detail'])}" if d.get("detail") else ""
                blocs.append(f'<div class="bloc"><div class="tete"><div class="entete"><h3>{e(d["diplome"])}</h3>'
                             f'<span class="date">{self.periode(d.get("debut"), d.get("fin"))}</span></div>'
                             f'<p class="ecole">{infos}{detail}</p></div></div>')
        notes = "".join(f'<p class="note">{e(n)}</p>' for n in self.cv.get("notes_formation", []))
        return (f'<section class="formation" data-section="formation">\n{self.titre("formation")}\n'
                + "\n".join(blocs) + notes + "\n</section>")

    def s_competences(self, colonne: str) -> str:
        groupes = self.cv.get("competences", [])
        if not groupes:
            return ""
        items = []
        libres = [g for g in groupes if isinstance(g, str)]
        for g in groupes:
            if isinstance(g, dict):
                items.append(f"<li><strong>{e(g['groupe'])}</strong>{e(', '.join(g.get('elements', [])))}</li>")
        if libres:
            items.append(f"<li>{e(', '.join(libres))}</li>")
        return (f'<section class="competences" data-section="competences">\n<h2>{e(self.plan["titre_competences"])}</h2>\n'
                f'<ul>{"".join(items)}</ul>\n</section>')

    def s_certifications(self, colonne: str) -> str:
        certs = self.cv.get("certifications", [])
        if not certs:
            return ""
        items = []
        for c in certs:
            if isinstance(c, dict):
                txt = c["nom"]
                if c.get("organisme"):
                    txt += f" — {c['organisme']}"
                if c.get("annee"):
                    txt += f" ({c['annee']})"
            else:
                txt = c
            items.append(f"<li>{e(txt)}</li>")
        return (f'<section data-section="certifications" data-mobile="certifications">\n{self.titre("certifications")}\n'
                f'<ul class="points">{"".join(items)}</ul>\n</section>')

    def s_langues(self, colonne: str) -> str:
        langues = self.cv.get("langues", [])
        if not langues:
            return ""
        items = "".join(
            (f"<li><strong>{e(l['langue'])}</strong>{self.dp}{e(l['niveau'])}</li>" if l.get("niveau") else f"<li><strong>{e(l['langue'])}</strong></li>")
            if isinstance(l, dict) else f"<li>{e(l)}</li>"
            for l in langues)
        return (f'<section data-section="langues" data-mobile="langues">\n{self.titre("langues")}\n'
                f'<ul class="points">{items}</ul>\n</section>')

    def s_qualites(self, colonne: str) -> str:
        soft, interets = self.cv.get("soft_skills", []), self.cv.get("interets", [])
        if not soft and not interets:
            return ""
        cle = "soft_interets" if soft and interets else ("soft_skills" if soft else "interets")
        items = []
        if soft:
            texte = ", ".join(soft)
            items.append(f"<li>{e(texte[0].upper() + texte[1:])}</li>")
        if interets:
            texte = ", ".join(interets)
            if soft:
                texte = f"{self.t['interets']}{self.dp}{texte}"
            else:
                texte = texte[0].upper() + texte[1:]
            items.append(f"<li>{texte_html(texte)}</li>")
        return (f'<section data-section="qualites" data-mobile="qualites">\n{self.titre(cle)}\n'
                f'<ul class="points">{"".join(items)}</ul>\n</section>')

    # ---------- page complète ----------
    def colonne(self, nom: str) -> list[str]:
        sections = []
        for cle in self.plan[nom]:
            contenu = getattr(self, f"s_{cle}")(nom)
            if contenu:
                sections.append(contenu)
        return sections

    def page(self, theme: dict, liaison: bool = True) -> str:
        ident = self.cv["identite"]
        css = (ASSETS / "cv.css").read_text(encoding="utf-8")
        js = (ASSETS / "ajustement.js").read_text(encoding="utf-8")
        principale = "\n\n".join(self.colonne("principale"))
        laterale_sections = self.colonne("laterale")
        laterale = ("\n    <aside class=\"laterale\">\n" + "\n\n".join(laterale_sections) + "\n    </aside>") if laterale_sections else ""
        style_corps = "" if laterale_sections else '<style>.corps { grid-template-columns: 1fr; }</style>'
        desc = f'{ident["nom"]} — {ident.get("titre", "")}'
        return f"""<!doctype html>
<html lang="{e(self.plan['langue'])}" data-liaison="{'oui' if liaison else 'non'}">
<head>
<meta charset="utf-8">
<title>CV — {e(ident["nom"])}</title>
<meta name="author" content="{e(ident["nom"])}">
<meta name="description" content="{e(desc)}">
<style>
{css}
:root {{ --accent: {theme["accent"]}; --accent-texte: {theme["accent_texte"]}; }}
</style>
{style_corps}
</head>
<body>
<div class="page">

{self.entete()}

  <div class="corps">
    <main class="principale">
{principale}
    </main>{laterale}
  </div>
</div>
<script>
{js}
</script>
</body>
</html>
"""

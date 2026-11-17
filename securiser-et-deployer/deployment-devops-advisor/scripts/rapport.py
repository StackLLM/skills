#!/usr/bin/env python3
"""
rapport.py — rend un fichier de constats en rapport HTML premium.

    python rapport.py constats.json -o "Audit-securite-MonProjet.html"

Le HTML ne s'écrit pas à la main. On écrit le JSON, le script rend la page.
Trois raisons : la charte est toujours tenue, les deux agents rendent la même
mise en page, et **les secrets sont masqués avant d'être écrits** — un oubli
humain ne peut pas faire fuiter une clé dans le rapport.

Le script refuse de rendre si un constat n'a pas de niveau de confiance, ou si
son niveau de criticité est inconnu. Un audit sans ces deux informations
raconte des certitudes qu'il n'a pas.

Forme du JSON : voir constats.exemple.json et references/rapport-html.md.
Aucune dépendance : bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import html as _html
import json
import re
import sys
from pathlib import Path

CRITICITES = {
    "CRITIQUE":    ("#9E2B20", "#FBF2F0", "#7E2118"),
    "ÉLEVÉ":       ("#B26A00", "#FDF8F0", "#8A5200"),
    "MOYEN":       ("#A08200", "#FBF8EA", "#7A6300"),
    "FAIBLE":      ("#3E88B5", "#E6F0F7", "#215C80"),
    "INFORMATION": ("#5C6873", "#F4F1EA", "#5C6873"),
}
ORDRE = list(CRITICITES)
CONFIANCES = ("Confirmé", "Probable", "À vérifier", "Non vérifiable")

# --- Masquage des secrets ----------------------------------------------------
# Filet de sécurité, pas la première ligne de défense : la skill dit déjà de ne
# jamais coller une valeur entière. Ces motifs rattrapent l'oubli.
MOTIFS_SECRET = [
    re.compile(r"\b(sk-[A-Za-z0-9_\-]{16,})"),              # OpenAI, OpenRouter
    re.compile(r"\b(sk_live_[A-Za-z0-9]{16,})"),            # Stripe
    re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,})"),          # GitHub
    re.compile(r"\b((?:AKIA|ASIA)[A-Z0-9]{12,})"),          # AWS
    re.compile(r"\b(AIza[A-Za-z0-9_\-]{30,})"),             # Google
    re.compile(r"\b(xox[abprs]-[A-Za-z0-9\-]{10,})"),       # Slack
    re.compile(r"\b(eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]+)"),  # JWT
    re.compile(r"://[^\s:/@]+:([^\s@]{6,})@"),              # mot de passe dans une URL
    re.compile(r"""(?i)\b(?:password|passwd|secret|token|api[_-]?key)\s*[=:]\s*["']?([^\s"',;]{8,})"""),
]


def masquer_valeur(valeur: str) -> str:
    """`sk-abcdefgh1234` devient `sk-a……34`. Assez pour reconnaître, pas pour s'en servir."""
    if len(valeur) <= 6:
        return "•" * len(valeur)
    return f"{valeur[:4]}{'•' * 8}{valeur[-2:]}"


def masquer(texte: str) -> str:
    for motif in MOTIFS_SECRET:
        def remplacer(m: re.Match) -> str:
            entier, valeur = m.group(0), m.group(1)
            return entier.replace(valeur, masquer_valeur(valeur))
        texte = motif.sub(remplacer, texte)
    return texte


def e(valeur) -> str:
    """Échappe pour le HTML, après masquage. Le gras passe par **texte**."""
    s = _html.escape(masquer(str(valeur if valeur is not None else "")), quote=False)
    morceaux = s.split("**")
    for i in range(1, len(morceaux), 2):
        morceaux[i] = f"<strong>{morceaux[i]}</strong>"
    return "".join(morceaux)


def mono(valeur) -> str:
    return f'<code>{e(valeur)}</code>' if valeur else ""


# --- Validation --------------------------------------------------------------

def valider(donnees: dict) -> list[str]:
    """Les erreurs qui empêchent de rendre le rapport."""
    erreurs = []
    for section in donnees.get("sections", []):
        for c in section.get("constats", []):
            ou = f"« {c.get('titre', 'sans titre')} »"
            if c.get("criticite") not in CRITICITES:
                erreurs.append(f"{ou} : criticité « {c.get('criticite')} » inconnue. "
                               f"Attendu : {', '.join(ORDRE)}.")
            if c.get("confiance") not in CONFIANCES:
                erreurs.append(f"{ou} : confiance « {c.get('confiance')} » manquante "
                               f"ou inconnue. Attendu : {', '.join(CONFIANCES)}.")
    return erreurs


# --- Rendu -------------------------------------------------------------------

def rendre_constat(c: dict) -> str:
    trait, fond, encre = CRITICITES[c["criticite"]]
    p = [f'<article class="constat" style="border-left-color:{trait}">',
         '  <div class="constat-tete">',
         f'    <span class="badge" style="background:{fond};color:{encre}">{e(c["criticite"])}</span>',
         f'    <span class="confiance">{e(c["confiance"])}</span>']
    if c.get("norme"):
        p.append(f'    <span class="norme">{e(c["norme"])}</span>')
    p += ['  </div>',
          f'  <h3>{e(c["titre"])}</h3>']

    for cle, libelle in (("pourquoi", "Pourquoi c'est dangereux"),
                         ("impact", "Ce qui peut arriver"),
                         ("ou", "Où"),
                         ("verifier", "Comment le constater"),
                         ("prouver", "Comment savoir que c'est réparé")):
        if not c.get(cle):
            continue
        valeur = mono(c[cle]) if cle == "ou" else e(c[cle])
        p += [f'  <div class="champ"><div class="champ-titre">{libelle}</div>',
              f'    <p>{valeur}</p></div>']

    if c.get("chemin"):
        etapes = '\n<span class="fleche">↓</span>\n'.join(
            f'<span class="etape">{e(x)}</span>' for x in c["chemin"])
        p += ['  <div class="champ"><div class="champ-titre">Le chemin</div>',
              f'    <div class="escalier">{etapes}</div></div>']

    if c.get("corriger"):
        pas = "".join(f"<li>{e(x)}</li>" for x in c["corriger"])
        p += ['  <div class="champ"><div class="champ-titre">Comment le corriger</div>',
              f'    <ol class="etapes">{pas}</ol></div>']

    p.append('</article>')
    return "\n".join(p)


def rendre(donnees: dict) -> str:
    sections = donnees.get("sections", [])
    tous = [c for s in sections for c in s.get("constats", [])]
    comptes = {n: sum(1 for c in tous if c["criticite"] == n) for n in ORDRE}

    cartes = "".join(
        f'<div class="compte" style="border-top-color:{CRITICITES[n][0]}">'
        f'<div class="compte-nombre" style="color:{CRITICITES[n][2]}">{comptes[n]}</div>'
        f'<div class="compte-nom">{n}</div></div>'
        for n in ORDRE if comptes[n])

    archi = "".join(
        f'<div class="fiche"><div class="fiche-label">{e(a.get("titre"))}</div>'
        f'<div class="fiche-valeur">{e(a.get("valeur"))}</div>'
        + (f'<div class="fiche-note">{e(a["note"])}</div>' if a.get("note") else "")
        + '</div>'
        for a in donnees.get("architecture", []))

    corps = []
    for s in sections:
        constats = s.get("constats", [])
        if not constats and not s.get("intro"):
            continue
        constats.sort(key=lambda c: ORDRE.index(c["criticite"]))
        corps.append(f'<section class="bloc"><h2>{e(s.get("titre"))}</h2>')
        if s.get("intro"):
            corps.append(f'<p class="intro">{e(s["intro"])}</p>')
        corps += [rendre_constat(c) for c in constats]
        corps.append("</section>")

    plan = ""
    if donnees.get("plan"):
        groupes = "".join(
            f'<div class="plan-groupe"><div class="plan-quand">{e(g.get("quand"))}</div>'
            f'<ol class="etapes">{"".join(f"<li>{e(x)}</li>" for x in g.get("actions", []))}</ol></div>'
            for g in donnees["plan"])
        plan = f'<section class="bloc"><h2>Plan de correction</h2>{groupes}</section>'

    checklists = ""
    if donnees.get("checklists"):
        blocs = "".join(
            f'<div class="carte"><h3>{e(cl.get("titre"))}</h3>'
            f'<ul class="cases">{"".join(f"<li>{e(x)}</li>" for x in cl.get("items", []))}</ul></div>'
            for cl in donnees["checklists"])
        checklists = f'<section class="bloc"><h2>Checklists</h2><div class="rangee">{blocs}</div></section>'

    limites = ""
    if donnees.get("limites"):
        items = "".join(f"<li>{e(x)}</li>" for x in donnees["limites"])
        limites = ('<section class="bloc"><h2>Ce qui n\'a pas pu être vérifié</h2>'
                   '<p class="intro">Un audit qui ne dit pas ses limites laisse croire '
                   'que tout a été regardé.</p>'
                   f'<div class="carte"><ul class="puces">{items}</ul></div></section>')

    depots = donnees.get("depots", [])
    ligne_depots = (f'<div class="fiche"><div class="fiche-label">Analysé</div>'
                    f'<div class="fiche-valeur">{e(", ".join(depots))}</div></div>'
                    if depots else "")

    return f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(donnees.get("titre", "Rapport"))} — {e(donnees.get("projet", ""))}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600&family=Source+Serif+4:wght@600&family=JetBrains+Mono&display=swap" rel="stylesheet">
<style>
:root{{
  --beige:#F2EDE1; --creme:#FAF7F0; --surface:#FFFFFF; --bordure:#E4DCCB; --sable:#EFE7D6;
  --encre:#1E2C38; --gris:#5C6873; --eteint:#96A1AB;
  --accent:#3E88B5; --accent-fonce:#215C80; --accent-pale:#E6F0F7; --accent-bord:#C3DCEB;
  --ombre:0 2px 6px rgba(30,44,56,.06);
}}
*{{box-sizing:border-box;}}
body{{margin:0;background:var(--beige);color:var(--encre);
  font-family:'IBM Plex Sans',Arial,sans-serif;font-size:15.5px;line-height:1.7;}}
h1,h2,h3{{font-family:'Source Serif 4',Georgia,serif;font-weight:600;margin:0;}}
code{{font-family:'JetBrains Mono',Consolas,monospace;font-size:13px;
  background:var(--creme);border:1px solid var(--bordure);border-radius:5px;
  padding:1px 5px;color:var(--accent-fonce);word-break:break-all;}}
.page{{max-width:980px;margin:0 auto;padding:0 28px 80px;}}

.couverture{{background:var(--creme);border-bottom:1px solid var(--bordure);
  padding:72px 28px 56px;margin-bottom:44px;}}
.couverture-corps{{max-width:980px;margin:0 auto;}}
.surtitre{{font-size:11.5px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;
  color:var(--accent-fonce);}}
.couverture h1{{font-size:46px;line-height:1.15;margin:14px 0 10px;}}
.sous{{font-size:18px;color:var(--gris);max-width:640px;}}
.risque{{display:inline-block;margin-top:26px;padding:8px 20px;border-radius:999px;
  background:var(--accent-pale);border:1px solid var(--accent-bord);
  color:var(--accent-fonce);font-weight:600;font-size:13.5px;
  letter-spacing:.06em;text-transform:uppercase;}}

.fiches{{display:flex;flex-wrap:wrap;gap:14px;margin-top:30px;}}
.fiche{{flex:1 1 200px;background:var(--surface);border:1px solid var(--bordure);
  border-radius:14px;box-shadow:var(--ombre);padding:14px 18px;}}
.fiche-label{{font-size:11.5px;font-weight:600;letter-spacing:.1em;
  text-transform:uppercase;color:var(--accent-fonce);}}
.fiche-valeur{{font-size:16px;font-weight:600;margin-top:4px;}}
.fiche-note{{font-size:13.5px;color:var(--gris);margin-top:3px;}}

.comptes{{display:flex;flex-wrap:wrap;gap:14px;margin:0 0 40px;}}
.compte{{flex:1 1 120px;background:var(--surface);border:1px solid var(--bordure);
  border-top-width:4px;border-radius:14px;box-shadow:var(--ombre);
  padding:16px 18px;text-align:center;}}
.compte-nombre{{font-family:'Source Serif 4',Georgia,serif;font-size:36px;font-weight:600;
  line-height:1;}}
.compte-nom{{font-size:11.5px;font-weight:600;letter-spacing:.1em;
  text-transform:uppercase;color:var(--gris);margin-top:6px;}}

.bloc{{margin:0 0 52px;}}
.bloc h2{{font-size:30px;padding-bottom:12px;border-bottom:1px solid var(--bordure);
  margin-bottom:20px;}}
.intro{{color:var(--gris);margin:0 0 22px;max-width:720px;}}
.rangee{{display:flex;flex-wrap:wrap;gap:16px;align-items:stretch;}}
.carte{{flex:1 1 300px;background:var(--surface);border:1px solid var(--bordure);
  border-radius:20px;box-shadow:var(--ombre);padding:22px 26px;}}
.carte h3{{font-size:19px;margin-bottom:10px;}}

.constat{{background:var(--surface);border:1px solid var(--bordure);border-left-width:5px;
  border-radius:20px;box-shadow:var(--ombre);padding:24px 28px;margin:0 0 18px;}}
.constat-tete{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:10px;}}
.badge{{font-size:11.5px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;
  padding:4px 12px;border-radius:999px;}}
.confiance{{font-family:'JetBrains Mono',Consolas,monospace;font-size:12px;
  color:var(--gris);border:1px solid var(--bordure);border-radius:999px;padding:3px 10px;}}
.norme{{font-size:12px;color:var(--eteint);}}
.constat h3{{font-size:19px;line-height:1.35;margin-bottom:14px;}}
.champ{{margin-top:14px;}}
.champ-titre{{font-size:11.5px;font-weight:600;letter-spacing:.1em;
  text-transform:uppercase;color:var(--accent-fonce);margin-bottom:3px;}}
.champ p{{margin:0;}}

.escalier{{background:var(--creme);border:1px solid var(--bordure);border-radius:14px;
  padding:16px 20px;text-align:center;}}
.etape{{display:block;font-size:14.5px;font-weight:600;}}
.fleche{{display:block;color:var(--accent);font-size:16px;line-height:1.4;}}

ol.etapes{{margin:6px 0 0;padding-left:0;list-style:none;counter-reset:pas;}}
ol.etapes li{{position:relative;padding:5px 0 5px 34px;counter-increment:pas;}}
ol.etapes li::before{{content:counter(pas);position:absolute;left:0;top:7px;
  width:22px;height:22px;border-radius:50%;background:var(--accent-pale);
  border:1px solid var(--accent-bord);color:var(--accent-fonce);
  font-size:12px;font-weight:600;text-align:center;line-height:20px;}}
ul.cases,ul.puces{{margin:0;padding-left:0;list-style:none;}}
ul.cases li{{position:relative;padding:5px 0 5px 28px;}}
ul.cases li::before{{content:"";position:absolute;left:0;top:11px;width:13px;height:13px;
  border:1.5px solid var(--accent-bord);border-radius:4px;background:var(--creme);}}
ul.puces li{{position:relative;padding:4px 0 4px 18px;}}
ul.puces li::before{{content:"—";position:absolute;left:0;color:var(--eteint);}}

.plan-groupe{{background:var(--surface);border:1px solid var(--bordure);border-radius:20px;
  box-shadow:var(--ombre);padding:20px 26px;margin-bottom:14px;}}
.plan-quand{{font-size:11.5px;font-weight:600;letter-spacing:.1em;text-transform:uppercase;
  color:var(--accent-fonce);}}

.pied{{background:var(--creme);border-top:1px solid var(--bordure);
  padding:26px;text-align:center;color:var(--eteint);font-size:13px;}}
@media print{{body{{background:#fff;}} .constat,.carte,.fiche{{break-inside:avoid;}}}}
</style></head><body>

<header class="couverture"><div class="couverture-corps">
  <div class="surtitre">{e(donnees.get("surtitre", "Rapport"))}</div>
  <h1>{e(donnees.get("titre", ""))}</h1>
  <p class="sous">{e(donnees.get("projet", ""))}{" · " + e(donnees["date"]) if donnees.get("date") else ""}</p>
  {f'<div class="risque">Risque global : {e(donnees["risque_global"])}</div>' if donnees.get("risque_global") else ""}
  <div class="fiches">{ligne_depots}</div>
</div></header>

<main class="page">
  {f'<section class="bloc"><h2>En résumé</h2><div class="carte"><p>{e(donnees["resume"])}</p></div></section>' if donnees.get("resume") else ""}
  {f'<div class="comptes">{cartes}</div>' if cartes else ""}
  {f'<section class="bloc"><h2>Ce que fait ce projet</h2><div class="fiches">{archi}</div></section>' if archi else ""}
  {"".join(corps)}
  {plan}
  {checklists}
  {limites}
</main>

<footer class="pied">{e(donnees.get("pied", "Rapport établi à partir du code du projet. Les valeurs sensibles sont masquées."))}</footer>
</body></html>
"""


def main():
    p = argparse.ArgumentParser(description="Rend un rapport HTML premium.")
    p.add_argument("constats", help="Le fichier JSON des constats.")
    p.add_argument("--sortie", "-o", help="Le HTML produit (défaut : même nom).")
    args = p.parse_args()

    source = Path(args.constats)
    if not source.is_file():
        print(f"Fichier introuvable : {source}", file=sys.stderr)
        raise SystemExit(1)
    donnees = json.loads(source.read_text(encoding="utf-8"))

    erreurs = valider(donnees)
    if erreurs:
        print("Le rapport n'est pas rendu. À corriger d'abord :", file=sys.stderr)
        for erreur in erreurs:
            print("  - " + erreur, file=sys.stderr)
        raise SystemExit(1)

    sortie = Path(args.sortie) if args.sortie else source.with_suffix(".html")
    sortie.parent.mkdir(parents=True, exist_ok=True)
    sortie.write_text(rendre(donnees), encoding="utf-8")

    tous = [c for s in donnees.get("sections", []) for c in s.get("constats", [])]
    compte = ", ".join(f"{n} : {sum(1 for c in tous if c['criticite'] == n)}"
                       for n in ORDRE if any(c["criticite"] == n for c in tous))
    print(f"Rapport écrit : {sortie}")
    print(f"{len(tous)} constats — {compte or 'aucun'}")
    print("Ouvrir la page et la regarder avant de la transmettre.")


if __name__ == "__main__":
    main()

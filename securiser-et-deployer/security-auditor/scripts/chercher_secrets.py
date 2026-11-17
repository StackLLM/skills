#!/usr/bin/env python3
"""
chercher_secrets.py — cherche les clés, jetons et mots de passe d'un projet.

    python chercher_secrets.py <projet> -o secrets.md
    python chercher_secrets.py <projet> --historique -o secrets.md

Le script sort des **pistes**, pas des verdicts. Il ne sait pas si une valeur
est un vrai secret ou un exemple : il classe, il masque, et il laisse
l'humain trancher en ouvrant le fichier.

Les valeurs sont toujours masquées : `sk-o••••••••98`. Aucune valeur entière
n'est écrite, ni dans la sortie, ni dans le fichier produit.

`--historique` relit aussi les commits passés. Un secret retiré du code reste
dans l'historique, et reste compromis.

Aucune dépendance : bibliothèque standard uniquement.
"""

from __future__ import annotations

import argparse
import math
import re
import subprocess
import sys
from pathlib import Path

IGNORES = {
    "node_modules", ".git", "dist", "build", "out", ".next", ".nuxt", ".venv",
    "venv", "__pycache__", "vendor", "target", "coverage", ".turbo", ".cache",
    "site-packages", ".pytest_cache", ".mypy_cache", "obj",
}
BINAIRES = {".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".ico", ".woff",
            ".woff2", ".ttf", ".otf", ".mp4", ".mp3", ".exe", ".dll", ".so",
            ".pyc", ".jar", ".class", ".db", ".sqlite", ".sqlite3"}
TAILLE_MAX = 800_000

# (nom, motif, groupe de la valeur). Le groupe 1 porte la valeur à masquer.
MOTIFS = [
    ("Clé de fournisseur d'IA", re.compile(r"\b(sk-(?:or-v1-|ant-|proj-)?[A-Za-z0-9_\-]{20,})")),
    ("Clé Stripe en production", re.compile(r"\b((?:sk|rk)_live_[A-Za-z0-9]{16,})")),
    ("Jeton GitHub", re.compile(r"\b(gh[pousr]_[A-Za-z0-9]{20,})")),
    ("Clé AWS", re.compile(r"\b((?:AKIA|ASIA)[A-Z0-9]{16})")),
    ("Clé Google", re.compile(r"\b(AIza[A-Za-z0-9_\-]{30,})")),
    ("Jeton Slack", re.compile(r"\b(xox[abprs]-[A-Za-z0-9\-]{10,})")),
    ("Jeton JWT", re.compile(r"\b(eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{5,})")),
    ("Clé privée", re.compile(r"(-----BEGIN [A-Z ]*PRIVATE KEY-----)")),
    ("Mot de passe dans une URL", re.compile(r"[a-z+]+://[^\s:/@]+:([^\s@\"']{6,})@")),
    # Les guillemets sont facultatifs : dans un fichier .env il n'y en a pas,
    # et c'est précisément là que vivent les secrets.
    ("Secret posé en dur", re.compile(
        r"""(?i)(?:password|passwd|pwd|secret|secret_key|api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret)"""
        r"""["']?\s*[=:]\s*["']?([^"'\s,;)}]{8,})""")),
]

# Ce qui trahit un exemple plutôt qu'un vrai secret.
FACTICES = re.compile(
    r"(?i)^(your|my|the)?[-_ ]?(api|secret|access|auth)?[-_ ]?(key|token|password|secret)"
    r"|^(x{3,}|\.{3,}|\*{3,}|•{3,})|change[-_ ]?me|placeholder|example|exemple|dummy"
    r"|todo|fixme|<[^>]+>|\{\{.*\}\}|\$\{.*\}|^test$|^demo$|^none$|^null$|^abc123")

FICHIERS_EXEMPLE = re.compile(r"(?i)\.(example|sample|template|dist)$|\.env\.(example|sample|template)"
                              r"|readme|\.md$|/docs?/|/tests?/|_test\.|\.spec\.")


def entropie(valeur: str) -> float:
    """Mesure du désordre d'une chaîne. Une vraie clé est très désordonnée."""
    if not valeur:
        return 0.0
    return -sum((n := valeur.count(c) / len(valeur)) * math.log2(n)
                for c in set(valeur))


def masquer(valeur: str) -> str:
    if len(valeur) <= 6:
        return "•" * len(valeur)
    return f"{valeur[:4]}{'•' * 8}{valeur[-2:]}"


def probablement_factice(valeur: str, chemin: str) -> bool:
    """Un exemple, ou un vrai secret ? On se trompe du côté de l'alerte."""
    if FACTICES.search(valeur):
        return True
    # Une valeur peu désordonnée et courte n'est presque jamais une clé.
    return entropie(valeur) < 2.6 and len(valeur) < 24


def parcourir(racine: Path):
    for chemin in racine.rglob("*"):
        if not chemin.is_file():
            continue
        if any(p in IGNORES for p in chemin.parts):
            continue
        if chemin.suffix.lower() in BINAIRES:
            continue
        try:
            if chemin.stat().st_size > TAILLE_MAX:
                continue
        except OSError:
            continue
        yield chemin


def fouiller_texte(texte: str, ou: str) -> list[dict]:
    trouvailles = []
    for numero, ligne in enumerate(texte.splitlines(), 1):
        if len(ligne) > 4000:                    # ligne minifiée : on garde le début
            ligne = ligne[:4000]
        for nom, motif in MOTIFS:
            for m in motif.finditer(ligne):
                valeur = m.group(1)
                trouvailles.append({
                    "type": nom,
                    "ou": ou,
                    "ligne": numero,
                    "valeur": masquer(valeur),
                    "entropie": round(entropie(valeur), 2),
                    "factice": probablement_factice(valeur, ou),
                })
    return trouvailles


def fouiller_fichiers(racine: Path) -> tuple[list[dict], int]:
    trouvailles, lus = [], 0
    for chemin in parcourir(racine):
        try:
            texte = chemin.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        lus += 1
        rel = chemin.relative_to(racine).as_posix()
        for t in fouiller_texte(texte, rel):
            # Un fichier d'exemple ou de doc abaisse fortement le soupçon.
            if FICHIERS_EXEMPLE.search("/" + rel):
                t["factice"] = True
            trouvailles.append(t)
    return trouvailles, lus


def fouiller_historique(racine: Path, limite: int) -> list[dict]:
    """Les secrets des commits passés. Un fichier supprimé les garde."""
    try:
        sortie = subprocess.run(
            ["git", "-C", str(racine), "log", f"-{limite}", "-p", "--no-color",
             "--diff-filter=AM", "--", "."],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", timeout=180)
    except (FileNotFoundError, subprocess.TimeoutExpired) as erreur:
        print(f"Historique non lu : {erreur}", file=sys.stderr)
        return []
    if sortie.returncode != 0:
        print("Historique non lu : ce dossier n'est pas un dépôt Git, "
              "ou il est vide.", file=sys.stderr)
        return []

    trouvailles, commit, fichier = [], "?", "?"
    for ligne in sortie.stdout.splitlines():
        if ligne.startswith("commit "):
            commit = ligne.split()[1][:7]
        elif ligne.startswith("+++ b/"):
            fichier = ligne[6:]
        elif ligne.startswith("+") and not ligne.startswith("+++"):
            for t in fouiller_texte(ligne[1:], f"{fichier} (commit {commit})"):
                t["ligne"] = 0
                trouvailles.append(t)
    return trouvailles


def rendre(reels: list[dict], factices: list[dict], historique: list[dict],
           racine: Path, lus: int) -> str:
    l = [f"# Secrets — {racine.name}", "",
         f"{lus} fichiers lus.", "",
         "> **Des pistes, pas des verdicts.** Un script ne sait pas si une "
         "valeur est un vrai secret. Ouvrir chaque fichier avant de conclure.",
         "",
         "> Toutes les valeurs sont masquées. Elles ne le sont pas dans le "
         "projet : c'est bien le problème.", ""]

    def tableau(titre: str, items: list[dict], note: str) -> list[str]:
        if not items:
            return [f"## {titre}", "", "*Rien trouvé.*", ""]
        out = [f"## {titre} ({len(items)})", "", note, "",
               "| Type | Où | Ligne | Valeur masquée | Désordre |",
               "|---|---|---|---|---|"]
        for t in items[:120]:
            out.append(f"| {t['type']} | `{t['ou']}` | {t['ligne'] or '—'} | "
                       f"`{t['valeur']}` | {t['entropie']} |")
        if len(items) > 120:
            out.append(f"| … | | | | {len(items) - 120} autres |")
        return out + [""]

    l += tableau("À traiter en priorité", reels,
                 "Forme et désordre d'une vraie clé, hors fichier d'exemple. "
                 "**Considérer chacune comme compromise** tant que le "
                 "contraire n'est pas montré.")
    l += tableau("Probablement des exemples", factices,
                 "Valeur factice, ou fichier d'exemple, de test ou de "
                 "documentation. À confirmer d'un coup d'œil.")
    l += tableau("Dans l'historique Git", historique,
                 "Un secret retiré du code **reste** dans l'historique, et "
                 "reste compromis. Le retirer ne suffit pas : il faut le "
                 "révoquer.")

    l += ["## Ce qu'il faut faire maintenant", "",
          "Pour chaque valeur de la première section, dans cet ordre :", "",
          "1. Identifier le fournisseur et le compte.",
          "2. **Révoquer la clé.** C'est la seule étape qui arrête le risque.",
          "3. Créer une nouvelle clé, avec les droits minimum.",
          "4. La ranger dans les variables d'environnement du serveur.",
          "5. Retirer la valeur du code.",
          "6. Vérifier que le fichier est dans `.gitignore`.",
          "7. Redéployer, puis vérifier que l'ancienne clé ne marche plus.", "",
          "Procédure détaillée : `references/secrets.md`.", ""]
    return "\n".join(l)


def main():
    p = argparse.ArgumentParser(description="Cherche les secrets d'un projet.")
    p.add_argument("projet")
    p.add_argument("--historique", action="store_true",
                   help="Lire aussi les commits passés.")
    p.add_argument("--commits", type=int, default=400,
                   help="Nombre de commits à relire (défaut : 400).")
    p.add_argument("--sortie", "-o", help="Fichier Markdown produit.")
    args = p.parse_args()

    racine = Path(args.projet).resolve()
    if not racine.is_dir():
        print(f"Dossier introuvable : {racine}", file=sys.stderr)
        raise SystemExit(1)

    trouvailles, lus = fouiller_fichiers(racine)
    reels = [t for t in trouvailles if not t["factice"]]
    factices = [t for t in trouvailles if t["factice"]]
    historique = fouiller_historique(racine, args.commits) if args.historique else []
    historique = [t for t in historique if not t["factice"]]

    print(f"{lus} fichiers lus.", file=sys.stderr)
    print(f"À traiter en priorité : {len(reels)}", file=sys.stderr)
    print(f"Probablement des exemples : {len(factices)}", file=sys.stderr)
    if args.historique:
        print(f"Dans l'historique : {len(historique)}", file=sys.stderr)
    elif (racine / ".git").exists():
        print("Historique non lu. Relancer avec --historique : un secret "
              "retiré du code y reste.", file=sys.stderr)

    markdown = rendre(reels, factices, historique, racine, lus)
    if args.sortie:
        chemin = Path(args.sortie)
        chemin.parent.mkdir(parents=True, exist_ok=True)
        chemin.write_text(markdown, encoding="utf-8")
        print(f"Écrit : {chemin}", file=sys.stderr)
    else:
        sys.stdout.write(markdown)


if __name__ == "__main__":
    main()

"""Crée le socle d'un projet : copie le modèle (commun + pile choisie) et remplace les noms.

    python creer_socle.py <dossier> --nom "La Fourchette" --pile python --type vitrine \
        --depot Org/depot [--depot Miroir/depot] [--prefixe APP] [--port 8000] [--essai]

Règles :
- n'écrase jamais un fichier qui existe déjà (il est listé comme « gardé ») ;
- ne remplace que les marqueurs connus ({{NOM}}, {{PREFIXE}}…) : les {{…}} de GitHub Actions restent intacts ;
- --essai montre ce qui serait créé, sans rien écrire.
Sans dépendance : Python 3.10 ou plus suffit.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date
from pathlib import Path

MODELE = Path(__file__).resolve().parent.parent / "modele"
PILES = {
    "python": {
        "libelle": "Python + FastAPI",
        "prerequis": ", Python 3.12 ou plus et uv",
        "installation": "```bash\nuv sync --directory backend\n```",
    },
    "node": {
        "libelle": "Node + TypeScript",
        "prerequis": "",
        "installation": "Le backend est installé par `npm install` (espaces de travail npm).",
    },
}
TYPES = ("vitrine", "saas", "interne", "api")
DEPOT = re.compile(r"^[\w.-]+/[\w.-]+$")
PREFIXE = re.compile(r"^[A-Z][A-Z0-9]{1,11}$")

LISEZMOI_CONTENU = """# Contenu du client

Le contenu du site (textes, carte, photos…) vit ici, **séparé du code** :

- `donnees/` : les textes et réglages, en JSON ;
- `medias/` : les images et documents.

En production, ce dossier est copié une seule fois sur le disque de données au premier lancement.
Ensuite, c'est le CMS qui le modifie : une nouvelle livraison du code ne l'écrase jamais.
"""


def nom_technique(nom: str) -> str:
    """« La Fourchette » → « la-fourchette » : minuscules, sans accent, tirets."""
    sans_accent = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", sans_accent.lower()).strip("-") or "projet"


def marqueurs(args: argparse.Namespace) -> dict[str, str]:
    pile = PILES[args.pile]
    depots = args.depot or ["organisation/depot"]
    return {
        "NOM": args.nom,
        "NOM_TECHNIQUE": nom_technique(args.nom),
        "PREFIXE": args.prefixe,
        "PORT": str(args.port),
        "TYPE": args.type,
        "DATE": date.today().isoformat(),
        "PILE_LIBELLE": pile["libelle"],
        "PREREQUIS_PILE": pile["prerequis"],
        "INSTALLATION_PILE": pile["installation"],
        "DEPOT_PRINCIPAL": depots[0],
        "DEPOT_PRINCIPAL_MINUSCULES": depots[0].lower(),
        "DEPOTS_JSON": json.dumps(depots),
    }


def remplacer(texte: str, valeurs: dict[str, str]) -> str:
    # Un seul passage, sur les seuls marqueurs connus : une valeur qui contient {{…}} n'est pas re-remplacée.
    motif = re.compile(r"\{\{(" + "|".join(map(re.escape, valeurs)) + r")\}\}")
    return motif.sub(lambda m: valeurs[m.group(1)], texte)


def fichiers_du_modele(pile: str) -> dict[Path, Path]:
    """Chemin relatif dans le projet → fichier du modèle. La pile l'emporte sur le commun."""
    fichiers: dict[Path, Path] = {}
    for dossier in (MODELE / "commun", MODELE / pile):
        for source in sorted(p for p in dossier.rglob("*") if p.is_file()):
            if "__pycache__" in source.parts:
                continue
            fichiers[source.relative_to(dossier)] = source
    return fichiers


def creer(cible: Path, args: argparse.Namespace) -> tuple[list[Path], list[Path]]:
    valeurs = marqueurs(args)
    crees: list[Path] = []
    gardes: list[Path] = []
    a_ecrire = {rel: source.read_bytes() for rel, source in fichiers_du_modele(args.pile).items()}
    if args.type == "vitrine":
        a_ecrire[Path("contenu/LISEZMOI.md")] = LISEZMOI_CONTENU.encode()
        a_ecrire[Path("contenu/donnees/.gitkeep")] = b""
        a_ecrire[Path("contenu/medias/.gitkeep")] = b""

    for rel, octets in a_ecrire.items():
        destination = cible / rel
        if destination.exists():
            gardes.append(rel)
            continue
        crees.append(rel)
        if args.essai:
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            texte = octets.decode("utf-8")
        except UnicodeDecodeError:
            destination.write_bytes(octets)
            continue
        # write_bytes garde les fins de ligne du modèle (CRLF des .bat, LF ailleurs).
        destination.write_bytes(remplacer(texte, valeurs).encode("utf-8"))
        if destination.suffix == ".sh":
            destination.chmod(0o755)
    return crees, gardes


def lire_arguments(argv: list[str]) -> argparse.Namespace:
    analyseur = argparse.ArgumentParser(description="Crée le socle frontend/backend d'un projet.")
    analyseur.add_argument("dossier", type=Path, help="dossier du projet (créé s'il n'existe pas)")
    analyseur.add_argument("--nom", required=True, help="nom lisible du projet, ex. « La Fourchette »")
    analyseur.add_argument("--pile", choices=sorted(PILES), default="python", help="pile du backend (défaut : python)")
    analyseur.add_argument("--type", choices=TYPES, default="saas", help="type de projet (défaut : saas)")
    analyseur.add_argument(
        "--depot", action="append", help="dépôt GitHub org/nom ; le premier est le principal, les suivants des miroirs"
    )
    analyseur.add_argument("--prefixe", default="APP", help="préfixe des variables d'environnement (défaut : APP)")
    analyseur.add_argument("--port", type=int, default=8000, help="port interne du service (défaut : 8000)")
    analyseur.add_argument("--essai", action="store_true", help="montrer sans rien écrire")
    args = analyseur.parse_args(argv)
    for depot in args.depot or []:
        if not DEPOT.match(depot):
            analyseur.error(f"--depot doit être de la forme organisation/depot (reçu : {depot})")
    if not PREFIXE.match(args.prefixe):
        analyseur.error("--prefixe : 2 à 12 caractères, majuscules et chiffres, commençant par une lettre (ex. CMS)")
    if not 1 <= args.port <= 65_535:
        analyseur.error("--port doit être entre 1 et 65535")
    return args


def main(argv: list[str] | None = None) -> int:
    args = lire_arguments(sys.argv[1:] if argv is None else argv)
    cible = args.dossier.resolve()
    crees, gardes = creer(cible, args)
    verbe = "à créer" if args.essai else "créé(s)"
    print(f"Socle {args.pile} ({args.type}) pour « {args.nom} » dans {cible}")
    print(f"  {len(crees)} fichier(s) {verbe}")
    for rel in gardes:
        print(f"  gardé (existe déjà) : {rel.as_posix()}")
    if not args.depot:
        print(
            "  Attention : aucun --depot donné. Remplacer « organisation/depot » dans .github/livraison.json et image.yml."
        )
    if not args.essai:
        print("\nÉtapes suivantes :")
        print("  1. npm create vite@latest frontend -- --template react-ts   (puis Vitest et TypeScript strict)")
        if args.pile == "python":
            print("  2. npm install ; uv lock --directory backend ; uv sync --directory backend")
        else:
            print("  2. npm install")
        print("  3. npm run verifier   → tout doit être vert avant la première ligne de métier")
        print("  4. git init -b dev ; premier commit ; push ; vérifier la CI sur GitHub")
        print("  5. Régler GitHub : protections de main et dev, mails des CI vertes (references/git-et-livraison.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

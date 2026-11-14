"""Inventaire du socle d'un projet existant : ce qui est présent, partiel ou absent, bloc par bloc.

    python3 auditer.py <dossier-du-projet> [-o audit.json] [--en-ligne]

Lecture seule. N'ouvre jamais un fichier .env (seul son suivi par Git est vérifié).
Le script donne des INDICES avec leur preuve (fichier, ligne) : il ne juge pas la qualité du code.
Le jugement, c'est la lecture qui suit (references/audit.md). Chaque indice se vérifie avant d'entrer
dans le rapport ; un indice faux se range dans « Faux positifs écartés ».

Le frontend et le backend sont reconnus à leur contenu (package.json, pyproject…), pas à leur nom :
un projet en web/ + api/ est audité comme un projet en frontend/ + backend/, et l'écart de nom est signalé.
--en-ligne compare les actions GitHub à leur dernière version (demande gh connecté).
Sans dépendance : Python 3.10 ou plus.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from pathlib import Path

IGNORES = {
    "node_modules",
    ".git",
    "dist",
    "build",
    ".venv",
    "venv",
    "__pycache__",
    ".next",
    "coverage",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".turbo",
    ".cache",
    "vendor",
    ".ssr",
}
# Dossiers d'outillage : du code qui ne tourne pas en production. Exclus des contrôles d'écriture.
OUTILLAGE = {"outils", "scripts", "tools", "livrables", "e2e", "fixtures", "medias-sources"}
EXTENSIONS_CODE = {".ts", ".tsx", ".js", ".jsx", ".mjs", ".py"}
TAILLE_MAX_LUE = 400_000
LIGNES_FICHIER_LONG = 400
LIGNES_README_LONG = 800
MAX_PREUVES = 5

# Fin de maintenance des versions majeures (sources : nodejs.org/en/about/previous-releases, devguide.python.org/versions).
FIN_NODE = {16: "2023-09", 18: "2025-04", 20: "2026-04", 22: "2027-04"}
FIN_PYTHON = {"3.8": "2024-10", "3.9": "2025-10", "3.10": "2026-10"}
DATE_AUDIT_MIN = "2026-11"  # mise à jour avec la skill : une version finie avant cette date est signalée

FRAMEWORKS_FRONT = re.compile(r'"(vite|react|next|vue|svelte|@angular/core|astro)"\s*:')
# Les piles de l'équipe (references/piles.md) : Express + Prisma, Fastify + better-sqlite3, Node sans framework.
FRAMEWORKS_BACK_NODE = re.compile(
    r'"(express|fastify|@prisma/client|prisma|better-sqlite3|drizzle-orm|pg)"\s*:|node[^"]*src/(index|server|main)\.ts'
)

SECRETS = [
    (re.compile(r"AKIA[0-9A-Z]{16}"), "clé AWS"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"), "clé d'API (sk-…)"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}"), "jeton GitHub"),
    (re.compile(r"\bnfp_[A-Za-z0-9]{20,}"), "jeton Netlify"),
    (re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"), "clé privée"),
    # Dernière règle : les tests ont le droit à de faux mots de passe, elle les ignore.
    (
        re.compile(r"""(?i)(password|mot_?de_?passe|secret|api_?key)\s*[:=]\s*['"][^'"\s]{8,}['"]"""),
        "mot de passe ou secret écrit en dur",
    ),
]

# Motifs stricts : chacun a déjà donné un faux positif sous une forme plus large
# (coordonnées contenant 429, requestIdleCallback pris pour un identifiant de requête…).
LIMITEUR = re.compile(
    r"status_code\s*=\s*429|HTTP_429|\b429\b\s*[,)].*(trop|many|limit)|Retry-After|rate.?limit|ratelimit|"
    r"\bLimiteur\b|creerLimiteur|slowapi|express-rate-limit|@fastify/rate-limit|flask_limiter|Flask-Limiter|throttl",
    re.I,
)
# Une authentification ENTRANTE (le service vérifie quelqu'un). Pas « Authorization » seul : un en-tête envoyé
# à GitHub ou à une API d'IA est un appel sortant. Pas « session » seul : c'est aussi la session de la base.
AUTHENTIFICATION = re.compile(
    r"WWW-Authenticate|compare_digest|timingSafeEqual|checkpw|verify_password|bcrypt\.compare|argon2.*verify|"
    r"jwt\.(decode|verify)|login_required|flask_login|LoginManager|exiger_jeton|['\"]/(api/)?(login|connexion|auth)",
    re.I,
)
ID_REQUETE = re.compile(r"x-request-id|\brequest[_-]id\b|\bid_requete\b|\bidRequete\b", re.I)
JOURNAL = re.compile(
    r"getLogger|logging\.(basicConfig|config)|\bpino\b|\bwinston\b|structlog|loguru|creerJournal|configurer_journal|"
    r"logger\s*:\s*(true|\{)|\bmorgan\b"
)
# Les routes déclarées sous un préfixe (APIRouter(prefix="/sante") + get("/vivant")) comptent aussi.
SANTE_VIVANT = re.compile(r"""/sante/vivant|/healthz\b|/livez?\b|/health/live|["']/vivant["']""")
SANTE_PRET = re.compile(r"""/sante/pret|/readyz?\b|/health/ready|["']/pret["']""")
SANTE_UNIQUE = re.compile(r"""["'](/api)?/(sante|health|status|ping)["']""")
ENTETES = re.compile(r"Content-Security-Policy|X-Content-Type-Options|nosniff|\bhelmet\b|@fastify/helmet|flask_talisman|Talisman\(")
# Un mot de passe réellement manipulé (affecté, typé, colonne), pas le mot dans une liste de champs à masquer.
MOT_DE_PASSE = re.compile(r"\b(password|mot_de_passe|motDePasse|hashed_password)\w*\s*(:|=)", re.I)
HACHAGE = re.compile(r"argon2|bcrypt|scrypt|pbkdf2")
TAILLE_MAX = re.compile(r"\b413\b|TAILLE_MAX|max.?body|maxBodyLength|client_max_body_size|content-length", re.I)


@dataclass
class Bloc:
    numero: int
    nom: str
    etat: str = "absent"  # present | partiel | absent
    preuves: list[str] = field(default_factory=list)
    manques: list[str] = field(default_factory=list)


class Projet:
    def __init__(self, racine: Path) -> None:
        self.racine = racine
        self.fichiers = list(self._parcourir(racine))
        self._textes: dict[Path, str] = {}

    def _parcourir(self, dossier: Path) -> Iterator[Path]:
        for chemin in dossier.iterdir():
            # Les dossiers cachés (.cloneme, .idea…) ne sont pas le projet, sauf .github.
            if chemin.name in IGNORES or (chemin.is_dir() and chemin.name.startswith(".") and chemin.name != ".github"):
                continue
            if chemin.is_dir():
                yield from self._parcourir(chemin)
            elif chemin.is_file():
                yield chemin

    def rel(self, chemin: Path) -> str:
        return chemin.relative_to(self.racine).as_posix()

    def existe(self, *chemins: str) -> str | None:
        return next((c for c in chemins if (self.racine / c).exists()), None)

    def texte(self, chemin: Path) -> str:
        # Un .env n'est jamais lu : il peut contenir des secrets.
        if chemin.name == ".env" or (chemin.name.startswith(".env.") and not chemin.name.endswith(".example")):
            return ""
        if chemin not in self._textes:
            try:
                lisible = chemin.stat().st_size < 2_000_000
                self._textes[chemin] = chemin.read_text(encoding="utf-8")[:TAILLE_MAX_LUE] if lisible else ""
            except (UnicodeDecodeError, OSError):
                self._textes[chemin] = ""
        return self._textes[chemin]

    def chercher(self, motif: re.Pattern[str], fichiers: list[Path]) -> list[str]:
        trouves: list[str] = []
        for fichier in fichiers:
            for numero, ligne in enumerate(self.texte(fichier).splitlines(), 1):
                if motif.search(ligne):
                    trouves.append(f"{self.rel(fichier)}:{numero}")
        return trouves

    def git(self, *args: str) -> str:
        try:
            return subprocess.run(
                ["git", "-C", str(self.racine), *args], capture_output=True, text=True, timeout=30, check=False
            ).stdout
        except (OSError, subprocess.TimeoutExpired):
            return ""


def est_test(chemin: Path) -> bool:
    nom = chemin.name
    return (
        bool({"tests", "test", "__tests__"} & set(chemin.parts))
        or ".test." in nom
        or ".spec." in nom
        or nom.startswith("test_")
    )


def est_outillage(p: Projet, chemin: Path) -> bool:
    parties = p.rel(chemin).split("/")
    return bool(OUTILLAGE & set(parties[:-1])) or ".config." in chemin.name or chemin.name.startswith("eslint")


def roles(p: Projet) -> tuple[list[Path], list[Path]]:
    """Les dossiers du frontend et du backend, reconnus à leur contenu, puis à leur nom."""
    fronts: list[Path] = []
    backs: list[Path] = []
    for dossier in sorted(
        d for d in p.racine.iterdir() if d.is_dir() and d.name not in IGNORES and not d.name.startswith(".")
    ):
        paquet = dossier / "package.json"
        texte_paquet = p.texte(paquet) if paquet.exists() else ""
        python = any((dossier / f).exists() for f in ("pyproject.toml", "requirements.txt", "manage.py", "setup.py"))
        if FRAMEWORKS_FRONT.search(texte_paquet) and not FRAMEWORKS_BACK_NODE.search(texte_paquet):
            fronts.append(dossier)
        # Noms rencontrés dans les projets de l'équipe : backend/server/api et frontend/ui/web.
        elif python or FRAMEWORKS_BACK_NODE.search(texte_paquet) or dossier.name in {"backend", "server", "api"}:
            backs.append(dossier)
        elif dossier.name in {"frontend", "ui", "web", "client"}:
            fronts.append(dossier)
    # Projets d'un seul bloc (application Next ou Vite à la racine, outil Flask à la racine) : la racine joue le rôle.
    paquet_racine = p.texte(p.racine / "package.json") if (p.racine / "package.json").exists() else ""
    if not fronts and FRAMEWORKS_FRONT.search(paquet_racine):
        fronts.append(p.racine)
    python_racine = any((p.racine / f).exists() for f in ("pyproject.toml", "requirements.txt", "app.py", "manage.py"))
    if not backs and (python_racine or FRAMEWORKS_BACK_NODE.search(paquet_racine)):
        backs.append(p.racine)
    return fronts, backs


def sous(p: Projet, dossiers: list[Path], fichiers: list[Path]) -> list[Path]:
    return [f for f in fichiers if any(d in f.parents for d in dossiers)]


def etat(bloc: Bloc, attendus: int) -> Bloc:
    """attendus : nombre d'éléments vérifiés. Tout présent → present ; rien → absent ; sinon partiel."""
    trouves = max(0, attendus - len(bloc.manques))
    bloc.etat = "present" if trouves == attendus else "absent" if trouves == 0 else "partiel"
    bloc.preuves = bloc.preuves[: MAX_PREUVES * 3]
    return bloc


def apercu(trouves: list[str]) -> str:
    return ", ".join(trouves[:MAX_PREUVES]) + (
        f" (+{len(trouves) - MAX_PREUVES})" if len(trouves) > MAX_PREUVES else ""
    )


def versions_actions(actions: list[str], en_ligne: bool) -> list[str]:
    """Les actions dont la version majeure est en retard sur la dernière publiée (avec --en-ligne)."""
    if not en_ligne:
        return []
    retards: list[str] = []
    for action in actions:
        nom, _, version = action.partition("@")
        try:
            derniere = subprocess.run(
                ["gh", "api", f"repos/{nom}/releases/latest", "-q", ".tag_name"],
                capture_output=True,
                text=True,
                timeout=20,
                check=False,
            ).stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            continue
        majeure = re.match(r"v?(\d+)", version)
        derniere_majeure = re.match(r"v?(\d+)", derniere)
        if majeure and derniere_majeure and int(majeure[1]) < int(derniere_majeure[1]):
            retards.append(f"{action} (dernière : {derniere})")
    return retards


def auditer(racine: Path, en_ligne: bool = False) -> dict[str, object]:
    p = Projet(racine)
    fronts, backs = roles(p)
    code = [f for f in p.fichiers if f.suffix in EXTENSIONS_CODE and not est_test(f)]
    produit = [f for f in code if not est_outillage(p, f)]
    code_back = sous(p, backs, produit) or produit
    tests = [f for f in p.fichiers if f.suffix in EXTENSIONS_CODE and est_test(f)]
    workflows = [f for f in p.fichiers if ".github/workflows" in p.rel(f) and f.suffix in {".yml", ".yaml"}]
    texte_ci = "\n".join(p.texte(f) for f in workflows)
    dockerfiles = [f for f in p.fichiers if f.name == "Dockerfile" or f.name.startswith("Dockerfile.")]
    suivis = set(p.git("ls-files").splitlines())
    python_present = any(f.suffix == ".py" for f in code_back)
    blocs: list[Bloc] = []
    alertes: list[str] = []

    # 1. Structure
    b = Bloc(1, "Structure")
    # Six éléments : chaque rôle existe, chaque rôle porte le bon nom, infra/, docs/.
    # Un projet en ui/ + server/ est donc « partiel », pas « absent » : son découpage est bon, ses noms non.
    for role, dossiers, attendu in (("frontend", fronts, "frontend"), ("backend", backs, "backend")):
        if not dossiers:
            b.manques += [f"aucun {role} reconnu", f"nom {attendu}/"]
        elif all(d.name == attendu for d in dossiers):
            b.preuves.append(f"{attendu}/")
        else:
            noms = ", ".join(f"{d.name if d != racine else '(racine)'}/" for d in dossiers)
            b.preuves.append(f"{role} reconnu dans {noms}")
            b.manques.append(f"nom {attendu}/ (ici {noms}) : à harmoniser, ou exception écrite dans docs/decisions/")
    for dossier in ("infra", "docs"):
        (b.preuves.append(f"{dossier}/") if (racine / dossier).is_dir() else b.manques.append(f"dossier {dossier}/"))
    blocs.append(etat(b, 6))

    # 2. Configuration
    b = Bloc(2, "Configuration")
    exemple = [p.rel(f) for f in p.fichiers if f.name == ".env.example"]
    (b.preuves.append(f".env.example : {', '.join(exemple)}") if exemple else b.manques.append(".env.example"))
    env_suivis = [f for f in suivis if re.search(r"(^|/)\.env(\.[^/]*)?$", f) and not f.endswith(".example")]
    if env_suivis:
        b.manques.append(f".env suivi par Git : {', '.join(env_suivis)} (secret à changer)")
        alertes.append(f"BLOQUANT probable : .env suivi par Git ({', '.join(env_suivis)})")
    else:
        b.preuves.append("aucun .env suivi par Git")
    en_dur = [
        t
        for t in p.chercher(re.compile(r"https?://(localhost|127\.0\.0\.1)(:\d+)?"), produit)
        if "config" not in t.lower()
    ]
    if en_dur:
        b.manques.append(
            f"adresses localhost dans le code (vérifier : un repli limité au développement est correct) : {apercu(en_dur)}"
        )
    else:
        b.preuves.append("pas d'adresse localhost dans le code")
    suivis_code = [f for f in p.fichiers if p.rel(f) in suivis]
    suivis_hors_tests = [f for f in suivis_code if not est_test(f)]
    secrets = [
        f"{t} ({nom})"
        for i, (motif, nom) in enumerate(SECRETS)
        for t in p.chercher(motif, suivis_hors_tests if i == len(SECRETS) - 1 else suivis_code)
    ]
    if secrets:
        b.manques.append(f"secrets possibles dans des fichiers suivis : {apercu(secrets)}")
        alertes.append(f"BLOQUANT probable : secret dans Git ({apercu(secrets)})")
    else:
        b.preuves.append("aucun motif de secret connu dans les fichiers suivis")
    blocs.append(etat(b, 4))

    # 3. Écriture du code (code de production seulement : l'outillage et les réglages sont exclus)
    b = Bloc(3, "Écriture du code")
    attendus = 3
    if any(f.suffix in {".ts", ".tsx"} for f in produit):
        attendus += 1
        tsconfigs = [f for f in p.fichiers if f.name.startswith("tsconfig") and f.suffix == ".json"]
        strict = [p.rel(f) for f in tsconfigs if re.search(r'"strict"\s*:\s*true', p.texte(f))]
        coupe = [p.rel(f) for f in tsconfigs if re.search(r'"strict"\s*:\s*false', p.texte(f))]
        # TypeScript 6 et plus : strict est le réglage par défaut. Il suffit de ne pas le couper.
        paquets = "\n".join(p.texte(f) for f in p.fichiers if f.name == "package.json")
        recent = any(int(v) >= 6 for v in re.findall(r'"typescript"\s*:\s*"[~^>=]*(\d+)', paquets))
        if coupe:
            b.manques.append(f"TypeScript strict coupé : {', '.join(coupe)}")
        elif strict or recent:
            b.preuves.append(f"TypeScript strict : {', '.join(strict) or 'par défaut (TypeScript 6 ou plus)'}")
        else:
            b.manques.append("TypeScript strict")
    if python_present:
        attendus += 1
        reglages = [
            f for f in p.fichiers if f.name in {"pyproject.toml", "ruff.toml", ".ruff.toml", "mypy.ini", "setup.cfg"}
        ]
        outils_py = [p.rel(f) for f in reglages if re.search(r"\[(tool\.)?(ruff|mypy|pyright)", p.texte(f))]
        (
            b.preuves.append(f"Python vérifié : {', '.join(outils_py)}")
            if outils_py
            else b.manques.append("Python sans ruff ni mypy/pyright")
        )
    any_ts = p.chercher(re.compile(r":\s*any\b|as any\b|<any>"), [f for f in produit if f.suffix in {".ts", ".tsx"}])
    vides = p.chercher(re.compile(r"catch\s*(\([^)]*\))?\s*\{\s*\}|except(\s+[\w.]+)?\s*:\s*pass\b"), produit)
    longs = [f"{p.rel(f)} ({n} lignes)" for f in produit if (n := p.texte(f).count("\n")) > LIGNES_FICHIER_LONG]
    for trouves, libelle in (
        (any_ts, "« any »"),
        (vides, "erreurs avalées (catch/except vides)"),
        (longs, f"fichiers de plus de {LIGNES_FICHIER_LONG} lignes"),
    ):
        (b.manques.append(f"{libelle} : {apercu(trouves)}") if trouves else b.preuves.append(f"aucun : {libelle}"))
    blocs.append(etat(b, attendus))

    # 4. Tests, par rôle
    b = Bloc(4, "Tests")
    for role, dossiers in (("frontend", fronts), ("backend", backs)):
        nombre = len(sous(p, dossiers, tests)) if dossiers else 0
        (b.preuves.append(f"{nombre} fichier(s) de test {role}") if nombre else b.manques.append(f"tests {role}"))
    blocs.append(etat(b, 2))

    # 5. CI
    b = Bloc(5, "CI")
    attendus = 3
    (
        b.preuves.append(f"workflows : {', '.join(p.rel(f) for f in workflows)}")
        if workflows
        else b.manques.append(".github/workflows/ci.yml")
    )
    exacte = re.search(r"npm ci|uv sync[^\n]*--frozen|pip install -r", texte_ci)
    (
        b.preuves.append("installation exacte")
        if exacte
        else b.manques.append("installation exacte (npm ci / uv sync --frozen)")
    )
    (
        b.preuves.append("tests lancés")
        if re.search(r"\btest|pytest", texte_ci)
        else b.manques.append("tests lancés par la CI")
    )
    if python_present and workflows:
        attendus += 1
        python_ci = re.search(r"ruff|mypy|pyright|flake8|npm run (lint|verifier)", texte_ci)
        (
            b.preuves.append("Python vérifié en CI")
            if python_ci
            else b.manques.append("lint et types Python absents de la CI")
        )
    for version in sorted(set(re.findall(r"node-version:\s*['\"]?(\d+)", texte_ci + p.texte(racine / "netlify.toml")))):
        fin = FIN_NODE.get(int(version))
        if fin and fin < DATE_AUDIT_MIN:
            b.manques.append(f"Node {version} n'est plus maintenu depuis {fin}")
    for version in sorted(set(re.findall(r"python-version:\s*['\"]?(3\.\d+)", texte_ci))):
        fin = FIN_PYTHON.get(version)
        if fin and fin < DATE_AUDIT_MIN:
            b.manques.append(f"Python {version} n'est plus maintenu depuis {fin}")
    actions = sorted(set(re.findall(r"uses:\s*([\w.-]+/[\w.-]+@[\w.-]+)", texte_ci)))
    retards = versions_actions(actions, en_ligne)
    if retards:
        b.manques.append(f"actions en retard d'une version majeure : {apercu(retards)}")
    elif actions:
        b.preuves.append(
            f"actions utilisées ({'à jour' if en_ligne else 'versions non vérifiées : relancer avec --en-ligne'}) : {', '.join(actions)}"
        )
    # Une image publiée doit attendre la CI du même commit.
    for wf in workflows:
        texte = p.texte(wf)
        if re.search(r"docker/build-push-action|docker push", texte) and "needs:" not in texte:
            b.manques.append(f"{p.rel(wf)} publie une image sans attendre la CI (aucun needs)")
            alertes.append(f"IMPORTANT : {p.rel(wf)} publie une image sans attendre la CI")
    blocs.append(
        etat(
            b,
            attendus + len([m for m in b.manques if "plus maintenu" in m or "retard" in m or "publie une image" in m]),
        )
    )

    # 6. Branches et livraison
    b = Bloc(6, "Branches et livraison")
    branches = p.git("branch", "-a", "--format=%(refname:short)").split()
    for nom in ("main", "dev"):
        (
            b.preuves.append(f"branche {nom}")
            if any(x.split("/")[-1] == nom for x in branches)
            else b.manques.append(f"branche {nom}")
        )
    (
        b.preuves.append("script de livraison")
        if p.existe(".github/livrer.mjs", "livrer.bat", "livrer.sh")
        else b.manques.append("script livrer (vérifie la CI du commit, puis pousse vers main)")
    )
    (
        b.preuves.append("contrôle « prêt pour main » dans la CI")
        if "merge-base --is-ancestor" in texte_ci
        else b.manques.append("job pret-pour-main (main peut avancer sans conflit)")
    )
    blocs.append(etat(b, 4))

    # 7. Docker : chaque Dockerfile est jugé seul, avec le .dockerignore de son dossier
    b = Bloc(7, "Image Docker")
    attendus = 1
    (
        b.preuves.append(f"Dockerfile : {', '.join(p.rel(f) for f in dockerfiles)}")
        if dockerfiles
        else b.manques.append("Dockerfile")
    )
    for fichier in dockerfiles:
        attendus += 4
        texte = p.texte(fichier)
        nom = p.rel(fichier)
        derniere_image = (re.findall(r"^\s*FROM\s+(\S+)", texte, re.M) or [""])[-1]
        if not re.search(r"^\s*USER\s+(?!root\b)\S", texte, re.M):
            precision = " (nginx : image nginx-unprivileged)" if "nginx" in derniere_image else ""
            b.manques.append(f"{nom} : tourne en root, aucun USER{precision}")
        else:
            b.preuves.append(f"{nom} : utilisateur sans root")
        (
            b.preuves.append(f"{nom} : HEALTHCHECK")
            if "HEALTHCHECK" in texte
            else b.manques.append(f"{nom} : aucun HEALTHCHECK")
        )
        images = re.findall(r"^\s*FROM\s+(\S+)", texte, re.M)
        larges = [i for i in images if ":" not in i or i.endswith(":latest") or re.search(r":\d+(-[a-z]+)?$", i)]
        (
            b.manques.append(f"{nom} : image de base peu épinglée ({', '.join(larges)})")
            if larges
            else b.preuves.append(f"{nom} : images épinglées")
        )
        ignore = next((d / ".dockerignore" for d in (fichier.parent, racine) if (d / ".dockerignore").exists()), None)
        if ignore and ".env" in p.texte(ignore):
            b.preuves.append(f"{nom} : .dockerignore exclut .env ({p.rel(ignore)})")
        else:
            b.manques.append(f"{nom} : aucun .dockerignore qui exclut .env dans son dossier")
    blocs.append(etat(b, attendus))

    # 8. Santé (code du backend)
    b = Bloc(8, "Santé")
    vivant, pret, unique = (p.chercher(m, code_back) for m in (SANTE_VIVANT, SANTE_PRET, SANTE_UNIQUE))
    if vivant or pret:
        (
            b.preuves.append(f"« vivant » : {apercu(vivant)}")
            if vivant
            else b.manques.append("adresse « vivant » (liveness)")
        )
        (
            b.preuves.append(f"« prêt » : {apercu(pret)}")
            if pret
            else b.manques.append("adresse « prêt » (readiness), qui contrôle la base")
        )
    elif unique:
        b.preuves.append(f"une seule adresse de santé : {apercu(unique)}")
        b.manques.append("séparer « vivant » et « prêt » ; vérifier que l'adresse contrôle la base et ne révèle rien")
    else:
        b.manques += ["adresse « vivant » (liveness)", "adresse « prêt » (readiness)"]
    blocs.append(etat(b, 2))

    # 9. Protection : code du backend, plus les réglages des serveurs devant lui (nginx, Caddy, Netlify)
    b = Bloc(9, "Protection")
    reglages_web = [f for f in p.fichiers if f.suffix == ".conf" or f.name in {"_headers", "netlify.toml", "Caddyfile"}]
    limites = p.chercher(LIMITEUR, code_back)
    auth = p.chercher(AUTHENTIFICATION, code_back)
    (b.preuves.append(f"limites d'essais : {apercu(limites)}") if limites else b.manques.append("limites d'essais"))
    if auth and not limites:
        alertes.append(f"BLOQUANT probable : authentification sans limite d'essais ({apercu(auth)})")
    entetes = p.chercher(ENTETES, code_back + reglages_web)
    (
        b.preuves.append(f"en-têtes de sécurité : {apercu(entetes)}")
        if entetes
        else b.manques.append("en-têtes de sécurité")
    )
    if p.chercher(MOT_DE_PASSE, code_back):
        hachage = p.chercher(HACHAGE, code_back)
        (
            b.preuves.append(f"mots de passe hachés : {apercu(hachage)}")
            if hachage
            else b.manques.append("mots de passe hachés (argon2id)")
        )
    else:
        b.preuves.append("pas de mot de passe stocké (vérifier le mode d'accès : jeton, SSO…)")
    taille = p.chercher(TAILLE_MAX, code_back + reglages_web)
    (
        b.preuves.append(f"taille max des requêtes : {apercu(taille)}")
        if taille
        else b.manques.append("taille max des requêtes")
    )
    blocs.append(etat(b, 4))

    # 10. Journaux (code du backend)
    b = Bloc(10, "Journaux")
    for motif, libelle in ((JOURNAL, "journal structuré"), (ID_REQUETE, "identifiant de requête")):
        trouves = p.chercher(motif, code_back)
        (b.preuves.append(f"{libelle} : {apercu(trouves)}") if trouves else b.manques.append(libelle))
    blocs.append(etat(b, 2))

    # 11. Données
    b = Bloc(11, "Données")
    # Alembic, Flask-Migrate, prisma migrate, drizzle-kit : tous rangent leurs migrations dans un dossier.
    migrations = [p.rel(f) for f in p.fichiers if re.search(r"(migrations?|alembic|drizzle)/", p.rel(f))]
    version_schema = p.chercher(re.compile(r"user_version|schema_version|version_schema"), code_back)
    if migrations or version_schema:
        b.preuves.append(f"schéma versionné : {apercu(migrations or version_schema)}")
    else:
        b.manques.append("migrations ou version du schéma (à confirmer : la base en a-t-elle besoin ?)")
    (
        b.preuves.append("script de sauvegarde")
        if p.existe("infra/sauvegarde.sh", "scripts/sauvegarde.sh", "scripts/sauvegarder.sh", "backup.sh")
        else b.manques.append("script de sauvegarde")
    )
    (
        b.preuves.append("script de restauration")
        if p.existe("infra/restaurer.sh", "scripts/restaurer.sh", "restore.sh")
        else b.manques.append("script de restauration (testé)")
    )
    blocs.append(etat(b, 3))

    # 12. Documentation
    b = Bloc(12, "Documentation")
    readme = racine / "README.md"
    lignes_readme = p.texte(readme).count("\n") if readme.exists() else 0
    if lignes_readme < 20:
        b.manques.append("README qui lance le projet en 5 minutes")
    elif lignes_readme > LIGNES_README_LONG:
        b.preuves.append(f"README ({lignes_readme} lignes)")
        b.manques.append(
            f"README de {lignes_readme} lignes : garder le lancement et l'exploitation, ranger le reste dans docs/"
        )
    else:
        b.preuves.append(f"README ({lignes_readme} lignes)")
    decisions = racine / "docs" / "decisions"
    (
        b.preuves.append("docs/decisions/")
        if decisions.is_dir() and any(decisions.iterdir())
        else b.manques.append("décisions écrites (docs/decisions/)")
    )
    blocs.append(etat(b, 2))

    resume = {e: sum(1 for x in blocs if x.etat == e) for e in ("present", "partiel", "absent")}
    return {
        "projet": str(racine),
        "roles": {"frontend": [p.rel(d) for d in fronts], "backend": [p.rel(d) for d in backs]},
        "resume": resume,
        "alertes": alertes,
        "blocs": [asdict(x) for x in blocs],
    }


def afficher(resultat: dict[str, object]) -> None:
    symboles = {"present": "[ok]     ", "partiel": "[partiel]", "absent": "[absent] "}
    print(f"Socle de {resultat['projet']}")
    print(f"Rôles reconnus : {resultat['roles']}")
    print(f"Résumé : {resultat['resume']}\n")
    for alerte in resultat["alertes"]:  # type: ignore[attr-defined]
        print(f"  ! {alerte}")
    if resultat["alertes"]:
        print()
    for bloc in resultat["blocs"]:  # type: ignore[attr-defined]
        print(f"{symboles[bloc['etat']]} {bloc['numero']:>2}. {bloc['nom']}")
        for manque in bloc["manques"]:
            print(f"             manque : {manque}")
    print("\nCe sont des indices : chaque ligne se vérifie en lisant le code (references/audit.md).")


def main(argv: list[str] | None = None) -> int:
    analyseur = argparse.ArgumentParser(description="Inventaire du socle d'un projet (lecture seule).")
    analyseur.add_argument("dossier", type=Path)
    analyseur.add_argument("-o", "--sortie", type=Path, help="écrire le résultat complet en JSON")
    analyseur.add_argument(
        "--en-ligne", action="store_true", help="comparer les actions GitHub à leur dernière version (gh)"
    )
    args = analyseur.parse_args(sys.argv[1:] if argv is None else argv)
    racine = args.dossier.resolve()
    if not racine.is_dir():
        analyseur.error(f"dossier introuvable : {racine}")
    resultat = auditer(racine, en_ligne=args.en_ligne)
    afficher(resultat)
    if args.sortie:
        args.sortie.write_text(json.dumps(resultat, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Détail : {args.sortie}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

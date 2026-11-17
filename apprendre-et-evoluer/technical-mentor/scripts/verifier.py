#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vérifie une fiche Technical Mentor contre la checklist de la skill.

Ne juge pas le fond — il faut lire la fiche pour ça. Il attrape ce qui se
contrôle mécaniquement : structure des six étapes, présence des blocs
obligatoires, analogies interdites, corrections visibles, métadonnées.

    python verifier.py                      # toutes les fiches du dossier
    python verifier.py rate-limiting.html   # une seule
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Le dossier des fiches, sous le dossier personnel de la machine.
# Ecrit relativement : un chemin en dur avec un nom d'utilisateur ne
# marche que sur une seule machine.
DOSSIER_DEFAUT = Path.home() / "Documents" / "REVISION-TECHNIQUE" / "Technical-words"

# Les étapes, selon le mode de la fiche (métadonnée `mentor-mode`).
#
# Le mode notion en compte sept : il explique la solution en mots avant tout
# code. Le mode architecture en compte six : on y décrit un système qui existe
# déjà, il n'y a pas de solution à défendre.
ETAPES = {
    "notion": ["probleme", "mecanisme", "solution", "oeuvre",
               "ingenieur", "expert", "controle"],
    "architecture": ["vue", "mecanisme", "oeuvre", "ingenieur", "expert", "controle"],
}

# Au-dela de ce nombre de mots, une phrase est trop longue pour la regle du
# francais simple. Conseil, pas erreur : une enumeration peut legitimement
# depasser.
MOTS_PAR_PHRASE = 32

# Les analogies que la skill interdit. On cherche le mot entier, hors balises.
ANALOGIES = [
    "cuisine", "cuisinier", "restaurant", "serveur de salle", "chef étoilé",
    "voiture", "garage", "moteur de voiture", "volant",
    "facteur", "boîte aux lettres", "enveloppe",
    "videur", "boîte de nuit", "vigile",
    "recette de grand-mère", "gâteau",
]

# Langages présents dans highlight.min.js (11.9.0), sans module à charger.
LANGAGES_INCLUS = {
    "bash", "c", "cpp", "csharp", "css", "diff", "go", "graphql", "ini", "java",
    "javascript", "json", "kotlin", "less", "lua", "makefile", "markdown",
    "objectivec", "perl", "php", "php-template", "plaintext", "python",
    "python-repl", "r", "ruby", "rust", "scss", "shell", "sql", "swift",
    "typescript", "vbnet", "wasm", "xml", "yaml",
}

SUJETS_OFFENSIFS = [
    "injection", "exploitation", "attaque", "vulnerabilite", "vulnérabilité",
    "xss", "csrf", "idor", "brute force", "hacking",
]


class Fiche:
    def __init__(self, chemin: Path) -> None:
        self.chemin = chemin
        self.html = chemin.read_text(encoding="utf-8", errors="replace")
        # le texte visible, sans balises ni CSS ni scripts
        sans_style = re.sub(r"<(style|script)\b.*?</\1>", " ", self.html, flags=re.S | re.I)
        self.texte = re.sub(r"<[^>]+>", " ", sans_style)
        mode = re.search(r'<meta name="mentor-mode" content="([^"]+)"', self.html)
        self.mode = mode.group(1) if mode else "notion"
        sujet = re.search(r'<meta name="mentor-sujet" content="([^"]+)"', self.html)
        self.sujet = sujet.group(1) if sujet else ""
        self.erreurs: list[str] = []
        self.avertis: list[str] = []

    # -- utilitaires ------------------------------------------------------

    def compte(self, motif: str) -> int:
        return len(re.findall(motif, self.html, re.I))

    def exige(self, condition: bool, message: str) -> None:
        if not condition:
            self.erreurs.append(message)

    def conseille(self, condition: bool, message: str) -> None:
        if not condition:
            self.avertis.append(message)

    # -- contrôles --------------------------------------------------------

    def controler(self) -> None:
        self.metadonnees()
        self.structure()
        self.pedagogie()
        self.entretien()
        self.correction_cachee()
        self.analogies()
        self.securite()
        self.classes_definies()
        self.classes_svg_uniques()
        self.langages_charges()
        self.francais_simple()
        if self.mode == "architecture":
            self.architecture()
        else:
            self.solution()
        if self.sujet == "outil":
            self.outil()

    def classes_svg_uniques(self) -> None:
        """Les `<style>` d'un SVG inline s'appliquent à toute la page.

        Deux schémas qui définissent la même classe (`.lb`, `.t`) se mélangent :
        le second hérite des règles du premier, et un texte se retrouve décalé
        ou rogné. Chaque schéma doit préfixer ses classes.
        """
        vues: dict[str, set[int]] = {}
        for i, svg in enumerate(re.findall(r"<svg\b.*?</svg>", self.html, re.S | re.I)):
            for bloc in re.findall(r"<style>(.*?)</style>", svg, re.S):
                for classe in set(re.findall(r"\.([a-zA-Z][\w-]*)\s*\{", bloc)):
                    vues.setdefault(classe, set()).add(i)
        doublons = sorted(c for c, schemas in vues.items() if len(schemas) > 1)
        self.exige(
            not doublons,
            "classes définies dans plusieurs schémas : " + ", ".join(doublons)
            + " — préfixer les classes de chaque SVG",
        )

    def langages_charges(self) -> None:
        """Chaque `language-X` doit être inclus dans highlight.js ou chargé en module.

        Sinon la coloration abandonne le bloc et la console affiche
        « Could not find the language ».
        """
        employes = set(re.findall(r'class="language-([\w-]+)', self.html))
        modules = set(re.findall(r"/languages/([\w-]+)\.min\.js", self.html))
        manquants = sorted(employes - LANGAGES_INCLUS - modules)
        self.exige(
            not manquants,
            "langage de code sans module highlight.js : " + ", ".join(manquants)
            + " — charger …/languages/<nom>.min.js, ou utiliser language-plaintext",
        )

    def architecture(self) -> None:
        """Ce que le mode architecture exige en plus : la carte et les échanges."""
        self.exige(self.compte(r"<svg\b") >= 2,
                   "mode architecture : il faut au moins deux schémas (la carte, une séquence)")
        self.exige(re.search(r'language-(http|json)', self.html) is not None,
                   "mode architecture : aucun échange montré en texte (bloc http ou json)")
        self.conseille(self.compte(r'class="def"') >= 5,
                       "mode architecture : moins de cinq rôles définis pour les pièces de la carte")

    def classes_definies(self) -> None:
        """Toute classe employée dans la page doit exister dans le style injecté.

        Les classes internes aux SVG sont déclarées dans le `<defs>` de chaque
        schéma, et `language-*` vient de la coloration syntaxique : on les écarte.
        """
        style = re.search(r'<style id="charte">(.*?)</style>', self.html, re.S)
        if not style:
            return
        definies = set(re.findall(r"\.([a-zA-Z][\w-]*)", style.group(1)))

        sans_svg = re.sub(r"<svg\b.*?</svg>", " ", self.html, flags=re.S | re.I)
        sans_style = re.sub(r"<style\b.*?</style>", " ", sans_svg, flags=re.S | re.I)
        employees = set()
        for attribut in re.findall(r'class="([^"]+)"', sans_style):
            employees.update(attribut.split())
        employees = {c for c in employees if not c.startswith("language-")}

        manquantes = sorted(employees - definies)
        self.exige(
            not manquantes,
            "classe sans règle CSS : " + ", ".join(manquantes)
            + " — ajouter la règle dans references/mentor.css",
        )

    def metadonnees(self) -> None:
        for nom in ("mentor-domaine", "mentor-date", "mentor-resume"):
            self.exige(f'name="{nom}"' in self.html, f"métadonnée {nom} absente")
        self.exige(
            "CHARTE:DEBUT" in self.html and "CHARTE:FIN" in self.html,
            "marques de charte absentes : indexer.py ne pourra pas injecter le style",
        )
        self.exige(
            len(re.findall(r"CHARTE:DEBUT", self.html)) == 1
            and self.compte(r"\.container") >= 1,
            "charte non injectée : relancer indexer.py --maj-charte",
        )

    def structure(self) -> None:
        for e in ETAPES.get(self.mode, ETAPES["notion"]):
            self.exige(f'id="{e}"' in self.html, f"étape manquante : id=\"{e}\"")
        self.exige(self.compte(r'class="parcours"') == 1, "barre de parcours absente")
        attendu = len(ETAPES.get(self.mode, ETAPES["notion"]))
        self.exige(self.compte(r'class="etape-tete"') >= attendu,
                   f"moins de {attendu} têtes d'étape pour le mode {self.mode}")

    def section(self, identifiant: str) -> str:
        """Le HTML d'une seule étape, de sa balise ouvrante à la section suivante."""
        debut = re.search(rf'<section[^>]*id="{identifiant}"', self.html)
        if not debut:
            return ""
        suite = re.search(r"<section\b", self.html[debut.end():])
        fin = debut.end() + (suite.start() if suite else len(self.html))
        return self.html[debut.start():fin]

    def solution(self) -> None:
        """L'étape 3 explique la solution en mots. Pas en code."""
        bloc = self.section("solution")
        if not bloc:
            return  # l'absence de l'étape est déjà signalée par structure()

        decisions = len(re.findall(r'class="decision"', bloc, re.I))
        self.exige(
            decisions >= 3,
            f"étape 3 : seulement {decisions} décision(s) — il en faut trois, "
            "chacune avec ses options et sa conséquence",
        )
        for marque, message in (
            (r'class="d-choix"', "aucun choix retenu (.d-choix) dans les décisions"),
            (r'class="a-dire"', "bloc « ce que je dis » absent de l'étape 3"),
            (r'class="bloc limite"', "bloc « ce que ça ne règle pas » absent de l'étape 3"),
            (r'class="bloc cle"', "la solution en une phrase (.bloc cle) est absente de l'étape 3"),
            (r"<table", "tableau de raccord au problème absent de l'étape 3"),
        ):
            self.exige(bool(re.search(marque, bloc, re.I)), f"étape 3 : {message}")

        self.exige(
            "<pre" not in bloc.lower(),
            "étape 3 : un bloc de code s'y trouve — le code appartient à l'étape 4, "
            "l'étape 3 doit se lire à voix haute",
        )

        choix = len(re.findall(r'class="d-choix"', bloc, re.I))
        self.conseille(
            choix >= decisions,
            f"{decisions} décision(s) pour {choix} choix retenu(s) : "
            "une décision sans conséquence écrite est une préférence",
        )

    def outil(self) -> None:
        """Un sujet « outil » doit sortir le lecteur avec 80 % du savoir utile.

        Quatre manques se contrôlent mécaniquement : l'étape des bonnes
        pratiques, l'étape FAQ, le tableau « où ça tourne » et le nombre de
        questions traitées.
        """
        for ident, message in (
            ("pratiques", "étape « Bonnes pratiques » absente (id=\"pratiques\")"),
            ("faq", "étape « FAQ » absente (id=\"faq\")"),
        ):
            self.exige(f'id="{ident}"' in self.html, f"sujet outil : {message}")

        faq = self.section("faq")
        questions = len(re.findall(r'<details class="faq"', faq, re.I))
        self.exige(
            questions >= 8,
            f"sujet outil : seulement {questions} question(s) dans la FAQ — il en "
            "faut huit, écrites avec les mots du lecteur",
        )
        self.exige(
            "<details class=\"faq\" open" not in faq.lower(),
            "sujet outil : une réponse de la FAQ est ouverte par défaut",
        )

        pratiques = self.section("pratiques")
        lignes = len(re.findall(r"<tr>", pratiques, re.I))
        self.conseille(
            lignes >= 9,
            f"sujet outil : {lignes - 1 if lignes else 0} bonne(s) pratique(s) — "
            "il en faut huit à douze, chacune avec « si on ne le fait pas »",
        )

        self.exige(
            re.search(r"[Oo][uù]\s+(ça|tout ça|cela)\s+tourne", self.texte) is not None,
            "sujet outil : aucun passage « où ça tourne » — il faut dire sur quelle "
            "machine l'outil s'exécute, qui la fournit et qui la paie",
        )

    def francais_simple(self) -> None:
        """Longueur des phrases, mesurée uniquement sur les paragraphes.

        Les titres, les badges, les cellules de tableau et les entrées du menu
        n'ont pas de ponctuation finale : les compter comme des phrases donnait
        des alertes fausses. Seul le contenu des `<p>` est mesuré.
        """
        corps = re.sub(r"<(pre|svg|style|script)\b.*?</\1>", " ", self.html, flags=re.S | re.I)

        longues = []
        for brut in re.findall(r"<p\b[^>]*>(.*?)</p>", corps, re.S | re.I):
            texte = re.sub(r"<[^>]+>", " ", brut)
            texte = re.sub(r"\s+", " ", texte).strip()
            for phrase in re.split(r"(?<=[.!?:;])\s+", texte):
                mots = phrase.split()
                if len(mots) > MOTS_PAR_PHRASE:
                    longues.append(" ".join(mots[:10]) + "…")

        self.conseille(
            not longues,
            f"{len(longues)} phrase(s) de plus de {MOTS_PAR_PHRASE} mots dans un "
            "paragraphe — à couper : " + " | ".join(longues[:3]),
        )

    def pedagogie(self) -> None:
        self.exige(self.compte(r'class="def"') >= 2,
                   "moins de deux définitions : un terme dur non défini est probable")
        self.exige(self.compte(r'class="code-bloc"') >= 2,
                   "moins de deux blocs de code : l'étape 3 n'est pas une vraie mise en œuvre")
        self.exige(self.compte(r'class="expl"') >= 1,
                   "aucune explication ligne par ligne sous un bloc de code")
        self.exige("<svg" in self.html, "aucun schéma")
        self.exige(self.compte(r'class="bloc verif"') >= 1,
                   "aucun bloc « Vérifier » : la fiche ne dit pas comment prouver que ça marche")
        self.exige(self.compte(r'class="bloc piege"') >= 1, "aucun piège signalé")
        self.conseille(self.compte(r'class="niv ') >= 3,
                       "moins de trois marques de niveau (essentiel / mise en œuvre / avancé)")
        self.conseille(self.compte(r'class="prerequis"') >= 1,
                       "aucun bloc de prérequis")

        # un schéma doit porter des noms réels, pas « Serveur » / « Service A »
        schemas = " ".join(re.findall(r"<svg\b.*?</svg>", self.html, re.S | re.I))
        generiques = re.findall(r">(Service [A-Z]|Serveur ?\d?|Composant [A-Z]|Système)<", schemas)
        self.conseille(not generiques,
                       f"schéma aux noms génériques : {', '.join(set(generiques))}")

    def entretien(self) -> None:
        self.exige(self.compte(r'class="rep"') >= 1, "réponse courte d'entretien absente")
        self.exige(self.compte(r'class="rep longue"') >= 1, "réponse approfondie absente")
        self.exige(self.compte(r'class="relance"') >= 4,
                   "moins de quatre relances : l'entretien s'arrêtera au deuxième échange")
        self.exige(self.compte(r'class="ne-pas-dire"') >= 1, "bloc « à ne pas dire » absent")

    def correction_cachee(self) -> None:
        quiz = self.compte(r'class="quiz"')
        details = self.compte(r"<details")
        ouverts = self.compte(r"<details[^>]+open")
        self.exige(quiz >= 3, f"seulement {quiz} question(s) de contrôle")
        self.exige(details >= quiz,
                   "une correction au moins n'est pas dans un <details> : elle est visible")
        self.exige(ouverts == 0, "un <details open> laisse une correction visible")

    def analogies(self) -> None:
        trouves = []
        bas = self.texte.lower()
        for mot in ANALOGIES:
            if re.search(r"\b" + re.escape(mot), bas):
                trouves.append(mot)
        self.exige(not trouves, f"analogie interdite : {', '.join(trouves)}")

    def securite(self) -> None:
        """Un script ne peut pas décider si une fiche est offensive.

        Une fiche qui explique une *protection* — le rate limiting, le hachage —
        parle d'attaques sans en montrer aucune : elle n'a pas besoin du bandeau.
        Une fiche qui montre comment *produire* l'effet en a besoin.
        Le contrôle reste donc un avertissement, à trancher en relisant.
        """
        bas = (self.chemin.stem + " " + self.texte[:4000]).lower()
        if any(m in bas for m in SUJETS_OFFENSIFS):
            self.conseille(
                'class="cadre-legal"' in self.html,
                "sujet sensible sans bandeau de cadre légal — obligatoire "
                "seulement si la fiche montre comment produire l'effet, "
                "pas si elle explique une protection",
            )

        for motif, nom in (
            (r"rm -rf", "rm -rf"),
            (r"FLUSHALL", "FLUSHALL"),
            (r"DROP\s+(TABLE|DATABASE)", "DROP TABLE / DATABASE"),
            (r"prune\s+-a", "docker system prune -a"),
        ):
            if re.search(motif, self.html, re.I):
                self.conseille(
                    'class="danger' in self.html,
                    f"commande destructive ({nom}) sans aucune marque .danger dans la fiche",
                )


def controler_fiche(chemin: Path) -> bool:
    f = Fiche(chemin)
    f.controler()
    etat = "OK " if not f.erreurs else "KO "
    print(f"\n{etat} {chemin.name}")
    for e in f.erreurs:
        print(f"     [erreur] {e}")
    for a in f.avertis:
        print(f"     [a voir] {a}")
    if not f.erreurs and not f.avertis:
        print("     toutes les vérifications mécaniques passent")
    return not f.erreurs


def main() -> int:
    for flux in (sys.stdout, sys.stderr):
        if hasattr(flux, "reconfigure"):
            flux.reconfigure(encoding="utf-8", errors="replace")

    p = argparse.ArgumentParser(description="Vérifie les fiches Technical Mentor.")
    p.add_argument("fiche", nargs="?", help="une fiche précise (sinon, toutes)")
    p.add_argument("--dossier", default=str(DOSSIER_DEFAUT))
    args = p.parse_args()

    dossier = Path(args.dossier)
    if args.fiche:
        cibles = [dossier / args.fiche if not Path(args.fiche).is_absolute() else Path(args.fiche)]
    else:
        cibles = [c for c in sorted(dossier.glob("*.html")) if c.name != "index.html"]

    if not cibles:
        print("Aucune fiche à vérifier.")
        return 1

    resultats = [controler_fiche(c) for c in cibles if c.is_file()]
    bons = sum(resultats)
    print(f"\n{bons}/{len(resultats)} fiche(s) sans erreur bloquante.")
    return 0 if bons == len(resultats) else 1


if __name__ == "__main__":
    sys.exit(main())

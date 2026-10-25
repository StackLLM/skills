"""Domaines professionnels : détection et plan de CV adapté.

La détection par mots-clés sert de second avis reproductible : le modèle
reste juge et peut imposer « domaine » et « niveau » dans le JSON du CV.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import date

# ---------------------------------------------------------------------------
# Signaux de détection (minuscules, sans accents). Poids : 1 par occurrence.
# ---------------------------------------------------------------------------
SIGNAUX: dict[str, list[str]] = {
    "tech": [
        "developpeur", "developer", "software", "logiciel", "full-stack", "full stack", "frontend", "backend",
        "react", "angular", "vue", "node", "python", "java", "typescript", "javascript", "php", "laravel",
        "django", "flask", "api", "devops", "docker", "kubernetes", "cloud", "aws", "azure", "gcp", "sql",
        "mongodb", "git", "ci/cd", "data scientist", "machine learning", "cybersecurite", "reseaux", "sysadmin",
        "n8n", "automatisation", "scrum", "data analyst", "data science", "data engineer", "analyse de donnees",
        "pandas", "numpy", "scikit-learn", "etl", "big data", "business intelligence",
    ],
    "ingenierie": [
        "ingenieur", "engineer", "mecanique", "electrique", "electronique", "automatisme", "automate", "plc",
        "genie civil", "structure", "bureau d'etudes", "catia", "solidworks", "autocad", "matlab", "simulink",
        "production", "maintenance", "qualite", "lean", "six sigma", "iso", "hse", "procede", "industrialisation",
        "methodes", "chantier", "btp", "energie", "thermique",
    ],
    "finance": [
        "finance", "financier", "comptable", "comptabilite", "audit", "controle de gestion", "controleur",
        "tresorerie", "fiscalite", "ifrs", "consolidation", "reporting", "budget", "analyste financier",
        "banque", "credit", "risque", "investissement", "m&a", "sage", "excel", "vba", "power bi", "cfa", "acca",
        "bilan", "p&l", "kpi",
    ],
    "marketing": [
        "marketing", "communication", "digital", "seo", "sea", "social media", "reseaux sociaux", "community",
        "contenu", "content", "brand", "marque", "campagne", "google ads", "meta ads", "emailing", "crm",
        "growth", "acquisition", "ga4", "hubspot", "canva", "influence", "evenementiel",
    ],
    "commercial": [
        "commercial", "vente", "ventes", "sales", "business developer", "prospection", "chiffre d'affaires",
        "portefeuille clients", "negociation", "account manager", "key account", "b2b", "b2c", "objectifs",
        "closing", "salesforce", "pipeline", "relation client", "conseiller clientele", "teleconseiller",
    ],
    "management": [
        "manager", "management", "directeur", "director", "head of", "responsable", "chef de projet",
        "project manager", "pmo", "pmp", "prince2", "equipe de", "encadrement", "leadership", "strategie",
        "transformation", "pilotage", "comite de direction", "p&l",
    ],
    "design": [
        "designer", "design", "ui", "ux", "figma", "adobe", "photoshop", "illustrator", "indesign", "after effects",
        "motion", "graphiste", "direction artistique", "branding", "maquette", "prototype", "behance", "dribbble",
        "typographie", "identite visuelle",
    ],
    "sante": [
        "infirmier", "infirmiere", "medecin", "pharmacien", "pharmacie", "aide-soignant", "kinesitherapeute",
        "sage-femme", "patient", "patients", "soins", "hopital", "clinique", "chu", "urgences", "bloc operatoire",
        "laboratoire", "biologie medicale", "dentaire", "sante",
    ],
    "juridique": [
        "juriste", "avocat", "droit", "juridique", "contentieux", "contrats", "conformite", "compliance",
        "notaire", "barreau", "rgpd", "propriete intellectuelle", "droit des affaires", "droit social",
        "veille juridique", "due diligence", "clerc",
    ],
}

LIBELLES_DOMAINE = {
    "tech": "Tech / IT", "ingenierie": "Ingénierie", "finance": "Finance / Business",
    "marketing": "Marketing / Communication", "commercial": "Commercial / Vente", "management": "Management",
    "design": "Design", "sante": "Santé", "juridique": "Juridique", "autre": "Généraliste",
}

# ---------------------------------------------------------------------------
# Plans de sections par domaine.
#   principale / laterale : ordre des sections dans chaque colonne.
#   competences : titre de la section compétences.
#   chiffres : met en gras les résultats chiffrés (%, montants, ×N).
# Les sections vides sont simplement omises.
# ---------------------------------------------------------------------------
PLANS: dict[str, dict] = {
    "tech": {
        "principale": ["profil", "experiences", "projets", "certifications"],
        "laterale": ["formation", "competences", "langues", "qualites"],
        "competences": "Compétences techniques", "chiffres": False,
    },
    "ingenierie": {
        "principale": ["profil", "experiences", "projets", "certifications"],
        "laterale": ["formation", "competences", "langues", "qualites"],
        "competences": "Expertise technique", "chiffres": True,
    },
    "finance": {
        "principale": ["profil", "realisations", "experiences", "certifications"],
        "laterale": ["formation", "competences", "langues", "qualites"],
        "competences": "Compétences clés", "chiffres": True,
    },
    "marketing": {
        "principale": ["profil", "realisations", "experiences", "projets"],
        "laterale": ["competences", "formation", "certifications", "langues", "qualites"],
        "competences": "Compétences", "chiffres": True,
    },
    "commercial": {
        "principale": ["profil", "realisations", "experiences"],
        "laterale": ["competences", "formation", "certifications", "langues", "qualites"],
        "competences": "Compétences commerciales", "chiffres": True,
    },
    "management": {
        "principale": ["profil", "realisations", "experiences"],
        "laterale": ["competences", "formation", "certifications", "langues", "qualites"],
        "competences": "Compétences de direction", "chiffres": True,
    },
    "design": {
        "principale": ["profil", "experiences", "projets"],
        "laterale": ["competences", "formation", "certifications", "langues", "qualites"],
        "competences": "Expertise et outils", "chiffres": False,
    },
    "sante": {
        "principale": ["profil", "experiences", "formation"],
        "laterale": ["competences", "certifications", "langues", "qualites"],
        "competences": "Compétences cliniques", "chiffres": False,
    },
    "juridique": {
        "principale": ["profil", "experiences", "formation"],
        "laterale": ["competences", "certifications", "langues", "qualites"],
        "competences": "Domaines d'expertise", "chiffres": False,
    },
    "autre": {
        "principale": ["profil", "experiences", "realisations", "projets"],
        "laterale": ["formation", "competences", "certifications", "langues", "qualites"],
        "competences": "Compétences", "chiffres": False,
    },
}

# Titres de sections (standards ATS) en français et en anglais.
TITRES = {
    "fr": {
        "profil": "Profil", "experiences": "Expériences professionnelles", "experiences_junior": "Expériences et stages",
        "projets": "Projets", "realisations": "Réalisations clés", "formation": "Formation",
        "certifications": "Certifications", "langues": "Langues", "qualites": "Qualités et intérêts",
        "soft_skills": "Soft skills", "interets": "Centres d'intérêt", "soft_interets": "Soft skills et intérêts",
        "present": "Présent", "ans": "ans",
    },
    "en": {
        "profil": "Summary", "experiences": "Professional Experience", "experiences_junior": "Experience and Internships",
        "projets": "Projects", "realisations": "Key Achievements", "formation": "Education",
        "certifications": "Certifications", "langues": "Languages", "qualites": "Skills and Interests",
        "soft_skills": "Soft skills", "interets": "Interests", "soft_interets": "Soft skills and interests",
        "present": "Present", "ans": "years old",
    },
}

TITRES_COMPETENCES_EN = {
    "Compétences techniques": "Technical Skills", "Expertise technique": "Technical Expertise",
    "Compétences clés": "Core Skills", "Compétences": "Skills", "Compétences commerciales": "Sales Skills",
    "Compétences de direction": "Leadership Skills", "Expertise et outils": "Expertise and Tools",
    "Compétences cliniques": "Clinical Skills", "Domaines d'expertise": "Areas of Expertise",
}

# Marchés où la photo n'est pas d'usage (risque de discrimination à l'embauche).
MARCHES_SANS_PHOTO = {"usa", "etats-unis", "us", "uk", "royaume-uni", "canada", "irlande", "australie"}


def sans_accents(texte: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", texte.lower()) if unicodedata.category(c) != "Mn")


POIDS_TITRE = 3  # le poste visé est le signal le plus fiable


def _compter(texte: str) -> dict[str, int]:
    t = sans_accents(texte)
    return {d: sum(len(re.findall(r"(?<![a-z])" + re.escape(m) + r"(?![a-z])", t)) for m in mots)
            for d, mots in SIGNAUX.items()}


def detecter_domaine(texte: str, titre: str = "") -> dict:
    """Score chaque domaine par mots-clés (titre visé ×3) ; renvoie le meilleur et le détail."""
    scores = _compter(texte)
    if titre:
        for d, n in _compter(titre).items():
            scores[d] += POIDS_TITRE * n
    ordre = sorted(scores, key=scores.get, reverse=True)
    meilleur = ordre[0] if scores[ordre[0]] >= 3 else "autre"
    # Marketing et commercial se recoupent : on garde le plus marqué, mais on signale.
    return {"domaine": meilleur, "scores": scores, "second": ordre[1]}


_DATE = re.compile(r"(?:(\d{1,2})[/.-])?(\d{4})")


def parse_date(valeur: str | None, aujourd_hui: date | None = None) -> date | None:
    """« 03/2025 », « 2025 », « Présent » → date (1er du mois)."""
    if not valeur:
        return None
    v = sans_accents(str(valeur))
    if any(m in v for m in ("present", "aujourd", "actuel", "en cours", "current", "now")):
        return aujourd_hui or date.today()
    m = _DATE.search(v)
    if not m:
        return None
    mois = int(m.group(1)) if m.group(1) else 1
    if not 1 <= mois <= 12:
        return None
    return date(int(m.group(2)), mois, 1)


def annees_experience(cv: dict) -> float:
    """Années d'expérience hors stages, périodes qui se chevauchent fusionnées."""
    periodes = []
    for e in cv.get("experiences", []):
        intitule = sans_accents(f"{e.get('poste', '')} {e.get('type', '')}")
        if any(m in intitule for m in ("stage", "stagiaire", "intern", "alternance", "apprenti")):
            continue
        d, f = parse_date(e.get("debut")), parse_date(e.get("fin") or "present")
        if d and f and f >= d:
            periodes.append((d, f))
    periodes.sort()
    total, fin_courante, debut_courant = 0.0, None, None
    for d, f in periodes:
        if fin_courante and d <= fin_courante:
            fin_courante = max(fin_courante, f)
            continue
        if fin_courante:
            total += (fin_courante - debut_courant).days
        debut_courant, fin_courante = d, f
    if fin_courante:
        total += (fin_courante - debut_courant).days
    return round(total / 365.25, 1)


def detecter_niveau(cv: dict) -> str:
    annees = annees_experience(cv)
    if annees < 2:
        return "junior"
    if annees < 8:
        return "confirme"
    return "senior"


def texte_du_cv(cv: dict) -> str:
    """Tout le texte utile du CV, pour la détection."""
    morceaux = [cv.get("identite", {}).get("titre", ""), cv.get("profil", "")]
    for e in cv.get("experiences", []):
        morceaux += [e.get("poste", ""), e.get("entreprise", ""), *e.get("points", [])]
    for g in cv.get("competences", []):
        morceaux += [g.get("groupe", ""), *g.get("elements", [])] if isinstance(g, dict) else [str(g)]
    for p in cv.get("projets", []):
        morceaux += [p.get("nom", ""), p.get("description", "")]
    for f in cv.get("formation", []):
        morceaux += [f.get("diplome", "")]
    morceaux += [str(c) for c in cv.get("certifications", [])]
    morceaux += cv.get("realisations", [])
    return "\n".join(m for m in morceaux if m)


def plan_pour(cv: dict) -> dict:
    """Plan final (domaine, niveau, sections par colonne, titres)."""
    domaine = cv.get("domaine") or "auto"
    if domaine == "auto" or domaine not in PLANS:
        domaine = detecter_domaine(texte_du_cv(cv), cv.get("identite", {}).get("titre", ""))["domaine"]
    niveau = cv.get("niveau") or "auto"
    if niveau == "auto":
        niveau = detecter_niveau(cv)
    base = PLANS[domaine]
    principale, laterale = list(base["principale"]), list(base["laterale"])

    if niveau == "junior":
        # Profil junior : la formation passe juste après le profil, les projets remontent.
        for col in (principale, laterale):
            if "formation" in col:
                col.remove("formation")
        principale.insert(1, "formation")
        if "projets" in principale and "experiences" in principale:
            principale.remove("projets")
            principale.insert(principale.index("experiences") + 1, "projets")
        elif cv.get("projets") and "projets" not in principale:
            principale.insert(principale.index("experiences") + 1 if "experiences" in principale else 2, "projets")

    # Sections présentes dans les données mais absentes du plan : on ne perd rien.
    for cle in ("realisations", "projets", "certifications"):
        if cv.get(cle) and cle not in principale and cle not in laterale:
            (principale if cle != "certifications" else laterale).append(cle)

    langue = cv.get("langue", "fr")
    titre_comp = cv.get("titre_competences") or base["competences"]
    if langue == "en":
        titre_comp = TITRES_COMPETENCES_EN.get(titre_comp, titre_comp)
    return {
        "domaine": domaine,
        "libelle_domaine": LIBELLES_DOMAINE[domaine],
        "niveau": niveau,
        "annees_experience": annees_experience(cv),
        "principale": principale,
        "laterale": laterale,
        "titre_competences": titre_comp,
        "chiffres_en_gras": base["chiffres"],
        "titres": TITRES.get(langue, TITRES["fr"]),
        "langue": langue,
    }


def photo_autorisee(cv: dict) -> tuple[bool, str]:
    """La photo n'apparaît que si elle est fournie et d'usage sur le marché visé."""
    if not cv.get("photo"):
        return False, "aucune photo fournie"
    marche = sans_accents(cv.get("marche", "maroc"))
    if marche in MARCHES_SANS_PHOTO and not cv.get("photo_forcee"):
        return False, f"photo retirée : peu d'usage au marché « {cv.get('marche')} » (forcer avec photo_forcee)"
    return True, "photo incluse"

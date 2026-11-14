"""En-têtes de sécurité posés sur chaque réponse, en local comme en ligne.

La politique de contenu (CSP) part de « rien sauf soi-même » : on n'ouvre que ce qui sert,
une source à la fois, avec un commentaire qui dit pourquoi.
"""

from __future__ import annotations

from urllib.parse import urlsplit

POLITIQUE_CONTENU = "; ".join(
    [
        "default-src 'self'",
        "script-src 'self'",
        "style-src 'self'",
        "img-src 'self' data:",
        "font-src 'self'",
        "connect-src 'self'",
        "object-src 'none'",
        "base-uri 'self'",
        "form-action 'self'",
        "frame-ancestors 'none'",
    ]
)

ENTETES_SECURITE: dict[str, str] = {
    "Content-Security-Policy": POLITIQUE_CONTENU,
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=(), payment=(), usb=()",
    "X-Frame-Options": "DENY",
    "Cross-Origin-Opener-Policy": "same-origin",
}

# HSTS seulement quand le service est servi en HTTPS : sinon le navigateur l'ignore, ou bloque le local.
HSTS = "max-age=31536000; includeSubDomains"


def origine_acceptee(origine_requete: str | None, origine_service: str, hote_requete: str | None) -> bool:
    """Une requête qui modifie doit venir de notre propre origine (protection contre la falsification, CSRF).

    Sans en-tête Origin (outil en ligne de commande, serveur à serveur), on laisse passer : ce n'est pas un navigateur.
    """
    if not origine_requete:
        return True
    if origine_service and origine_requete == origine_service:
        return True
    return bool(hote_requete) and urlsplit(origine_requete).netloc == hote_requete

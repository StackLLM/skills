"""L'application FastAPI : santé, API, puis le frontend compilé.

Chaque requête reçoit un identifiant, ses en-têtes de sécurité, et une ligne de journal.
Une erreur attendue renvoie un message utile ; une panne renvoie un 500 générique, le détail part au journal.
Lancement : uvicorn app.main:application (voir package.json à la racine).
"""

from __future__ import annotations

import math
import re
import time
import uuid
from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .config import Config
from .journal import configurer_journal
from .limites import Limiteur
from .sante import Controle, disque_inscriptible
from .sante import routeur as routeur_sante
from .securite import ENTETES_SECURITE, HSTS, origine_acceptee

TAILLE_MAX_CORPS = 16 * 1024
HEURE = 3600.0
ID_REQUETE = re.compile(r"^[\w-]{8,64}$")
METHODES_SANS_EFFET = {"GET", "HEAD", "OPTIONS"}


class ErreurHttp(HTTPException):
    """Une erreur prévue : le statut et le message partent tels quels vers le client."""


# ---- Le formulaire de contact : un exemple complet de route (validation, limite, réponse) ----


class MessageContact(BaseModel):
    """Validation à la frontière : ce qui sort d'ici est sûr et typé."""

    nom: str = Field(min_length=1, max_length=120)
    email: EmailStr
    message: str = Field(min_length=1, max_length=2_000)


def adresse_visiteur(request: Request) -> str:
    """X-Forwarded-For seulement derrière un proxy de confiance : sinon n'importe qui choisit son adresse."""
    config: Config = request.app.state.config
    transmise = request.headers.get("x-forwarded-for")
    if config.proxy and transmise:
        return transmise.split(",")[0].strip()
    return request.client.host if request.client else "inconnue"


def limite_contact(request: Request) -> None:
    limiteur: Limiteur = request.app.state.limite_contact
    verdict = limiteur.essayer(f"contact:{adresse_visiteur(request)}")
    if not verdict.accepte:
        secondes = math.ceil(verdict.reessayer_dans)
        raise ErreurHttp(
            429,
            f"Trop de messages envoyés. Réessayez dans {math.ceil(secondes / 60)} minutes.",
            headers={"Retry-After": str(secondes)},
        )


routeur_api = APIRouter(prefix="/api")


@routeur_api.post("/contact", status_code=202, dependencies=[Depends(limite_contact)])
async def recevoir_contact(contact: MessageContact, request: Request) -> dict[str, bool]:
    # Le métier (envoi du mail, enregistrement) vient ici, dans un service à part, testé sans HTTP.
    request.app.state.journal.info("message de contact reçu", extra={"longueur": len(contact.message)})
    return {"recu": True}


# ---- Les couches communes à toutes les requêtes ----


class _CorpsTropGrandError(Exception):
    pass


class LimiteTailleCorps:
    """Refuse un corps trop grand (413) sans le garder en mémoire. Middleware ASGI : il voit les octets arriver.

    La taille annoncée (Content-Length) est vérifiée tout de suite ; un corps envoyé par morceaux est compté
    au fil de la lecture, et coupé dès qu'il dépasse.
    """

    def __init__(self, application: ASGIApp, taille_max: int) -> None:
        self.application = application
        self.taille_max = taille_max

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.application(scope, receive, send)
            return
        trop_grand = JSONResponse({"erreur": "Requête trop grande."}, status_code=413)
        annoncee = dict(scope["headers"]).get(b"content-length")
        if annoncee and annoncee.isdigit() and int(annoncee) > self.taille_max:
            await trop_grand(scope, receive, send)
            return

        lus = 0
        reponse_commencee = False

        async def recevoir_en_comptant() -> Message:
            nonlocal lus
            message = await receive()
            if message["type"] == "http.request":
                lus += len(message.get("body", b""))
                if lus > self.taille_max:
                    raise _CorpsTropGrandError
            return message

        async def envoyer(message: Message) -> None:
            nonlocal reponse_commencee
            reponse_commencee = reponse_commencee or message["type"] == "http.response.start"
            await send(message)

        try:
            await self.application(scope, recevoir_en_comptant, envoyer)
        except _CorpsTropGrandError:
            if not reponse_commencee:
                await trop_grand(scope, receive, send)


def creer_application(config: Config | None = None, controles: dict[str, Controle] | None = None) -> FastAPI:
    """Fabrique de l'application : les tests créent la leur, avec leur configuration."""
    config = config or Config()
    journal = configurer_journal(config.niveau_journal, json_actif=config.production)
    # La documentation interactive (/docs) seulement en local : en ligne, elle décrit l'API à tout le monde.
    application = FastAPI(
        title="{{NOM}}",
        docs_url=None if config.production else "/docs",
        redoc_url=None,
        openapi_url=None if config.production else "/openapi.json",
    )
    application.state.config = config
    application.state.journal = journal
    application.state.limite_contact = Limiteur(maximum=5, fenetre=HEURE)
    application.state.controles = {"disque": disque_inscriptible(config.donnees), **(controles or {})}

    @application.middleware("http")
    async def chaque_requete(request: Request, suivant: Callable[[Request], Awaitable[Response]]) -> Response:
        debut = time.perf_counter()
        recu = request.headers.get("x-request-id", "")
        # L'identifiant d'un proxy de confiance est repris (même identifiant de bout en bout) ; sinon on en crée un.
        id_requete = recu if config.proxy and ID_REQUETE.match(recu) else str(uuid.uuid4())
        request.state.id_requete = id_requete

        if request.method not in METHODES_SANS_EFFET and not origine_acceptee(
            request.headers.get("origin"), config.origine, request.headers.get("host")
        ):
            reponse: Response = JSONResponse({"erreur": "Origine refusée."}, status_code=403)
        else:
            try:
                reponse = await suivant(request)
            except Exception:
                journal.exception("erreur inattendue", extra={"id_requete": id_requete, "route": request.url.path})
                reponse = JSONResponse(
                    {"erreur": "Erreur interne. Réessayez plus tard.", "id_requete": id_requete}, status_code=500
                )

        reponse.headers["X-Request-Id"] = id_requete
        reponse.headers.update(ENTETES_SECURITE)
        if config.origine.startswith("https://"):
            reponse.headers["Strict-Transport-Security"] = HSTS
        # La santé est appelée toutes les 30 secondes : elle ne remplit pas le journal.
        if not request.url.path.startswith("/sante/"):
            journal.info(
                "requête",
                extra={
                    "id_requete": id_requete,
                    "methode": request.method,
                    "route": request.url.path,
                    "statut": reponse.status_code,
                    "duree_ms": round((time.perf_counter() - debut) * 1000),
                },
            )
        return reponse

    @application.exception_handler(HTTPException)
    async def erreur_prevue(_: Request, erreur: HTTPException) -> JSONResponse:
        return JSONResponse({"erreur": erreur.detail}, status_code=erreur.status_code, headers=erreur.headers)

    @application.exception_handler(RequestValidationError)
    async def saisie_refusee(_: Request, erreur: RequestValidationError) -> JSONResponse:
        champs = sorted({str(e["loc"][-1]) for e in erreur.errors() if e.get("loc")})
        return JSONResponse({"erreur": "Saisie invalide.", "champs": champs}, status_code=400)

    application.add_middleware(LimiteTailleCorps, taille_max=TAILLE_MAX_CORPS)
    application.include_router(routeur_sante)
    application.include_router(routeur_api)

    @application.api_route(
        "/api/{reste:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False
    )
    async def api_inconnue(reste: str) -> None:
        raise ErreurHttp(404, "Adresse d'API inconnue.")

    _servir_site(application, config.site)
    return application


def _servir_site(application: FastAPI, dossier: Path) -> None:
    """Sert le frontend compilé, s'il existe. Une adresse sans extension renvoie index.html (une seule page)."""
    index = dossier / "index.html"
    if not index.is_file():
        return
    if (dossier / "assets").is_dir():
        application.mount("/assets", StaticFiles(directory=dossier / "assets"), name="assets")
    racine = dossier.resolve()

    @application.get("/{chemin:path}", include_in_schema=False)
    async def site(chemin: str) -> FileResponse:
        fichier = (racine / chemin).resolve()
        # Le chemin résolu doit rester dans le dossier du site : pas de ../ possible.
        if fichier.is_relative_to(racine) and fichier.is_file():
            return FileResponse(fichier)
        if Path(chemin).suffix:
            raise ErreurHttp(404, "Page introuvable.")
        return FileResponse(index, headers={"Cache-Control": "no-cache"})


application = creer_application()

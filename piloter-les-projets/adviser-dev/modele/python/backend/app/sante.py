"""Santé du service, en deux questions :

- vivant : le processus répond-il ? Ne touche à rien, pour rester rapide même quand tout va mal.
- prêt   : peut-il servir des requêtes ? Lance chaque contrôle (base, disque…), avec un délai max.

Limite à connaître : un serveur arrêté ne peut pas prévenir de sa propre panne. Il faut aussi une
surveillance extérieure qui appelle /sante/pret.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import Awaitable, Callable
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

Controle = Callable[[], bool | Awaitable[bool]]

DELAI_CONTROLE = 2.0


async def _executer(controle: Controle, delai: float) -> bool:
    async def lancer() -> bool:
        resultat = controle()
        return await resultat if isinstance(resultat, Awaitable) else resultat

    try:
        return await asyncio.wait_for(lancer(), timeout=delai)
    # Un contrôle qui plante ou dépasse le délai est un contrôle en panne : on le dit, sans faire tomber /sante/pret.
    except Exception:
        return False


async def etat_pret(controles: dict[str, Controle], delai: float = DELAI_CONTROLE) -> tuple[bool, dict[str, str]]:
    resultats = await asyncio.gather(*(_executer(c, delai) for c in controles.values()))
    detail = {nom: "ok" if bon else "panne" for nom, bon in zip(controles, resultats, strict=True)}
    return all(resultats), detail


def disque_inscriptible(dossier: Path) -> Controle:
    """Contrôle courant : le dossier de données existe et on peut y écrire."""

    def controler() -> bool:
        dossier.mkdir(parents=True, exist_ok=True)
        return os.access(dossier, os.W_OK)

    return controler


routeur = APIRouter(prefix="/sante", tags=["santé"])


@routeur.get("/vivant")
async def vivant() -> dict[str, str]:
    return {"etat": "ok"}


@routeur.get("/pret")
async def pret(request: Request) -> JSONResponse:
    bon, detail = await etat_pret(request.app.state.controles)
    return JSONResponse({"etat": "ok" if bon else "panne", "controles": detail}, status_code=200 if bon else 503)

"""Fixtures communes : une configuration de test, une application et son client, dans un dossier temporaire.

Les tests ne lisent jamais backend/.env : leur configuration est écrite ici.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Config
from app.limites import Limiteur
from app.main import creer_application
from app.sante import Controle

FabriqueClient = Callable[..., TestClient]


@pytest.fixture
def config(tmp_path: Path) -> Config:
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("<!doctype html><title>Accueil</title>", encoding="utf-8")
    return Config(_env_file=None, donnees=tmp_path / "donnees", site=site)  # type: ignore[call-arg]


@pytest.fixture
def fabriquer_client(config: Config) -> Iterator[FabriqueClient]:
    """Crée un client sur une application neuve ; `controles` ajoute des contrôles de santé."""
    clients: list[TestClient] = []

    def fabriquer(controles: dict[str, Controle] | None = None, **reglages: object) -> TestClient:
        application = creer_application(config.model_copy(update=reglages), controles)
        application.state.limite_contact = Limiteur(maximum=2, fenetre=60)
        client = TestClient(application)
        clients.append(client)
        return client

    yield fabriquer
    for client in clients:
        client.close()


@pytest.fixture
def client(fabriquer_client: FabriqueClient) -> TestClient:
    return fabriquer_client()

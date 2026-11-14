"""Configuration du backend : lue une seule fois, au démarrage, depuis l'environnement (et backend/.env).

Une valeur obligatoire absente en production arrête le démarrage, avec un message clair :
mieux vaut un serveur qui refuse de démarrer qu'un serveur qui démarre faux.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DOSSIER_BACKEND = Path(__file__).resolve().parent.parent

NiveauJournal = Literal["debug", "info", "warning", "error"]


class Config(BaseSettings):
    """Tous les réglages du service. Les tests créent la leur : Config(_env_file=None, ...)."""

    model_config = SettingsConfigDict(env_prefix="{{PREFIXE}}_", env_file=DOSSIER_BACKEND / ".env", extra="ignore")

    environnement: Literal["developpement", "production"] = "developpement"
    port: int = Field(default={{PORT}}, ge=1, le=65_535)
    # Derrière un proxy local, on n'écoute que la machine ; en conteneur, {{PREFIXE}}_HOTE=0.0.0.0.
    hote: str = "127.0.0.1"
    # Adresse publique du service (https://…), sans / final. Sert au contrôle d'origine.
    origine: str = ""
    # Vrai si un proxy de confiance est devant : on lit alors X-Forwarded-For.
    proxy: bool = False
    donnees: Path = DOSSIER_BACKEND / "data"
    # Dossier du frontend compilé, servi par le backend s'il existe.
    site: Path = DOSSIER_BACKEND.parent / "frontend" / "dist"
    journal: NiveauJournal | None = None

    @property
    def production(self) -> bool:
        return self.environnement == "production"

    @property
    def niveau_journal(self) -> NiveauJournal:
        return self.journal or ("info" if self.production else "debug")

    @field_validator("origine")
    @classmethod
    def _origine_propre(cls, valeur: str) -> str:
        valeur = valeur.strip().rstrip("/")
        if valeur and not valeur.startswith(("http://", "https://")):
            raise ValueError(f"doit ressembler à https://exemple.ma (reçu : {valeur})")
        return valeur

    @model_validator(mode="after")
    def _obligatoire_en_production(self) -> Self:
        if self.production and not self.origine:
            raise ValueError("{{PREFIXE}}_ORIGINE manque : en production, il faut l'adresse publique du service (https://…).")
        return self

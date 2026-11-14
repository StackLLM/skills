"""Journaux : une ligne par événement, sur la sortie standard. C'est Docker ou l'hébergeur qui les range.

En production : JSON (lisible par les outils). En local : une ligne courte, lisible par un humain.
Jamais de secret ici : les champs sensibles connus sont masqués avant l'écriture.
"""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import UTC, datetime
from typing import Any, cast

SENSIBLE = re.compile(r"mot.?de.?passe|password|jeton|token|secret|cle|key|cookie|authorization", re.IGNORECASE)
CHAMPS_STANDARD = set(vars(logging.makeLogRecord({})))


def masquer(valeur: Any) -> Any:
    """Remplace la valeur des champs sensibles, à tous les niveaux d'une structure."""
    if isinstance(valeur, dict):
        return {cle: "***" if SENSIBLE.search(str(cle)) else masquer(v) for cle, v in valeur.items()}
    if isinstance(valeur, list):
        return [masquer(v) for v in valeur]
    return valeur


def _champs(enregistrement: logging.LogRecord) -> dict[str, Any]:
    """Les champs passés avec extra={...}, masqués."""
    propres = {cle: v for cle, v in vars(enregistrement).items() if cle not in CHAMPS_STANDARD}
    return cast(dict[str, Any], masquer(propres))


class FormatJson(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        ligne = {
            "heure": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "niveau": record.levelname.lower(),
            "message": record.getMessage(),
            **_champs(record),
        }
        if record.exc_info:
            ligne["erreur"] = self.formatException(record.exc_info)
        return json.dumps(ligne, ensure_ascii=False, default=str)


class FormatLisible(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        details = " ".join(f"{cle}={v}" for cle, v in _champs(record).items())
        ligne = f"{record.levelname:<7} {record.getMessage()}{'  ' + details if details else ''}"
        return ligne + ("\n" + self.formatException(record.exc_info) if record.exc_info else "")


def configurer_journal(niveau: str, *, json_actif: bool) -> logging.Logger:
    """Configure le journal du service. Appelée une fois, au démarrage."""
    journal = logging.getLogger("service")
    journal.handlers.clear()
    sortie = logging.StreamHandler(sys.stdout)
    sortie.setFormatter(FormatJson() if json_actif else FormatLisible())
    journal.addHandler(sortie)
    journal.setLevel(niveau.upper())
    journal.propagate = False
    return journal

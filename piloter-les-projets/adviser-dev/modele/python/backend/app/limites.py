"""Limites d'essais (rate limiting) : au-delà de `maximum` essais dans la fenêtre, la clé est refusée.

Limite à connaître : les compteurs vivent en mémoire. Un redémarrage les remet à zéro, et avec
plusieurs instances (plusieurs workers uvicorn compris) chacune compte de son côté. Dans ces cas,
les ranger dans la base ou dans Redis, en gardant la même interface.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from threading import Lock

# Nombre de clés au-delà duquel on nettoie les fenêtres terminées : la mémoire reste bornée.
NETTOYAGE_APRES = 10_000


@dataclass(frozen=True)
class Verdict:
    accepte: bool
    reessayer_dans: float = 0.0


@dataclass
class _Compteur:
    nombre: int
    debut: float


class Limiteur:
    def __init__(self, maximum: int, fenetre: float, horloge: Callable[[], float] = time.monotonic) -> None:
        if maximum < 1 or fenetre <= 0:
            raise ValueError("Un limiteur demande maximum ≥ 1 et une fenêtre > 0.")
        self._maximum = maximum
        self._fenetre = fenetre
        self._horloge = horloge
        self._compteurs: dict[str, _Compteur] = {}
        self._verrou = Lock()

    def essayer(self, cle: str) -> Verdict:
        """Compte un essai pour cette clé et dit s'il est accepté."""
        with self._verrou:
            maintenant = self._horloge()
            if len(self._compteurs) > NETTOYAGE_APRES:
                self._nettoyer(maintenant)
            compteur = self._compteurs.get(cle)
            if compteur is None or maintenant - compteur.debut >= self._fenetre:
                compteur = _Compteur(nombre=0, debut=maintenant)
                self._compteurs[cle] = compteur
            compteur.nombre += 1
            if compteur.nombre <= self._maximum:
                return Verdict(accepte=True)
            return Verdict(accepte=False, reessayer_dans=compteur.debut + self._fenetre - maintenant)

    def rendre(self, cle: str) -> None:
        """Rend un essai compté d'avance, quand il s'est révélé bon (connexion réussie)."""
        with self._verrou:
            compteur = self._compteurs.get(cle)
            if compteur and compteur.nombre > 0:
                compteur.nombre -= 1

    def _nettoyer(self, maintenant: float) -> None:
        for cle in [c for c, compteur in self._compteurs.items() if maintenant - compteur.debut >= self._fenetre]:
            del self._compteurs[cle]

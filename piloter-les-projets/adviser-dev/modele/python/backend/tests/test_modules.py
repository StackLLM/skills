"""Tests unitaires : configuration, limites d'essais, journaux. Sans serveur, sans réseau."""

from __future__ import annotations

import json
import logging

import pytest
from pydantic import ValidationError

from app.config import Config
from app.journal import FormatJson, masquer
from app.limites import Limiteur


class TestConfiguration:
    def test_donne_des_valeurs_sures_par_defaut(self) -> None:
        config = Config(_env_file=None)  # type: ignore[call-arg]
        assert config.production is False
        assert config.port == {{PORT}}
        assert config.hote == "127.0.0.1"
        assert config.proxy is False

    def test_refuse_de_demarrer_en_production_sans_adresse_publique(self) -> None:
        with pytest.raises(ValidationError, match="{{PREFIXE}}_ORIGINE"):
            Config(_env_file=None, environnement="production")  # type: ignore[call-arg]

    def test_refuse_un_port_invalide(self) -> None:
        with pytest.raises(ValidationError):
            Config(_env_file=None, port=70_000)  # type: ignore[call-arg]

    def test_retire_le_slash_final_de_l_origine(self) -> None:
        assert Config(_env_file=None, origine="https://exemple.ma/").origine == "https://exemple.ma"  # type: ignore[call-arg]


class TestLimites:
    def test_accepte_jusqu_au_maximum_puis_refuse_avec_le_temps_restant(self) -> None:
        maintenant = [0.0]
        limiteur = Limiteur(maximum=2, fenetre=10, horloge=lambda: maintenant[0])
        assert limiteur.essayer("a").accepte
        assert limiteur.essayer("a").accepte
        maintenant[0] = 4
        verdict = limiteur.essayer("a")
        assert not verdict.accepte
        assert verdict.reessayer_dans == 6

    def test_repart_a_zero_quand_la_fenetre_est_finie(self) -> None:
        maintenant = [0.0]
        limiteur = Limiteur(maximum=1, fenetre=10, horloge=lambda: maintenant[0])
        limiteur.essayer("a")
        maintenant[0] = 10
        assert limiteur.essayer("a").accepte

    def test_compte_chaque_cle_separement(self) -> None:
        limiteur = Limiteur(maximum=1, fenetre=10)
        limiteur.essayer("a")
        assert limiteur.essayer("b").accepte

    def test_un_essai_rendu_ne_compte_plus(self) -> None:
        limiteur = Limiteur(maximum=1, fenetre=10)
        limiteur.essayer("a")
        limiteur.rendre("a")
        assert limiteur.essayer("a").accepte


class TestJournal:
    def test_masque_les_champs_sensibles_meme_imbriques(self) -> None:
        brut = {"identifiant": "admin", "mot_de_passe": "x", "session": {"jeton": "y"}}
        assert masquer(brut) == {"identifiant": "admin", "mot_de_passe": "***", "session": {"jeton": "***"}}

    def test_ecrit_une_ligne_json_avec_le_niveau_et_les_champs(self) -> None:
        enregistrement = logging.makeLogRecord({"msg": "requête", "levelname": "INFO", "statut": 200, "token": "z"})
        ligne = json.loads(FormatJson().format(enregistrement))
        assert ligne["niveau"] == "info"
        assert ligne["message"] == "requête"
        assert ligne["statut"] == 200
        assert ligne["token"] == "***"

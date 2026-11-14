"""Tests d'intégration : la vraie application, avec un dossier temporaire, sans réseau."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.conftest import FabriqueClient

CONTACT_VALIDE = {"nom": "Mourad", "email": "mourad@exemple.ma", "message": "Bonjour"}


def panne() -> bool:
    raise ConnectionError("base injoignable")


class TestSante:
    def test_vivant_repond_sans_rien_controler(self, client: TestClient) -> None:
        reponse = client.get("/sante/vivant")
        assert reponse.status_code == 200
        assert reponse.json() == {"etat": "ok"}

    def test_pret_repond_200_quand_le_disque_est_inscriptible(self, client: TestClient) -> None:
        reponse = client.get("/sante/pret")
        assert reponse.status_code == 200
        assert reponse.json() == {"etat": "ok", "controles": {"disque": "ok"}}

    def test_pret_repond_503_quand_une_dependance_est_en_panne(self, fabriquer_client: FabriqueClient) -> None:
        reponse = fabriquer_client({"base": panne}).get("/sante/pret")
        assert reponse.status_code == 503
        assert reponse.json() == {"etat": "panne", "controles": {"disque": "ok", "base": "panne"}}


class TestProtection:
    def test_chaque_reponse_porte_les_entetes_de_securite(self, client: TestClient) -> None:
        reponse = client.get("/")
        assert reponse.headers["x-content-type-options"] == "nosniff"
        assert "default-src 'self'" in reponse.headers["content-security-policy"]
        assert reponse.headers["x-frame-options"] == "DENY"
        assert len(reponse.headers["x-request-id"]) >= 8

    def test_ignore_l_identifiant_de_requete_du_visiteur_sans_proxy(self, client: TestClient) -> None:
        reponse = client.get("/sante/vivant", headers={"X-Request-Id": "choisi-par-le-visiteur"})
        assert reponse.headers["x-request-id"] != "choisi-par-le-visiteur"

    def test_reprend_l_identifiant_derriere_un_proxy_de_confiance(self, fabriquer_client: FabriqueClient) -> None:
        reponse = fabriquer_client(proxy=True).get("/sante/vivant", headers={"X-Request-Id": "abc-12345678"})
        assert reponse.headers["x-request-id"] == "abc-12345678"

    def test_refuse_une_requete_qui_modifie_venant_d_une_autre_origine(self, client: TestClient) -> None:
        reponse = client.post("/api/contact", json=CONTACT_VALIDE, headers={"Origin": "https://pirate.exemple"})
        assert reponse.status_code == 403

    def test_refuse_un_corps_trop_grand(self, client: TestClient) -> None:
        reponse = client.post("/api/contact", json={**CONTACT_VALIDE, "message": "x" * 20_000})
        assert reponse.status_code == 413

    def test_bloque_apres_le_maximum_de_messages_avec_retry_after(self, client: TestClient) -> None:
        assert client.post("/api/contact", json=CONTACT_VALIDE).status_code == 202
        assert client.post("/api/contact", json=CONTACT_VALIDE).status_code == 202
        bloque = client.post("/api/contact", json=CONTACT_VALIDE)
        assert bloque.status_code == 429
        assert int(bloque.headers["retry-after"]) > 0

    def test_ne_sert_aucun_fichier_hors_du_dossier_du_site(self, client: TestClient) -> None:
        assert client.get("/%2e%2e/%2e%2e/pyproject.toml").status_code == 404

    def test_une_adresse_d_api_inconnue_repond_404_en_json(self, client: TestClient) -> None:
        reponse = client.get("/api/inconnue")
        assert reponse.status_code == 404
        assert "inconnue" in reponse.json()["erreur"]


class TestContact:
    def test_accepte_un_message_complet(self, client: TestClient) -> None:
        reponse = client.post("/api/contact", json=CONTACT_VALIDE)
        assert reponse.status_code == 202
        assert reponse.json() == {"recu": True}

    def test_refuse_une_adresse_e_mail_invalide_en_nommant_le_champ(self, client: TestClient) -> None:
        reponse = client.post("/api/contact", json={**CONTACT_VALIDE, "email": "pas-une-adresse"})
        assert reponse.status_code == 400
        assert reponse.json()["champs"] == ["email"]


def test_le_site_d_une_page_renvoie_index_pour_une_adresse_sans_extension(client: TestClient) -> None:
    reponse = client.get("/compte/reglages")
    assert reponse.status_code == 200
    assert "<title>Accueil</title>" in reponse.text


def test_une_panne_inattendue_renvoie_500_sans_detail(fabriquer_client: FabriqueClient) -> None:
    client = fabriquer_client()

    @client.app.get("/api/boum")  # type: ignore[attr-defined, misc]
    async def boum() -> None:
        raise RuntimeError("détail interne à ne pas montrer")

    # La route ajoutée après coup passe derrière la route « API inconnue » : on la place en tête.
    client.app.router.routes.insert(0, client.app.router.routes.pop())  # type: ignore[attr-defined]
    reponse = TestClient(client.app, raise_server_exceptions=False).get("/api/boum")  # type: ignore[arg-type]
    assert reponse.status_code == 500
    assert "détail interne" not in reponse.text
    assert reponse.json()["id_requete"]

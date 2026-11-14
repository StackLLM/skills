"""Tests : python3 -m unittest test_generer_widget (depuis scripts/).

Le moteur est celui de la skill `map-projet` : les mêmes cartes doivent
donner les mêmes phases, les mêmes verdicts et les mêmes couleurs.
Le rendu, lui, est propre à la réponse : un fragment, pas une page."""

import copy
import json
import unittest
from pathlib import Path

import generer_widget as g
import moteur as m

DOSSIER = Path(__file__).parent


def lot(phase, statut, titre="Lot", source="doc.md"):
    return {"titre": titre, "phase": phase, "statut": statut, "source": source}


def volet(nom, *lots, **autres):
    return {"nom": nom, "resume": "Résumé court.", "lots": list(lots), **autres}


def carte(*volets):
    return {"type": "projet", "nom": "Test", "date": "2026-11-04",
            "verdict": "Verdict.", "prochaine_action": "Action.",
            "volets": list(volets)}


class Controle(unittest.TestCase):
    def test_exemple_valide(self):
        exemple = json.loads((DOSSIER / "exemple-projet.json").read_text("utf-8"))
        self.assertEqual(m.verifier(exemple), [])

    def test_lot_sans_source_refuse(self):
        c = carte(volet("A", lot("Cadrage", "fait", source="")))
        self.assertTrue(any("pas de source" in x for x in m.verifier(c)))

    def test_a_confirmer_accepte_sans_source(self):
        c = carte(volet("A", lot("Cadrage", "a_confirmer", source="")))
        self.assertEqual(m.verifier(c), [])

    def test_texte_trop_long_refuse(self):
        c = carte(volet("A", lot("Cadrage", "fait")))
        c["verdict"] = "x" * 151
        self.assertTrue(any("À raccourcir" in x for x in m.verifier(c)))

    def test_valeur_calculee_refusee(self):
        c = carte(volet("A", lot("Cadrage", "fait"), phase="Bêta"))
        self.assertTrue(any("champ inconnu" in x for x in m.verifier(c)))

    def test_element_qui_n_est_pas_un_objet_refuse(self):
        c = carte(volet("A"))
        c["volets"] = ["front"]
        self.assertTrue(any("objet" in x for x in m.verifier(c)))

    def test_orga_exige_la_derniere_activite(self):
        c = {"type": "orga", "nom": "O", "date": "2026-11-04", "verdict": "V",
             "prochaine_action": "A", "projets": [volet("P", lot("Cadrage", "a_faire"))]}
        self.assertTrue(any("derniere_activite" in x for x in m.verifier(c)))

    def test_phase_inconnue_refusee(self):
        c = carte(volet("A", lot("Recette", "fait")))
        self.assertTrue(any("phase inconnue" in x for x in m.verifier(c)))

    def test_sans_lot_exige_phase_et_source(self):
        erreurs = m.verifier(carte(volet("A")))
        self.assertEqual(len(erreurs), 2)

    def test_phase_estimee_interdite_avec_lots(self):
        c = carte(volet("A", lot("Cadrage", "fait"), phase_estimee="Bêta"))
        self.assertTrue(any("réservée" in x for x in m.verifier(c)))


class Calculs(unittest.TestCase):
    def test_case_verte_si_tout_fait(self):
        self.assertEqual(m.etat_case([lot("Cadrage", "fait")]), "fait")

    def test_case_bleue_si_melange(self):
        lots = [lot("Cadrage", "fait"), lot("Cadrage", "a_venir")]
        self.assertEqual(m.etat_case(lots), "ouvert")

    def test_case_rouge_si_bloquant(self):
        lots = [lot("Cadrage", "fait"), lot("Cadrage", "bloquant")]
        self.assertEqual(m.etat_case(lots), "bloque")

    def test_case_pointillee_si_rien_de_prouve(self):
        lots = [lot("Bêta", "a_confirmer"), lot("Bêta", "a_venir")]
        self.assertEqual(m.etat_case(lots), "confirmer")

    def test_a_confirmer_ne_fait_pas_avancer_la_phase(self):
        v = volet("A", lot("Construction", "fait"), lot("Lancement", "a_confirmer"))
        self.assertEqual(m.PHASES[m.position(v)], "Construction")

    def test_lot_ouvert_n_avance_pas_si_phase_d_avant_pas_finie(self):
        v = volet("A", lot("Construction", "fait"), lot("Construction", "a_faire"),
                  lot("Bêta", "a_faire"))
        self.assertEqual(m.PHASES[m.position(v)], "Construction")

    def test_lot_ouvert_avance_si_phase_d_avant_finie(self):
        v = volet("A", lot("Construction", "fait"), lot("Pré-production", "bloquant"))
        self.assertEqual(m.PHASES[m.position(v)], "Pré-production")

    def test_seul_un_lot_a_confirmer_donne_a_confirmer(self):
        v = volet("A", lot("Cadrage", "a_confirmer"))
        self.assertEqual(m.verdict_element(v, "2026-11-04"), "À confirmer")

    def test_a_l_arret_passe_avant_a_trancher(self):
        v = volet("A", lot("Cadrage", "fait"), lot("Cadrage", "a_trancher"),
                  derniere_activite="2026-01-01")
        self.assertEqual(m.verdict_element(v, "2026-11-04"), "À l'arrêt")

    def test_une_cause_commune_compte_une_fois(self):
        a = lot("Cadrage", "bloquant")
        a["cause"] = "hebergeur"
        b = lot("Cadrage", "bloquant")
        b["cause"] = "hebergeur"
        c = lot("Cadrage", "bloquant")
        t = m.totaux([volet("A", a), volet("B", b, c)])
        self.assertEqual(t["bloquants"], 2)

    def test_case_grise_si_tout_a_venir(self):
        self.assertEqual(m.etat_case([lot("Bêta", "a_venir")]), "avenir")

    def test_position_ignore_les_phases_a_venir(self):
        v = volet("A", lot("Construction", "fait"), lot("Lancement", "a_venir"))
        self.assertEqual(m.position(v), 1)

    def test_un_volet_en_avance_ne_tire_pas_le_projet(self):
        volets = [volet("A", lot("Lancement", "fait")),
                  volet("B", lot("Construction", "fait")),
                  volet("C", lot("Cadrage", "fait"))]
        self.assertEqual(m.PHASES[m.phase_projet(volets)], "Construction")

    def test_exemple_est_en_preproduction(self):
        exemple = json.loads((DOSSIER / "exemple-projet.json").read_text("utf-8"))
        rang = m.phase_projet(exemple["volets"])
        self.assertEqual(m.PHASES[rang], "Pré-production")

    def test_verdict_bloque_passe_avant_tout(self):
        v = volet("A", lot("Cadrage", "fait"), lot("Cadrage", "a_trancher"),
                  lot("Cadrage", "bloquant"))
        self.assertEqual(m.verdict_element(v, "2026-11-04"), "Bloqué")

    def test_verdict_a_l_arret(self):
        v = volet("A", lot("Cadrage", "fait"), lot("Construction", "a_faire"),
                  derniere_activite="2026-08-01")
        self.assertEqual(m.verdict_element(v, "2026-11-04"), "À l'arrêt")

    def test_verdict_termine(self):
        v = volet("A", lot("Lancement", "fait"))
        self.assertEqual(m.verdict_element(v, "2026-11-04"), "Terminé")

    def test_verdict_sans_lot_a_confirmer(self):
        v = volet("A", phase_estimee="Bêta", source_phase="README")
        self.assertEqual(m.verdict_element(v, "2026-11-04"), "À confirmer")


class Rendu(unittest.TestCase):
    def orga(self):
        return {"type": "orga", "nom": "Orga", "date": "2026-11-04",
                "verdict": "V.", "prochaine_action": "A.",
                "projets": [
                    volet("Calme", lot("Construction", "fait"),
                          lot("Construction", "a_faire", "Reste visible")),
                    volet("Urgent", lot("Cadrage", "bloquant", "Le bloquant")),
                ]}

    def test_orga_met_le_bloque_en_premier(self):
        noms = [p["nom"] for p in m.trier(self.orga())]
        self.assertEqual(noms, ["Urgent", "Calme"])

    def test_orga_ne_liste_que_ce_qui_reste(self):
        """Sur une orga, la carte d'un projet ne liste pas les lots faits :
        leur nombre est déjà sur la ligne d'avancement."""
        c = self.orga()
        c["projets"][0]["lots"][0]["titre"] = "Lot terminé"
        html = g.rendu_orga(c)["map"]
        self.assertIn("Reste visible", html)
        self.assertNotIn("Lot terminé", html)

    def test_orga_refuse_un_projet_fini_mais_pas_lance(self):
        c = self.orga()
        c["projets"] = [volet("Fini", lot("Construction", "fait"),
                              derniere_activite="2026-11-01")]
        self.assertTrue(any("Lancement" in x for x in m.verifier(c)))

    def test_frise_grise_une_phase_ou_rien_n_est_fait(self):
        """Un lot ouvert ne suffit pas : tant que rien n'est livré, c'est gris."""
        volets = [volet("A", lot("Cadrage", "a_trancher"),
                        lot("Construction", "en_cours"))]
        html = g.frise(volets, 1)
        self.assertIn('<div class="etape f-gris"><b>Cadrage</b>0 / 1 lot', html)
        self.assertNotIn('f-bleu', html)

    def test_frise_bleue_des_qu_un_lot_est_fait(self):
        volets = [volet("A", lot("Construction", "fait"),
                        lot("Construction", "a_faire"))]
        self.assertIn('<div class="etape f-bleu ici">', g.frise(volets, 1))

    def test_frise_verte_quand_la_phase_est_finie(self):
        volets = [volet("A", lot("Cadrage", "fait"))]
        self.assertIn('<div class="etape f-vert ici"><b>Cadrage</b>1 / 1 lot',
                      g.frise(volets, 0))

    def test_le_fragment_n_est_pas_une_page(self):
        """Pas de doctype, pas de <html>, pas de fond : le chat fournit le cadre."""
        pages = g.rendu_projet(carte(volet("A", lot("Cadrage", "fait"))))
        for fragment in pages.values():
            self.assertNotIn("<!doctype", fragment.lower())
            self.assertNotIn("<body", fragment.lower())
            self.assertTrue(fragment.startswith("<style>"))

    def test_aucune_couleur_ecrite_en_dur(self):
        """Une couleur en dur casserait le mode sombre du chat."""
        import re
        pages = g.rendu_projet(carte(volet("A", lot("Cadrage", "fait"))))
        for nom, fragment in pages.items():
            self.assertEqual(re.findall(r"#[0-9a-fA-F]{3,6}", fragment), [],
                             f"couleur en dur dans {nom}")

    def test_singulier_quand_il_y_a_un_seul_bloquant(self):
        html = g.nombres({"elements": 1, "total": 1, "faits": 0, "bloquants": 1,
                           "a_trancher": 1}, "volets")
        self.assertIn("<span>bloquant</span>", html)
        self.assertIn("<span>décision à trancher</span>", html)

    def test_une_seule_map(self):
        """Deux images dans une réponse, on en regarde une."""
        self.assertEqual(set(g.rendu_orga(self.orga())), {"map"})
        c = carte(volet("A", lot("Cadrage", "fait")))
        self.assertEqual(set(g.rendu_projet(c)), {"map"})

    def test_le_texte_est_echappe(self):
        """Un nom de volet ne doit jamais devenir du code dans la réponse.

        Le fragment porte un `<script>` à lui, celui du réglage des colonnes :
        on vérifie donc qu'il n'y en a toujours qu'un, et que le nom du volet
        est bien ressorti échappé."""
        c = carte(volet("<script>", lot("Cadrage", "fait", "a & b")))
        html = g.rendu_projet(copy.deepcopy(c))["map"]
        self.assertEqual(html.count("<script>"), 1)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("a &amp; b", html)

    def test_le_volet_et_son_sous_titre_sont_sur_deux_lignes(self):
        """« Site publicfrontend/src/site » : les deux collés, illisible."""
        c = carte(volet("Site public", lot("Cadrage", "fait"),
                        sous_titre="Ce que voit le client"))
        html = g.rendu_projet(c)["map"]
        self.assertIn("display:block", html)
        self.assertIn('.mp td.nom{', html)
        self.assertIn("padding-right", html)

    def test_le_reglage_des_colonnes_est_la(self):
        html = g.rendu_projet(carte(volet("A", lot("Cadrage", "fait"))))["map"]
        self.assertIn('<div class="cartes">', html)
        self.assertIn('data-c="3" class="actif"', html)
        self.assertTrue(html.rstrip().endswith("</script>"))


if __name__ == "__main__":
    unittest.main()

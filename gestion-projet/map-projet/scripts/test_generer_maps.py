"""Tests du générateur : python -m unittest test_generer_maps (depuis scripts/)."""

import copy
import re
import json
import unittest
from pathlib import Path

import generer_maps as g

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
        self.assertEqual(g.verifier(exemple), [])

    def test_lot_sans_source_refuse(self):
        c = carte(volet("A", lot("Cadrage", "fait", source="")))
        self.assertTrue(any("pas de source" in x for x in g.verifier(c)))

    def test_a_confirmer_accepte_sans_source(self):
        c = carte(volet("A", lot("Cadrage", "a_confirmer", source="")))
        self.assertEqual(g.verifier(c), [])

    def test_texte_trop_long_refuse(self):
        c = carte(volet("A", lot("Cadrage", "fait")))
        c["verdict"] = "x" * 151
        self.assertTrue(any("À raccourcir" in x for x in g.verifier(c)))

    def test_valeur_calculee_refusee(self):
        c = carte(volet("A", lot("Cadrage", "fait"), phase="Bêta"))
        self.assertTrue(any("champ inconnu" in x for x in g.verifier(c)))

    def test_element_qui_n_est_pas_un_objet_refuse(self):
        c = carte(volet("A"))
        c["volets"] = ["front"]
        self.assertTrue(any("objet" in x for x in g.verifier(c)))

    def test_orga_exige_la_derniere_activite(self):
        c = {"type": "orga", "nom": "O", "date": "2026-11-04", "verdict": "V",
             "prochaine_action": "A", "projets": [volet("P", lot("Cadrage", "a_faire"))]}
        self.assertTrue(any("derniere_activite" in x for x in g.verifier(c)))

    def test_phase_inconnue_refusee(self):
        c = carte(volet("A", lot("Recette", "fait")))
        self.assertTrue(any("phase inconnue" in x for x in g.verifier(c)))

    def test_sans_lot_exige_phase_et_source(self):
        erreurs = g.verifier(carte(volet("A")))
        self.assertEqual(len(erreurs), 2)

    def test_phase_estimee_interdite_avec_lots(self):
        c = carte(volet("A", lot("Cadrage", "fait"), phase_estimee="Bêta"))
        self.assertTrue(any("réservée" in x for x in g.verifier(c)))


class Calculs(unittest.TestCase):
    def test_case_verte_si_tout_fait(self):
        self.assertEqual(g.etat_case([lot("Cadrage", "fait")]), "fait")

    def test_case_bleue_si_melange(self):
        lots = [lot("Cadrage", "fait"), lot("Cadrage", "a_venir")]
        self.assertEqual(g.etat_case(lots), "ouvert")

    def test_case_rouge_si_bloquant(self):
        lots = [lot("Cadrage", "fait"), lot("Cadrage", "bloquant")]
        self.assertEqual(g.etat_case(lots), "bloque")

    def test_case_pointillee_si_rien_de_prouve(self):
        lots = [lot("Bêta", "a_confirmer"), lot("Bêta", "a_venir")]
        self.assertEqual(g.etat_case(lots), "confirmer")

    def test_a_confirmer_ne_fait_pas_avancer_la_phase(self):
        v = volet("A", lot("Construction", "fait"), lot("Lancement", "a_confirmer"))
        self.assertEqual(g.PHASES[g.position(v)], "Construction")

    def test_lot_ouvert_n_avance_pas_si_phase_d_avant_pas_finie(self):
        v = volet("A", lot("Construction", "fait"), lot("Construction", "a_faire"),
                  lot("Bêta", "a_faire"))
        self.assertEqual(g.PHASES[g.position(v)], "Construction")

    def test_lot_ouvert_avance_si_phase_d_avant_finie(self):
        v = volet("A", lot("Construction", "fait"), lot("Pré-production", "bloquant"))
        self.assertEqual(g.PHASES[g.position(v)], "Pré-production")

    def test_seul_un_lot_a_confirmer_donne_a_confirmer(self):
        v = volet("A", lot("Cadrage", "a_confirmer"))
        self.assertEqual(g.verdict_element(v, "2026-11-04"), "À confirmer")

    def test_a_l_arret_passe_avant_a_trancher(self):
        v = volet("A", lot("Cadrage", "fait"), lot("Cadrage", "a_trancher"),
                  derniere_activite="2026-01-01")
        self.assertEqual(g.verdict_element(v, "2026-11-04"), "À l'arrêt")

    def test_une_cause_commune_compte_une_fois(self):
        a = lot("Cadrage", "bloquant")
        a["cause"] = "hebergeur"
        b = lot("Cadrage", "bloquant")
        b["cause"] = "hebergeur"
        c = lot("Cadrage", "bloquant")
        t = g.totaux([volet("A", a), volet("B", b, c)])
        self.assertEqual(t["bloquants"], 2)

    def test_case_grise_si_tout_a_venir(self):
        self.assertEqual(g.etat_case([lot("Bêta", "a_venir")]), "avenir")

    def test_repartir_place_dans_la_colonne_la_plus_courte(self):
        html = g.repartir([("A", 10), ("B", 1), ("C", 1)], 2)
        self.assertEqual(html.count('class="colonne"'), 2)
        self.assertIn('<div class="colonne">BC</div>', html)

    def test_position_ignore_les_phases_a_venir(self):
        v = volet("A", lot("Construction", "fait"), lot("Lancement", "a_venir"))
        self.assertEqual(g.position(v), 1)

    def test_un_volet_en_avance_ne_tire_pas_le_projet(self):
        volets = [volet("A", lot("Lancement", "fait")),
                  volet("B", lot("Construction", "fait")),
                  volet("C", lot("Cadrage", "fait"))]
        self.assertEqual(g.PHASES[g.phase_projet(volets)], "Construction")

    def test_exemple_est_en_preproduction(self):
        exemple = json.loads((DOSSIER / "exemple-projet.json").read_text("utf-8"))
        rang = g.phase_projet(exemple["volets"])
        self.assertEqual(g.PHASES[rang], "Pré-production")

    def test_verdict_bloque_passe_avant_tout(self):
        v = volet("A", lot("Cadrage", "fait"), lot("Cadrage", "a_trancher"),
                  lot("Cadrage", "bloquant"))
        self.assertEqual(g.verdict_element(v, "2026-11-04"), "Bloqué")

    def test_verdict_a_l_arret(self):
        v = volet("A", lot("Cadrage", "fait"), lot("Construction", "a_faire"),
                  derniere_activite="2026-08-01")
        self.assertEqual(g.verdict_element(v, "2026-11-04"), "À l'arrêt")

    def test_verdict_termine(self):
        v = volet("A", lot("Lancement", "fait"))
        self.assertEqual(g.verdict_element(v, "2026-11-04"), "Terminé")

    def test_verdict_sans_lot_a_confirmer(self):
        v = volet("A", phase_estimee="Bêta", source_phase="README")
        self.assertEqual(g.verdict_element(v, "2026-11-04"), "À confirmer")


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
        noms = [p["nom"] for p in g.trier(self.orga())]
        self.assertEqual(noms, ["Urgent", "Calme"])

    def test_orga_lots_restants_cache_les_lots_faits(self):
        c = self.orga()
        c["projets"][0]["lots"][0]["titre"] = "Lot terminé"
        html = g.rendu_orga(c)["lots-restants"]
        self.assertIn("Reste visible", html)
        self.assertNotIn("Lot terminé", html)

    def test_orga_refuse_un_projet_fini_mais_pas_lance(self):
        c = self.orga()
        c["projets"] = [volet("Fini", lot("Construction", "fait"),
                              derniere_activite="2026-11-01")]
        self.assertTrue(any("Lancement" in x for x in g.verifier(c)))

    def test_frise_garde_en_bleu_une_phase_passee_non_finie(self):
        volets = [volet("A", lot("Cadrage", "a_trancher"),
                        lot("Construction", "en_cours"))]
        self.assertIn('etape ouverte', g.frise_projet(volets, 1))

    def test_singulier_quand_il_y_a_un_seul_bloquant(self):
        html = g.chiffres({"elements": 1, "total": 1, "faits": 0, "bloquants": 1,
                           "a_trancher": 1}, "volets")
        self.assertIn("<span>bloquant</span>", html)
        self.assertIn("<span>décision à trancher</span>", html)

    def test_noms_des_deux_maps(self):
        self.assertEqual(set(g.rendu_orga(self.orga())),
                         {"par-projet", "lots-restants"})
        c = carte(volet("A", lot("Cadrage", "fait")))
        self.assertEqual(set(g.rendu_projet(c)), {"par-volet", "par-lot"})

    def test_le_texte_est_echappe(self):
        c = carte(volet("<script>", lot("Cadrage", "fait", "a & b")))
        html = g.rendu_projet(copy.deepcopy(c))["par-lot"]
        self.assertNotIn("<script>", html)
        self.assertIn("a &amp; b", html)

    def test_widget_respecte_show_widget(self):
        c = carte(volet("A", lot("Cadrage", "fait"), lot("Bêta", "a_faire")))
        page = g.rendu_projet(c)["par-volet"]
        w = g.widget(page, "A : résumé")
        self.assertTrue(w.startswith('<h2 class="sr-only">A : résumé</h2>'))
        for interdit in (r"<!doctype", r"<html[\s>]", r"<head[\s>]", r"<body[\s>]",
                         r"/\*", r"<!--"):
            self.assertIsNone(re.search(interdit, w.lower()), interdit)
        self.assertIsNone(re.search(r"font-weight:\s*(?!400|500)\d+", w))
        self.assertIsNone(re.search(r"font-size:\s*(\d|10)(\.\d+)?px", w))
        self.assertNotIn("#", re.search(r"<style>(.*)</style>", w, re.S).group(1))
        self.assertIn('<div class="mp">', w)
        self.assertIn("Cadrage", w)

    def test_choix_des_colonnes(self):
        c = carte(volet("A", lot("Cadrage", "fait")), volet("B", lot("Cadrage", "fait")))
        self.assertIn('data-n="3"', g.rendu_projet(copy.deepcopy(c))["par-volet"])
        self.assertIn('data-n="1"', g.rendu_projet(copy.deepcopy(c), 1)["par-volet"])
        page = g.rendu_projet(copy.deepcopy(c))["par-volet"]
        self.assertIn('data-i="0"', page)
        self.assertIn('data-i="1"', page)
        w = g.widget(page, "r", 2)
        self.assertIn('<section class="colonnes" data-n="2">', w)
        for n in (1, 2, 3):
            self.assertIn(f'data-n="{n}" aria-pressed', w)


if __name__ == "__main__":
    unittest.main()

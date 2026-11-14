/** Limites d'essais (rate limiting) : au-delà de `maximum` essais dans la fenêtre, la clé est refusée.
 *  Limite à connaître : les compteurs vivent en mémoire. Un redémarrage les remet à zéro, et avec
 *  plusieurs instances chacune compte de son côté. Dans ces cas, les ranger dans la base ou dans Redis
 *  (même interface `Limiteur`). */

export type Verdict = { accepte: true } | { accepte: false; reessayerDansMs: number }

export type Limiteur = {
  /** Compte un essai pour cette clé et dit s'il est accepté. */
  essayer: (cle: string) => Verdict
  /** Rend un essai compté d'avance, quand il s'est révélé bon (connexion réussie). */
  rendre: (cle: string) => void
}

type Compteur = { nombre: number; debut: number }

/** Nombre de clés au-delà duquel on nettoie les fenêtres terminées : la mémoire reste bornée. */
const NETTOYAGE_APRES = 10_000

export function creerLimiteur({ maximum, fenetreMs, horloge = Date.now }: { maximum: number; fenetreMs: number; horloge?: () => number }): Limiteur {
  if (maximum < 1 || fenetreMs < 1) throw new Error('Un limiteur demande maximum ≥ 1 et fenetreMs ≥ 1.')
  const compteurs = new Map<string, Compteur>()

  const nettoyer = (maintenant: number) => {
    for (const [cle, compteur] of compteurs) if (maintenant - compteur.debut >= fenetreMs) compteurs.delete(cle)
  }

  return {
    essayer(cle) {
      const maintenant = horloge()
      if (compteurs.size > NETTOYAGE_APRES) nettoyer(maintenant)
      const actuel = compteurs.get(cle)
      const compteur = actuel && maintenant - actuel.debut < fenetreMs ? actuel : { nombre: 0, debut: maintenant }
      compteur.nombre += 1
      compteurs.set(cle, compteur)
      if (compteur.nombre <= maximum) return { accepte: true }
      return { accepte: false, reessayerDansMs: compteur.debut + fenetreMs - maintenant }
    },
    rendre(cle) {
      const compteur = compteurs.get(cle)
      if (compteur && compteur.nombre > 0) compteur.nombre -= 1
    },
  }
}

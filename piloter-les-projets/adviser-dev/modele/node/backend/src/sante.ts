/** Santé du service, en deux questions :
 *  - vivant : le processus répond-il ? Ne touche à rien, pour rester rapide même quand tout va mal.
 *  - prêt   : peut-il servir des requêtes ? Lance chaque contrôle (base, disque…), avec un délai max.
 *  Limite à connaître : un serveur arrêté ne peut pas prévenir de sa propre panne. Il faut aussi une
 *  surveillance extérieure qui appelle /sante/pret. */
import { accessSync, constants, mkdirSync } from 'node:fs'

export type Controle = () => boolean | Promise<boolean>
export type EtatPret = { pret: boolean; controles: Record<string, 'ok' | 'panne'> }

const DELAI_CONTROLE_MS = 2_000

async function avecDelai(controle: Controle, delaiMs: number): Promise<boolean> {
  let minuterie: NodeJS.Timeout | undefined
  const delai = new Promise<boolean>(accepter => { minuterie = setTimeout(() => accepter(false), delaiMs) })
  try {
    return await Promise.race([Promise.resolve().then(controle), delai])
  } catch {
    return false
  } finally {
    clearTimeout(minuterie)
  }
}

export function creerSante(controles: Record<string, Controle>, delaiMs = DELAI_CONTROLE_MS) {
  return {
    vivant: () => ({ etat: 'ok' as const }),
    async pret(): Promise<EtatPret> {
      const noms = Object.keys(controles)
      const resultats = await Promise.all(noms.map(nom => avecDelai(controles[nom]!, delaiMs)))
      const detail = Object.fromEntries(noms.map((nom, i) => [nom, resultats[i] ? 'ok' : 'panne'] as const))
      return { pret: resultats.every(Boolean), controles: detail }
    },
  }
}

/** Contrôle courant : le dossier de données existe et on peut y écrire. */
export const disqueInscriptible = (dossier: string): Controle => () => {
  mkdirSync(dossier, { recursive: true })
  accessSync(dossier, constants.W_OK)
  return true
}

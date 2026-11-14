/** Journaux : une ligne par événement, sur la sortie standard. C'est Docker ou l'hébergeur qui les range.
 *  En production : JSON (lisible par les outils). En local : une ligne courte, lisible par un humain.
 *  Jamais de secret ici : les champs sensibles connus sont masqués avant l'écriture. */
import type { NiveauJournal } from './config.ts'

export type Champs = Record<string, unknown>
export type Journal = Record<NiveauJournal, (message: string, champs?: Champs) => void>

const ORDRE: Record<NiveauJournal, number> = { debug: 0, info: 1, warning: 2, error: 3 }
const SENSIBLE = /mot.?de.?passe|password|jeton|token|secret|cle|key|cookie|authorization/i

/** Remplace la valeur des champs sensibles, à tous les niveaux d'un objet. */
export function masquer(valeur: unknown): unknown {
  if (Array.isArray(valeur)) return valeur.map(masquer)
  if (valeur && typeof valeur === 'object') {
    return Object.fromEntries(Object.entries(valeur).map(([cle, v]) => [cle, SENSIBLE.test(cle) ? '***' : masquer(v)]))
  }
  return valeur
}

export type OptionsJournal = {
  /** JSON en production ; ligne lisible en local. */
  json?: boolean
  /** Où écrire une ligne. Les tests passent leur propre fonction. */
  ecrire?: (ligne: string) => void
  horloge?: () => Date
}

const ecrireSortie = (ligne: string) => { process.stdout.write(`${ligne}\n`) }

export function creerJournal(niveauMin: NiveauJournal, { json = true, ecrire = ecrireSortie, horloge = () => new Date() }: OptionsJournal = {}): Journal {
  const noter = (niveau: NiveauJournal) => (message: string, champs: Champs = {}) => {
    if (ORDRE[niveau] < ORDRE[niveauMin]) return
    const propres = masquer(champs) as Champs
    if (json) {
      ecrire(JSON.stringify({ heure: horloge().toISOString(), niveau, message, ...propres }))
      return
    }
    const details = Object.entries(propres).map(([cle, v]) => `${cle}=${typeof v === 'string' ? v : JSON.stringify(v)}`).join(' ')
    ecrire(`${niveau.toUpperCase().padEnd(7)} ${message}${details ? `  ${details}` : ''}`)
  }
  return { debug: noter('debug'), info: noter('info'), warning: noter('warning'), error: noter('error') }
}

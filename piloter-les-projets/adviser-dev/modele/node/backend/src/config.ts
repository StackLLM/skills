/** Configuration du backend : lue une seule fois, au démarrage, depuis l'environnement.
 *  Une valeur obligatoire absente en production arrête le démarrage, avec un message clair :
 *  mieux vaut un serveur qui refuse de démarrer qu'un serveur qui démarre faux. */
import { resolve } from 'node:path'

export const dossierBackend = resolve(import.meta.dirname, '..')

export type NiveauJournal = 'debug' | 'info' | 'warning' | 'error'

export type Config = {
  production: boolean
  port: number
  hote: string
  /** Adresse publique du service (https://…), sans / final. Sert au contrôle d'origine. */
  origine: string
  /** Vrai si un proxy de confiance est devant : on lit alors X-Forwarded-For. */
  derriereProxy: boolean
  dossierDonnees: string
  /** Dossier du frontend compilé, servi par le backend s'il existe. */
  dossierSite: string
  journal: NiveauJournal
}

export class ConfigInvalide extends Error {}

const NIVEAUX: readonly NiveauJournal[] = ['debug', 'info', 'warning', 'error']

function lireEntier(valeur: string | undefined, defaut: number, nom: string): number {
  if (valeur === undefined || valeur === '') return defaut
  const nombre = Number(valeur)
  if (!Number.isInteger(nombre) || nombre <= 0 || nombre > 65_535) throw new ConfigInvalide(`${nom} doit être un port entre 1 et 65535 (reçu : ${valeur}).`)
  return nombre
}

/** Lit et valide la configuration. `env` est injectable : les tests passent leur propre environnement. */
export function lireConfig(env: NodeJS.ProcessEnv = process.env): Config {
  const production = env.NODE_ENV === 'production'
  const derriereProxy = env.{{PREFIXE}}_PROXY === '1'
  const origine = (env.{{PREFIXE}}_ORIGINE ?? '').trim().replace(/\/$/, '')
  if (production && !origine) throw new ConfigInvalide('{{PREFIXE}}_ORIGINE manque : en production, il faut l\'adresse publique du service (https://…).')
  if (origine && !/^https?:\/\/[^/]+$/.test(origine)) throw new ConfigInvalide(`{{PREFIXE}}_ORIGINE doit ressembler à https://exemple.ma (reçu : ${origine}).`)

  const journal = (env.{{PREFIXE}}_JOURNAL || (production ? 'info' : 'debug')) as NiveauJournal
  if (!NIVEAUX.includes(journal)) throw new ConfigInvalide(`{{PREFIXE}}_JOURNAL doit valoir ${NIVEAUX.join(', ')} (reçu : ${journal}).`)

  return {
    production,
    port: lireEntier(env.PORT ?? env.{{PREFIXE}}_PORT, {{PORT}}, '{{PREFIXE}}_PORT'),
    // Derrière un proxy local, on n'écoute que la machine ; en conteneur, {{PREFIXE}}_HOTE=0.0.0.0.
    hote: env.{{PREFIXE}}_HOTE || '127.0.0.1',
    origine,
    derriereProxy,
    dossierDonnees: resolve(dossierBackend, env.{{PREFIXE}}_DONNEES || 'data'),
    dossierSite: resolve(dossierBackend, env.{{PREFIXE}}_SITE || '../frontend/dist'),
    journal,
  }
}

/** Démarrage : configuration → application → écoute. Et l'arrêt propre, quand Docker envoie SIGTERM. */
import { creerApplication } from './application.ts'
import { ConfigInvalide, lireConfig, type Config } from './config.ts'
import { creerJournal } from './journal.ts'

/** Temps laissé aux requêtes en cours avant de couper, à l'arrêt. */
const DELAI_ARRET_MS = 10_000

function lireConfigOuQuitter(): Config {
  try {
    return lireConfig()
  } catch (erreur) {
    if (!(erreur instanceof ConfigInvalide)) throw erreur
    console.error(`Configuration invalide : ${erreur.message}`)
    process.exit(1)
  }
}

const config = lireConfigOuQuitter()

const journal = creerJournal(config.journal, { json: config.production })
const serveur = creerApplication(config, { journal })

serveur.listen(config.port, config.hote, () => {
  journal.info('service démarré', { adresse: `http://${config.hote}:${config.port}`, production: config.production })
})

// Une promesse rejetée sans traitement est un bug : on la journalise et on s'arrête proprement.
process.on('unhandledRejection', raison => {
  journal.error('promesse rejetée sans traitement', { raison: raison instanceof Error ? raison.stack : String(raison) })
  arreter('unhandledRejection', 1)
})

function arreter(signal: string, code = 0) {
  journal.info('arrêt demandé', { signal })
  // Plus de nouvelles connexions ; les requêtes en cours finissent, puis on sort.
  serveur.close(() => process.exit(code))
  serveur.closeIdleConnections()
  setTimeout(() => {
    journal.warning('arrêt forcé : des requêtes ne se sont pas terminées à temps')
    process.exit(code || 1)
  }, DELAI_ARRET_MS).unref()
}

process.on('SIGTERM', () => arreter('SIGTERM'))
process.on('SIGINT', () => arreter('SIGINT'))

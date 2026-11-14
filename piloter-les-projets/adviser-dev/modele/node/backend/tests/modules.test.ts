/** Tests unitaires : configuration, limites d'essais, journaux. Sans serveur, sans réseau. */
import assert from 'node:assert/strict'
import { describe, test } from 'node:test'
import { ConfigInvalide, lireConfig } from '../src/config.ts'
import { creerJournal, masquer } from '../src/journal.ts'
import { creerLimiteur } from '../src/limites.ts'

describe('configuration', () => {
  test('donne des valeurs sûres par défaut en local', () => {
    const config = lireConfig({})
    assert.equal(config.production, false)
    assert.equal(config.port, {{PORT}})
    assert.equal(config.hote, '127.0.0.1')
    assert.equal(config.derriereProxy, false)
  })

  test('refuse de démarrer en production sans adresse publique', () => {
    assert.throws(() => lireConfig({ NODE_ENV: 'production' }), ConfigInvalide)
  })

  test('refuse un port invalide avec un message qui dit quoi corriger', () => {
    assert.throws(() => lireConfig({ {{PREFIXE}}_PORT: 'abc' }), /{{PREFIXE}}_PORT/)
  })

  test('retire le / final de l\'origine', () => {
    assert.equal(lireConfig({ {{PREFIXE}}_ORIGINE: 'https://exemple.ma/' }).origine, 'https://exemple.ma')
  })
})

describe('limites d\'essais', () => {
  test('accepte jusqu\'au maximum, puis refuse avec le temps restant', () => {
    let maintenant = 0
    const limiteur = creerLimiteur({ maximum: 2, fenetreMs: 1_000, horloge: () => maintenant })
    assert.equal(limiteur.essayer('a').accepte, true)
    assert.equal(limiteur.essayer('a').accepte, true)
    maintenant = 400
    assert.deepEqual(limiteur.essayer('a'), { accepte: false, reessayerDansMs: 600 })
  })

  test('repart à zéro quand la fenêtre est finie', () => {
    let maintenant = 0
    const limiteur = creerLimiteur({ maximum: 1, fenetreMs: 1_000, horloge: () => maintenant })
    limiteur.essayer('a')
    maintenant = 1_000
    assert.equal(limiteur.essayer('a').accepte, true)
  })

  test('compte chaque clé séparément', () => {
    const limiteur = creerLimiteur({ maximum: 1, fenetreMs: 1_000 })
    limiteur.essayer('a')
    assert.equal(limiteur.essayer('b').accepte, true)
  })

  test('un essai rendu ne compte plus', () => {
    const limiteur = creerLimiteur({ maximum: 1, fenetreMs: 1_000 })
    limiteur.essayer('a')
    limiteur.rendre('a')
    assert.equal(limiteur.essayer('a').accepte, true)
  })
})

describe('journaux', () => {
  test('masque les champs sensibles, même imbriqués', () => {
    assert.deepEqual(masquer({ identifiant: 'admin', motDePasse: 'x', session: { jeton: 'y' } }), { identifiant: 'admin', motDePasse: '***', session: { jeton: '***' } })
  })

  test('écrit une ligne JSON avec l\'heure et le niveau', () => {
    const lignes: string[] = []
    const journal = creerJournal('info', { ecrire: ligne => { lignes.push(ligne) }, horloge: () => new Date('2026-01-01T00:00:00Z') })
    journal.info('requête', { statut: 200 })
    assert.deepEqual(JSON.parse(lignes[0]!), { heure: '2026-01-01T00:00:00.000Z', niveau: 'info', message: 'requête', statut: 200 })
  })

  test('n\'écrit rien sous le niveau minimum', () => {
    const lignes: string[] = []
    creerJournal('warning', { ecrire: ligne => { lignes.push(ligne) } }).info('bavard')
    assert.equal(lignes.length, 0)
  })
})

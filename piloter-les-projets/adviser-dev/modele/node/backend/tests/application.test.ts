/** Tests d'intégration : la vraie application, sur un port libre, avec un dossier temporaire. */
import assert from 'node:assert/strict'
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from 'node:fs'
import type { AddressInfo } from 'node:net'
import { tmpdir } from 'node:os'
import { join } from 'node:path'
import { after, before, describe, test } from 'node:test'
import { creerApplication, validerContact } from '../src/application.ts'
import { lireConfig } from '../src/config.ts'
import { creerJournal } from '../src/journal.ts'
import { creerLimiteur } from '../src/limites.ts'

const lignes: string[] = []
const journal = creerJournal('debug', { ecrire: ligne => { lignes.push(ligne) } })

async function demarrer(env: NodeJS.ProcessEnv = {}, controles = {}) {
  const dossier = mkdtempSync(join(tmpdir(), 'socle-'))
  const site = join(dossier, 'site')
  mkdirSync(site)
  writeFileSync(join(site, 'index.html'), '<!doctype html><title>Accueil</title>')
  const config = lireConfig({ {{PREFIXE}}_DONNEES: join(dossier, 'donnees'), {{PREFIXE}}_SITE: site, ...env })
  const serveur = creerApplication(config, { journal, controles, limiteContact: creerLimiteur({ maximum: 2, fenetreMs: 60_000 }) })
  await new Promise<void>(accepter => serveur.listen(0, '127.0.0.1', accepter))
  const adresse = `http://127.0.0.1:${(serveur.address() as AddressInfo).port}`
  const fermer = async () => {
    await new Promise(accepter => serveur.close(accepter))
    rmSync(dossier, { recursive: true, force: true })
  }
  return { adresse, fermer }
}

const contactValide = { nom: 'Mourad', email: 'mourad@exemple.ma', message: 'Bonjour' }
const envoyerContact = (adresse: string, corps: unknown, entetes: Record<string, string> = {}) =>
  fetch(`${adresse}/api/contact`, { method: 'POST', headers: { 'Content-Type': 'application/json', ...entetes }, body: JSON.stringify(corps) })

describe('santé', () => {
  let service: Awaited<ReturnType<typeof demarrer>>
  before(async () => { service = await demarrer() })
  after(() => service.fermer())

  test('/sante/vivant répond 200 sans rien contrôler', async () => {
    const reponse = await fetch(`${service.adresse}/sante/vivant`)
    assert.equal(reponse.status, 200)
    assert.deepEqual(await reponse.json(), { etat: 'ok' })
  })

  test('/sante/pret répond 200 quand le disque est inscriptible', async () => {
    const reponse = await fetch(`${service.adresse}/sante/pret`)
    assert.equal(reponse.status, 200)
    assert.deepEqual(await reponse.json(), { etat: 'ok', controles: { disque: 'ok' } })
  })
})

test('/sante/pret répond 503 quand une dépendance est en panne', async () => {
  const service = await demarrer({}, { base: () => { throw new Error('base injoignable') } })
  try {
    const reponse = await fetch(`${service.adresse}/sante/pret`)
    assert.equal(reponse.status, 503)
    assert.deepEqual(await reponse.json(), { etat: 'panne', controles: { disque: 'ok', base: 'panne' } })
  } finally {
    await service.fermer()
  }
})

describe('protection', () => {
  let service: Awaited<ReturnType<typeof demarrer>>
  before(async () => { service = await demarrer() })
  after(() => service.fermer())

  test('chaque réponse porte les en-têtes de sécurité et un identifiant de requête', async () => {
    const reponse = await fetch(`${service.adresse}/`)
    assert.equal(reponse.headers.get('x-content-type-options'), 'nosniff')
    assert.match(reponse.headers.get('content-security-policy') ?? '', /default-src 'self'/)
    assert.equal(reponse.headers.get('x-frame-options'), 'DENY')
    assert.match(reponse.headers.get('x-request-id') ?? '', /^[\w-]{8,}$/)
  })

  test('un identifiant de requête envoyé par le visiteur est ignoré sans proxy de confiance', async () => {
    const reponse = await fetch(`${service.adresse}/sante/vivant`, { headers: { 'X-Request-Id': 'choisi-par-le-visiteur' } })
    assert.notEqual(reponse.headers.get('x-request-id'), 'choisi-par-le-visiteur')
  })

  test('refuse une requête qui modifie venant d\'une autre origine', async () => {
    const reponse = await envoyerContact(service.adresse, contactValide, { Origin: 'https://pirate.exemple' })
    assert.equal(reponse.status, 403)
  })

  test('refuse un corps trop grand avec 413', async () => {
    const reponse = await envoyerContact(service.adresse, { ...contactValide, message: 'x'.repeat(20_000) })
    assert.equal(reponse.status, 413)
  })

  test('ne sert aucun fichier hors du dossier du site', async () => {
    const reponse = await fetch(`${service.adresse}/%2e%2e/%2e%2e/package.json`)
    assert.equal(reponse.status, 404)
  })

  test('une adresse d\'API inconnue répond 404 en JSON', async () => {
    const reponse = await fetch(`${service.adresse}/api/inconnue`)
    assert.equal(reponse.status, 404)
    assert.match((await reponse.json() as { erreur: string }).erreur, /inconnue/)
  })
})

// Un service à lui : chaque essai compte, même refusé ensuite, et les autres tests en consomment.
test('bloque après le nombre maximum de messages, avec Retry-After', async () => {
  const service = await demarrer()
  try {
    assert.equal((await envoyerContact(service.adresse, contactValide)).status, 202)
    assert.equal((await envoyerContact(service.adresse, contactValide)).status, 202)
    const bloque = await envoyerContact(service.adresse, contactValide)
    assert.equal(bloque.status, 429)
    assert.ok(Number(bloque.headers.get('retry-after')) > 0)
  } finally {
    await service.fermer()
  }
})

test('le site d\'une seule page renvoie index.html pour une adresse sans extension', async () => {
  const service = await demarrer()
  try {
    const reponse = await fetch(`${service.adresse}/compte/reglages`)
    assert.equal(reponse.status, 200)
    assert.match(await reponse.text(), /<title>Accueil<\/title>/)
  } finally {
    await service.fermer()
  }
})

describe('validation du formulaire de contact', () => {
  test('accepte un message complet et retire les espaces', () => {
    assert.deepEqual(validerContact({ nom: ' Mourad ', email: 'mourad@exemple.ma', message: ' Bonjour ' }), { nom: 'Mourad', email: 'mourad@exemple.ma', message: 'Bonjour' })
  })

  test('refuse une adresse e-mail invalide', () => {
    assert.throws(() => validerContact({ ...contactValide, email: 'pas-une-adresse' }), /e-mail/)
  })

  test('refuse un corps qui n\'est pas un objet', () => {
    assert.throws(() => validerContact('texte'), /vide/)
  })
})

#!/usr/bin/env node
// CloneMe — relais local : enregistre les relevés du navigateur, et sert le site
// source depuis localhost pour pouvoir le mesurer comme le clone.
//
// Usage :
//   node relais-cloneme.mjs --dossier <projet>/.cloneme [--port 6099] [--source https://exemple.com]
//
// 1. Enregistrer (toujours actif) — depuis une page servie en localhost :
//      await fetch('http://127.0.0.1:6099/__cloneme/enregistrer?fichier=mesures/clone/P-01@1440.json',
//        { method: 'POST', body: JSON.stringify(resultat) })
//    Le fichier est écrit sous --dossier, jamais ailleurs.
//
// 2. Relayer la source (avec --source) — ouvrir http://localhost:6099/<chemin> dans le
//    navigateur : la page vient de https://exemple.com/<chemin>. Elle est alors en
//    localhost et peut appeler /__cloneme/enregistrer sans blocage.
//    Pourquoi : le navigateur intégré bloque les appels d'un site public vers localhost.
//
// 3. Mesurer en lot — depuis une page localhost (source relayée ou clone) :
//      (await import('http://127.0.0.1:6099/__cloneme/mesurer.js')).lancer({ cote: 'clone' })
//    Voir scripts/mesurer.js. Le relais sert aussi les fichiers de --dossier en lecture
//    (/__cloneme/fichier?nom=cibles.json).
//
// Lecture seule côté source : seules les requêtes GET et HEAD sont relayées.
// Écoute sur 127.0.0.1 uniquement. Arrêt : Ctrl+C.

import { createServer } from 'node:http'
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs'
import { dirname, resolve, sep } from 'node:path'
import { fileURLToPath } from 'node:url'

const arg = (nom, defaut) => {
  const i = process.argv.indexOf(`--${nom}`)
  return i > -1 ? process.argv[i + 1] : defaut
}
const dossier = arg('dossier')
const port = Number(arg('port', 6099))
// Seule l'origine compte (https://exemple.com) : mesurer.js envoie déjà le chemin complet.
const source = arg('source') ? new URL(arg('source')).origin : undefined
if (!dossier) {
  console.error('Usage : node relais-cloneme.mjs --dossier <projet>/.cloneme [--port 6099] [--source https://exemple.com]')
  process.exit(2)
}
const racine = resolve(dossier)
const local = `http://localhost:${port}`

const CORS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
  'Access-Control-Allow-Private-Network': 'true',
}

function enregistrer(req, res, url) {
  const nom = url.searchParams.get('fichier') ?? ''
  const cible = resolve(racine, nom)
  if (!nom || !/\.(json|txt|html|css|md)$/.test(nom) || !(cible.startsWith(racine + sep))) {
    res.writeHead(400, CORS); return res.end('nom de fichier refusé')
  }
  let corps = ''
  req.setEncoding('utf8')
  req.on('data', (m) => { corps += m; if (corps.length > 20_000_000) req.destroy() })
  req.on('end', () => {
    try {
      const texte = nom.endsWith('.json') ? JSON.stringify(JSON.parse(corps), null, 2) : corps
      mkdirSync(dirname(cible), { recursive: true })
      writeFileSync(cible, texte)
      console.log(`enregistré ${nom} (${Math.round(texte.length / 1024)} Ko)`)
      res.writeHead(200, CORS); res.end('ok')
    } catch (e) { res.writeHead(400, CORS); res.end(String(e)) }
  })
}

const SANS = new Set(['content-encoding', 'content-length', 'transfer-encoding', 'connection',
  'content-security-policy', 'content-security-policy-report-only', 'strict-transport-security', 'set-cookie',
  // Sans ce retrait, une source en « DENY » refuse d'être ouverte dans le cadre de mesure.
  'x-frame-options', 'cross-origin-opener-policy', 'cross-origin-embedder-policy', 'cross-origin-resource-policy'])

async function relayer(req, res, url) {
  if (!source) { res.writeHead(404, CORS); return res.end('relais de la source inactif (option --source)') }
  if (req.method !== 'GET' && req.method !== 'HEAD') { res.writeHead(405, CORS); return res.end('lecture seule') }
  try {
    const r = await fetch(source + url.pathname + url.search, {
      method: req.method, redirect: 'manual',
      headers: { 'user-agent': req.headers['user-agent'] ?? 'CloneMe', accept: req.headers.accept ?? '*/*',
        'accept-language': req.headers['accept-language'] ?? 'fr' },
    })
    const entetes = { ...CORS }
    r.headers.forEach((v, k) => { if (!SANS.has(k)) entetes[k] = v })
    if (entetes.location) entetes.location = entetes.location.replace(source, local)
    const type = r.headers.get('content-type') ?? ''
    if (/text\/html|text\/css|javascript|json/.test(type)) {
      // Les liens absolus vers la source restent dans le relais.
      // Aussi la forme échappée des données JSON (https:\/\/exemple.com).
      const echappe = (u) => u.replaceAll('/', '\\/')
      const texte = (await r.text()).split(source).join(local).split(echappe(source)).join(echappe(local))
      res.writeHead(r.status, entetes); return res.end(texte)
    }
    res.writeHead(r.status, entetes)
    res.end(Buffer.from(await r.arrayBuffer()))
  } catch (e) { res.writeHead(502, CORS); res.end(`relais en échec : ${e}`) }
}

// Outil de mesure côté navigateur (scripts/mesurer.js), servi à côté de ce fichier.
const outilMesure = resolve(dirname(fileURLToPath(import.meta.url)), 'mesurer.js')

function lireFichier(res, url) {
  const nom = url.searchParams.get('nom') ?? ''
  const cible = resolve(racine, nom)
  if (!nom || !cible.startsWith(racine + sep) || !existsSync(cible)) { res.writeHead(404, CORS); return res.end() }
  res.writeHead(200, { ...CORS, 'content-type': nom.endsWith('.json') ? 'application/json' : 'text/plain; charset=utf-8' })
  res.end(readFileSync(cible))
}

createServer((req, res) => {
  const url = new URL(req.url ?? '/', local)
  if (req.method === 'OPTIONS') { res.writeHead(204, CORS); return res.end() }
  if (url.pathname === '/__cloneme/enregistrer' && req.method === 'POST') return enregistrer(req, res, url)
  if (url.pathname === '/__cloneme/fichier') return lireFichier(res, url)
  if (url.pathname === '/__cloneme/mesurer.js') {
    res.writeHead(200, { ...CORS, 'content-type': 'text/javascript; charset=utf-8', 'cache-control': 'no-store' })
    return res.end(readFileSync(outilMesure))
  }
  return relayer(req, res, url)
}).listen(port, '127.0.0.1', () => {
  console.log(`Relais CloneMe : ${local}`)
  console.log(`  enregistre dans ${racine}`)
  if (source) console.log(`  relaie ${source} → ${local}`)
})

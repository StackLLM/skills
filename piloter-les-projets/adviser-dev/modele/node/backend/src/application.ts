/** L'application HTTP : santé, API, puis le frontend compilé.
 *  Chaque requête reçoit un identifiant, ses en-têtes de sécurité, et une ligne de journal.
 *  Une erreur attendue renvoie un message utile ; une panne renvoie un 500 générique, le détail part au journal. */
import { randomUUID } from 'node:crypto'
import { existsSync, readFileSync, statSync } from 'node:fs'
import { createServer, type IncomingMessage, type ServerResponse } from 'node:http'
import { extname, join, resolve, sep } from 'node:path'
import type { Config } from './config.ts'
import type { Journal } from './journal.ts'
import { creerLimiteur, type Limiteur } from './limites.ts'
import { disqueInscriptible, creerSante, type Controle } from './sante.ts'
import { ENTETES_SECURITE, HSTS, origineAcceptee } from './securite.ts'

const TAILLE_MAX_CORPS = 16 * 1024
const HEURE = 60 * 60_000
const LONGUEUR_MAX_MESSAGE = 2_000
const FORMAT_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const ID_REQUETE = /^[\w-]{8,64}$/

const TYPES: Record<string, string> = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg',
  '.webp': 'image/webp', '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.txt': 'text/plain; charset=utf-8',
}

/** Une erreur prévue : le statut et le message partent tels quels vers le client. */
export class ErreurHttp extends Error {
  readonly statut: number
  readonly entetes: Record<string, string>

  constructor(statut: number, message: string, entetes: Record<string, string> = {}) {
    super(message)
    this.statut = statut
    this.entetes = entetes
  }
}

export type Outils = {
  journal: Journal
  /** Contrôles de /sante/pret en plus du disque (base, services externes…). */
  controles?: Record<string, Controle>
  limiteContact?: Limiteur
}

type Contexte = { req: IncomingMessage; res: ServerResponse; url: URL; ip: string; idRequete: string }

function envoyerJson(res: ServerResponse, statut: number, corps: unknown, entetes: Record<string, string> = {}) {
  res.writeHead(statut, { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store', ...entetes })
  res.end(JSON.stringify(corps))
}

/** Le client reçoit le 413, puis la connexion se ferme : on ne lit pas la suite d'un corps refusé. */
const tropGrand = () => new ErreurHttp(413, 'Requête trop grande.', { Connection: 'close' })

function lireCorpsJson(req: IncomingMessage): Promise<unknown> {
  return new Promise((accepter, rejeter) => {
    const annoncee = Number(req.headers['content-length'] ?? 0)
    if (annoncee > TAILLE_MAX_CORPS) {
      rejeter(tropGrand())
      return
    }
    const morceaux: Buffer[] = []
    let taille = 0
    req.on('data', (morceau: Buffer) => {
      if (taille > TAILLE_MAX_CORPS) return
      taille += morceau.length
      if (taille > TAILLE_MAX_CORPS) {
        // Pas de destroy ici : la réponse 413 doit d'abord partir. Le reste du corps est ignoré.
        morceaux.length = 0
        rejeter(tropGrand())
        return
      }
      morceaux.push(morceau)
    })
    req.on('error', rejeter)
    req.on('end', () => {
      try {
        accepter(JSON.parse(Buffer.concat(morceaux).toString('utf8') || 'null'))
      } catch {
        rejeter(new ErreurHttp(400, 'Le corps de la requête n\'est pas un JSON valide.'))
      }
    })
  })
}

export type MessageContact = { nom: string; email: string; message: string }

/** Validation à la frontière : ce qui sort de cette fonction est sûr et typé. */
export function validerContact(corps: unknown): MessageContact {
  if (!corps || typeof corps !== 'object') throw new ErreurHttp(400, 'Formulaire vide.')
  const { nom, email, message } = corps as Record<string, unknown>
  const texte = (valeur: unknown) => (typeof valeur === 'string' ? valeur.trim() : '')
  const propre = { nom: texte(nom), email: texte(email), message: texte(message) }
  if (!propre.nom || propre.nom.length > 120) throw new ErreurHttp(400, 'Le nom est obligatoire (120 caractères au plus).')
  if (!FORMAT_EMAIL.test(propre.email) || propre.email.length > 254) throw new ErreurHttp(400, 'L\'adresse e-mail n\'est pas valide.')
  if (!propre.message || propre.message.length > LONGUEUR_MAX_MESSAGE) throw new ErreurHttp(400, `Le message est obligatoire (${LONGUEUR_MAX_MESSAGE} caractères au plus).`)
  return propre
}

export function creerApplication(config: Config, outils: Outils) {
  const { journal } = outils
  const sante = creerSante({ disque: disqueInscriptible(config.dossierDonnees), ...outils.controles })
  const limiteContact = outils.limiteContact ?? creerLimiteur({ maximum: 5, fenetreMs: HEURE })
  const racineSite = resolve(config.dossierSite)

  /** L'adresse du visiteur. X-Forwarded-For seulement derrière un proxy de confiance : sinon n'importe qui la choisit. */
  const adresseVisiteur = (req: IncomingMessage) => {
    const transmise = req.headers['x-forwarded-for']
    if (config.derriereProxy && typeof transmise === 'string') return transmise.split(',')[0]!.trim()
    return req.socket.remoteAddress ?? 'inconnue'
  }

  async function routerApi({ req, res, url, ip }: Contexte) {
    if (url.pathname === '/api/contact' && req.method === 'POST') {
      const verdict = limiteContact.essayer(`contact:${ip}`)
      if (!verdict.accepte) {
        const secondes = Math.ceil(verdict.reessayerDansMs / 1000)
        throw new ErreurHttp(429, `Trop de messages envoyés. Réessayez dans ${Math.ceil(secondes / 60)} minutes.`, { 'Retry-After': String(secondes) })
      }
      const contact = validerContact(await lireCorpsJson(req))
      // Le métier (envoi du mail, enregistrement) vient ici, dans un service à part, testé sans HTTP.
      journal.info('message de contact reçu', { longueur: contact.message.length })
      envoyerJson(res, 202, { recu: true })
      return
    }
    throw new ErreurHttp(404, 'Adresse d\'API inconnue.')
  }

  /** Sert le frontend compilé. Le chemin demandé est résolu puis vérifié dans le dossier : pas de ../ possible. */
  function servirSite({ res, url }: Contexte) {
    let chemin: string
    try {
      chemin = resolve(racineSite, `.${decodeURIComponent(url.pathname)}`)
    } catch {
      throw new ErreurHttp(400, 'Adresse invalide.')
    }
    if (chemin !== racineSite && !chemin.startsWith(racineSite + sep)) throw new ErreurHttp(404, 'Page introuvable.')
    if (existsSync(chemin) && statSync(chemin).isDirectory()) chemin = join(chemin, 'index.html')
    // Application d'une seule page : toute adresse sans extension renvoie index.html.
    if (!existsSync(chemin) && !extname(chemin)) chemin = join(racineSite, 'index.html')
    if (!existsSync(chemin)) throw new ErreurHttp(404, 'Page introuvable.')
    const estHtml = extname(chemin) === '.html'
    res.writeHead(200, {
      'Content-Type': TYPES[extname(chemin)] ?? 'application/octet-stream',
      // Les fichiers de Vite portent une empreinte dans leur nom : ils se gardent longtemps. Le HTML, jamais.
      'Cache-Control': estHtml ? 'no-cache' : 'public, max-age=31536000, immutable',
    })
    res.end(readFileSync(chemin))
  }

  async function traiter(contexte: Contexte) {
    const { req, res, url } = contexte
    if (req.method === 'GET' && url.pathname === '/sante/vivant') return envoyerJson(res, 200, sante.vivant())
    if (req.method === 'GET' && url.pathname === '/sante/pret') {
      const etat = await sante.pret()
      return envoyerJson(res, etat.pret ? 200 : 503, { etat: etat.pret ? 'ok' : 'panne', controles: etat.controles })
    }
    const modifie = !['GET', 'HEAD', 'OPTIONS'].includes(req.method ?? 'GET')
    if (modifie && !origineAcceptee(req.headers.origin, config.origine, req.headers.host)) throw new ErreurHttp(403, 'Origine refusée.')
    if (url.pathname.startsWith('/api/')) return routerApi(contexte)
    if (req.method !== 'GET' && req.method !== 'HEAD') throw new ErreurHttp(405, 'Méthode non autorisée.')
    return servirSite(contexte)
  }

  return createServer(async (req, res) => {
    const debut = performance.now()
    const recu = req.headers['x-request-id']
    // L'identifiant d'un proxy de confiance est repris (même identifiant de bout en bout) ; sinon on en crée un.
    const idRequete = config.derriereProxy && typeof recu === 'string' && ID_REQUETE.test(recu) ? recu : randomUUID()
    const url = new URL(req.url ?? '/', 'http://local')
    const ip = adresseVisiteur(req)
    res.setHeader('X-Request-Id', idRequete)
    for (const [nom, valeur] of Object.entries(ENTETES_SECURITE)) res.setHeader(nom, valeur)
    if (config.origine.startsWith('https://')) res.setHeader('Strict-Transport-Security', HSTS)

    try {
      await traiter({ req, res, url, ip, idRequete })
    } catch (erreur) {
      if (erreur instanceof ErreurHttp) {
        if (!res.headersSent) envoyerJson(res, erreur.statut, { erreur: erreur.message }, erreur.entetes)
      } else {
        journal.error('erreur inattendue', { idRequete, route: url.pathname, erreur: erreur instanceof Error ? erreur.stack : String(erreur) })
        if (!res.headersSent) envoyerJson(res, 500, { erreur: 'Erreur interne. Réessayez plus tard.', idRequete })
      }
    } finally {
      // La santé est appelée toutes les 30 secondes : elle ne remplit pas le journal.
      if (!url.pathname.startsWith('/sante/')) {
        journal.info('requête', { idRequete, methode: req.method, route: url.pathname, statut: res.statusCode, dureeMs: Math.round(performance.now() - debut) })
      }
    }
  })
}

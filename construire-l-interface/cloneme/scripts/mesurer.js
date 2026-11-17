// CloneMe — mesures en lot, côté navigateur. Servi par relais-cloneme.mjs.
//
// Depuis la source relayée (http://localhost:6099/…) ou depuis le clone (http://localhost:<port>/…) :
//
//   (await import('http://127.0.0.1:6099/__cloneme/mesurer.js')).lancer({ cote: 'source' })
//   (await import('http://127.0.0.1:6099/__cloneme/mesurer.js')).lancer({ cote: 'clone', pages: ['P-03'] })
//
// Lit .cloneme/cibles.json (via le relais), ouvre chaque page dans un cadre caché à
// chaque largeur (les @media du cadre suivent sa largeur), relève l'empreinte, et
// l'enregistre dans .cloneme/mesures/<cote>/<P-xx>@<largeur>.json.
// Rend la main tout de suite : suivre l'avancement dans le journal du relais.

// Le relais qui a servi ce fichier : son port suit l'option --port.
const RELAIS = new URL(import.meta.url).origin

const PROPRIETES = ['fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'letterSpacing', 'textTransform', 'color',
  'backgroundColor', 'backgroundImage', 'borderTopWidth', 'borderTopStyle', 'borderTopColor', 'borderRadius', 'boxShadow',
  'paddingTop', 'paddingRight', 'paddingBottom', 'paddingLeft', 'marginTop', 'marginBottom', 'display', 'gap',
  'gridTemplateColumns', 'flexDirection', 'justifyContent', 'alignItems', 'textAlign', 'position', 'opacity', 'zIndex']

/** Empreinte d'une page déjà chargée dans la fenêtre `w`. `cibles` : { nom: sélecteur }. */
export function empreinte(w, cibles) {
  const d = w.document
  const out = {
    largeur: w.innerWidth, hauteurPage: d.documentElement.scrollHeight,
    debordementHorizontal: d.documentElement.scrollWidth > w.innerWidth, titre: d.title,
    compte: { liens: d.querySelectorAll('a[href]').length, images: d.querySelectorAll('img').length,
      titres: d.querySelectorAll('h1,h2,h3').length },
    cibles: {},
  }
  for (const [nom, sel] of Object.entries(cibles)) {
    const e = d.querySelector(sel)
    if (!e) { out.cibles[nom] = null; continue }
    const r = e.getBoundingClientRect(), c = w.getComputedStyle(e)
    out.cibles[nom] = { x: Math.round(r.x), y: Math.round(r.y + w.scrollY), l: Math.round(r.width), h: Math.round(r.height),
      texte: (e.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 60), ...Object.fromEntries(PROPRIETES.map((p) => [p, c[p]])) }
  }
  return out
}

const pause = (ms) => new Promise((ok) => setTimeout(ok, ms))

/** Côté source, l'URL d'origine devient son chemin dans le relais. */
const adresse = (cote, page) => (cote === 'source' ? (() => { const u = new URL(page.source); return u.pathname + u.search })() : page.clone)

/**
 * `sortie` : sous-dossier de mesures/ (par défaut = `cote`). Ex. `sortie: 'clone-avant'`
 * pour garder l'état du clone avant une modification (mode Mettre à jour).
 * Une page en échec n'arrête pas le lot : l'erreur est écrite dans
 * mesures/<sortie>/_erreurs.txt, et _fini.txt est toujours écrit à la fin.
 */
export function lancer({ cote, pages, largeurs = [1440, 1024, 768, 375], attente = 4000, sortie } = {}) {
  if (cote !== 'source' && cote !== 'clone') throw new Error("cote doit valoir 'source' ou 'clone'")
  const dossier = sortie ?? cote
  const envoyer = (nom, corps) => fetch(`${RELAIS}/__cloneme/enregistrer?fichier=mesures/${dossier}/${nom}`, { method: 'POST', body: corps })
  const erreurs = []
  const travail = (async () => {
    try {
      const toutes = await (await fetch(`${RELAIS}/__cloneme/fichier?nom=cibles.json`)).json()
      const ids = pages ?? Object.keys(toutes)
      for (const id of ids) for (const l of largeurs) {
        const cadre = document.createElement('iframe')
        try {
          const page = toutes[id]
          if (!page) throw new Error(`page ${id} absente de cibles.json`)
          const cibles = Object.fromEntries(Object.entries(page.cibles).map(([nom, s]) => [nom, s[cote]]))
          cadre.style.cssText = `position:absolute;left:-99999px;top:0;width:${l}px;height:900px;border:0`
          document.body.appendChild(cadre)
          await new Promise((ok) => { cadre.onload = ok; cadre.src = adresse(cote, page) })
          await pause(attente) // laisse finir les entrées animées au chargement
          await envoyer(`${id}@${l}.json`, JSON.stringify(empreinte(cadre.contentWindow, cibles)))
        } catch (e) {
          erreurs.push(`${id}@${l} : ${e}`)
        } finally {
          cadre.remove()
        }
      }
    } catch (e) {
      erreurs.push(`lot : ${e}`)
    } finally {
      if (erreurs.length) await envoyer('_erreurs.txt', erreurs.join('\n')).catch(() => {})
      await envoyer('_fini.txt', `${new Date().toISOString()}\nerreurs : ${erreurs.length}`).catch(() => {})
    }
  })()
  travail.catch((e) => console.error('CloneMe mesurer :', e))
  return `lancé : ${cote} → mesures/${dossier}, ${pages ? pages.join(', ') : 'toutes les pages'}, largeurs ${largeurs.join('/')}`
}

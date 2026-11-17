#!/usr/bin/env node
// CloneMe — compare l'empreinte du site source et celle du clone.
//
// Usage :
//   node comparer-empreintes.mjs <source.json> <clone.json> [--tout]
//   node comparer-empreintes.mjs --dossier <.cloneme/mesures> [--tout] [--a source --b clone]
//     (compare chaque source/<nom>.json avec clone/<nom>.json)
//
// Les empreintes sont produites par le script de valider-et-comparer.md §2.
// Sortie : tableau Markdown des écarts, classés fort / moyen / faible.
// --tout affiche aussi les écarts faibles. Code de sortie 1 s'il reste un écart fort.

import { readFileSync, readdirSync, existsSync } from 'node:fs'
import { join, basename } from 'node:path'

const args = process.argv.slice(2)
const tout = args.includes('--tout')
const option = (nom, defaut) => { const i = args.indexOf(`--${nom}`); return i > -1 ? args[i + 1] : defaut }
const gauche = option('a', 'source'), droite = option('b', 'clone')
const valeursOptions = new Set([option('a'), option('b')].filter(Boolean))
const positionnels = args.filter(a => !a.startsWith('--') && !valeursOptions.has(a))

let paires = []
if (args.includes('--dossier')) {
  const d = positionnels[0]
  if (!d) usage()
  // --a / --b : comparer deux autres sous-dossiers, ex. --a clone-avant --b clone (mode Mettre à jour).
  const src = join(d, gauche), cln = join(d, droite)
  for (const f of readdirSync(src).filter(f => f.endsWith('.json'))) {
    if (existsSync(join(cln, f))) paires.push([join(src, f), join(cln, f)])
    else console.log(`⚠ ${f} : pas d'empreinte côté clone`)
  }
} else {
  if (positionnels.length !== 2) usage()
  paires = [positionnels]
}

function usage() {
  console.error('Usage : node comparer-empreintes.mjs <source.json> <clone.json> [--tout]\n' +
    '        node comparer-empreintes.mjs --dossier <.cloneme/mesures> [--tout]')
  process.exit(2)
}

const PX = ['fontSize', 'lineHeight', 'letterSpacing', 'borderTopWidth', 'paddingTop', 'paddingRight',
  'paddingBottom', 'paddingLeft', 'marginTop', 'marginBottom', 'gap']
const GEO = ['x', 'y', 'l', 'h']
const COULEURS = ['color', 'backgroundColor', 'borderTopColor']
const IGNORES = new Set(['texte', 'opacity', ...PX, ...GEO, ...COULEURS, 'fontFamily', 'backgroundImage'])

const px = v => (v === 'normal' ? null : parseFloat(v))
// next/font et équivalents renomment la police (« __Inter_a1b2c3 », « __Inter_Fallback_a1b2c3 ») :
// on compare le nom de famille réel.
const premierePolice = v => (v || '').split(',')[0].replace(/["']/g, '').trim()
  .replace(/^__/, '').replace(/_Fallback/i, '').replace(/_[0-9a-f]{5,8}$/i, '').replace(/_/g, ' ').toLowerCase()
const couleur = v => (v || '').replace(/\s+/g, '').replace(/^rgba\((\d+,\d+,\d+),1\)$/, 'rgb($1)')
const fondNormalise = v => (v || 'none').replace(/url\(["']?[^"')]*\/([^/"')]+)["']?\)/g, 'url($1)')

function graviteEcart(a, b) {
  const d = Math.abs(a - b), r = d / Math.max(Math.abs(a), Math.abs(b), 1)
  if (d > 8 && r > 0.05) return 'fort'
  if (d >= 3) return 'moyen'
  if (d > 0) return 'faible'
  return null
}

let totalFort = 0
for (const [fs, fc] of paires) {
  const s = JSON.parse(readFileSync(fs, 'utf8')), c = JSON.parse(readFileSync(fc, 'utf8'))
  const ecarts = []
  const ajoute = (g, cible, prop, vs, vc, note = '') => g && ecarts.push({ g, cible, prop, vs, vc, note })

  if (s.largeur !== c.largeur) ajoute('fort', '(page)', 'largeur', s.largeur, c.largeur, 'mesures à des largeurs différentes')
  const dh = Math.abs(s.hauteurPage - c.hauteurPage) / Math.max(s.hauteurPage, 1)
  ajoute(dh > 0.1 ? 'fort' : dh > 0.03 ? 'moyen' : dh > 0 ? 'faible' : null, '(page)', 'hauteurPage', s.hauteurPage, c.hauteurPage)
  if (c.debordementHorizontal) ajoute('fort', '(page)', 'débordement horizontal', s.debordementHorizontal, true)
  if (s.titre !== c.titre) ajoute('moyen', '(page)', 'title', s.titre, c.titre)
  for (const k of Object.keys(s.compte ?? {}))
    if (s.compte[k] !== c.compte?.[k]) ajoute('moyen', '(page)', `nombre de ${k}`, s.compte[k], c.compte?.[k])

  const noms = new Set([...Object.keys(s.cibles ?? {}), ...Object.keys(c.cibles ?? {})])
  for (const nom of noms) {
    const a = s.cibles?.[nom], b = c.cibles?.[nom]
    if (!a || !b) { ajoute('fort', nom, 'présence', a ? 'oui' : 'absente', b ? 'oui' : 'absente'); continue }
    if ((a.opacity === '0') !== (b.opacity === '0'))
      ajoute('moyen', nom, 'opacity', a.opacity, b.opacity, 'souvent une apparition au défilement non déclenchée ici')
    for (const p of GEO) ajoute(graviteEcart(a[p], b[p]), nom, p, a[p], b[p])
    for (const p of PX) {
      const va = px(a[p]), vb = px(b[p])
      if (va === null || vb === null) { if (a[p] !== b[p]) ajoute('moyen', nom, p, a[p], b[p]); continue }
      const g = graviteEcart(va, vb)
      ajoute(g === 'fort' && p !== 'fontSize' ? 'moyen' : g, nom, p, a[p], b[p])
    }
    if (premierePolice(a.fontFamily) !== premierePolice(b.fontFamily)) ajoute('fort', nom, 'fontFamily', premierePolice(a.fontFamily), premierePolice(b.fontFamily))
    for (const p of COULEURS) if (couleur(a[p]) !== couleur(b[p])) ajoute(p === 'borderTopColor' ? 'moyen' : 'fort', nom, p, a[p], b[p])
    if (fondNormalise(a.backgroundImage) !== fondNormalise(b.backgroundImage))
      ajoute('moyen', nom, 'backgroundImage', fondNormalise(a.backgroundImage).slice(0, 50), fondNormalise(b.backgroundImage).slice(0, 50))
    for (const p of Object.keys(a)) if (!IGNORES.has(p) && String(a[p]) !== String(b[p])) ajoute('moyen', nom, p, a[p], b[p])
    // Les blancs (retours à la ligne, tabulations du HTML source) ne comptent pas.
    // Les textes sont coupés à 60 caractères : on compare sur la longueur commune.
    const blancs = (t) => t.replace(/\s+/g, ' ').trim()
    if (a.texte && b.texte) {
      const ta = blancs(a.texte), tb = blancs(b.texte), n = Math.min(ta.length, tb.length)
      if (ta.slice(0, n) !== tb.slice(0, n)) ajoute('faible', nom, 'texte', a.texte, b.texte)
    }
  }

  const ordre = { fort: 0, moyen: 1, faible: 2 }
  ecarts.sort((x, y) => ordre[x.g] - ordre[y.g])
  const n = g => ecarts.filter(e => e.g === g).length
  totalFort += n('fort')
  console.log(`\n## ${basename(fs, '.json')} — ${n('fort')} fort · ${n('moyen')} moyen · ${n('faible')} faible`)
  const visibles = ecarts.filter(e => tout || e.g !== 'faible')
  if (!visibles.length) { console.log('\nAucun écart à corriger.'); continue }
  console.log('\n| Gravité | Cible | Propriété | Source | Clone | Note |\n|---|---|---|---|---|---|')
  const cel = v => String(v ?? '—').replace(/\|/g, '\\|').slice(0, 60)
  for (const e of visibles) console.log(`| ${e.g} | ${cel(e.cible)} | ${e.prop} | ${cel(e.vs)} | ${cel(e.vc)} | ${e.note} |`)
}
process.exit(totalFort ? 1 : 0)

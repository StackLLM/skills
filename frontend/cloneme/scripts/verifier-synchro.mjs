#!/usr/bin/env node
// CloneMe — vérifie que design.md, palette.md et animation.md correspondent au code.
//
// Usage : node verifier-synchro.mjs <racine-du-projet-cloné>
//
// Quatre contrôles :
//   1. chaque variable `--x` des tableaux de palette.md / animation.md existe dans
//      tokens.css avec la même valeur (valeur de base, hors @media), et inversement ;
//   2. chaque ID (P-xx, C-xx, A-xx) défini dans les .md a sa marque `cloneme:` dans
//      le code, et inversement ;
//   3. chaque constante JS listée dans animation.md (`NOM` ou `NOM.champ` + nombre)
//      se retrouve, avec son nombre, dans lib/animations.ts ;
//   4. aucune couleur, police ou courbe CSS écrite en dur hors de tokens.css
//      (une ligne qui contient `cloneme-ok` est tolérée : exception assumée).
// Ne contrôle pas : les durées en dur, les valeurs par largeur (@media).
// Code de sortie : 0 si tout est synchronisé, 1 sinon.

import { readFileSync, existsSync, readdirSync, statSync } from 'node:fs'
import { join, relative, sep } from 'node:path'

const racine = process.argv[2]
if (!racine) {
  console.error('Usage : node verifier-synchro.mjs <racine-du-projet-cloné>')
  process.exit(2)
}

const lire = f => (existsSync(f) ? readFileSync(f, 'utf8') : null)
const dossierSrc = [join(racine, 'ui', 'src'), join(racine, 'src')].find(existsSync)
if (!dossierSrc) {
  console.error(`Aucun dossier source trouvé (ui/src ou src) dans ${racine}`)
  process.exit(2)
}

const md = Object.fromEntries(['design.md', 'palette.md', 'animation.md'].map(f => [f, lire(join(racine, f))]))
const manquants = Object.entries(md).filter(([, v]) => v === null).map(([k]) => k)

// Tous les fichiers de code du projet (hors tests et dépendances).
function lister(dossier) {
  const out = []
  for (const nom of readdirSync(dossier)) {
    if (nom === 'node_modules' || nom === 'dist' || nom === 'test' || nom.startsWith('.')) continue
    const p = join(dossier, nom)
    if (statSync(p).isDirectory()) out.push(...lister(p))
    else if (/\.(tsx?|jsx?|css|html)$/.test(nom) && !/\.test\.|\.spec\./.test(nom)) out.push(p)
  }
  return out
}
const racineUi = join(dossierSrc, '..')
const fichiers = [
  ...lister(dossierSrc),
  ...['tailwind.config.js', 'tailwind.config.ts', 'index.html'].map(f => join(racineUi, f)).filter(existsSync),
]
const fichierTokens = fichiers.find(f => f.endsWith(`styles${sep}tokens.css`)) ?? fichiers.find(f => f.endsWith('tokens.css'))

const erreurs = []
const avertissements = []
const rel = f => relative(racine, f).split(sep).join('/')

// ---------- 1. Tokens ----------
const normaliser = v => v.trim().replace(/\s+/g, ' ').replace(/\s*,\s*/g, ', ').replace(/\s*\/\s*/g, ' / ').toLowerCase()

const tokensMd = new Map()
for (const f of ['palette.md', 'animation.md']) {
  if (!md[f]) continue
  for (const m of md[f].matchAll(/^\|\s*`(--[\w-]+)`\s*\|\s*`([^`]*)`\s*\|/gm)) {
    if (tokensMd.has(m[1]) && normaliser(tokensMd.get(m[1]).valeur) !== normaliser(m[2]))
      erreurs.push(`[token] ${m[1]} défini deux fois avec deux valeurs (${tokensMd.get(m[1]).fichier} et ${f})`)
    tokensMd.set(m[1], { valeur: m[2], fichier: f })
  }
}

const tokensCss = new Map()
if (!fichierTokens) {
  erreurs.push('[token] tokens.css introuvable dans le code')
} else {
  // Les @media redéfinissent des valeurs par largeur : seules les valeurs de base comptent ici.
  let css = readFileSync(fichierTokens, 'utf8').replace(/\/\*[\s\S]*?\*\//g, '')
  css = css.replace(/@media[^{]*\{(?:[^{}]*\{[^{}]*\})*[^{}]*\}/g, '')
  for (const m of css.matchAll(/(--[\w-]+)\s*:/g)) {
    // La valeur s'arrête au premier « ; » hors guillemets et hors parenthèses :
    // une image SVG en ligne contient « ;charset=… ».
    let i = m.index + m[0].length, prof = 0, guillemet = null, valeur = ''
    for (; i < css.length; i++) {
      const c = css[i]
      if (guillemet) { if (c === guillemet) guillemet = null }
      else if (c === '"' || c === "'") guillemet = c
      else if (c === '(') prof++
      else if (c === ')') prof--
      else if ((c === ';' || c === '}') && prof === 0) break
      valeur += c
    }
    if (!tokensCss.has(m[1])) tokensCss.set(m[1], valeur)
  }
}

for (const [nom, { valeur, fichier }] of tokensMd) {
  if (!tokensCss.has(nom)) erreurs.push(`[token] ${nom} (${fichier}) absent de tokens.css`)
  else if (normaliser(tokensCss.get(nom)) !== normaliser(valeur))
    erreurs.push(`[token] ${nom} : ${fichier} dit \`${valeur}\`, tokens.css dit \`${tokensCss.get(nom).trim()}\``)
}
if (fichierTokens) for (const nom of tokensCss.keys())
  if (!tokensMd.has(nom)) erreurs.push(`[token] ${nom} présent dans tokens.css, non documenté dans palette.md ni animation.md`)

// ---------- 2. Identifiants ----------
const idsMd = new Map()
for (const [f, texte] of Object.entries(md)) {
  if (!texte) continue
  for (const m of texte.matchAll(/^(?:\|\s*|#{2,4}\s+)(~~)?([PCA]-\d{2,3})\b/gm)) {
    if (m[1]) continue // ID barré : élément retiré
    if (!idsMd.has(m[2])) idsMd.set(m[2], f)
  }
}

const idsCode = new Map()
for (const f of fichiers) {
  const texte = readFileSync(f, 'utf8')
  for (const m of texte.matchAll(/cloneme:\s*((?:[PCA]-\d{2,3})(?:\s*[,/]\s*[PCA]-\d{2,3})*)/g))
    for (const id of m[1].match(/[PCA]-\d{2,3}/g)) (idsCode.get(id) ?? idsCode.set(id, new Set()).get(id)).add(rel(f))
}

for (const [id, f] of idsMd) if (!idsCode.has(id)) erreurs.push(`[id] ${id} défini dans ${f}, aucune marque « cloneme: ${id} » dans le code`)
for (const [id, fs] of idsCode) if (!idsMd.has(id)) erreurs.push(`[id] ${id} marqué dans ${[...fs].join(', ')}, absent des fichiers .md`)

// ---------- 3. Constantes JS d'animation.md ----------
// Une ligne « | `NOM.champ` | 1000 ms | … » doit retrouver NOM et 1000 dans lib/animations.ts.
const fichierAnimJs = fichiers.find(f => /lib[\\/]animations\.(ts|js)$/.test(f))
let constantesJs = 0
if (md['animation.md']) {
  const codeAnim = fichierAnimJs ? readFileSync(fichierAnimJs, 'utf8') : ''
  for (const m of md['animation.md'].matchAll(/^\|\s*`([A-Z][A-Z0-9_]*)((?:\.\w+)*)`\s*\|\s*([^|]+)\|/gm)) {
    const nombre = m[3].match(/-?\d+(?:\.\d+)?/)?.[0]
    if (!nombre) continue
    constantesJs++
    const nom = m[1] + m[2]
    if (!fichierAnimJs) { erreurs.push(`[constante] ${nom} décrite dans animation.md, lib/animations.ts introuvable`); continue }
    const debut = codeAnim.search(new RegExp(`\\b${m[1]}\\s*[:=]`))
    if (debut < 0) { erreurs.push(`[constante] ${nom} décrite dans animation.md, absente de ${rel(fichierAnimJs)}`); continue }
    // La valeur est lue sur la ligne de la constante (ou de son champ : NOM.champ).
    const champ = m[2].split('.').filter(Boolean).pop()
    const reste = codeAnim.slice(debut)
    const pos = champ ? reste.search(new RegExp(`\\b${champ}\\s*:`)) : 0
    const ligne = pos < 0 ? '' : reste.slice(pos).split('\n')[0]
    if (!new RegExp(`(^|[^\\d.])${nombre.replace('.', '\\.')}(?![\\d])`).test(ligne))
      erreurs.push(`[constante] ${nom} : animation.md dit ${nombre}, le code dit « ${ligne.trim().slice(0, 60)} »`)
  }
}

// ---------- 4. Valeurs en dur ----------
// Les courbes en tableau dans animations.ts ([0.22, 1, 0.36, 1]) ne sont pas signalées :
// seule la forme CSS cubic-bezier( l'est, elle doit passer par une variable de tokens.css.
const motifs = [
  { nom: 'couleur hexadécimale', re: /(?<=[\s:'"(\[,=])(?<!(?:href|to)=["'])#[0-9a-fA-F]{3,8}(?![\w-])/g },
  { nom: 'couleur rgb/hsl', re: /\b(?:rgba?|hsla?)\(/g },
  { nom: 'courbe cubic-bezier', re: /cubic-bezier\(/g },
  { nom: 'famille de police', re: /font-family\s*:(?!\s*(?:var\(|inherit|initial|unset))/g },
]
// Tolérés : couleurs des icônes SVG en ligne (attributs fill, stroke, stop-color), noms
// déclarés dans un @font-face, et toute ligne marquée « cloneme-ok ».
const SVG = /\b(?:fill|stroke|stop-color|flood-color|lighting-color)\s*=/
for (const f of fichiers) {
  if (f === fichierTokens) continue
  if (/tailwind\.config|index\.html$/.test(f)) continue
  const lignes = readFileSync(f, 'utf8').split('\n')
  let dansFontFace = false
  lignes.forEach((ligne, i) => {
    if (/@font-face/.test(ligne)) dansFontFace = true
    const fin = dansFontFace && ligne.includes('}')
    if (!ligne.includes('cloneme-ok') && !SVG.test(ligne)) {
      for (const { nom, re } of motifs) {
        if (dansFontFace && nom === 'famille de police') continue
        re.lastIndex = 0
        if (re.test(ligne)) erreurs.push(`[en dur] ${rel(f)}:${i + 1} — ${nom} : ${ligne.trim().slice(0, 90)}`)
      }
    }
    if (fin) dansFontFace = false
  })
}

// ---------- Rapport ----------
if (manquants.length) erreurs.unshift(`Fichiers de référence absents : ${manquants.join(', ')}`)
console.log('CloneMe — synchronisation fichiers ↔ code')
console.log(`Projet : ${racine}`)
console.log(`Tokens : ${tokensMd.size} dans les .md, ${tokensCss.size} dans tokens.css`)
console.log(`IDs    : ${idsMd.size} dans les .md, ${idsCode.size} marqués dans le code`)
console.log(`Constantes JS d'animation.md contrôlées : ${constantesJs}`)
console.log('Non contrôlé : les valeurs redéfinies par largeur (@media de tokens.css) — à relire à la main.')
console.log('')
for (const a of avertissements) console.log(`⚠ ${a}`)
if (!erreurs.length) {
  console.log('✅ Synchronisé : aucun écart.')
  process.exit(0)
}
console.log(`❌ ${erreurs.length} écart(s) :`)
for (const e of erreurs) console.log(`  - ${e}`)
process.exit(1)

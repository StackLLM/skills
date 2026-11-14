// Livrer : envoie vers main le dernier commit de la branche de recette, à la main,
// et seulement si la CI de CE commit est verte sur GitHub. Lancé par livrer.bat ou livrer.sh.
//
//   1. sur la recette : git commit --allow-empty -m "livraison"; git push   → la CI tourne, le mail arrive
//   2. CI verte : livrer.bat (ou sh livrer.sh)                              → main, dans chaque dépôt
//
// Les dépôts et la branche de recette sont dans .github/livraison.json.
// Jamais de force : si main a bougé à côté, git refuse et rien n'est écrasé.
// Demande : git, et gh connecté (gh auth login).
import { execFileSync } from 'node:child_process'
import { readFileSync } from 'node:fs'
import { createInterface } from 'node:readline/promises'

const MARQUEUR = 'livraison'
const reglages = JSON.parse(readFileSync(new URL('./livraison.json', import.meta.url), 'utf8'))
const { depots, brancheRecette, workflowCi } = reglages
if (!Array.isArray(depots) || !depots.length) arreter('.github/livraison.json : la liste « depots » est vide.')
const principal = depots[0]

function lancer(commande, args) {
  return execFileSync(commande, args, { encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] }).trim()
}

function arreter(message) {
  console.error(`\n${message}\nRien n'a été poussé.`)
  process.exit(1)
}

// 1. La bonne branche, le bon commit, rien en attente.
const branche = lancer('git', ['rev-parse', '--abbrev-ref', 'HEAD'])
const sha = lancer('git', ['rev-parse', 'HEAD'])
const message = lancer('git', ['log', '-1', '--format=%s'])
if (branche === 'main') arreter('Tu es sur main. La livraison part de la branche de recette.')
if (branche !== brancheRecette) arreter(`La livraison part de « ${brancheRecette} », et tu es sur « ${branche} ».`)
if (message !== MARQUEUR) arreter(`Le dernier commit n'est pas « ${MARQUEUR} » (c'est : ${message}).`)
if (lancer('git', ['status', '--porcelain'])) arreter('Des fichiers sont modifiés et pas commités. Les commiter ou les ranger d\'abord.')

// 2. Le commit doit être celui que GitHub a vérifié : poussé, et identique sur la branche distante.
let distante = ''
try {
  distante = lancer('git', ['rev-parse', '--abbrev-ref', '@{u}'])
} catch {
  arreter(`La branche ${branche} n'est pas encore sur GitHub. Lancer : git push -u origin ${branche}`)
}
try {
  lancer('git', ['fetch', '--quiet', 'origin'])
} catch {
  arreter('GitHub ne répond pas (git fetch). Vérifier la connexion.')
}
if (lancer('git', ['rev-parse', distante]) !== sha) arreter(`Ce commit n'est pas encore sur GitHub (${distante}), ou la branche a bougé. Lancer : git push`)

// 3. La CI de ce commit précis : terminée et verte (elle contient le contrôle « prêt pour main »).
let runs = []
try {
  runs = JSON.parse(lancer('gh', ['run', 'list', '-R', principal, '--commit', sha, '--json', 'workflowName,status,conclusion,url']))
} catch {
  arreter('gh ne répond pas. Installer GitHub CLI puis : gh auth login')
}
const ci = runs.filter(run => run.workflowName === workflowCi)
if (!ci.length) arreter('Aucune CI trouvée pour ce commit. Attendre qu\'elle démarre, puis relancer.')
if (ci.some(run => run.status !== 'completed')) arreter(`La CI tourne encore : attendre le mail.\n${ci[0].url}`)
const rouge = ci.find(run => run.conclusion !== 'success')
if (rouge) arreter(`La CI n'est pas verte (${rouge.conclusion}). Corriger, recommiter « ${MARQUEUR} », pousser.\n${rouge.url}`)

// 4. Confirmation explicite, puis poussée sans force vers chaque dépôt.
console.log(`\nCI verte pour ${sha.slice(0, 7)} (branche ${branche}).`)
console.log(`Ce commit va devenir main dans :\n${depots.map(depot => `  - ${depot}`).join('\n')}`)
const question = createInterface({ input: process.stdin, output: process.stdout })
const reponse = (await question.question('Taper OUI pour livrer : ')).trim()
question.close()
if (reponse !== 'OUI') arreter('Livraison annulée.')

const livres = []
for (const depot of depots) {
  try {
    execFileSync('git', ['push', `https://github.com/${depot}.git`, `${sha}:refs/heads/main`], { stdio: 'inherit' })
    livres.push(depot)
    console.log(`main à jour : ${depot}`)
  } catch {
    // Les dépôts déjà livrés le restent : le dire, pour ne pas laisser croire que rien n'est parti.
    console.error(`\nÉchec de la poussée vers ${depot}. Si main a bougé là-bas : git merge origin/main sur la recette, puis une nouvelle livraison.`)
    console.error(livres.length ? `Déjà livrés : ${livres.join(', ')}.` : 'Rien n\'a été poussé.')
    process.exit(1)
  }
}
console.log('\nLivraison faite. L\'image Docker se construit sur GitHub depuis main.')

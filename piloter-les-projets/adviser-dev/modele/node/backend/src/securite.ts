/** En-têtes de sécurité posés sur chaque réponse, en local comme en ligne.
 *  La politique de contenu (CSP) part de « rien sauf soi-même » : on n'ouvre que ce qui sert,
 *  une source à la fois, avec un commentaire qui dit pourquoi. */

export const POLITIQUE_CONTENU = [
  "default-src 'self'",
  "script-src 'self'",
  "style-src 'self'",
  "img-src 'self' data:",
  "font-src 'self'",
  "connect-src 'self'",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'",
].join('; ')

export const ENTETES_SECURITE: Readonly<Record<string, string>> = {
  'Content-Security-Policy': POLITIQUE_CONTENU,
  'X-Content-Type-Options': 'nosniff',
  'Referrer-Policy': 'strict-origin-when-cross-origin',
  'Permissions-Policy': 'camera=(), microphone=(), geolocation=(), payment=(), usb=()',
  'X-Frame-Options': 'DENY',
  'Cross-Origin-Opener-Policy': 'same-origin',
}

/** HSTS seulement quand le service est servi en HTTPS : sinon le navigateur l'ignore, ou pire, bloque le local. */
export const HSTS = 'max-age=31536000; includeSubDomains'

/** Une requête qui modifie doit venir de notre propre origine (protection contre la falsification, CSRF).
 *  Sans en-tête Origin (outil en ligne de commande, serveur à serveur), on laisse passer : ce n'est pas un navigateur. */
export function origineAcceptee(origineRequete: string | undefined, origineService: string, hoteRequete: string | undefined): boolean {
  if (!origineRequete) return true
  if (origineService && origineRequete === origineService) return true
  try {
    return new URL(origineRequete).host === hoteRequete
  } catch {
    return false
  }
}

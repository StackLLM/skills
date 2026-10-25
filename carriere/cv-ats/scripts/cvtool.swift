// cvtool — outil natif macOS de la skill cv-ats.
//
//   cvtool render <cv.html> <sortie.pdf> [titre] [auteur]
//       Charge le HTML dans WebKit, lance l'ajustement automatique de la page
//       (window.ajuster, défini dans le gabarit), puis exporte un PDF A4
//       vectoriel : texte sélectionnable, liens cliquables, une ou deux pages.
//       Affiche sur stdout le JSON de l'ajustement.
//
//   cvtool photo <entree> <sortie.jpg> [cote_px]
//       Détecte le visage (framework Vision) et recadre en carré au cadrage
//       de référence V4 : visage centré, un peu d'air au-dessus des cheveux,
//       haut des épaules visible. Sans visage détecté : recadrage centré haut.
//
//   cvtool apercu <cv.pdf> <dossier> [largeur_px]
//       Rend chaque page en PNG pour le contrôle visuel.
//
//   cvtool texte <cv.pdf>
//       Extrait le texte page par page et les liens, comme le lirait un ATS.
//
// Compilé automatiquement par cv.py (swiftc -O) : rien à installer.

import AppKit
import ImageIO
import PDFKit
import Vision
import WebKit

let A4 = CGRect(x: 0, y: 0, width: 595.28, height: 841.89)
let LARGEUR: CGFloat = 794, HAUTEUR_PAGE: CGFloat = 1123   // A4 en px CSS (96 dpi)

func erreur(_ message: String) -> Never {
    FileHandle.standardError.write((message + "\n").data(using: .utf8)!)
    exit(1)
}

func json(_ objet: Any) -> String {
    let data = try! JSONSerialization.data(withJSONObject: objet, options: [.sortedKeys])
    return String(data: data, encoding: .utf8)!
}

// MARK: - render

final class Rendu: NSObject, WKNavigationDelegate {
    let fenetre: NSWindow
    let web: WKWebView
    let sortie: URL
    let titre: String, auteur: String

    init(sortie: URL, titre: String, auteur: String) {
        let cadre = NSRect(x: 0, y: 0, width: LARGEUR, height: HAUTEUR_PAGE)
        fenetre = NSWindow(contentRect: cadre, styleMask: [.borderless], backing: .buffered, defer: false)
        web = WKWebView(frame: cadre, configuration: WKWebViewConfiguration())
        self.sortie = sortie
        self.titre = titre
        self.auteur = auteur
        super.init()
        fenetre.contentView = web
        web.navigationDelegate = self
    }

    func webView(_ w: WKWebView, didFail n: WKNavigation!, withError e: Error) { erreur("chargement : \(e)") }
    func webView(_ w: WKWebView, didFailProvisionalNavigation n: WKNavigation!, withError e: Error) { erreur("chargement : \(e)") }

    func webView(_ w: WKWebView, didFinish n: WKNavigation!) {
        // Polices et images chargées, puis ajustement de la mise en page.
        let script = """
            await document.fonts.ready;
            await Promise.all([...document.images].map(i => i.decode().catch(() => null)));
            return JSON.stringify(window.ajuster ? window.ajuster() : { pages: 1 });
            """
        w.callAsyncJavaScript(script, arguments: [:], in: nil, in: .page) { resultat in
            switch resultat {
            case .failure(let e): erreur("ajustement : \(e)")
            case .success(let valeur):
                let texte = valeur as? String ?? "{}"
                let infos = (try? JSONSerialization.jsonObject(with: texte.data(using: .utf8)!)) as? [String: Any] ?? [:]
                let pages = max(1, infos["pages"] as? Int ?? 1)
                print(texte)
                self.exporter(pages: pages)
            }
        }
    }

    func exporter(pages: Int) {
        let hauteur = HAUTEUR_PAGE * CGFloat(pages)
        web.setFrameSize(NSSize(width: LARGEUR, height: hauteur))
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            let config = WKPDFConfiguration()
            config.rect = CGRect(x: 0, y: 0, width: LARGEUR, height: hauteur)
            self.web.createPDF(configuration: config) { resultat in
                switch resultat {
                case .failure(let e): erreur("createPDF : \(e)")
                case .success(let data): self.decouper(data, pages: pages)
                }
            }
        }
    }

    /// Découpe le rendu continu en pages A4 exactes (vectoriel), puis recopie
    /// les liens, que le redessin CoreGraphics ne conserve pas.
    func decouper(_ data: Data, pages: Int) {
        guard let source = CGPDFDocument(CGDataProvider(data: data as CFData)!),
              let page = source.page(at: 1) else { erreur("PDF WebKit illisible") }
        let boite = page.getBoxRect(.mediaBox)
        let hPage = boite.height / CGFloat(pages)
        let ex = A4.width / boite.width, ey = A4.height / hPage

        var media = A4
        guard let ctx = CGContext(sortie as CFURL, mediaBox: &media, nil) else { erreur("écriture impossible") }
        for i in 0..<pages {
            // Page i (depuis le haut) = bande [bas, bas + hPage] du rendu continu.
            let bas = boite.height - CGFloat(i + 1) * hPage
            ctx.beginPDFPage(nil)
            ctx.saveGState()
            ctx.scaleBy(x: ex, y: ey)
            ctx.translateBy(x: 0, y: -bas)
            ctx.clip(to: CGRect(x: 0, y: bas, width: boite.width, height: hPage))
            ctx.drawPDFPage(page)
            ctx.restoreGState()
            ctx.endPDFPage()
        }
        ctx.closePDF()

        guard let liensSource = PDFDocument(data: data)?.page(at: 0),
              let final = PDFDocument(url: sortie) else { erreur("relecture impossible") }
        for annot in liensSource.annotations where annot.type == "Link" {
            guard let url = annot.url ?? (annot.action as? PDFActionURL)?.url else { continue }
            let r = annot.bounds
            let i = min(pages - 1, max(0, Int((boite.height - r.midY) / hPage)))
            let bas = boite.height - CGFloat(i + 1) * hPage
            guard let cible = final.page(at: i) else { continue }
            let lien = PDFAnnotation(
                bounds: CGRect(x: r.minX * ex, y: (r.minY - bas) * ey, width: r.width * ex, height: r.height * ey),
                forType: .link, withProperties: nil)
            lien.url = url
            lien.border = PDFBorder()
            lien.border?.lineWidth = 0
            cible.addAnnotation(lien)
        }
        final.documentAttributes = [
            PDFDocumentAttribute.titleAttribute: titre,
            PDFDocumentAttribute.authorAttribute: auteur,
            PDFDocumentAttribute.creatorAttribute: "cv-ats",
        ]
        guard final.write(to: sortie) else { erreur("réécriture impossible") }
        exit(0)
    }
}

func commandeRender(_ args: [String]) {
    guard args.count >= 2 else { erreur("usage : cvtool render <cv.html> <sortie.pdf> [titre] [auteur]") }
    let entree = URL(fileURLWithPath: args[0]).standardizedFileURL
    let sortie = URL(fileURLWithPath: args[1]).standardizedFileURL
    let app = NSApplication.shared
    app.setActivationPolicy(.prohibited)
    let rendu = Rendu(sortie: sortie, titre: args.count > 2 ? args[2] : "CV", auteur: args.count > 3 ? args[3] : "")
    rendu.web.loadFileURL(entree, allowingReadAccessTo: entree.deletingLastPathComponent())
    DispatchQueue.main.asyncAfter(deadline: .now() + 60) { erreur("délai dépassé (60 s)") }
    withExtendedLifetime(rendu) { app.run() }
}

// MARK: - photo

// Cadrage de référence (V4), mesuré sur la photo validée par le client :
// le visage détecté occupe HAUTEUR_VISAGE du côté du carré, son centre est à
// CENTRE_Y du haut. Le centre horizontal du visage est centré.
let HAUTEUR_VISAGE: CGFloat = 0.485
let CENTRE_Y: CGFloat = 0.495

func commandePhoto(_ args: [String]) {
    guard args.count >= 2 else { erreur("usage : cvtool photo <entree> <sortie.jpg> [cote_px]") }
    let cote = args.count > 2 ? CGFloat(Double(args[2]) ?? 480) : 480
    guard let image = NSImage(contentsOf: URL(fileURLWithPath: args[0])),
          let cg = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else { erreur("image illisible : \(args[0])") }
    let W = CGFloat(cg.width), H = CGFloat(cg.height)

    let requete = VNDetectFaceRectanglesRequest()
    try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([requete])
    let visages = (requete.results ?? []).sorted { $0.boundingBox.width * $0.boundingBox.height > $1.boundingBox.width * $1.boundingBox.height }

    var carre: CGRect
    var infos: [String: Any] = ["visages": visages.count]
    if let v = visages.first {
        // Vision : coordonnées normalisées, origine en bas à gauche.
        let b = v.boundingBox
        let vx = b.midX * W, vy = (1 - b.midY) * H, vh = b.height * H
        var s = vh / HAUTEUR_VISAGE
        s = min(s, W, H)
        var x = vx - s / 2, y = vy - CENTRE_Y * s
        x = min(max(0, x), W - s)
        y = min(max(0, y), H - s)
        carre = CGRect(x: x, y: y, width: s, height: s)
        infos["visage"] = ["x": Int(vx), "y": Int(vy), "hauteur": Int(vh)]
    } else {
        let s = min(W, H)
        carre = CGRect(x: (W - s) / 2, y: max(0, (H - s) * 0.2), width: s, height: s)
        infos["visage"] = NSNull()
    }
    infos["recadrage"] = ["x": Int(carre.minX), "y": Int(carre.minY), "cote": Int(carre.width)]

    guard let decoupe = cg.cropping(to: carre) else { erreur("recadrage impossible") }
    let n = Int(min(cote, carre.width))
    // Contexte RGB sans alpha (RGBX) : JPEG compact, image correctement dessinée.
    let espace = CGColorSpace(name: CGColorSpace.sRGB)!
    guard let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: n * 4, space: espace,
                              bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue) else { erreur("contexte image") }
    ctx.interpolationQuality = .high
    ctx.draw(decoupe, in: CGRect(x: 0, y: 0, width: n, height: n))
    guard let finale = ctx.makeImage() else { erreur("image finale") }

    // Contrôle : une photo vide ou noire ne doit jamais partir chez le client.
    let pixels = ctx.data!.bindMemory(to: UInt8.self, capacity: n * n * 4)
    var somme = 0.0, somme2 = 0.0
    for i in stride(from: 0, to: n * n * 4, by: 4) {
        let l = 0.2126 * Double(pixels[i]) + 0.7152 * Double(pixels[i + 1]) + 0.0722 * Double(pixels[i + 2])
        somme += l; somme2 += l * l
    }
    let total = Double(n * n), moyenne = somme / total
    infos["luminosite_moyenne"] = Int(moyenne)
    infos["contraste_ecart_type"] = Int(sqrt(max(0, somme2 / total - moyenne * moyenne)))

    let url = URL(fileURLWithPath: args[1]) as CFURL
    guard let dest = CGImageDestinationCreateWithURL(url, "public.jpeg" as CFString, 1, nil) else { erreur("écriture JPEG") }
    CGImageDestinationAddImage(dest, finale, [kCGImageDestinationLossyCompressionQuality: 0.88] as CFDictionary)
    guard CGImageDestinationFinalize(dest) else { erreur("écriture JPEG") }
    infos["cote_px"] = n
    print(json(infos))
}

// MARK: - texte

func commandeTexte(_ args: [String]) {
    guard let chemin = args.first, let doc = PDFDocument(url: URL(fileURLWithPath: chemin)) else { erreur("PDF illisible") }
    var pages: [String] = []
    var liens: [String] = []
    var tailles: [[Double]] = []
    for i in 0..<doc.pageCount {
        guard let p = doc.page(at: i) else { continue }
        pages.append(p.string ?? "")
        let b = p.bounds(for: .mediaBox)
        tailles.append([Double(b.width), Double(b.height)])
        for a in p.annotations where a.type == "Link" {
            if let u = a.url ?? (a.action as? PDFActionURL)?.url { liens.append(u.absoluteString) }
        }
    }
    let attrs = doc.documentAttributes ?? [:]
    print(json([
        "pages": doc.pageCount,
        "textes": pages,
        "liens": liens,
        "formats": tailles,
        "titre": attrs[PDFDocumentAttribute.titleAttribute] as? String ?? "",
        "auteur": attrs[PDFDocumentAttribute.authorAttribute] as? String ?? "",
    ]))
}

// MARK: - apercu

/// Rend chaque page du PDF en PNG (contrôle visuel), largeur en pixels.
func commandeApercu(_ args: [String]) {
    guard args.count >= 2, let doc = PDFDocument(url: URL(fileURLWithPath: args[0])) else {
        erreur("usage : cvtool apercu <cv.pdf> <dossier> [largeur_px]")
    }
    let largeur = args.count > 2 ? CGFloat(Double(args[2]) ?? 1400) : 1400
    let dossier = URL(fileURLWithPath: args[1])
    try? FileManager.default.createDirectory(at: dossier, withIntermediateDirectories: true)
    let base = URL(fileURLWithPath: args[0]).deletingPathExtension().lastPathComponent
    var fichiers: [String] = []
    for i in 0..<doc.pageCount {
        guard let page = doc.page(at: i) else { continue }
        let b = page.bounds(for: .mediaBox)
        let echelle = largeur / b.width
        let w = Int(b.width * echelle), h = Int(b.height * echelle)
        let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: w, pixelsHigh: h, bitsPerSample: 8,
                                   samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                                   colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
        NSGraphicsContext.saveGraphicsState()
        let ctx = NSGraphicsContext(bitmapImageRep: rep)!
        NSGraphicsContext.current = ctx
        let cg = ctx.cgContext
        cg.setFillColor(NSColor.white.cgColor)
        cg.fill(CGRect(x: 0, y: 0, width: w, height: h))
        cg.scaleBy(x: echelle, y: echelle)
        page.draw(with: .mediaBox, to: cg)
        NSGraphicsContext.restoreGraphicsState()
        let sortie = dossier.appendingPathComponent("\(base)-p\(i + 1).png")
        try! rep.representation(using: .png, properties: [:])!.write(to: sortie)
        fichiers.append(sortie.path)
    }
    print(json(["apercus": fichiers]))
}

// MARK: - point d'entrée

var args = CommandLine.arguments.dropFirst()
guard let commande = args.popFirst() else { erreur("commandes : render | photo | texte | apercu") }
switch commande {
case "render": commandeRender(Array(args))
case "photo": commandePhoto(Array(args))
case "texte": commandeTexte(Array(args))
case "apercu": commandeApercu(Array(args))
default: erreur("commande inconnue : \(commande)")
}

/* =========================================================================
   Ajustement automatique de la page — appelé par cvtool avant l'export.

   Objectif : tout le contenu sur une page A4, sans rien couper, avec la
   densité la plus proche possible de la référence V4.

   1. Équilibrage : les sections « mobiles » (certifications, langues,
      qualités) passent d'une colonne à l'autre si cela évite un débordement.
   2. Densité : si ça déborde, on resserre d'abord les espacements (--air),
      puis, en dernier recours, le texte (--txt), jamais sous 94 %.
   3. Aération : si la page est trop vide, on augmente les espacements
      (jusqu'à 170 %), puis légèrement le texte (jusqu'à 108 %).
   4. Deux pages : seulement si la densité minimale ne suffit pas. Aucun
      bloc n'est coupé entre deux pages.

   Renvoie un rapport JSON lu par cv.py (contrôle qualité).
   ========================================================================= */

window.ajuster = function () {
  const MM = 96 / 25.4;
  const H = 297 * MM;               // hauteur d'une page en px CSS
  const MARGE_HAUT = 10 * MM, MARGE_BAS = 9 * MM;

  const racine = document.documentElement;
  const page = document.querySelector(".page");
  const corps = document.querySelector(".corps");
  const principale = document.querySelector(".principale");
  const laterale = document.querySelector(".laterale");

  // Position d'origine des sections mobiles, pour repartir de zéro à chaque essai.
  const origine = [...document.querySelectorAll("section[data-mobile]")]
    .map((s) => ({ s, parent: s.parentElement, avant: s.nextElementSibling }));

  /* Pas de mot seul en dernière ligne : les deux derniers mots de chaque
     paragraphe sont placés dans un <span class="insecable"> (white-space: nowrap).
     Jamais d'espace insécable U+00A0 : certains lecteurs PDF (et ATS) perdent
     alors toute la fin de ligne. text-wrap: pretty ferait mieux, mais tous les
     WebKit ne l'ont pas. */
  function lierDerniersMots() {
    for (const el of document.querySelectorAll(".principale ul.points > li, .principale section > p, .laterale li")) {
      if (el.querySelector(".insecable")) continue;
      const marcheur = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      let dernier = null;
      for (let n = marcheur.nextNode(); n; n = marcheur.nextNode()) if (/\S\s+\S/.test(n.nodeValue)) dernier = n;
      if (!dernier) continue;
      const m = dernier.nodeValue.match(/^([\s\S]*\s)(\S+\s+\S+)(\s*)$/);
      // On ne lie que si les deux mots restent courts : un long groupe peut se couper.
      if (!m || m[2].length > 24) continue;
      const span = document.createElement("span");
      span.className = "insecable";
      span.textContent = m[2];
      dernier.nodeValue = m[1];
      dernier.parentNode.insertBefore(span, dernier.nextSibling);
      if (m[3]) span.after(document.createTextNode(m[3]));
    }
  }
  // Désactivable par cv.py (data-liaison="non") si l'ordre de lecture ATS en souffre.
  if (racine.dataset.liaison !== "non") lierDerniersMots();

  function regler(air, txt, pages) {
    racine.style.setProperty("--air", air.toFixed(3));
    racine.style.setProperty("--txt", txt.toFixed(3));
    page.style.height = pages * 297 + "mm";
    // Sur deux pages, l'encadré latéral s'arrête avec son contenu (pas de boîte vide en page 2).
    if (laterale) laterale.style.alignSelf = pages > 1 ? "start" : "";
  }

  function restaurer() {
    for (const { s, parent, avant } of origine) parent.insertBefore(s, avant && avant.parentElement === parent ? avant : null);
    document.querySelectorAll("[data-pousse]").forEach((el) => {
      el.style.marginTop = "";
      el.removeAttribute("data-pousse");
    });
  }

  /* Coordonnées : une ligne si possible, sinon deux lignes sans « · » orphelin. */
  function coordonnees() {
    const ul = document.querySelector(".coordonnees");
    if (!ul) return false;
    ul.classList.remove("sur-deux-lignes");
    ul.querySelectorAll(".debut-ligne").forEach((li) => li.classList.remove("debut-ligne"));
    if (ul.scrollWidth <= ul.clientWidth + 1) return false;
    ul.classList.add("sur-deux-lignes");
    let haut = null;
    for (const li of ul.children) {
      const t = Math.round(li.getBoundingClientRect().top);
      if (haut !== null && t > haut + 2) li.classList.add("debut-ligne");
      haut = t;
    }
    return true;
  }

  function basContenu(col) {
    const enfants = [...col.children];
    if (!enfants.length) return col.getBoundingClientRect().top;
    return Math.max(...enfants.map((e) => e.getBoundingClientRect().bottom));
  }

  /* Place restante (px) en bas de chaque colonne ; négatif = débordement. */
  function marges() {
    const bas = corps.getBoundingClientRect().bottom;
    const padLat = laterale ? parseFloat(getComputedStyle(laterale).paddingBottom) : 0;
    return {
      principale: bas - basContenu(principale),
      laterale: laterale ? bas - padLat - basContenu(laterale) : Infinity,
    };
  }

  const tient = (m) => m.principale >= 0 && m.laterale >= 0;
  const score = (m) => Math.min(m.principale, m.laterale);

  /* Déplace des sections mobiles tant que cela améliore la colonne la plus serrée. */
  function equilibrer() {
    if (!laterale) return marges();
    let m = marges();
    for (let tour = 0; tour < 6 && !tient(m); tour++) {
      const depuis = m.laterale < m.principale ? laterale : principale;
      const vers = depuis === laterale ? principale : laterale;
      const candidates = [...depuis.querySelectorAll(":scope > section[data-mobile]")];
      let meilleur = null;
      for (const s of candidates.reverse()) {
        const parent = s.parentElement, avant = s.nextElementSibling;
        vers.appendChild(s);
        const n = marges();
        if (score(n) > score(m) && (!meilleur || score(n) > score(meilleur.m))) meilleur = { s, m: n };
        parent.insertBefore(s, avant);
      }
      if (!meilleur) break;
      vers.appendChild(meilleur.s);
      m = marges();
    }
    return m;
  }

  /* Mode deux pages : pousse sur la page 2 tout bloc qui chevaucherait la coupure. */
  function paginer() {
    const limite = H - MARGE_BAS, reprise = H + MARGE_HAUT;
    for (const col of [principale, laterale].filter(Boolean)) {
      const atomes = col.querySelectorAll("h2, .tete, ul.points > li, .competences li, .formation .bloc, section > p, .note");
      for (const a of atomes) {
        const r = a.getBoundingClientRect();
        const top = r.top + window.scrollY, bas = top + r.height;
        // Un titre ne reste jamais seul en bas de page : on garde ~12 mm derrière lui.
        const garde = a.matches("h2, .tete") ? 12 * MM : 0;
        if (top < limite && bas + garde > limite) {
          const delta = reprise - top;
          a.style.marginTop = parseFloat(getComputedStyle(a).marginTop) + delta + "px";
          a.setAttribute("data-pousse", "1");
        }
      }
    }
  }

  /* Paragraphes dont la dernière ligne ne contient qu'un seul mot : à reformuler. */
  function lignesCourtes() {
    const resultats = [];
    for (const el of document.querySelectorAll(".principale ul.points > li, .principale section > p")) {
      const mots = [];
      const marcheur = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
      for (let n = marcheur.nextNode(); n; n = marcheur.nextNode()) {
        for (const m of n.nodeValue.matchAll(/\S+/g)) {
          const r = document.createRange();
          r.setStart(n, m.index);
          r.setEnd(n, m.index + m[0].length);
          const rect = r.getClientRects()[0];
          if (rect) mots.push(Math.round(rect.top));
        }
      }
      const lignes = new Set(mots);
      if (lignes.size < 2) continue;
      const derniere = Math.max(...lignes);
      if (mots.filter((t) => Math.abs(t - derniere) <= 2).length === 1) {
        resultats.push(el.textContent.trim().replace(/\s+/g, " ").slice(-60));
      }
    }
    return resultats;
  }

  /* Débordements horizontaux (texte coupé à droite). */
  function debordementsHorizontaux() {
    const out = [];
    const droite = page.getBoundingClientRect().right - 13 * MM + 1;
    for (const el of document.querySelectorAll("h1, .titre, .coordonnees li, h3, .date, li, p")) {
      if (el.getBoundingClientRect().right > droite) out.push(el.textContent.trim().slice(0, 50));
    }
    return out;
  }

  // ---------- Recherche de la mise en page ----------
  const PALIERS = [[1, 1], [0.92, 1], [0.85, 1], [0.8, 0.98], [0.76, 0.96], [0.72, 0.94]];
  let pages = 1, choix = null, m = null;

  for (const [air, txt] of PALIERS) {
    restaurer(); regler(air, txt, 1); coordonnees();
    m = equilibrer();
    if (tient(m)) { choix = { air, txt }; break; }
  }

  if (choix && choix.air === 1 && choix.txt === 1) {
    // Page trop vide : on aère, sans dépasser 170 % d'espacement et 108 % de texte.
    for (let a = 1.05; a <= 1.7001; a += 0.05) {
      restaurer(); regler(a, 1, 1); coordonnees();
      if (tient(equilibrer())) choix.air = a; else break;
    }
    for (let t = 1.01; t <= 1.0801; t += 0.01) {
      restaurer(); regler(choix.air, t, 1); coordonnees();
      if (tient(equilibrer())) choix.txt = t; else break;
    }
    restaurer(); regler(choix.air, choix.txt, 1); coordonnees();
    m = equilibrer();
  }

  if (!choix) {
    // Deux pages, à la densité de référence si possible.
    pages = 2;
    for (const [air, txt] of PALIERS) {
      restaurer(); regler(air, txt, 2); coordonnees();
      paginer();
      m = marges();
      if (tient(m)) { choix = { air, txt }; break; }
    }
  }

  const deplacees = [...document.querySelectorAll("section[data-mobile]")]
    .filter((s) => s.parentElement !== origine.find((o) => o.s === s).parent)
    .map((s) => s.dataset.mobile);

  // Part de la dernière page laissée vide sous la colonne la plus longue.
  const hauteurUtile = corps.getBoundingClientRect().height;
  const vide = Math.max(0, Math.min(m.principale, m.laterale === Infinity ? m.principale : m.laterale));

  return {
    pages,
    part_vide: +(vide / (hauteurUtile / pages)).toFixed(2),
    air: choix ? +choix.air.toFixed(2) : null,
    txt: choix ? +choix.txt.toFixed(2) : null,
    debordement: !choix,
    marges_px: { principale: Math.round(m.principale), laterale: m.laterale === Infinity ? null : Math.round(m.laterale) },
    deplacees,
    coordonnees_sur_deux_lignes: !!document.querySelector(".coordonnees.sur-deux-lignes"),
    lignes_courtes: lignesCourtes(),
    debordements_horizontaux: debordementsHorizontaux(),
    corps_texte_pt: +(8.95 * (choix ? choix.txt : 0.94)).toFixed(2),
  };
};

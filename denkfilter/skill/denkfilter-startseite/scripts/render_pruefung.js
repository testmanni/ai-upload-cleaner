// Render-Prüfung der DENKFILTER-Startseite mit Playwright (Chromium headless).
//
//   node render_pruefung.js PFAD/denkfilter-startseite.html [SCREENSHOT-ORDNER]
//
// Voraussetzung: Node mit dem Paket "playwright" und einem Chromium.
// Prüft bei 1600, 1366, 1280, 1024, 768, 390, 320 px: horizontaler Überlauf,
// herausragende oder abgeschnittene Elemente, eingebettete Schriften geladen,
// Lauftext mobil >= 16 px, Touchziele >= 24 px, keine externen Abrufe.
// Dazu Sprach- und Schemawechsel per Klick, Tastaturfokus und alle Einblender.
// Exit-Code 1, wenn ein Problem gefunden wurde.
const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const DATEI = path.resolve(process.argv[2] || 'denkfilter-startseite.html');
const OUT = path.resolve(process.argv[3] || path.join(path.dirname(DATEI), 'pruefung-screenshots'));
const URL = 'file://' + DATEI;
const BREITEN = [1600, 1366, 1280, 1024, 768, 390, 320];
fs.mkdirSync(OUT, { recursive: true });

async function seite(browser, w, h = 900) {
  const ctx = await browser.newContext({ viewport: { width: w, height: h } });
  const page = await ctx.newPage();
  const extern = [];
  await page.route('**/*', r => {
    const u = r.request().url();
    if (!u.startsWith('file:') && !u.startsWith('data:')) { extern.push(u); return r.abort(); }
    return r.continue();
  });
  await page.goto(URL);
  await page.evaluate(() => document.fonts.ready);
  return { page, ctx, extern };
}

(async () => {
  const browser = await chromium.launch();
  let probleme = 0;
  const melde = t => { probleme++; console.log('  ! ' + t); };

  for (const w of BREITEN) {
    const { page, ctx, extern } = await seite(browser, w);
    const r = await page.evaluate((w) => {
      const p = [];
      const de = document.documentElement;
      if (de.scrollWidth > innerWidth) p.push('horizontaler Überlauf ' + de.scrollWidth);
      const archivo = document.fonts.check('900 40px Archivo'), inter = document.fonts.check('400 16px Inter');
      if (!archivo || !inter) p.push('Schriften nicht geladen');
      const sichtbar = el => { const b = el.getBoundingClientRect(), s = getComputedStyle(el); return b.width > 0 && b.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
      for (const el of document.querySelectorAll('.site *')) {
        if (!sichtbar(el) || el.closest('svg') || el.closest('.einblender') || el.closest('.schema-text')) continue;
        const b = el.getBoundingClientRect();
        if (b.right > innerWidth + 0.5 || b.left < -0.5) p.push('ragt heraus: ' + el.tagName + '.' + el.className);
        const s = getComputedStyle(el);
        if (s.overflow === 'hidden' && el.scrollWidth > el.clientWidth + 1 && !el.matches('.visual,.karte,.kasten'))
          p.push('abgeschnitten: ' + el.tagName + '.' + el.className);
      }
      let minText = null;
      if (w <= 768) {
        minText = 99;
        for (const el of document.querySelectorAll('.site main p, .site main li')) {
          if (!sichtbar(el)) continue;
          const fs = parseFloat(getComputedStyle(el).fontSize); minText = Math.min(minText, fs);
          if (fs < 16) p.push('Lauftext < 16 px: ' + el.textContent.trim().slice(0, 40));
        }
      }
      let minT = 999;
      for (const el of document.querySelectorAll('.site main a, .site header a, .site label, .site footer a')) {
        if (!sichtbar(el)) continue;
        const b = el.getBoundingClientRect(); minT = Math.min(minT, b.width, b.height);
        if (b.width < 24 || b.height < 24) p.push('Touchziel < 24 px: ' + el.textContent.trim().slice(0, 30));
      }
      return { p, minText, minT: Math.round(minT), htmlBg: getComputedStyle(de).backgroundColor };
    }, w);
    console.log(`${w}px: min. Lauftext ${r.minText ?? '-'} · min. Touchziel ${r.minT}px · html ${r.htmlBg}`);
    r.p.forEach(melde);
    if (extern.length) melde('externe Abrufe: ' + extern.join(', '));
    await page.screenshot({ path: `${OUT}/de-hell-${w}.png`, fullPage: true });
    await ctx.close();
  }

  // Sprache und Farbschema per Klick
  {
    const { page, ctx } = await seite(browser, 1366);
    const titel = () => page.evaluate(() => document.querySelector('.fall-titel').innerText);
    const de = await titel();
    await page.click('label[for=lang-en]');
    const en = await titel();
    if (de === en) melde('Sprachwechsel ändert den Fall-Titel nicht');
    await page.click('label[for=theme-dark]'); await page.waitForTimeout(400);
    const bg = await page.evaluate(() => getComputedStyle(document.documentElement).backgroundColor);
    if (bg === 'rgb(246, 248, 251)') melde('Dunkelmodus ändert den html-Hintergrund nicht');
    await page.screenshot({ path: `${OUT}/en-dunkel-1366.png`, fullPage: true });
    console.log(`Sprache: "${de}" -> "${en}" · dunkel: html ${bg}`);
    await ctx.close();
  }

  // Tastatur: sichtbarer Fokus auf den ersten Bedienelementen
  {
    const { page, ctx } = await seite(browser, 1366);
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Tab');
      const f = await page.evaluate(() => {
        const a = document.activeElement;
        const ziel = a.classList.contains('ui-toggle') ? document.querySelector(`label[for="${a.id}"]`) : a;
        const s = getComputedStyle(ziel);
        return { name: a.id || a.getAttribute('href'), ok: s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) >= 2 };
      });
      if (!f.ok) melde('kein sichtbarer Fokus auf ' + f.name);
    }
    await ctx.close();
  }

  // Einblender öffnen und schließen
  for (const w of [1366, 390]) {
    const { page, ctx } = await seite(browser, w);
    const ids = await page.evaluate(() => [...document.querySelectorAll('.einblender')].map(e => e.id));
    for (const id of ids) {
      await page.click(`.fuss-recht a[href="#${id}"]`); await page.waitForTimeout(250);
      const r = await page.evaluate(id => {
        const e = document.getElementById(id), b = e.querySelector('.einblender-panel').getBoundingClientRect();
        return { offen: getComputedStyle(e).display === 'block', drin: b.left >= 0 && b.right <= innerWidth, sw: document.documentElement.scrollWidth };
      }, id);
      if (!r.offen || !r.drin || r.sw > w) melde(`Einblender ${id} bei ${w}px: ${JSON.stringify(r)}`);
      await page.click(`#${id} .einblender-zu`); await page.waitForTimeout(200);
      if (await page.evaluate(id => getComputedStyle(document.getElementById(id)).display, id) !== 'none') melde(`Einblender ${id} schließt nicht`);
    }
    console.log(`Einblender bei ${w}px geprüft: ${ids.join(', ')}`);
    await ctx.close();
  }

  await browser.close();
  console.log(`Probleme gesamt: ${probleme} · Screenshots: ${OUT}`);
  process.exit(probleme ? 1 : 0);
})();

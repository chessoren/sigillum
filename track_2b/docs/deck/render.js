// Render each 1800x1200 (3:2) slide of deck.html to PNG.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const path = require('path'); const fs = require('fs');
(async () => {
  const out = path.join(__dirname, process.env.DECK_OUT || 'slides'); fs.mkdirSync(out, { recursive: true });
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  const p = await b.newPage({ viewport: { width: 1800, height: 1200 }, deviceScaleFactor: 1 });
  await p.goto('file://' + path.join(__dirname, process.env.DECK_HTML || 'deck.html'), { waitUntil: 'networkidle' });
  await p.evaluate(() => document.fonts.ready);
  const slides = await p.$$('.slide');
  for (let i = 0; i < slides.length; i++) await slides[i].screenshot({ path: path.join(out, `slide-${String(i + 1).padStart(2, '0')}.png`) });
  console.log(slides.length, 'slides');
  await b.close();
})();

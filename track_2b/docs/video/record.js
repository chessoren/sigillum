// Records the demo: one real-screen scene per narration segment (no mock-ups).
// usage: node record.js [scene-id ...]   → docs/video/scenes/<id>.webm
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'); const path = require('path'); const { execSync } = require('child_process');
const BASE = process.env.BASE || 'http://localhost:8080';
const DIR = __dirname; const OUT = path.join(DIR, 'scenes'); fs.mkdirSync(OUT, { recursive: true });
const NAR = JSON.parse(fs.readFileSync(path.join(DIR, 'narration.json')));
const dur = (id) => parseFloat(execSync(`ffprobe -v error -show_entries format=duration -of csv=p=0 ${path.join(DIR, 'voice', id + '.mp3')}`).toString()) + 0.6;
const W = 1920, H = 1080;

async function subs(p, it) {
  await p.evaluate(({ fr, en }) => {
    let el = document.getElementById('demo-subs');
    if (!el) {
      el = document.createElement('div'); el.id = 'demo-subs';
      el.style.cssText = 'position:fixed;left:50%;bottom:34px;transform:translateX(-50%);z-index:9999;max-width:1400px;width:max-content;background:rgba(26,11,12,.86);color:#fff;border-radius:22px;padding:14px 26px;text-align:center;font-family:"Sigillum Sans",sans-serif;box-shadow:0 10px 40px #0004;backdrop-filter:blur(12px)';
      document.body.appendChild(el);
    }
    el.innerHTML = `<div style="font-size:27px;font-weight:600;letter-spacing:-.02em;line-height:1.25">${fr}</div><div style="font-size:21px;opacity:.72;letter-spacing:-.01em;margin-top:4px;line-height:1.25">${en}</div>`;
  }, it);
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function smooth(p, y, ms = 1200) {
  await p.evaluate(({ y, ms }) => new Promise((res) => {
    const y0 = scrollY, t0 = performance.now();
    const f = (t) => { const k = Math.min(1, (t - t0) / ms), e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2; scrollTo(0, y0 + (y - y0) * e); k < 1 ? requestAnimationFrame(f) : res(); };
    requestAnimationFrame(f);
  }), { y, ms });
}
async function toEl(p, sel, offset = 120, ms = 1200) {
  const y = await p.evaluate(({ sel, offset }) => { const el = document.querySelector(sel); return el ? el.getBoundingClientRect().top + scrollY - offset : scrollY; }, { sel, offset });
  await smooth(p, y, ms);
}
async function cursorClick(p, sel) {
  const box = await (await p.$(sel)).boundingBox();
  await p.evaluate(({ x, y }) => {
    let c = document.getElementById('demo-cursor');
    if (!c) { c = document.createElement('div'); c.id = 'demo-cursor'; c.style.cssText = 'position:fixed;z-index:10000;width:26px;height:26px;border-radius:999px;background:rgba(218,41,28,.35);border:2px solid #da291c;pointer-events:none;transition:left .6s cubic-bezier(.22,1,.36,1),top .6s cubic-bezier(.22,1,.36,1)'; document.body.appendChild(c); c.style.left = (x - 200) + 'px'; c.style.top = (y + 120) + 'px'; }
    requestAnimationFrame(() => { c.style.left = (x - 13) + 'px'; c.style.top = (y - 13) + 'px'; });
  }, { x: box.x + box.width / 2, y: box.y + box.height / 2 });
  await sleep(750);
  await p.click(sel);
}

let R = null;
const id = (name, which = 'last') => { const xs = R.filter((r) => r.name === name).sort((a, b) => a.examined_at.localeCompare(b.examined_at)); return (which === 'first' ? xs[0] : xs[xs.length - 1]).id; };

const SCENES = {
  '01': async (p) => { await p.goto(`${BASE}/index.html?lang=fr`); await sleep(400); },
  '02': async (p, d) => { await p.goto(`${BASE}/index.html?lang=fr`); await smooth(p, 330, 1500); await sleep(d * 1000 - 1900); },
  '03': async (p) => { await p.goto(`${BASE}/index.html?lang=fr`); await toEl(p, '#q-title', 90, 10); await sleep(300); await toEl(p, '#q-grid', 300, 2600); },
  '04': async (p) => { await p.goto(`${BASE}/report.html?id=${id('chat-commune')}&lang=fr`); await sleep(2600); await toEl(p, '#q4', 140, 1800); await sleep(1500); await toEl(p, '#q2', 140, 1500); },
  '05': async (p) => { await p.goto(`${BASE}/report.html?id=${id('assistant-ecole', 'first')}&lang=fr`); await sleep(1500); await toEl(p, '#gaps', 100, 1600); },
  '06': async (p) => { await p.goto(`${BASE}/report.html?id=${id('assistant-ecole', 'first')}&lang=fr#gaps`); await sleep(600); await toEl(p, '#gaps', 100, 10); await sleep(2600); await cursorClick(p, '#gaps .shows'); await sleep(400); await toEl(p, '#q4', 140, 1800); },
  '07': async (p) => { await p.goto(`${BASE}/report.html?id=${id('assistant-ecole', 'first')}&lang=fr`); await sleep(2000); await toEl(p, '.fixes', 260, 1600); await sleep(1200); await cursorClick(p, '.timeline a:last-of-type'); await sleep(2200); },
  '08': async (p) => { await p.goto(`${BASE}/report.html?id=${id('civicgpt')}&lang=fr`); await sleep(1300); for (const l of ['de', 'it', 'rm']) { await cursorClick(p, `.tabs button[data-l="${l}"]`); await sleep(1900); } },
  '09': async (p) => { await p.goto(`${BASE}/community.html?lang=fr`); await sleep(3200); await toEl(p, '.collage', 60, 2600); },
  '10': async (p) => { await p.goto(`${BASE}/report.html?id=${id('sigillum')}&lang=fr`); await sleep(2600); await toEl(p, '.timeline', 420, 1800); },
  '11': async (p, d) => { await p.goto(`${BASE}/offline.html`); await sleep(3800); await p.goto(`${BASE}/index.html?lang=fr`); await sleep(400); await smooth(p, 99999, 2600); },
};

(async () => {
  R = await (await fetch(`${BASE}/api/reports`)).json();
  const only = process.argv.slice(2);
  const b = await chromium.launch({ args: ['--no-sandbox'] });
  for (const it of NAR) {
    if (only.length && !only.includes(it.id)) continue;
    const d = dur(it.id);
    const ctx = await b.newContext({ viewport: { width: W, height: H }, recordVideo: { dir: OUT, size: { width: W, height: H } } });
    const p = await ctx.newPage();
    const t0 = Date.now();
    await p.addInitScript(() => { try { localStorage.setItem('sigillum-lang', 'fr'); } catch {} });
    p.on('load', () => subs(p, it).catch(() => {}));
    await SCENES[it.id](p, d).catch((e) => console.error(it.id, e.message));
    await subs(p, it).catch(() => {});
    const left = d * 1000 - (Date.now() - t0) + 1200; if (left > 0) await sleep(left);
    const v = p.video(); await ctx.close();
    const src = await v.path(); fs.renameSync(src, path.join(OUT, `${it.id}.webm`));
    // remember when the page became usable: trim the white start later
    fs.writeFileSync(path.join(OUT, `${it.id}.json`), JSON.stringify({ total: (Date.now() - t0) / 1000, voice: d }));
    console.log(it.id, 'recorded', d.toFixed(1), 's');
  }
  await b.close();
})();

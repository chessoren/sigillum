/* Sigillum — interface. No framework, no CDN, no tracking. */
"use strict";

const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const params = new URLSearchParams(location.search);

/* ------------------------------------------------------------------ i18n */
const UI = {
  en: {
    banner: "An open transparency instrument — not an official certification",
    bannerInfo: "Sigillum is an independent open-source project built for Hack Apertus. It is not affiliated with the Swiss Confederation.",
    menu: "Menu", close: "Close",
    nav: { home: "Home", how: "How it works", method: "Method", community: "Community audit", self: "Sigillum's own seal", source: "Source code" },
    heroTitle: "Sovereign? Prove it.",
    heroLead: "A grade from A to E for the sovereignty of any AI tool — with proof behind every answer.",
    askPlaceholder: "Examine a project: a Git URL or a sample name",
    try: "Try", examineBtn: "Examine",
    manifesto: (p) => `Sigillum asks ${p.five} five questions of any AI project, looks for ${p.proof} proof behind every answer and, when there is none, says so: ${p.unknown} unknown.`,
    miniAsk: "Paste a public Git URL…",
    f1t: "One letter anyone can read.", f1b: "Like the energy label or the Nutri-Score: from A (fully sovereign) to E (dependent on foreign services), with five pictograms. A mayor, a CIO or a pupil gets it in ten seconds.", f1l: "See a seal",
    f2t: "No proof? The seal says “unknown”.", f2b: "Every answer points to a file and a line anyone can open. A claim without a trace never earns more than C.", f2l: "Read the proof rule",
    f3t: "The weakest link decides.", f3b: "Perfect on four questions, but data leaves the country? That is not an A. A strict, reliable signal beats a flattering average.", f3l: "See the method",
    f4t: "A dated seal that expires.", f4b: "Each seal carries a date, the commit examined and a SHA-256 fingerprint. It expires after 90 days: a project that changes must be examined again.", f4l: "Verify a seal",
    qTitle: "Five questions. One proof for each.",
    qLead: "Sigillum reads the code and configuration, never the users' data. Each answer cites the evidence it rests on.",
    best: "Best", worst: "Worst",
    qa: { 1: ["On a machine the organisation controls", "Closed model at a foreign company"], 2: ["Nothing leaves", "Questions and documents leave the country"], 3: ["Everything works, and it is tested", "Everything stops"], 4: ["Nobody: no tracking, no telemetry", "Trackers watch the users"], 5: ["Licence, reproducible build, tests", "Nothing to check"] },
    apTitle: "Apertus reads, compares and explains. The evidence decides.",
    apBody: "Apertus extracts what a project claims about itself, sets each claim against the traces found in the code, and explains the verdict in plain language — in German, French, Italian and Romansh. Every answer is checked: a quote must exist word for word, every line must cite real evidence. The grade itself never depends on the model.",
    apLink: "See this gap in its report",
    selfTitle: "We started with ourselves.",
    selfLead: "Before measuring anyone else, Sigillum examined itself with the strictest rule — and published its limits. Then the public Apertus ecosystem, aggregated and anonymous.",
    selfBtn: "See Sigillum's own seal",
    commTitle: "Public Apertus projects, aggregated", commSub: "anonymous · no project named",
    beforeAfter: "Before / after: a team fixes its report", ethicsTitle: "Our rules",
    ethics: ["Only public projects", "Aggregated and anonymous", "Right of reply before naming", "A free service, not a trial", "Sigillum first, on itself"],
    footerTag: "An open seal, checkable by anyone", poweredBy: "Explained by Apertus, Switzerland's open LLM", license: "Open source · Apache-2.0 · CC-BY-4.0",
    says: "The project says", shows: "The traces show", source: "Source", rule: "rule", apertusSrc: "Apertus",
    examined: "Examined", commit: "commit", expires: "expires", seal: "seal", files: "files",
    plainTitle: "In plain words", plainSrcAp: "Written by Apertus", plainSrcConf: "Confirmed by Apertus — identical to the reviewed template", plainSrcTpl: "Reviewed template — Apertus not reachable or answer rejected",
    questionsTitle: "The five answers, with their evidence",
    proof: { reproducible: "reproducible proof", trace: "trace in the code", declared: "declaration only", none: "no proof" },
    kind: { trace: "trace", artifact: "artifact", declaration: "claim", absence: "absence" },
    fixesTitle: "To move up a letter", noFixes: "Nothing to fix on the five questions. Keep the seal fresh: examine again when the project changes.",
    historyTitle: "History", embedTitle: "Embed this seal", download: "Download the report (JSON)",
    gapsTitle: "What the project says, and what the traces show", noGaps: "No contradiction found between the documentation and the traces.",
    unknownCap: "Unknown is shown as unknown — and caps the grade at C.",
    weakest: "Weakest link", notOfficial: "Transparency instrument, not a legal certification.",
    ethicsNote: "This is an example project created by the Sigillum team.",
    running: "Examining…", steps: { scan: "Reading files", grade: "Grading on evidence", "apertus:claims": "Apertus reads the documentation", "apertus:reconcile": "Apertus compares claims and traces", explain: "Apertus explains" },
    error: "The examination failed", back: "All seals",
    reportsTitle: "Recent seals", noApertus: "Apertus not reachable: deterministic grade, template explanations.",
    model: "model", endpoint: "endpoint", calls: "calls", rejected: "answers rejected by checks",
    excluded: "Paths excluded by the project (published, not hidden)",
    commIntro: "Hack Apertus submissions become public after 24 October. Until then, we applied the seal to every public Hugging Face Space that uses Apertus. Results are aggregated: no project is named without its team's consent.",
    commProjects: "public projects examined", commForeignLLM: "call the model through a foreign service", commTelemetry: "ship telemetry on by default", commOffline: "would keep working offline",
    commTop: "Most frequent dependency abroad", commDist: "Distribution of grades",
    commMethod: "Method: shallow clone of each public Space, static analysis only, no request to the projects' running apps, no data about users.",
  },
  fr: {
    banner: "Un instrument de transparence ouvert — pas une certification officielle",
    bannerInfo: "Sigillum est un projet open source indépendant, créé pour Hack Apertus. Il n'est pas affilié à la Confédération suisse.",
    menu: "Menu", close: "Fermer",
    nav: { home: "Accueil", how: "Comment ça marche", method: "Méthode", community: "Bilan de la communauté", self: "Le sceau de Sigillum", source: "Code source" },
    heroTitle: "Souverain ? Prouvez-le.",
    heroLead: "Une note de A à E pour la souveraineté d'un outil d'IA — avec une preuve pour chaque réponse.",
    askPlaceholder: "Examiner un projet : une URL Git ou un exemple",
    try: "Essayer", examineBtn: "Examiner",
    manifesto: (p) => `Sigillum pose ${p.five} cinq questions à n'importe quel projet d'IA, cherche ${p.proof} une preuve pour chaque réponse et, quand il n'en trouve pas, il le dit : ${p.unknown} inconnu.`,
    miniAsk: "Collez une URL Git publique…",
    f1t: "Une lettre, lisible par tous.", f1b: "Comme l'étiquette énergie ou le Nutri-Score : de A (pleinement souverain) à E (dépendant de l'étranger), avec cinq pictogrammes. Un maire, un DSI ou un élève le comprend en dix secondes.", f1l: "Voir un sceau",
    f2t: "Sans preuve, le sceau dit : inconnu.", f2b: "Chaque réponse renvoie à un fichier et à une ligne que chacun peut ouvrir. Une affirmation sans trace ne dépasse jamais C.", f2l: "Lire la règle de la preuve",
    f3t: "Le maillon faible décide.", f3b: "Parfait sur quatre questions, mais des données qui partent à l'étranger ? Ce n'est pas A. Mieux vaut un signal sévère et fiable qu'une moyenne flatteuse.", f3l: "Voir la méthode",
    f4t: "Un sceau daté, qui expire.", f4b: "Chaque sceau porte une date, le commit examiné et une empreinte SHA-256. Il expire après 90 jours : un projet qui change doit être réexaminé.", f4l: "Vérifier un sceau",
    qTitle: "Cinq questions. Une preuve pour chacune.",
    qLead: "Sigillum lit le code et la configuration, jamais les données des utilisateurs. Chaque réponse cite la preuve sur laquelle elle repose.",
    best: "Au mieux", worst: "Au pire",
    qa: { 1: ["Sur une machine que l'organisation contrôle", "Un modèle fermé, chez une entreprise étrangère"], 2: ["Rien ne sort", "Questions et documents quittent le pays"], 3: ["Tout marche, et c'est testé", "Tout s'arrête"], 4: ["Personne : ni suivi, ni télémétrie", "Des traceurs observent les utilisateurs"], 5: ["Licence, construction reproductible, tests", "Rien à vérifier"] },
    apTitle: "Apertus lit, rapproche et explique. Les preuves décident.",
    apBody: "Apertus extrait ce qu'un projet affirme de lui-même, confronte chaque affirmation aux traces trouvées dans le code, puis explique le verdict en langage simple — en allemand, français, italien et romanche. Chaque réponse est contrôlée : une citation doit exister mot pour mot, chaque ligne doit citer une preuve réelle. La note, elle, ne dépend jamais du modèle.",
    apLink: "Voir cet écart dans son rapport",
    selfTitle: "Nous avons commencé par nous-mêmes.",
    selfLead: "Avant de mesurer qui que ce soit, Sigillum s'est examiné avec la règle la plus stricte, et publie ses limites. Puis l'écosystème Apertus public, agrégé et anonyme.",
    selfBtn: "Voir le sceau de Sigillum",
    commTitle: "Projets Apertus publics, agrégés", commSub: "anonyme · aucun projet nommé",
    beforeAfter: "Avant / après : une équipe corrige son rapport", ethicsTitle: "Nos règles",
    ethics: ["Seulement du public", "Agrégé et anonyme", "Droit de réponse avant de nommer", "Un service offert, pas un procès", "Sigillum d'abord, sur lui-même"],
    footerTag: "Un sceau ouvert, vérifiable par tous", poweredBy: "Expliqué par Apertus, le LLM ouvert suisse", license: "Open source · Apache-2.0 · CC-BY-4.0",
    says: "Le projet dit", shows: "Les traces montrent", source: "Source", rule: "règle", apertusSrc: "Apertus",
    examined: "Examiné le", commit: "commit", expires: "expire le", seal: "sceau", files: "fichiers",
    plainTitle: "En mots simples", plainSrcAp: "Rédigé par Apertus", plainSrcConf: "Confirmé par Apertus — identique au gabarit relu", plainSrcTpl: "Gabarit relu — Apertus injoignable ou réponse rejetée",
    questionsTitle: "Les cinq réponses, avec leurs preuves",
    proof: { reproducible: "preuve reproductible", trace: "trace dans le code", declared: "simple déclaration", none: "aucune preuve" },
    kind: { trace: "trace", artifact: "artefact", declaration: "affirmation", absence: "absence" },
    fixesTitle: "Pour monter d'une lettre", noFixes: "Rien à corriger sur les cinq questions. Gardez le sceau à jour : réexaminez quand le projet change.",
    historyTitle: "Historique", embedTitle: "Intégrer ce sceau", download: "Télécharger le rapport (JSON)",
    gapsTitle: "Ce que dit le projet, et ce que montrent les traces", noGaps: "Aucune contradiction entre la documentation et les traces.",
    unknownCap: "L'inconnu est affiché comme inconnu — et plafonne la note à C.",
    weakest: "Maillon faible", notOfficial: "Instrument de transparence, pas une certification légale.",
    ethicsNote: "Projet d'exemple créé par l'équipe Sigillum.",
    running: "Examen en cours…", steps: { scan: "Lecture des fichiers", grade: "Notation sur preuves", "apertus:claims": "Apertus lit la documentation", "apertus:reconcile": "Apertus rapproche affirmations et traces", explain: "Apertus explique" },
    error: "L'examen a échoué", back: "Tous les sceaux",
    reportsTitle: "Sceaux récents", noApertus: "Apertus injoignable : note déterministe, explications par gabarit.",
    model: "modèle", endpoint: "point d'accès", calls: "appels", rejected: "réponses rejetées par les contrôles",
    excluded: "Chemins exclus par le projet (publiés, pas cachés)",
    commIntro: "Les projets de Hack Apertus deviennent publics après le 24 octobre. D'ici là, nous avons appliqué le sceau à tous les Spaces publics de Hugging Face qui utilisent Apertus. Les résultats sont agrégés : aucun projet n'est nommé sans l'accord de son équipe.",
    commProjects: "projets publics examinés", commForeignLLM: "appellent le modèle via un service étranger", commTelemetry: "embarquent une télémétrie active par défaut", commOffline: "continueraient de marcher hors ligne",
    commTop: "Dépendance étrangère la plus fréquente", commDist: "Répartition des notes",
    commMethod: "Méthode : clone superficiel de chaque Space public, analyse statique uniquement, aucune requête vers les applications en ligne, aucune donnée sur les utilisateurs.",
  },
};
let LANG = params.get("lang") || (() => { try { return localStorage.getItem("sigillum-lang"); } catch { return null; } })() || "en";
if (!UI[LANG]) LANG = "en";
const T = () => UI[LANG];
const PLAIN_LANGS = ["fr", "de", "it", "rm", "en"];
const LANG_LABEL = { fr: "Français", de: "Deutsch", it: "Italiano", rm: "Rumantsch", en: "English" };

/* ---------------------------------------------------------------- icons */
const I = {
  q1: '<rect x="6" y="6" width="12" height="12" rx="2.5"/><path d="M9.5 2.5v3.5M14.5 2.5v3.5M9.5 18v3.5M14.5 18v3.5M2.5 9.5H6M2.5 14.5H6M18 9.5h3.5M18 14.5h3.5"/><rect x="9.5" y="9.5" width="5" height="5" rx="1"/>',
  q2: '<path d="M12 15V3"/><path d="m7 7.5 5-4.5 5 4.5"/><path d="M4.5 13v6a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2v-6"/>',
  q3: '<path d="m3 3 18 18"/><path d="M8.6 16.4a5 5 0 0 1 6.3-.4"/><path d="M5 12.7a10 10 0 0 1 4.1-2.4"/><path d="M14.5 10.4A10 10 0 0 1 19 12.7"/><path d="M1.7 9.1a15 15 0 0 1 4-2.6"/><path d="M10.6 5.1A15 15 0 0 1 22.3 9.1"/><circle cx="12" cy="19.6" r="1" fill="currentColor" stroke="none"/>',
  q4: '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>',
  q5: '<circle cx="10.5" cy="10.5" r="7"/><path d="m20.5 20.5-4.9-4.9"/><path d="m7.5 10.6 2.1 2.1 3.9-4"/>',
  arrow: '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><circle cx="12" cy="7.8" r=".6" fill="currentColor"/>',
  close: '<path d="M6 6l12 12M18 6 6 18"/>',
  left: '<path d="m15 6-6 6 6 6"/>', right: '<path d="m9 6 6 6-6 6"/>',
  pause: '<path d="M9 6v12M15 6v12"/>', play: '<path d="M8 5.5v13l10-6.5z" fill="currentColor"/>',
  git: '<circle cx="6" cy="6" r="2.4"/><circle cx="6" cy="18" r="2.4"/><circle cx="18" cy="8" r="2.4"/><path d="M6 8.4v7.2"/><path d="M18 10.4c0 4-6 3.2-11 6"/>',
  folder: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/>',
  link: '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
  stamp: '<path d="M9 3h6l-1 7h-4z"/><path d="M4 14h16v3H4z"/><path d="M6 20h12"/>',
  check: '<path d="m5 12.5 4.5 4.5L19 7.5"/>',
};
const icon = (n, extra = "") => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" ${extra}>${I[n]}</svg>`;
/* Swiss cross mark: 32-unit square, arms 6 wide and 7 long beyond the centre square (arms 1/6 longer than wide). */
const CROSS = `<svg class="cross" viewBox="0 0 32 32" aria-hidden="true"><rect width="32" height="32" rx="7" fill="#FF0000"/><rect x="13" y="6" width="6" height="20" fill="#fff"/><rect x="6" y="13" width="20" height="6" fill="#fff"/></svg>`;
const LAUREL = (flip) => `<svg class="laurel" viewBox="0 0 26 52" ${flip ? 'style="transform:scaleX(-1)"' : ""} aria-hidden="true"><path d="M20 50C8 42 4 28 8 4" fill="none" stroke="currentColor" stroke-width="1.4"/>${[8, 15, 22, 29, 36, 43].map((y, i) => `<path d="M${7 + i * .6} ${y}c-5-1-7-4-6-7 4 0 6 3 6 7Z M${8 + i * .7} ${y + 2}c4-3 8-3 9 0-3 2-6 2-9 0Z" fill="currentColor"/>`).join("")}</svg>`;
const ALPS = `<svg class="alps" viewBox="0 0 686 240" preserveAspectRatio="none" aria-hidden="true">
  <path d="M0 150 L70 96 L120 128 L190 58 L250 112 L300 84 L360 140 L420 70 L470 104 L540 40 L600 100 L650 78 L686 96 V240 H0Z" fill="#da291c" fill-opacity=".07"/>
  <path d="M0 186 L90 120 L150 160 L230 100 L300 150 L380 108 L450 162 L520 118 L600 168 L686 128 V240 H0Z" fill="#da291c" fill-opacity=".1"/>
  <path d="M540 40 L556 52 L548 54 L560 66 L540 58 L528 62Z M190 58 L204 70 L196 72 L206 82 L190 74 L180 78Z" fill="#fff" fill-opacity=".9"/>
  <path d="M0 214 L120 176 L260 200 L400 170 L540 204 L686 180 V240 H0Z" fill="#da291c" fill-opacity=".13"/></svg>`;

const Q_KEYS = { 1: "q1", 2: "q2", 3: "q3", 4: "q4", 5: "q5" };
const SHORT = { en: { 1: "Model", 2: "Data", 3: "Offline", 4: "Third parties", 5: "Verifiable" },
                fr: { 1: "Modèle", 2: "Données", 3: "Hors ligne", 4: "Tiers", 5: "Vérifiable" } };
let I18N = null;
const api = (p, o) => fetch(p, o).then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); });
const qName = (q) => (I18N ? I18N.question[q][LANG] || I18N.question[q].en : "");
const fmtDate = (iso) => new Date(iso).toLocaleDateString(LANG === "fr" ? "fr-CH" : "en-GB", { day: "2-digit", month: "short", year: "numeric" });
const gradeLabel = (g) => (I18N ? I18N.grade[g][LANG] || I18N.grade[g].en : g);
const reasonText = (r) => {
  const t = (I18N.reason[r.code] || {})[LANG] || (I18N.reason[r.code] || {}).en || r.code;
  return t.replace(/\{(\w+)\}/g, (_, k) => esc(r.params?.[k] ?? ""));
};
const fixText = (f) => esc((I18N.fix[f.code] || {})[LANG] || (I18N.fix[f.code] || {}).en || f.code);
const lvlClass = (l) => (l === "unknown" ? "g-unknown" : `g-${l}`);
const lvlChar = (l) => (l === "unknown" ? "?" : l);

/* ---------------------------------------------------------- the seal */
function sealCard(r, { big = false, link = true, dim = false } = {}) {
  const levels = r.questions ? r.questions.map((q) => q.level) : r.levels;
  const scale = "ABCDE".split("").map((g) => `<span class="g-${g} ${g === r.grade ? "on" : ""}">${g}</span>`).join("");
  const pictos = levels.map((l, i) => `
    <div class="picto ${dim ? "dim" : ""}" data-i="${i}">
      <div class="disc ${lvlClass(l)}" title="${esc(qName(i + 1))}">${icon(Q_KEYS[i + 1])}<span class="lvl">${lvlChar(l)}</span></div>
      <span class="cap">${esc(SHORT[LANG][i + 1])}</span>
    </div>`).join("");
  const name = r.project ? r.project.name : r.name;
  const commit = r.project ? r.project.commit : r.commit;
  const sealId = r.seal ? r.seal.id : "";
  const inner = `
    <div class="seal-top"><span class="seal-brand">${CROSS} Sigillum</span><span class="badge">${esc(fmtDate(r.examined_at))}</span></div>
    <h3 class="seal-name">${esc(name)}</h3>
    <div class="scale" role="img" aria-label="${r.grade}: ${esc(gradeLabel(r.grade))}">${scale}</div>
    <p class="seal-verdict">${r.grade} — ${esc(gradeLabel(r.grade))}</p>
    <div class="pictos">${pictos}</div>
    ${big ? `<div class="seal-meta"><span>${T().examined} <b>${esc(fmtDate(r.examined_at))}</b></span>${commit ? `<span>${T().commit} <b>${esc(commit)}</b></span>` : ""}<span>${T().expires} <b>${esc(fmtDate(r.expires_at))}</b></span>${sealId ? `<span>${T().seal} <b>#${esc(sealId)}</b></span>` : ""}</div>` : ""}`;
  return link
    ? `<a class="seal-card ${big ? "big" : ""}" href="report.html?id=${encodeURIComponent(r.id)}&lang=${LANG}" style="text-decoration:none">${inner}</a>`
    : `<div class="seal-card ${big ? "big" : ""}">${inner}</div>`;
}
function lightUp(el, delay = 260) {
  const p = $$(".picto", el);
  p.forEach((x) => x.classList.add("dim"));
  p.forEach((x, i) => setTimeout(() => x.classList.remove("dim"), 300 + i * delay));
}

/* ---------------------------------------------------- shared chrome */
function chrome(active) {
  const t = T();
  const banner = `<div class="gov-banner"><span>${esc(t.banner)}</span><button aria-label="${esc(t.bannerInfo)}" title="${esc(t.bannerInfo)}">${icon("info", 'width="14" height="14"')}</button></div>`;
  const header = `<header class="site-header"><a class="site-home-link" href="index.html?lang=${LANG}" aria-label="Sigillum">${CROSS}<span class="wordmark">Sigillum</span></a><button class="btn btn-primary site-menu-trigger" id="menu-btn" aria-expanded="false">${t.menu}</button></header>`;
  const links = [["home", "index.html"], ["how", "index.html#how"], ["method", "method.html"], ["community", "community.html"], ["self", "report.html?project=sigillum"], ["source", "method.html#source"]];
  const menu = `<div class="menu-scrim" id="menu-scrim"></div><div class="menu-panel" role="dialog" aria-label="${t.menu}"><button class="icon-btn close" id="menu-close" aria-label="${t.close}">${icon("close")}</button><nav>${links.map(([k, h]) => `<a href="${h}${h.includes("?") ? "&" : "?"}lang=${LANG}" ${k === active ? 'aria-current="page"' : ""}>${t.nav[k]}</a>`).join("")}</nav><div class="menu-note">${CROSS}<span>${esc(t.notOfficial)}</span></div><div class="lang-switch">${["fr", "en"].map((l) => `<button data-lang="${l}" aria-pressed="${l === LANG}">${LANG_LABEL[l]}</button>`).join("")}</div></div>`;
  const footer = `<footer class="site-footer"><nav class="footer-links">${links.slice(1).map(([k, h]) => `<a href="${h}${h.includes("?") ? "&" : "?"}lang=${LANG}">${t.nav[k]}</a>`).join("")}</nav>
    <div class="footer-wordmark" aria-hidden="true">Sigillum</div>
    <div class="credits"><div class="l"><span class="seal-mini">${CROSS}</span><span>${esc(t.poweredBy)}</span></div><div class="c">${LAUREL(false)}<span>${esc(t.footerTag)}</span>${LAUREL(true)}</div><div class="r">${esc(t.license)}</div></div>
    <div class="legal"><a href="method.html?lang=${LANG}#ethics">${LANG === "fr" ? "Éthique" : "Ethics"}</a><a href="method.html?lang=${LANG}#limits">${LANG === "fr" ? "Limites publiées" : "Published limits"}</a>${["fr", "en"].map((l) => `<a href="?${new URLSearchParams({ ...Object.fromEntries(params), lang: l })}" ${l === LANG ? 'aria-current="true"' : ""}>${LANG_LABEL[l]}</a>`).join("")}</div></footer>`;
  return { banner, header, menu, footer };
}
function mountChrome(active, { headerInShell = false } = {}) {
  const c = chrome(active);
  document.documentElement.lang = LANG;
  $("#banner").innerHTML = c.banner;
  if ($("#header")) $("#header").innerHTML = c.header;
  $("#menu").innerHTML = c.menu;
  $("#footer").innerHTML = c.footer;
  const open = (v) => { document.body.classList.toggle("menu-open", v); $("#menu-btn").setAttribute("aria-expanded", v); };
  $("#menu-btn").onclick = () => open(true);
  $("#menu-close").onclick = () => open(false);
  $("#menu-scrim").onclick = () => open(false);
  document.addEventListener("keydown", (e) => e.key === "Escape" && open(false));
  $$(".lang-switch button").forEach((b) => (b.onclick = () => { try { localStorage.setItem("sigillum-lang", b.dataset.lang); } catch {} const p = new URLSearchParams(location.search); p.set("lang", b.dataset.lang); location.search = p; }));
}

/* ------------------------------------------------------------ audits */
async function runAudit(target, out) {
  const t = T();
  out.innerHTML = `<div class="panel" style="max-width:520px;margin:24px auto 0;text-align:left"><h3 class="type-heading-s">${t.running}</h3><div class="progress" id="prog"></div></div>`;
  const steps = ["scan", "grade", "apertus:claims", "apertus:reconcile", "explain"];
  const draw = (cur) => {
    const idx = steps.indexOf(cur.startsWith("apertus:explain") ? "explain" : cur);
    $("#prog").innerHTML = steps.map((s, i) => `<div class="step ${i < idx ? "done" : i === idx ? "on" : ""}"><i></i>${esc(t.steps[s])}${s === "explain" && cur.startsWith("apertus:explain") ? " · " + esc(LANG_LABEL[cur.split(":")[2]] || "") : ""}</div>`).join("");
  };
  draw("scan");
  try {
    const { job } = await api("/api/audit", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ target }) });
    for (;;) {
      await new Promise((r) => setTimeout(r, 700));
      const j = await api(`/api/jobs/${job}`);
      if (j.step) draw(j.step);
      if (j.status === "done") { location.href = `report.html?id=${encodeURIComponent(j.report)}&lang=${LANG}`; return; }
      if (j.status === "error") throw new Error(j.error);
    }
  } catch (e) {
    out.innerHTML = `<div class="notice" style="max-width:520px;margin:24px auto 0">${esc(t.error)} — ${esc(e.message)}</div>`;
  }
}

/* ------------------------------------------------------------- home */
async function pageHome() {
  mountChrome("home");
  const t = T();
  const [reports] = await Promise.all([api("/api/reports").catch(() => [])]);
  const byName = (n) => reports.find((r) => r.name === n);
  $("#hero-title").textContent = t.heroTitle;
  $("#hero-lead").textContent = t.heroLead;
  const input = $("#ask-input");
  input.placeholder = t.askPlaceholder;
  $("#ask-send").setAttribute("aria-label", t.examineBtn);
  const samples = ["municipal-assistant", "town-hall-chat", "civicgpt", "school-assistant"];
  $("#examples").innerHTML = `<span class="type-label muted" style="align-self:center">${t.try}</span>` + samples.map((s) => `<button class="chip" data-t="${s === "school-assistant" ? "school-assistant-v1" : s}">${s}</button>`).join("");
  $$("#examples .chip").forEach((c) => (c.onclick = () => { input.value = c.dataset.t; input.focus(); }));
  $("#ask").onsubmit = (e) => { e.preventDefault(); if (input.value.trim()) runAudit(input.value.trim(), $("#ask-out")); };

  // carousel of real seals
  const deck = ["municipal-assistant", "town-hall-chat", "civicgpt", "school-assistant"].map(byName).filter(Boolean);
  let k = 0, playing = true, timer;
  const show = () => {
    if (!deck.length) return;
    $("#stage-card").innerHTML = sealCard(deck[k % deck.length]);
    if (!$("#stage .alps")) $("#stage").insertAdjacentHTML("afterbegin", ALPS);
    lightUp($("#stage-card"));
  };
  const next = (d = 1) => { k = (k + d + deck.length) % deck.length; show(); };
  const loop = () => { clearInterval(timer); if (playing) timer = setInterval(() => next(1), 5200); };
  $("#c-prev").onclick = () => { next(-1); loop(); };
  $("#c-next").onclick = () => { next(1); loop(); };
  $("#c-play").onclick = () => { playing = !playing; $("#c-play").innerHTML = icon(playing ? "pause" : "play"); loop(); };
  show(); loop();

  // manifesto
  $("#manifesto").innerHTML = t.manifesto({
    five: `<span class="inline-seals" aria-hidden="true">${["A", "B", "C", "D", "E"].map((g) => `<span class="g-${g}">${g}</span>`).join("")}</span>`,
    proof: `<span class="inline-pill red" aria-hidden="true">${icon("q5")}</span>`,
    unknown: `<span class="inline-pill q" aria-hidden="true">?</span>`,
  });
  $("#mini-input").placeholder = t.miniAsk;
  $("#mini").onsubmit = (e) => { e.preventDefault(); const v = $("#mini-input").value.trim(); if (v) { scrollTo({ top: 0, behavior: "smooth" }); input.value = v; runAudit(v, $("#ask-out")); } };

  // features
  const ex = byName("school-assistant") || reports[0];
  const self = byName("sigillum");
  const f = [
    ["f1", `<div class="stars"></div>${ex ? sealCard({ ...ex }, { link: false }).replace('class="seal-card', 'style="transform:scale(.72)" class="seal-card') : ""}`, "media-ink", ex ? `report.html?id=${ex.id}` : "#"],
    ["f2", `<div class="disc-xl" style="font:700 56px/1 var(--font-body);border:3px dashed var(--color-ink-900-45);background:#fff;box-shadow:none">?</div>`, "media-snow", "method.html#proof"],
    ["f3", `<div style="display:flex;gap:10px">${["A", "A", "A", "A", "E"].map((g, i) => `<div class="lvl-chip g-${g}" style="width:54px;height:54px;font-size:1.5rem;${i === 4 ? "background:#fff;color:var(--color-red-600);box-shadow:0 0 0 3px #fff" : "background:#ffffff33;color:#fff"}">${g}</div>`).join("")}</div>`, "media-red", "method.html#weakest"],
    ["f4", `<div class="disc-xl" style="width:auto;height:auto;border-radius:22px;padding:20px 24px;display:grid;gap:6px;text-align:left;background:#fff;box-shadow:var(--shadow-elevation-1)"><span class="type-eyebrow">${T().seal} #${self ? esc(self.id.slice(-6)) : "9f2c1a"}</span><span style="font:500 22px/1.1 var(--font-body);letter-spacing:-.04em">${self ? esc(fmtDate(self.examined_at)) : ""} → ${self ? esc(fmtDate(self.expires_at)) : ""}</span><span class="mono muted">sha256 · ${self ? esc((self.commit || "").slice(0, 7)) || "—" : "—"}</span></div>`, "media-paper", "method.html#dated"],
  ];
  $("#features").innerHTML = f.map(([key, media, cls, href]) => `
    <div class="feature"><div class="feature-media ${cls}">${media}</div>
    <div class="feature-copy"><h2 class="type-feature">${esc(t[key + "t"])}</h2><p class="type-body-l">${esc(t[key + "b"])}</p><a class="text-link" href="${href}${href.includes("?") ? "&" : "?"}lang=${LANG}">${esc(t[key + "l"])}</a></div></div>`).join("");

  // five questions
  $("#q-title").textContent = t.qTitle;
  $("#q-lead").textContent = t.qLead;
  $("#q-grid").innerHTML = [1, 2, 3, 4, 5].map((q) => `<div class="q-card"><div class="disc">${icon(Q_KEYS[q])}</div><h3>${esc(qName(q))}</h3><ul><li><i class="g-A">A</i><span>${esc(t.qa[q][0])}</span></li><li><i class="g-E">E</i><span>${esc(t.qa[q][1])}</span></li><li><i class="g-unknown">?</i><span>${esc(I18N.unknown[LANG])}</span></li></ul></div>`).join("");

  // Apertus section — a real gap from a real report
  $("#ap-title").textContent = t.apTitle;
  $("#ap-body").textContent = t.apBody;
  const gapRep = reports.find((r) => r.gaps > 0 && r.name === "school-assistant") || reports.find((r) => r.gaps > 0);
  if (gapRep) {
    const full = await api(`/api/reports/${gapRep.id}`);
    const g = full.gaps.find((x) => x.source === "apertus") || full.gaps[0];
    if (g) $("#ap-gap").innerHTML = gapCard(full, g);
    $("#ap-link").innerHTML = `<a class="text-link" href="report.html?id=${gapRep.id}&lang=${LANG}#gaps">${esc(t.apLink)} ${icon("arrow", 'width="16" height="16"')}</a>`;
  }
  const langRep = byName("civicgpt") || ex;
  if (langRep) {
    const full = await api(`/api/reports/${langRep.id}`);
    const ln = full.explanations.rm || full.explanations.de;
    if (ln) $("#ap-lines").innerHTML = ["de", "fr", "it", "rm"].map((l) => full.explanations[l] ? `<div class="card" style="padding:16px 18px;gap:6px"><span class="type-eyebrow">${LANG_LABEL[l]} ${full.explanations[l].source.startsWith("apertus") ? "· Apertus ✓" : ""}</span><span style="font-size:.95rem;letter-spacing:-.02em">${esc(full.explanations[l].lines[1].text)}</span></div>` : "").join("");
  }

  // ourselves first + community
  $("#self-title").textContent = t.selfTitle;
  $("#self-lead").textContent = t.selfLead;
  $("#self-btn").textContent = t.selfBtn;
  $("#self-btn").href = self ? `report.html?id=${self.id}&lang=${LANG}` : "#";
  const comm = await api("/api/community").catch(() => ({}));
  const v1 = reports.filter((r) => r.name === "school-assistant").sort((a, b) => a.examined_at.localeCompare(b.examined_at));
  $("#collage").innerHTML = `
    <div style="display:grid;gap:20px">${self ? sealCard(self) : ""}
      <div class="card"><h4>${esc(t.ethicsTitle)}</h4><ul class="reasons" style="gap:8px">${t.ethics.map((e) => `<li style="font-size:.9rem"><i class="g-A">${icon("check", 'width="14" height="14"')}</i><span>${esc(e)}</span></li>`).join("")}</ul></div></div>
    <div style="display:grid;gap:20px;margin-top:56px">${commCard(comm)}</div>
    <div style="display:grid;gap:20px">
      ${v1.length > 1 ? `<div class="card"><h4>${esc(t.beforeAfter)}</h4><div class="timeline">${v1.map((r, i) => `${i ? `<span class="arrow">${icon("arrow", 'width="22" height="22"')}</span>` : ""}<a href="report.html?id=${r.id}&lang=${LANG}"><span class="lvl-chip g-${r.grade}">${r.grade}</span>${i === 0 ? "v1" : "v" + (i + 1)}</a>`).join("")}</div><p class="type-body" style="font-size:.875rem">${LANG === "fr" ? "Télémétrie Streamlit coupée, CDN retiré, Apertus servi sur le serveur de l'école." : "Streamlit telemetry off, CDN removed, Apertus served on the school's server."}</p></div>` : ""}
      ${byName("civicgpt") ? sealCard(byName("civicgpt")) : ""}</div>`;
}

function commCard(c) {
  const t = T();
  if (!c || !c.count) return "";
  const max = Math.max(...Object.values(c.grades));
  return `<a class="card" href="community.html?lang=${LANG}" style="text-decoration:none"><span class="type-eyebrow">${esc(t.commSub)}</span><h3 style="font-size:1.1rem">${esc(t.commTitle)}</h3>
    <div style="display:flex;align-items:baseline;gap:10px"><span class="stat">${c.count}</span><span class="type-body">${esc(t.commProjects)}</span></div>
    <div class="bars">${"ABCDE".split("").map((g) => `<div class="bar"><i class="g-${g}">${g}</i><div class="track"><div class="fill" style="width:${max ? (100 * c.grades[g]) / max : 0}%;background:var(--grade-${g.toLowerCase()})"></div></div><span>${c.grades[g]}</span></div>`).join("")}</div>
    <div class="type-body" style="font-size:.875rem"><b style="color:var(--color-ink-900)">${c.pct.foreign_llm}%</b> ${esc(t.commForeignLLM)} · <b style="color:var(--color-ink-900)">${c.pct.telemetry_on}%</b> ${esc(t.commTelemetry)}</div></a>`;
}

function gapCard(rep, g) {
  const t = T();
  const ev = Object.fromEntries(rep.evidence.map((e) => [e.id, e]));
  const claim = g.source === "apertus" ? (rep.claims.apertus.find((c) => c.id === g.claim) || {}).quote : (ev[g.claim] || {}).snippet;
  const claimSrc = g.source === "apertus" ? "README" : `${(ev[g.claim] || {}).file}:${(ev[g.claim] || {}).line}`;
  const traces = g.evidence.map((id) => ev[id]).filter(Boolean);
  const shows = g.shows ? esc(g.shows) : traces.map((e) => e.host ? `${esc(e.host)} → ${esc(e.operator)}` : esc(e.detail)).join("<br>");
  return `<div class="gap"><div class="says"><span class="k">${esc(t.says)}</span><blockquote>“${esc((claim || "").replace(/^#+\s*/, ""))}”</blockquote><span class="src">${esc(claimSrc)}</span></div>
    <div class="shows"><span class="k">${esc(t.shows)}</span><span class="trace">${shows}</span>${traces.map((e) => `<span class="src">${e.host ? `<span class="jur ${esc(e.jurisdiction)}">${esc(e.jurisdiction)}</span> ${esc(e.host)} · ` : `${esc(e.detail || e.signal)} · `}${esc(e.file || "")}${e.line ? ":" + e.line : ""}</span>`).join("")}</div>
    <div class="gap-foot"><span class="badge ${g.source === "apertus" ? "apertus" : ""}">${g.source === "apertus" ? "Apertus" : t.rule}</span>${g.evidence.map((id) => `<a class="ev" href="report.html?id=${rep.id}&lang=${LANG}#${id}">${id}</a>`).join("")}</div></div>`;
}

/* ----------------------------------------------------------- report */
async function pageReport() {
  mountChrome(params.get("project") === "sigillum" ? "self" : "");
  const t = T();
  let id = params.get("id");
  const list = await api("/api/reports").catch(() => []);
  if (!id && params.get("project")) id = (list.find((r) => r.name === params.get("project")) || {}).id;
  if (!id) { $("#report").innerHTML = reportList(list); return; }
  const r = await api(`/api/reports/${id}`);
  document.title = `${r.project.name} · ${r.grade} — Sigillum`;
  const ev = Object.fromEntries(r.evidence.map((e) => [e.id, e]));
  const history = list.filter((x) => x.name === r.project.name).sort((a, b) => a.examined_at.localeCompare(b.examined_at));
  const isSample = /^(municipal-assistant|town-hall-chat|civicgpt|school-assistant)$/.test(r.project.name);
  const evChips = (ids) => ids.map((x) => `<a class="ev" href="#${x}">${x}</a>`).join("");

  const plainTabs = PLAIN_LANGS.filter((l) => r.explanations[l]);
  const firstTab = plainTabs.includes(LANG) ? LANG : plainTabs[0];
  const plain = (l) => {
    const x = r.explanations[l];
    return `<ul class="plain">${x.lines.map((ln) => { const lvl = r.questions[ln.q - 1].level; return `<li><span class="disc ${lvlClass(lvl)}">${icon(Q_KEYS[ln.q])}</span><div><p>${esc(ln.text)}</p><div class="evs">${evChips(ln.evidence)}</div></div></li>`; }).join("")}</ul>
      <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center"><span class="badge ${x.source.startsWith("apertus") ? "apertus" : ""}">${x.source === "apertus" ? `${esc(t.plainSrcAp)} · ${esc(r.apertus.model || "")}` : x.source === "apertus-confirmed" ? `${esc(t.plainSrcConf)} · ${esc(r.apertus.model || "")}` : esc(t.plainSrcTpl)}</span>${l === "rm" && x.source !== "apertus" ? '<span class="type-label muted">RM: Rumantsch Grischun</span>' : ""}</div>`;
  };
  const qsec = (q) => `
    <section class="qsec" id="q${q.q}"><div class="qhead"><div class="row"><span class="lvl-chip ${lvlClass(q.level)}">${lvlChar(q.level)}</span>${r.weakest.includes(q.q) && r.grade !== "A" ? `<span class="badge red">${esc(t.weakest)}</span>` : ""}</div><h3>${q.q}. ${esc(qName(q.q))}</h3><div class="row"><span class="badge"><span class="dot"></span>${esc(t.proof[q.proof])}</span></div></div>
      <div><ul class="reasons">${q.reasons.map((x) => `<li><i class="${lvlClass(x.level)}">${lvlChar(x.level)}</i><span>${reasonText(x)} ${evChips(x.evidence)}</span></li>`).join("")}</ul>
      <table class="ev-table">${r.evidence.filter((e) => e.q === q.q).map((e) => `<tr id="${e.id}"><td><span class="ev">${e.id}</span></td><td><div class="ev-kind">${esc(t.kind[e.kind] || e.kind)} · ${esc(e.signal)}</div>${e.host ? `<div style="margin:4px 0"><span class="jur ${esc(e.jurisdiction)}">${esc(e.jurisdiction)}</span> <b>${esc(e.host)}</b> — ${esc(e.operator || "")}</div>` : ""}${e.detail && !e.host ? `<div style="margin:4px 0">${esc(e.detail)}</div>` : e.detail ? `<div class="muted">${esc(e.detail)}</div>` : ""}${e.snippet ? `<code>${esc(e.snippet)}</code>` : ""}<div class="muted mono" style="margin-top:4px">${esc(e.file || "")}${e.line ? ":" + e.line : ""}</div></td></tr>`).join("")}</table></div></section>`;

  const ap = r.apertus || {};
  $("#report").innerHTML = `
    <div class="report-top">
      <div id="seal-wrap">${sealCard(r, { big: true, link: false })}</div>
      <div class="report-side">
        <span class="type-eyebrow">${isSample ? esc(t.ethicsNote) : esc(t.notOfficial)}</span>
        <h1 class="type-heading-l">${r.grade} — ${esc(gradeLabel(r.grade))}</h1>
        <p class="type-lead">${r.weakest.map((q) => esc(qName(q))).join(" · ")}${r.unknown.length ? ` — ${esc(t.unknownCap)}` : ""}</p>
        <div class="panel soft"><div style="display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;align-items:center"><h2 class="type-heading-s">${esc(t.plainTitle)}</h2><div class="tabs" role="tablist">${plainTabs.map((l) => `<button role="tab" data-l="${l}" aria-selected="${l === firstTab}">${l.toUpperCase()}</button>`).join("")}</div></div><div id="plain">${plain(firstTab)}</div></div>
        ${ap.used ? `<div class="type-label muted" style="line-height:1.6">Apertus · ${esc(t.model)} <b>${esc(ap.model)}</b> · ${esc(t.endpoint)} <span class="jur ${esc(ap.endpoint?.jurisdiction)}">${esc(ap.endpoint?.jurisdiction)}</span> ${esc(ap.endpoint?.host)} · ${ap.calls} ${esc(t.calls)} · ${ap.answers_rejected_by_checks} ${esc(t.rejected)}</div>` : `<div class="notice">${esc(t.noApertus)}</div>`}
      </div>
    </div>
    <section style="margin-top:96px" id="gaps"><h2 class="type-heading-m" style="margin-bottom:28px">${esc(t.gapsTitle)}</h2>${r.gaps.length ? `<div style="display:grid;gap:16px">${r.gaps.map((g) => gapCard(r, g)).join("")}</div>` : `<p class="type-body-l">${esc(t.noGaps)}</p>`}</section>
    <section style="margin-top:96px"><h2 class="type-heading-m" style="margin-bottom:12px">${esc(t.questionsTitle)}</h2>${r.questions.map(qsec).join("")}</section>
    ${r.project.excluded?.length ? `<div class="notice"><b>${esc(t.excluded)}</b><br>${r.project.excluded.map((x) => `<code class="mono">${esc(x.pattern)}</code> — ${esc(x.reason)}`).join("<br>")}</div>` : ""}
    <section style="margin-top:72px;display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px">
      <div class="panel soft"><h2 class="type-heading-s">${esc(t.fixesTitle)}</h2>${r.fixes.length ? `<ol class="fixes">${r.fixes.map((f) => `<li><span>${fixText(f)} <span class="type-label muted">Q${f.q}</span> ${evChips(f.evidence)}</span></li>`).join("")}</ol>` : `<p class="type-body">${esc(t.noFixes)}</p>`}</div>
      <div class="panel"><h2 class="type-heading-s">${esc(t.historyTitle)}</h2><div class="timeline">${history.map((h, i) => `${i ? `<span class="arrow">${icon("arrow", 'width="20" height="20"')}</span>` : ""}<a href="report.html?id=${h.id}&lang=${LANG}"><span class="lvl-chip g-${h.grade}" ${h.id === r.id ? 'style="box-shadow:0 0 0 3px #fff,0 0 0 5px var(--color-ink-900)"' : ""}>${h.grade}</span>${esc(fmtDate(h.examined_at))}</a>`).join("")}</div>
        <h2 class="type-heading-s" style="margin-top:12px">${esc(t.embedTitle)}</h2><img src="/api/badge/${r.id}.svg" alt="Sigillum ${r.grade}" width="236" height="40"><div class="code-snippet">![Sigillum ${r.grade}](/api/badge/${esc(r.id)}.svg)</div>
        <div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn btn-soft" href="/api/reports/${r.id}" download="${r.id}.json">${esc(t.download)}</a></div>
        <div class="type-label muted mono" style="line-height:1.5;overflow-wrap:anywhere">sha256 ${esc(r.seal.sha256)}<br>Sigillum ${esc(r.sigillum.version)} · method ${esc(r.sigillum.method)} · registry ${esc(r.sigillum.registry)} · ${r.project.code_files} ${esc(t.files)}</div></div>
    </section>`;
  $$(".tabs button").forEach((b) => (b.onclick = () => { $$(".tabs button").forEach((x) => x.setAttribute("aria-selected", x === b)); $("#plain").innerHTML = plain(b.dataset.l); }));
  lightUp($("#seal-wrap"), 320);
  if (location.hash) setTimeout(() => document.getElementById(location.hash.slice(1))?.scrollIntoView({ behavior: "smooth", block: "center" }), 400);
}
function reportList(list) {
  return `<h1 class="type-heading-l" style="margin:48px 0 32px">${esc(T().reportsTitle)}</h1><div class="list-grid">${list.map((r) => sealCard(r)).join("")}</div>`;
}

/* -------------------------------------------------------- community */
async function pageCommunity() {
  mountChrome("community");
  const t = T();
  const [c, list] = await Promise.all([api("/api/community").catch(() => ({})), api("/api/reports").catch(() => [])]);
  const self = list.find((r) => r.name === "sigillum");
  const max = c.count ? Math.max(...Object.values(c.grades)) : 1;
  $("#community").innerHTML = `
    <div class="big-center" style="padding-top:56px"><span class="type-eyebrow">${esc(t.commSub)}</span><h1 class="type-heading-l">${esc(t.nav.community)}</h1><p class="type-lead">${esc(t.commIntro)}</p></div>
    ${c.count ? `<div class="collage" style="grid-template-columns:repeat(auto-fit,minmax(280px,1fr))">
      <div class="card"><span class="type-eyebrow">1 · ${esc(t.nav.self)}</span>${self ? sealCard(self).replace('class="seal-card', 'style="box-shadow:none;padding:0" class="seal-card') : ""}</div>
      <div class="card"><span class="stat">${c.count}</span><span class="type-body">${esc(t.commProjects)}</span><h4 style="margin-top:8px">${esc(t.commDist)}</h4><div class="bars">${"ABCDE".split("").map((g) => `<div class="bar"><i class="g-${g}">${g}</i><div class="track"><div class="fill" style="width:${(100 * c.grades[g]) / max}%;background:var(--grade-${g.toLowerCase()})"></div></div><span>${c.grades[g]}</span></div>`).join("")}</div></div>
      <div class="card">${[["foreign_llm", t.commForeignLLM], ["telemetry_on", t.commTelemetry], ["offline", t.commOffline]].map(([k, l]) => `<div style="display:grid;gap:2px;border-bottom:1px solid var(--color-border-quaternary);padding-bottom:12px"><span class="stat" style="font-size:2.75rem">${c.pct[k]}%</span><span class="type-body">${esc(l)}</span></div>`).join("")}<div><h4>${esc(t.commTop)}</h4><p class="type-body-l" style="color:var(--color-ink-900)">${esc(c.top_foreign?.[0]?.operator || "—")} <span class="muted">· ${c.top_foreign?.[0]?.count || 0}/${c.count}</span></p></div></div>
    </div>
    <div class="panel soft" style="margin-top:32px"><h2 class="type-heading-s">${LANG === "fr" ? "Par question" : "Per question"}</h2><div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:18px">${[1, 2, 3, 4, 5].map((q) => `<div style="display:grid;gap:8px"><div style="display:flex;gap:8px;align-items:center"><span class="lvl-chip g-A" style="width:32px;height:32px;border-radius:999px">${icon(Q_KEYS[q], 'width="16" height="16"')}</span><b style="font-size:.9rem;letter-spacing:-.02em">${esc(qName(q))}</b></div><div class="bars">${["A", "B", "C", "D", "E", "unknown"].map((g) => `<div class="bar" style="grid-template-columns:18px 1fr 22px"><i class="${lvlClass(g)}" style="width:18px;height:18px;font-size:.6rem">${lvlChar(g)}</i><div class="track" style="height:7px"><div class="fill" style="width:${(100 * (c.per_question[q][g] || 0)) / c.count}%;background:${g === "unknown" ? "var(--color-ink-900-45)" : `var(--grade-${g.toLowerCase()})`}"></div></div><span style="font-size:.7rem">${c.per_question[q][g] || 0}</span></div>`).join("")}</div></div>`).join("")}</div></div>
    <p class="notice" style="margin-top:24px">${esc(t.commMethod)} ${esc(c.generated_at ? fmtDate(c.generated_at) : "")} · Sigillum ${esc(c.sigillum || "")}</p>` : ""}`;
}

/* ----------------------------------------------------------- method */
function pageMethod() {
  mountChrome("method");
  $$("[data-lang-block]").forEach((el) => (el.hidden = el.dataset.langBlock !== (LANG === "fr" ? "fr" : "en")));
}

/* -------------------------------------------------------------- boot */
(async () => {
  I18N = await api("/api/i18n").catch(() => null);
  const page = document.body.dataset.page;
  ({ home: pageHome, report: pageReport, community: pageCommunity, method: pageMethod }[page] || (() => {}))();
})();

// The page script. build.py inlines this file and replaces the data marker below.
// Sections: helpers, card parts, cards, search, render, controls, links.
const DATA = __DATA__;

// ---------- helpers ----------
const SC = {Archery:'c', Block:'c', 'Heavy Armor':'c', 'One-Handed':'c', Smithing:'c', 'Two-Handed':'c',
  Alteration:'m', Conjuration:'m', Destruction:'m', Enchanting:'m', Illusion:'m', Restoration:'m',
  Alchemy:'s', 'Light Armor':'s', Lockpicking:'s', Pickpocket:'s', Sneak:'s', Speech:'s'};
const REQ = {DG:'Dawnguard', HF:'Hearthfire', DB:'Dragonborn', CC:'a paid Creation', AE:'Anniversary Edition'};
const SCHOOLS = {c:'Combat', m:'Magic', s:'Stealth', k:'Craft'};
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;'}[c]));
const plural = (n, word) => `${n} ${word}${n === 1 ? '' : 's'}`;
const tagEv = ev => ev === 'derived' ? '<span class="sug">suggested</span>'
  : ev === 'partly-sourced' ? '<span class="sug">partly sourced</span>' : '';
const reqTag = r => `<span class="req" title="Needs ${esc(REQ[r] || r)}">${esc(r)}</span>`;
const gtag = t => t ? ` <b>${esc(t)}</b>` : '';

// A skill pill, colored by school.
const pill = (s, w, showW) => `<span class="pill sc-${SC[s]}"><i></i>${esc(s)}${showW ? ` <b>${w}</b>` : ''}</span>`;
// A pill that explains itself: hover shows the tip, and a tap, click or Enter prints it under the row,
// so phones and keyboards get it too. `inner` is trusted HTML; `cls` adds classes.
const tipPill = (inner, tip, cls = '') => tip
  ? `<button type="button" class="pill tip ${cls}" data-tip="${esc(tip)}" title="${esc(tip)}" aria-expanded="false">${inner}</button>`
  : `<span class="pill ${cls}">${inner}</span>`;
const tier = (label, skills) => skills.length
  ? `<div class="tier"><span>${label}</span><div class="sk">${skills.map(x => pill(x.s, x.w, true)).join('')}</div></div>` : '';
const pick = (label, inner) => `<div class="tier pick"><span>${label}</span><div class="sk">${inner}</div></div>`;

function bar(a) {
  const total = a[0] + a[1] + a[2] || 1;
  const part = (cls, i) => a[i] ? `<span class="${cls}" style="width:${a[i] / total * 100}%"></span>` : '';
  return `<div class="bar" role="img" aria-label="Health ${a[0]}, Magicka ${a[1]}, Stamina ${a[2]}">${part('hp', 0)}${part('mp', 1)}${part('spb', 2)}</div>`;
}
function lv(a) {
  const part = (cls, name, n) => n ? `<span class="${cls}">${name} ×${n}</span>` : '';
  return `<div class="lv"><span class="lab">Level 50</span>${part('h', 'Health', a[0])}${part('m', 'Magicka', a[1])}${part('s', 'Stamina', a[2])}</div>`;
}

const fams = [{id:'all', title:'All'}, ...DATA.fams, {id:'race', title:'Pure races'}, {id:'mods', title:'Challenge runs'}];
let st = {f:'all', q:'', style:'', base:false};
// Phones fold Gear, Race and In play behind one line, so a card stays short; wider screens show them open.
const PHONE = matchMedia('(max-width:640px)');

// ---------- card parts ----------
// Perks: grouped by skill, each chip colored by school. The tip names the NPCs who take it.
const perkHead = g => `<span class="pgs sc-${g.sc}"><i></i>${esc(g.s)}</span>`;
function perkGroups(groups) {
  const chip = p => tipPill(esc(p.n) + (p.by.length > 1 ? ` <b>×${p.by.length}</b>` : ''),
    p.by.length ? `Taken by ${p.by.join(', ')}` : '', 'pk');
  return groups.map(g => `<div class="pg">${perkHead(g)}${g.perks.map(chip).join('')}</div>`).join('');
}
function treeBlock(b) {
  if (!b.tree.length) return '';
  const chip = p => tipPill(`${esc(p.n)} <b>${p.lvl}</b>`, p.fx, 'pk');
  return `<div class="pg tree-h"><span class="psrc">Early perks from the skill tree (UESP), with the skill level each needs:</span></div>`
    + b.tree.map(g => `<div class="pg">${perkHead(g)}${g.perks.map(chip).join('')}</div>`).join('');
}
function perkBlock(b) {
  const wrap = inner => `<div class="perks"><div class="plab">Perks</div>${inner}</div>`;
  if (b.perks.length) {
    const src = b.hand ? `<div class="psrc">Named by community sources (ledger ${esc(b.perk_ref)}). <span class="sug">partly sourced</span></div>` : '';
    return wrap(perkGroups(b.perks) + src + treeBlock(b));
  }
  if (b.tree.length) return wrap(treeBlock(b));
  const none = b.hand ? 'The community sources name no perks for this build.' : 'No NPC of this class has perks listed on UESP.';
  return wrap(`<div class="psrc">${none}</div>`);
}

// Gear: signature sets (sourced, DLC/CC tagged), then the loadout (suggested). "As worn by" sits under More.
function gearLine(b) {
  const g = b.gear;
  const sig = g.sig.map(x => tipPill(esc(x.n) + gtag(x.tag), x.cc ? `Creation: ${x.cc}` : '', 'gsig')).join('');
  const loadout = [g.armor, ...g.hands].map(x => `<span class="pill">${esc(x)}</span>`).join('');
  return `<div class="tier gear"><span>Gear</span><div class="sk">${sig}${loadout}<span class="sug">suggested</span></div></div>`;
}
function wornBlock(b) {
  if (!b.gear.worn.length) return '';
  const item = i => esc(i.n) + (i.tag ? ` <span class="req">${esc(i.tag)}</span>` : '');
  const rows = b.gear.worn.map(w => `<div><b>${esc(w.npc)}</b>: ${w.items.map(item).join(', ')}</div>`).join('');
  return `<div class="worn"><div class="plab">As worn by</div>${rows}<div class="psrc">From their UESP pages. Not a full inventory.</div></div>`;
}
// Gear kits: requirement tags come from UESP (CC plus the Creation's name, or DLC).
function kitBlock(b, kits) {
  const kit = k => `<div class="kit"><div class="khead"><b>${esc(k.n)}</b>${k.dlc.map(reqTag).join('')}`
    + k.cc.map(c => `<span class="cc" title="A paid Creation, included in Anniversary Edition">CC: ${esc(c)}</span>`).join('')
    + `${tagEv(k.ev)}</div><span class="knote">${esc(k.note)}</span>`
    + (k.cc.length && k.base.length ? `<span class="knote">Base game: ${k.base.map(esc).join(', ')}.</span>` : '') + '</div>';
  const runs = b.mods.length
    ? `<div class="chal">Challenge runs that suit it: ${b.mods.map(m => `<button type="button" class="pair" data-mod="${esc(m)}">${esc(m)}</button>`).join(' ')}</div>` : '';
  return (kits.length ? `<div class="perks"><div class="plab">Gear kits</div>${kits.map(kit).join('')}</div>` : '') + runs;
}

function raceWhy(races) {
  const common = races[0].boosts.filter(s => races.every(r => r.boosts.includes(s)));
  if (common.length) return (races.length > 1 ? 'Both boost ' : 'Boosts ') + common.join(' and ') + '.';
  return races.map(r => r.race + ': ' + r.boosts.slice(0, 2).join(', ')).join('; ') + '.';
}
function raceLine(b) {
  if (!b.races.length) return '';
  const chip = r => `<button type="button" class="pair rc" data-build="${esc(r.race)}" title="Show ${esc(r.race)}. Boosts ${esc(r.boosts.join(', '))}">${esc(r.race)}</button>`;
  return `<div class="tier race"><span>Race</span><div class="sk">${b.races.map(chip).join('')}<span class="rwhy">${esc(raceWhy(b.races))}</span></div></div>`;
}

function cardHead(b) {
  const link = `<a class="lnk" href="#${esc(b.id)}" data-id="${esc(b.id)}" aria-label="Copy a link to ${esc(b.name)}" title="Copy a link to this build">Link</a>`;
  const aka = b.aka.length ? `<div class="aka">Also known as <b>${b.aka.map(esc).join('</b>, <b>')}</b></div>` : '';
  const npcs = b.npcs.length ? `<div class="npcs">Examples: <b>${b.npcs.map(esc).join('</b>, <b>')}</b></div>` : '';
  return `<div><div class="ttl"><h3>${esc(b.name)}</h3>${b.req.map(reqTag).join('')}${link}</div>${aka}<div class="insp">Inspired by: ${esc(b.insp)}</div>${npcs}</div>`;
}
// Gear, Race and In play: open on wide screens, during a search and from a link; folded on phones.
function fitBlock(b, open) {
  const play = b.play ? `<div class="play"><b>In play</b> ${esc(b.play)} <span class="sug">suggested</span></div>` : '';
  const isOpen = !PHONE.matches || open || st.q.trim();
  const label = b.play ? 'Gear, race and how to play it' : 'Gear and race';
  return `<details class="fit"${isOpen ? ' open' : ''}><summary>${label}</summary><div class="fitbody">${gearLine(b)}${raceLine(b)}${play}</div></details>`;
}
function attrBlock(b) {
  const why = b.why ? `<div class="why">NPC weights H ${b.npc[0]} · M ${b.npc[1]} · S ${b.npc[2]}. ${esc(b.why)}</div>` : '';
  return `<div class="attr">${bar(b.plan)}${lv(b.lv50)}${why}</div>`;
}
function picksBlock(b) {
  const s = b.stone;
  const stone = tipPill(esc(s.early), s.early_fx)
    + (s.final ? `<span class="arrow" aria-label="then">→</span>${tipPill(esc(s.final), s.final_fx)}` : '');
  const shouts = b.shouts.list.map(x => tipPill(esc(x.n) + (x.req !== 'vanilla' ? ` <b>${esc(x.req)}</b>` : ''), x.fx)).join('');
  const beast = b.beast ? pick('Beast form', `<span class="pill">${esc(b.beast)}</span>`) : '';
  const book = b.book ? pick('Black Book', tipPill(`${esc(b.book.book)}: ${esc(b.book.power)} <b>DB</b>`, b.book.fx) + tagEv(b.book.ev)) : '';
  return `<div class="tiers">${pick('Stone', stone + tagEv(s.ev))}${pick('Shouts', shouts + tagEv(b.shouts.ev))}${beast}${book}</div>`;
}
function variantRow(v) {
  const npcs = v.npcs.length ? `<span>Examples: ${v.npcs.map(esc).join(', ')}</span><br>` : '';
  const wears = v.sig.length ? `<span class="vperks">Wears: ${v.sig.map(i => esc(i.n) + gtag(i.tag)).join(', ')}</span>` : '';
  const perks = v.perks.length ? `<span class="vperks">Perks: ${v.perks.map(g => g.perks.map(p => esc(p.n)).join(', ')).join(' · ')}</span>` : '';
  return `<div class="v"><b>${esc(v.label)}</b>${npcs}<span>${esc(v.skills)} · H ${v.attr[0]} M ${v.attr[1]} S ${v.attr[2]}</span>${wears}${perks}</div>`;
}
function loreRow(x) {
  const wears = x.sig.length ? `<span class="vperks">Wears: ${x.sig.map(i => esc(i.n) + (i.tag ? ` (${esc(i.tag)})` : '')).join(', ')}</span>` : '';
  const where = x.where ? `<span class="where">In the game, ${esc(x.npc)} uses a class from the ${esc(x.where)} build.</span>` : '';
  return `<div class="v"><b>${esc(x.n)}</b>${x.req.map(r => ' ' + reqTag(r)).join('')} ${tagEv(x.ev)}<span class="chg">${esc(x.changes)}</span>${wears}${where}<span class="ref">Ledger ${esc(x.ref)}</span></div>`;
}
// "More": stone, shouts, perks, gear, variants and lore. "Base game only" hides kits and picks that need more.
function moreBlock(b, open) {
  const lore = b.lore.filter(x => !st.base || !x.req.length);
  const kits = b.kits.filter(k => !st.base || (!k.cc.length && !k.dlc.length));
  const parts = ['stone', 'shouts', b.perks.length ? 'perks' : '', kits.length ? 'gear' : '',
    b.variants.length ? plural(b.variants.length, 'variant') : '', lore.length ? plural(lore.length, 'lore pick') : ''].filter(Boolean);
  const label = parts.length > 2 ? parts.slice(0, -1).join(', ') + ' and ' + parts.at(-1) : parts.join(' and ');
  const variants = b.variants.length ? `<div class="vhead">Variants</div><div class="vlist">${b.variants.map(variantRow).join('')}</div>` : '';
  const lores = lore.length ? `<div class="vhead">Lore and community picks</div><div class="vlist">${lore.map(loreRow).join('')}</div>` : '';
  const source = b.hand ? `<div class="eid note">No class file. Weights set by hand from ledger ${esc(b.ref)}.</div>`
    : `<div class="eid">${b.eids.concat(...b.variants.map(v => v.eids)).map(esc).join(', ')}</div>`;
  return `<details class="more"${open ? ' open' : ''}><summary>More: ${esc(label)}</summary><div class="morebody">`
    + picksBlock(b) + perkBlock(b) + wornBlock(b) + kitBlock(b, kits) + variants + lores + source + '</div></details>';
}

// ---------- cards ----------
function card(b, open) {
  return `<article class="card" id="b-${esc(b.id)}">${cardHead(b)}
  <p class="desc">${esc(b.desc)}</p>
  ${b.hand ? '<div class="hand">Hand-set weights</div>' : ''}<div class="tiers">${tier('Primary', b.p)}${tier('Secondary', b.s)}${tier('Minor', b.m)}</div>
  ${fitBlock(b, open)}
  ${attrBlock(b)}
  ${moreBlock(b, open)}</article>`;
}
function raceCard(r) {
  return `<article class="card"><div><h3>${esc(r.race)}</h3><div class="insp">Racial power: ${esc(r.power)}</div></div>
  <p class="desc">${esc(r.note)}</p>
  <div class="tiers"><div class="tier"><span>Starts 25</span><div class="sk">${pill(r.sig)}</div></div><div class="tier"><span>Starts 20</span><div class="sk">${r.plus5.map(s => pill(s)).join('')}</div></div></div>
  <div class="attr">${bar(r.attr)}${lv(r.lv50)}</div></article>`;
}
function modCard(m) {
  const pairs = m.pairs.length
    ? `Pairs well with: ${m.pairs.map(n => `<button type="button" class="pair" data-build="${esc(n)}">${esc(n)}</button>`).join(' ')}` : 'Works with any build.';
  return `<article class="card"><div><h3>${esc(m.n)}</h3><div class="insp">Ledger ${esc(m.ref)} ${tagEv(m.ev)}</div></div><p class="desc">${esc(m.rule)}</p>
  <div class="chal">${pairs}</div></article>`;
}
const section = (head, cards) => `<section class="fam">${head}<div class="grid">${cards}</div></section>`;
const famHead = (title, blurb) => `<div class="famhead"><h2>${esc(title)}</h2><p>${esc(blurb)}</p></div>`;
const raceHead = famHead('Pure races', 'Only the skills a race starts with a bonus in. The +10 skill starts at 25, each +5 skill at 20.');
const modHead = famHead('Challenge runs', 'Restrictions you can add to any build. The pairings are the ones community sources suggest.');

// ---------- search ----------
// Everything a build can be found by. Built once per build.
const HAY = new Map();
function hay(b) {
  if (!HAY.has(b.id)) {
    const perkNames = groups => groups.flatMap(g => g.perks.map(p => p.n));
    const fam = DATA.fams.find(f => f.id === b.fam);
    HAY.set(b.id, [
      b.name, ...b.aka, b.insp, b.desc, b.play, fam ? fam.title : '',
      ...b.p.map(x => x.s), ...b.s.map(x => x.s), ...b.m.map(x => x.s),
      ...b.npcs, ...b.eids, ...b.req, ...b.mentions, ...b.mods,
      b.gear.armor, ...b.gear.hands, ...b.gear.sig.map(x => x.n), ...b.gear.worn.flatMap(w => w.items.map(i => i.n)),
      ...b.races.map(r => r.race), ...perkNames(b.perks), ...perkNames(b.tree),
      b.stone.early, b.stone.final || '', ...b.shouts.list.map(x => x.n),
      b.beast || '', b.book ? b.book.book + ' ' + b.book.power : '',
      ...b.kits.flatMap(k => [k.n, ...k.items, ...k.cc]),
      ...b.variants.flatMap(v => [v.label, v.skills, ...v.eids, ...v.npcs, ...v.sig.map(x => x.n), ...perkNames(v.perks)]),
      ...b.lore.flatMap(x => [x.n, x.npc, x.changes, ...x.sig.map(i => i.n)]),
    ].join(' | '));
  }
  return HAY.get(b.id);
}
// What a strong match looks at: name, alias, primary skill or a named character. A search_terms.yaml word
// ("tank") stands for a set of skills, so it also looks at secondary skills and the loadout.
const strongHay = (b, wide) => [b.name, ...b.aka, ...b.p.map(x => x.s), ...b.npcs,
  ...b.variants.flatMap(v => v.npcs), ...b.lore.flatMap(x => [x.n, x.npc]),
  ...(wide ? [...b.s.map(x => x.s), b.gear.armor, ...b.gear.hands] : [])].join(' | ');
const raceHay = r => [r.race, r.sig, ...r.plus5, r.note, r.power].join(' ');
const modHay = m => [m.n, m.rule, ...m.pairs].join(' ');

const norm = t => t.toLowerCase().replace(/[-‐-―]/g, ' ');
// A word matches from the start of a word: "orc" finds Orc but not sorcerer, "mage" not damage.
const wordRe = w => new RegExp('(^|[^a-z0-9])' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
// Player words the data never uses ("tank", "2h"), from data/search_terms.yaml: say -> the phrases it stands for.
const SAY = new Map(DATA.say.map(e => [e.say, e.means.map(m => norm(m).split(/\s+/).map(wordRe))]));

// A search: every word must match, in any order, with hyphens as spaces ("two handed" finds Two-Handed).
// A word from search_terms.yaml also matches when any phrase it stands for does.
function matcher(query) {
  let q = norm(query).replace(/\s+/g, ' ').trim();
  const terms = [];
  for (const say of [...SAY.keys()].sort((a, b) => b.length - a.length)) {
    const re = new RegExp('(^| )' + say.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '( |$)');
    if (re.test(q)) { terms.push({literal: say.split(' ').map(wordRe), means: SAY.get(say)}); q = q.replace(re, ' ').trim(); }
  }
  for (const w of q.split(' ').filter(Boolean)) terms.push({literal: [wordRe(w)], means: []});
  const all = (res, text) => res.every(r => r.test(text));
  const phrase = wordRe(norm(query).replace(/\s+/g, ' ').trim());
  return {
    wide: terms.some(x => x.means.length),
    has: text => { const t = norm(text); return terms.every(x => all(x.literal, t) || x.means.some(m => all(m, t))); },
    phrase: text => phrase.test(norm(text)),
  };
}
// Results where the words appear together, as typed, come first.
const phraseFirst = (list, m, text) => list.filter(x => m.phrase(text(x))).concat(list.filter(x => !m.phrase(text(x))));

// ---------- render ----------
// Filters: playstyle comes from build.py's playstyles(); "base game only" hides builds that need DLC or a Creation.
const keep = b => (!st.style || b.styles.includes(st.style)) && (!st.base || !b.req.length);
const keepRace = r => !st.style || r.styles.includes(st.style);

function renderBrowse() {
  let n = 0, html = '';
  for (const f of DATA.fams) {
    if (st.f !== 'all' && st.f !== f.id) continue;
    const builds = DATA.builds.filter(b => b.fam === f.id && keep(b));
    if (!builds.length) continue;
    n += builds.length;
    html += section(famHead(f.title, f.blurb), builds.map(b => card(b, false)).join(''));
  }
  const races = DATA.races.filter(keepRace);
  if ((st.f === 'all' || st.f === 'race') && races.length) { n += races.length; html += section(raceHead, races.map(raceCard).join('')); }
  if ((st.f === 'all' && !st.style) || st.f === 'mods') html += section(modHead, DATA.mods.map(modCard).join(''));
  return {html, count: st.f === 'mods' ? `${DATA.mods.length} challenge runs` : plural(n, 'build')};
}
// Search: builds whose name, alias, primary skill or a named character matches come first; builds that
// only mention the words in their text follow in a folded list.
function renderSearch() {
  const m = matcher(st.q);
  const famOk = b => st.f === 'all' || st.f === b.fam;
  const hits = DATA.builds.filter(b => famOk(b) && keep(b) && m.has(hay(b)));
  const strong = b => strongHay(b, m.wide);
  const best = phraseFirst(hits.filter(b => m.has(strong(b))), m, strong);
  const rest = phraseFirst(hits.filter(b => !m.has(strong(b))), m, hay);
  const races = st.f === 'all' || st.f === 'race' ? DATA.races.filter(r => keepRace(r) && m.has(raceHay(r))) : [];
  const bestR = races.filter(r => m.has(r.race)), restR = races.filter(r => !m.has(r.race));
  const cards = (builds, rs) => builds.map(b => card(b, true)).join('') + rs.map(raceCard).join('');
  const nb = best.length + bestR.length, nr = rest.length + restR.length;
  let html = '';
  if (nb) html += section(famHead('Best matches', 'Name, alias, primary skill or a named character matches.'), cards(best, bestR));
  if (nr) {
    const grid = `<div class="grid">${cards(rest, restR)}</div>`;
    html += nb ? `<details class="more-res fam"><summary>${plural(nr, 'more build')} mention “${esc(st.q.trim())}”</summary>${grid}</details>`
               : `<section class="fam">${famHead('Mentions', 'These builds mention it in their text.')}${grid}</section>`;
  }
  const runs = (st.f === 'all' && !st.style) || st.f === 'mods' ? DATA.mods.filter(x => m.has(modHay(x))) : [];
  if (runs.length) html += section(modHead, runs.map(modCard).join(''));
  const count = nb && nr ? `${plural(nb, 'best match').replace('matchs', 'matches')} · ${nr} more mention it` : plural(nb + nr, 'build');
  return {html, count: count + (runs.length ? ` · ${plural(runs.length, 'challenge run')}` : '')};
}
function render() {
  const {html, count} = st.q.trim() ? renderSearch() : renderBrowse();
  $('cnt').textContent = count;
  $('out').innerHTML = html || '<p class="empty">No builds match that search.</p>';
}

// ---------- controls ----------
const famsEl = $('fams'), styleEl = $('style'), searchEl = $('q');
const pressed = (on, attrs, label) => `<button type="button" aria-pressed="${on}" ${attrs}>${label}</button>`;
function chips() { famsEl.innerHTML = fams.map(f => pressed(st.f === f.id, `data-v="${f.id}"`, esc(f.title))).join(''); }
function seg() {
  styleEl.innerHTML = [['', 'Any'], ...Object.entries(SCHOOLS)]
    .map(([k, t]) => pressed(st.style === k, `data-s="${k}"`, (k ? `<i class="sw sc-${k}"></i>` : '') + t)).join('');
}
// The family chips scroll sideways; fade the right edge while more are off screen.
function fade() { famsEl.classList.toggle('more', famsEl.scrollLeft + famsEl.clientWidth < famsEl.scrollWidth - 4); }
function toResults() {
  const y = $('out').getBoundingClientRect().top + scrollY - document.querySelector('.controls').offsetHeight - 8;
  if (scrollY < y - 4) scrollTo({top: y, behavior: 'smooth'});
}
// Rebuilding a button row drops keyboard focus; put it back on the pressed button.
const refocus = el => { const on = el.querySelector('[aria-pressed="true"]'); if (on) on.focus({preventScroll: true}); return on; };

famsEl.onclick = e => {
  const b = e.target.closest('button'); if (!b) return;
  st.f = b.dataset.v; chips(); render();
  const on = refocus(famsEl); if (on) on.scrollIntoView({block: 'nearest', inline: 'nearest'});
  fade(); toResults();
};
famsEl.addEventListener('scroll', fade, {passive: true});
addEventListener('resize', fade);
styleEl.onclick = e => { const b = e.target.closest('button'); if (!b) return; st.style = b.dataset.s; seg(); render(); refocus(styleEl); };
$('base').onchange = e => { st.base = e.target.checked; render(); };
searchEl.addEventListener('input', e => { st.q = e.target.value; render(); });
searchEl.addEventListener('keydown', e => { if (e.key === 'Enter') { searchEl.blur(); toResults(); } });
searchEl.addEventListener('search', () => { if (searchEl.value) toResults(); });
PHONE.addEventListener('change', () => render());

$('out').addEventListener('click', e => {
  // Pairing buttons: a build or race chip searches for it; a challenge chip shows that challenge.
  const pair = e.target.closest('.pair');
  if (pair) {
    st.q = pair.dataset.build || pair.dataset.mod; searchEl.value = st.q; st.f = 'all';
    chips(); render(); toResults(); return;
  }
  // Tip pills: print the tip under the pill's row; a second press removes it.
  const tip = e.target.closest('.tip');
  if (tip) {
    const row = tip.closest('.sk, .pg'), shown = row.nextElementSibling;
    const wasOpen = tip.getAttribute('aria-expanded') === 'true';
    row.querySelectorAll('.tip').forEach(t => t.setAttribute('aria-expanded', 'false'));
    if (shown && shown.classList.contains('tipline')) shown.remove();
    if (!wasOpen) {
      tip.setAttribute('aria-expanded', 'true');
      row.insertAdjacentHTML('afterend', `<div class="tipline" role="status">${esc(tip.dataset.tip)}</div>`);
    }
    return;
  }
  // The Link button copies the build's full URL.
  const link = e.target.closest('.lnk');
  if (link && navigator.clipboard) {
    navigator.clipboard.writeText(location.href.split('#')[0] + '#' + link.dataset.id)
      .then(() => { link.textContent = 'Copied'; setTimeout(() => link.textContent = 'Link', 1500); }, () => {});
  }
});

// ---------- links ----------
// #<build id> opens that build. Ids a build used to have (link_aliases in builds.yaml) still work.
function openHash() {
  const asked = decodeURIComponent(location.hash.slice(1));
  const build = DATA.builds.find(b => b.id === asked || b.old.includes(asked));
  if (!build) return;
  st = {f:'all', q:'', style:'', base:false};
  searchEl.value = ''; $('base').checked = false;
  chips(); seg(); render();
  const el = $('b-' + build.id);
  el.querySelectorAll('details').forEach(d => d.open = true);
  el.classList.add('hl');
  scrollTo({top: el.getBoundingClientRect().top + scrollY - document.querySelector('.controls').offsetHeight - 8});
  setTimeout(() => el.classList.remove('hl'), 2000);
}
addEventListener('hashchange', openHash);

chips(); seg(); render(); fade(); openHash();

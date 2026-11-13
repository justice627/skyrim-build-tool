// One browser check of the built page: it loads, search finds a build by its community name, and a
// build link opens its card. Run after build.py:  node tests/smoke.js
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const url = 'file://' + path.resolve(__dirname, '..', 'dist', 'index.html');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });
  const errors = [];
  page.on('pageerror', e => errors.push('script error: ' + e.message));
  const check = (ok, what) => { if (!ok) errors.push(what); };
  const firstCard = () => page.locator('.card h3').first().innerText();

  await page.goto(url);
  const cards = await page.locator('article.card').count();
  check(cards >= 70, `expected at least 70 cards, found ${cards}`);

  await page.fill('#q', 'stealth archer');
  check(await firstCard() === 'Stealth Archer', `"stealth archer" should list Stealth Archer first, got ${await firstCard()}`);
  await page.fill('#q', 'two handed');
  check(await page.locator('article.card').count() > 0, '"two handed" should find builds');
  await page.fill('#q', 'zzzz');
  check(await page.locator('.empty').count() === 1, 'a search with no match should say so');

  await page.goto(url + '#scout');
  check(await page.locator('#b-scout details.more').evaluate(d => d.open), '#scout should open the Stealth Archer card');

  await browser.close();
  if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
  console.log(`smoke test passed (${cards} cards)`);
})();

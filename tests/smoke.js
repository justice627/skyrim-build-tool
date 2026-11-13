// One browser check of the built page: it loads, search works, build links open their card, tips can be
// pressed, and every control has a name. Run after build.py:  node tests/smoke.js
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

  await page.fill('#q', 'tank');
  check(await page.locator('article.card').count() > 0, '"tank" should find builds through search_terms.yaml');

  // A build link opens its card, and so does the id the build had before it was renamed.
  for (const hash of ['#thief', '#cutpurse']) {
    await page.goto(url + hash);
    await page.reload();
    check(await page.locator('#b-thief details.more').evaluate(d => d.open), `${hash} should open the Thief card`);
  }

  // Pressing a stone prints what it does under the row (phones and keyboards cannot hover).
  const stone = page.locator('#b-thief .pick .tip').first();
  await stone.focus();
  await page.keyboard.press('Enter');
  check(await page.locator('#b-thief .tipline').count() === 1, 'pressing a stone should show its effect');
  check(await stone.getAttribute('aria-expanded') === 'true', 'a pressed tip should say it is expanded');

  check(await page.evaluate(() => document.head.querySelector('title')?.textContent) === 'Skyrim Builds', 'the title belongs in <head>');
  check(await page.evaluate(() => !document.body.querySelector('title, meta, link')), 'no head tags in <body>');
  const unnamed = await page.evaluate(() => [...document.querySelectorAll('button, a, input')]
    .filter(el => !(el.textContent.trim() || el.getAttribute('aria-label') || el.labels?.length)).length);
  check(unnamed === 0, `${unnamed} controls have no accessible name`);

  await browser.close();
  if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
  console.log(`smoke test passed (${cards} cards)`);
})();

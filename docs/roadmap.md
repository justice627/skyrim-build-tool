# Roadmap

The living version is the Skyrim Build Tool Roadmap doc on claude.ai: https://claude.ai/artifact/W3LhGStR8tJfmkiDouXJmY
This copy holds what Claude Code needs to work through the phases. The research behind it is in `docs/research/community-build-ledger.md`.

## Order

Phase 0 (move to this repo) is done; the one step left is switching Settings > Pages > Source to "GitHub Actions". Phases 1 and 2 can start in either order. Phases 3 and 5 wait on Phase 1's fields, and Phase 4 waits on Phase 2's named variants. Phase 6 runs alongside all of them.

Phases 0 to 6 are done. What comes next is under "Next: phases 7 to 11", in order: 7 and 8 are small and independent, 9 is the main product change, 10 and 11 wait on 9.

## Phase 0: repo setup

Done when the repo is on GitHub, `validate.py` passes, and `build.py` reproduces the published page.

## Phase 1: fields that unlock the most

Add to every build: standing stone (early and final), shouts (two to four), requirements (vanilla, Dawnguard, Hearthfire, Dragonborn, Creation, AE, mod), evidence (sourced, partly sourced, derived) and aliases. Beast form and Black Book power moved to Phase 3, where the first builds that need them arrive.

- New lookup files: `data/stones.yaml`, `data/shouts.yaml`. Builds reference them by id and the validator checks that every id resolves.
- Defaults for the 56 builds come from ledger section F2 and are tagged derived.
- Done when every build shows a stone and shouts, and searching "stealth archer" finds Scout.
- Status: done. The stone and shout lists, and the race skill bonuses, were checked against UESP through its wiki API on 2026-11-11 and are tagged sourced. The per-build picks stay derived.

## Phase 2: names and named variants

Rename Cutpurse to Thief. Everything else from ledger B becomes an alias (Stealth Archer, Crusader, Witcher). Add Paladin as a variant of Vigilant of Stendarr rather than renaming it.

- Add the named-character variants from ledger C: Kodlak, Vilkas, Delphine, Karliah, Isran, Serana, Astrid, Tolfdir and the rest.
- Done when every row of ledgers B and C is applied or marked rejected.
- Status: done (2026-11-11).

| Rows | Result |
|---|---|
| B1 Cutpurse, B3 Prisoner, B7 Scout | Renamed to Thief, Crafter, Stealth Archer; old names are aliases |
| B9 Destruction mage, B12 Blade Binder | Renamed to True Mage, Bound Warrior; old names are aliases |
| B11 Housecarl | Renamed to Warrior, the class's own UESP name; Housecarl is an alias |
| B2, B6 | Variants renamed Knight and Burglar |
| B4 Vilkas, B5 Tolfdir | Kept as trainer variants; both show as Examples from UESP |
| B8 Crusader, B10 Archer, B13 Witcher, Paladin | Kept as aliases; Spellsword, Ranger, Witchblade and Vigilant keep their names |
| C12 to C37, C39, C40 | Added as lore picks under the ledger's parent build; where UESP puts the NPC's class elsewhere, the pick says so |
| C20 Bone Shepherd | Rejected: needs a mod. Mannimarco kept as a lore hook |
| C1 to C7, C10, C11, C38 | Added in Phase 3a under Tongue, Werewolf, Poisoner, Dual-wielder and Pugilist |
| C8, C9 | Deferred to Phase 3b with their parent, Druid |

## Phase 3a: the builds no class file can express

Status: done (2026-11-11). Six builds in a new family, "Community builds" (first named "Beyond the class files"): Pugilist (A1), Tongue (A2), Werewolf (A3), Pacifist (A4, with Puppet Master A7 as a lore pick), Poisoner (A5) and Dual-wielder (A14).

- Hand-set `weights` on the 1 to 4 scale: ledger core skills 3, secondary 2. Attribute ratios are derived. Never graded sourced.
- New fields: `beast_form` (Werewolf, Vampire Lord) and `black_book` (from `data/black_books.yaml`, sourced from UESP).
- Every perk, item, spell or power these builds name is listed in `mentions` and checked against UESP by `scripts/fetch_terms.py` and `validate.py`.
- The check corrected the ledger twice: Greybeard's Robes are unobtainable (dropped from Tongue), and the Ring of Bloodlust is Dragonborn, not Dawnguard. UESP lists 18 Black Book powers, not 21.
- Rejected: A2's "Way of the Voice" variant (needs Ordinator, a mod).

### Lore pick placement fix (2026-11-11)

The ledger grouped lore picks by theme, not skills, so 11 sat under builds they do not play like. Each moved to the build its skills match: Stormcrown and Jarl of the Voice to Warrior, Ash-King to Miraak, Ethereal Hunter to Ebony Warrior, Aela to Thief, Puppet Master to Mystic, Praying Mantis to Bandit chief, Cleric to Vigilant of Stendarr, Esbern to Conjurer, Oblivion Scout to Ranger, The Imperial Spectre to Rogue. Brynjolf, Mercer Frey and Astrid stay: they tweak one or two skills on their own UESP class's build. Battle Bard stays, reworded as additions to the Bard. `validate.py` now rejects picks whose skills barely overlap their build.

## Phase 3b: sourced extras

Status: done (2026-11-11). Eight more builds in "Community builds" (first named "Beyond the class files"): Spellshield (A6), Witchhunter (A8, vanilla skills only), Vampire Slayer (A9), Druid (A10), The Preserver (A11), The Madman (A12), Champion of Cyrodiil (A13, weights from FudgeMuppet's The Master) and Arcanist (A18, TheGamer's Spider Mastermind).

- Where a ledger row lists skills without saying which are core (A8, A11, A12, A13), the first two listed get 3 and the rest 2.
- Lore picks placed by skill fit, not by the ledger's parent: C8 Arcane Beastmaster under Spellshield, C9 Warden under Conjurer (neither fits Druid), A13's lore version Hero of Kvatch under Spellsword, A15 Agent under Trader, A16 Pilgrim under Blacksmith, A17 Battlemage under Bandit chief.
- Left out: Witchhunter's Purifier and Requiem template (mods). Held: Divine Crusader (A19, AE-or-mod question unresolved) and Warrior-Poet (A20, derived, spear is a mod).

## Phase 4: perks from UESP

Status: done (2026-11-12). The planned method (the user picks an NPC per build and supplies screenshots) was replaced: UESP NPC infoboxes have a `perks=` field the wiki API returns.

- Class builds and variants show the combined perks of every named NPC of their class, filtered to the skills on the card, grouped by skill, most-taken first. Tagged sourced.
- A perk counts as a player perk when its UESP page is a skill page (or Lycanthropy). Ambiguous titles (Barbarian, Ranger, Stealth, Necromage) resolve through UESP's "<name> (perk)" redirects. NPC-only perks (Extra Damage, MS02IncreaseDamage, IrilethVsDragons) are dropped.
- Coverage: 22 of 56 class builds and 9 variants. The rest have no named NPC with a perk list and say so on the card.
- Community builds show the key perks their ledger row names: Fists of Steel (Pugilist), Poisoned (Poisoner), Dual Flurry (Dual-wielder) and the werewolf tree (Werewolf). Partly sourced.
- Done criterion changed: every perk shown is sourced or marked, and gaps are visible. "Every primary skill shows a perk" is not reachable without guessing.
- Planner fix: Enchanting no longer counts as a spell school. Temple priest loses a wrong Magicka shift; Laborer, Citizen and Crafter now move their unused Magicka to Stamina.

## Phase 5: gear kits and challenge runs

Status: done (2026-11-12).

- `data/kits.yaml`: 13 kits (ledger D1 to D13) attached to builds. Every item is checked on UESP. Requirement tags are read from each item's UESP page header (`{{CC Header|<Creation>}}` or a DLC category), never typed by hand. Paid Creations show as "CC: <Creation>"; all of them ship in the Anniversary Edition bundle, so the ledger's CC versus AE split is dropped.
- The UESP check regrouped the ledger: Light of Day, Trueflame, Hopesfire, Magebane, Cleaver of St. Felms and Skull Crusher are all *Ghosts of the Tribunal*; Bloodthirst is *Dawnfang & Duskfang*; Sunder and Wraithguard are one Creation; Keening, Wuuthrad, Spellbreaker and Ring of Namira are base game.
- `data/modifiers.yaml`: 16 challenge runs (M1 to M14, with M5 split into stolen, purchased and crafted). Shown as their own section and chip, and as a line on the builds they pair with.
- Left out: D14 relic stand-ins (derived, for held builds) and D15 Black Book powers (already a field).

## Phase 6: verification

Status: done for everything checkable from a cloud session (2026-11-12). Record: `docs/sources/uesp-lore-checks.md`.

- Stones, shouts, race bonuses, Black Books, perks, kit items and their Creations: checked against UESP in earlier phases.
- Lore and item claims on the page: 22 checked. 16 confirmed, 4 reworded to what UESP says (Jagar Tharn, Hero of Kvatch, Wuuthrad, Champion of Cyrodiil), 2 corrected (Kodlak is a werewolf seeking a cure; Stendarr's Hammer drains the wielder's Stamina).
- Chrysamere, Sunder and Wraithguard are official Creations, Keening is base game. Divine Crusader (A19) can come back as a CC build.

Left for a person, because YouTube is blocked here. Watch and note anything that contradicts the page:

| Video | Build on the page | What to check |
|---|---|---|
| FudgeMuppet, The Sabre Cat | Pugilist (lore pick) | Race, the skills it adds (Conjuration, Restoration, Smithing), and which DLC spells it uses |
| FudgeMuppet, The Preserver | The Preserver | Skill order (Conjuration and Archery first?), Ritual Stone, the gear list |
| FudgeMuppet, The Mechanist | Spellsword (lore pick) and the Nerevarine relics kit | Stones (Lover, then Atronach), Block, Visage of Mzund, Keening |
| FudgeMuppet, The Ronin | Not on the page | Whether it is worth adding at all |

## Lore groups (2026-11-12)

Every UESP lore faction checked for how it fights (ledger G, `docs/research/lore-groups.md`). 616 groups: 134 described well enough to read in full, 324 too thin (listed as gaps), 158 that do not fight. No group needed a new build. 19 became aliases and 44 became lore picks under the build they play like. Not yet done: the 324 gap groups, and gear for lore picks (to look at with the gear review).

## Gear review (2026-11-12)

Every card has a Gear line: the group's own set where it has one (Imperial, Stormcloak, Thieves Guild, Shrouded, Nightingale, Blades, Penitus Oculatus, Thalmor, Forsworn, Vampire, Dawnguard, plus character sets such as Miraak's and Frea's), checked on UESP with DLC and Creation tags, then the suggested loadout. "As worn by" under More lists what Example characters wear (83 characters). Lore picks show their gear too (Indoril, bonemold, chitin, Stalhrim, Morag Tong). The check found three mismatches between a card and its gear, now noted: Blades armor and Frea's Nordic carved armor are heavy, and Dawnguard armor comes in light and heavy sets that must not be mixed.

## Race fit, early perks, refresh (2026-11-12)

- Every card has a Race line: the races whose starting skill bonuses best match the build (rule in `race_fit()`). Tapping a race shows it and the builds it fits.
- Primary skills with no perk on the card now show that tree's early perks with required levels (180 perks from UESP's 18 skill pages). Only 2 builds still show no perks at all.
- `scripts/refresh.py` runs the whole data chain in order. Search now matches from the start of a word ("orc" no longer finds sorcerers).

## Review fixes (2026-11-12)

- `validate.py`: a malformed Black Book now reports instead of crashing; community builds get the alias, family, description and name checks they were skipping.
- The "text names nothing outside `mentions`" rule is now enforced. The first run found 31 text blocks naming unlisted things; all are listed and checked on UESP (282 terms). Two had no UESP page and were corrected: Kodlak's "Skyforge Steel greatsword" is the Skyforge Steel Greatsword, and the Vampire's "Drain Life and Night Eye" are Vampiric Drain and Vampire's Sight. Illusion Assassin gained a DB tag: Bound Dagger is a Dragonborn spell.
- `scripts/fetch_classes.py` reads `classes.json` from the Skyrim:Classes table through the API. All 119 classes matched the PDF and screenshot read. `data/excluded_classes.yaml` lists the 40 rows left out.
- Search matches every word in any order and treats hyphens as spaces ("two handed", "heavy armor mage"). "How to read a build" starts closed.

## Next: phases 7 to 11 (from the 2026-11-12 system review)

The review's verdict: the data pipeline is the strong part and the page is the weak part. The repo checks its facts well, then prints a 96-card catalog (about 49 phone screens) that does not help anyone choose. So the next phases stop adding data layers. Phases 7 and 8 make what exists safe to change and fix what is broken; Phase 9 turns the catalog into a chooser; 10 and 11 build on that.

Each phase is one branch and ends with a working page (CLAUDE.md rule 4). Rule 5 holds throughout: no framework, no bundler, one HTML file out.

| Phase | What | Size | Waits on |
|---|---|---|---|
| 7 | Tests and pipeline cleanup | 1 to 2 sessions | nothing |
| 8 | Page shell, links, accessibility | 1 session | nothing |
| 9 | From catalog to chooser | 2 to 3 sessions | 8 (template split) |
| 10 | Play like a character | 1 to 2 sessions | 9 |
| 11 | Picks worth reading | 1 session | 9 |

## Phase 7: tests and pipeline cleanup

Status: done (2026-11-13). 62 unit tests and one browser smoke test run in CI before the deploy. The page output did not change, apart from two gear fixes below.

- All items below landed as written. The caches are in `data/uesp/`; `scripts/uesp.py` holds the API code; `build.py` renders from one `Sources` object and checks the pages it writes.
- The refactored fetch scripts were run against UESP and reproduced every cache.
- Gear spot check (`docs/sources/uesp-gear-spot-check.md`): 2 of 11 characters held something wrong. Balimund's "gear" was his shop, The Scorched Hammer, and Farkas's Wolf Armor came from a bug note. Both causes are fixed in `fetch_gear.py`; the card now says "Not a full inventory".
- Owner's decision: the Playwright smoke test is in (`tests/smoke.js`, CI-only dependency).
- Found, not changed: Temple priest has Restoration 3 and Conjuration 2 but a plan of zero Magicka. Its NPC file has no Magicka weight and its spell share (5 of 13) is under `plan()`'s 40% line. Rule 7 suggests a caster should get Magicka; decide in Phase 11 with the other picks.

Why: nothing tests the functions that decide what a player sees, and the four fetch scripts parse wikitext with regexes that fail silently when UESP changes a template.

- `tests/` with the standard library's `unittest` (no new dependency), run in CI before `validate.py`.
  - `common.py`: table tests for `playstyles`, `loadout`, `race_fit`, `early_perks` and `named_in_text`, plus `plan` and `split` from `build.py`. Use real builds as cases (Warrior, Stealth Archer, Monk, Pugilist, Temple priest) so a rule change shows which cards move.
  - Parsers: `fetch_classes.parse`, `fetch_terms.origin` and `section_origin`, `fetch_npcs.perks_of` and `summaries`, the `ENTRY` pattern in `fetch_skill_perks.py`. Each against a short saved wikitext sample in `tests/fixtures/`, including the awkward cases the code comments name (CC Header with `shortcut=`, Indoril Armor on Skyrim:Chitin, a root perk with no level).
- `scripts/uesp.py`: move `get`, the 50-title batching and "fetch wikitext for these titles" out of `fetch_npcs.py`; every fetch script repeats them. `get` should catch network errors only and report the last one, not swallow every exception (`fetch_npcs.py:37`).
- Fix `fetch_terms.py:86` (`min()` of an empty sequence when a row has no `||` or newline after the anchor).
- `build.py`: load each file once in `page_data()` and pass one context object to `render_build` in place of 11 positional arguments. Compute a build's perks once (they are computed twice at lines 217 to 218). Drop the second `json` import and the second `uesp_terms()` call.
- Build self-check: after writing `dist/index.html`, `build.py` re-reads it, parses the embedded JSON, and confirms every build id is there. Cheap, and it gives CI its first check of the output.
- Move the caches the build reads (`uesp-npc-classes.json`, `uesp-terms.json`, `uesp-npc-gear.json`, `uesp-skill-perks.json`) from `docs/sources/` to `data/uesp/`. They are build inputs, not documents. Raw reference copies (`.wiki`, PDF, screenshot, `uesp-lore-checks.md`) stay. Do this after `uesp.py` exists so the paths live in one place.
- `validate.py`: check that every ledger `ref` names a row that exists in `docs/research/` (today only the format is checked; all 102 refs happen to resolve).
- Be honest about "As worn by": `fetch_gear.py` infers gear from sentences containing "wears" or "wields" plus keep and drop patterns. Spot-check 10 characters against their UESP pages, save the result in `docs/sources/`, and grade the line `partly-sourced` if any are wrong.

Done when: `python -m unittest` passes in CI, a deliberately broken fixture fails a test, and the page output is unchanged apart from path moves.

Decision for the owner: whether to add one Playwright smoke test in CI (page loads, "stealth archer" finds its card, a `#id` link opens). It would be a CI-only dependency. Recommended, but after the Python checks, and only one test.

## Phase 8: page shell, links, accessibility

Why: small defects a visitor meets before reading any build.

- Broken links: the README advertises `#thief`, but the build's id is still `cutpurse`, so the link does nothing. Six renamed builds have stale ids (`housecarl`, `scout`, `cutpurse`, `destruction-mage`, `prisoner`, `blade-binder`). Rename the ids to match the names and keep the old ids as `link_aliases` that `openHash()` resolves, so shared links keep working. Update `kits.yaml` and `modifiers.yaml` references. Validator: an id must be the slug of the name, or say why not.
- Document head: `<title>` currently lands inside `<body>` in `index.html` because the fragment is wrapped whole. `build.py` should lift the fragment's head lines into `SKELETON`'s `<head>` and add a meta description and Open Graph tags. A page whose feature is shareable links should preview properly.
- Fonts: the page loads three families from Google Fonts, so it is not "self-contained" as the README says. Keep the fonts (they carry the look) but make sure every `font-family` has a system fallback, and reword the README claim.
- Accessibility pass (ai-hub's `skills/accessibility-review` is a usable checklist): 21 buttons had no text or label in the review's count; check keyboard use of chips, the playstyle segment and `details` rows; check contrast of muted text in both themes; announce the result count with `aria-live`.
- Search ranking: an exact phrase match should rank above an all-words match ("stealth archer" now lists 10 "more mention it" builds). Add a small `data/search_terms.yaml` of player words the data never uses (tank, 2h, necro, sword and board, dual wield), each mapped to skills or build ids, tagged derived.
- Split the template for editing, not for output: `src/page.html`, `src/page.css`, `src/page.js`, inlined by `build.py` into the same single file. Break `card()` into one function per card section; seven lines are over 400 characters today. This has to land before Phase 9 touches the card.

Done when: every README link works, `index.html` validates as HTML, the keyboard reaches every control, and `dist/index.html` is still one file.

## Phase 9: from catalog to chooser

Why: this is the review's main finding. A player arrives wanting to play something and gets 13 families to scroll. The data to answer them is already in the page.

- Skill picker: a row of the 18 skills above the families. Tap two or three and every build is ranked by how much of its weight sits in those skills (`race_fit()` turned around; no new data). Show the score's reason on each result ("One-Handed 3, Destruction 3"). State goes in the URL (`#pick=1HD,DES`) so a result can be shared.
- Playable or flavor: a `kind` field on builds, `play` or `flavor`. Flavor covers the cards that exist because every class must be used once (Citizen, Beggar, Laborer, most vendors and trainers). The default view shows playable builds; a toggle shows all. The "every class used exactly once" rule stays in the data. Expect roughly 35 playable builds; the owner decides each one, and the choice is tagged derived.
- Start here: `starter: true` on six to eight builds that suit a first character, shown as a row above the families, with one line on why each is forgiving.
- Shorter default card: name, one-line pitch, primary and secondary skills, gear line, attribute bar. Description, race, In play, stone, shouts, perks, variants and lore go behind the existing "More". Add an optional one-line `pitch` field; fall back to the description's first sentence.
- Filter state in the URL (family, playstyle, base game, search), so the back button and shared links restore the view.

Done when: from a cold start on a phone, picking "One-Handed" and "Destruction" shows a ranked answer on the first screen; the default page is under 15 phone screens; every build is still reachable with the toggle.

Risk: `kind` and `starter` are judgment calls on 70 builds. Do them in one sitting with the page open, not as research.

## Phase 10: play like a character

Why: the premise's unique hook is that every named NPC has a class. The cache holds 1,032 named NPCs; the page shows 132 as examples and cannot find the rest.

- NPC index: `build.py` adds a compact name-to-build map for every NPC in `uesp-npc-classes.json` (name, build id, variant if any). Searching "Farkas" or "Jenassa" answers "plays as Greatsword mercenary", with that NPC's own perks from the cache when UESP lists them (120 NPCs have a perk list).
- Watch the page weight: 1,032 names is roughly 40 KB. Fine, but measure it; the page is 277 KB now.
- Followers view (only if the NPC index gets used): a new `fetch_followers.py` reading UESP's Skyrim:Followers table, a `followers` filter, and for each build a derived "pairs well with" line naming followers whose class covers what the build lacks (a tank for a robed mage, an archer for a shield build). The pairing rule goes in `common.py` with its own tests.

Done when: any named NPC with a class resolves from search, and the count line says so ("1 character plays this build").

Gate before the followers view: check that it solves a problem the owner has while playing. If not, stop after the NPC index.

## Phase 11: picks worth reading

Why: the stone pick is derived on 63 of 70 builds and is nearly always the guardian stone for the archetype (Mage 21, Warrior 20, Thief 19). Unrelenting Force is on 33 builds. These lines take card space and say little.

- Stones: move the default into a `stone_for()` rule in `common.py` (like `loadout()`), with the rule stated on the page. Keep a `stone` field only where a ledger row cites a specific pick or the build needs a different one, and say why in a comment. A card then shows the stone prominently only when it is a real choice.
- Shouts: list the shouts that are distinctive for the build first, and fold the near-universal ones (Unrelenting Force, Whirlwind Sprint) into a shared "every build" note.
- Evidence summary: a footer generated from `data/sources.yaml` (source, what it feeds, grade, date retrieved from each cache's `retrieved` field). `sources.yaml` is prose nothing reads today; this makes the page's main claim checkable by a reader.

Done when: no card shows a pick that every similar card also shows, and the footer lists each source with its date.

## Closed

Decided not to do, so they stop reading as open work:

- The 324 lore "gap groups" in ledger G. They are too thinly described on UESP to become picks, and more lore picks make cards longer, which is the opposite of Phase 9.
- Saved characters, accounts, a leveling tracker. They break rule 5 and add upkeep.
- Wiring ai-hub's shared `AGENTS.md` block into this repo. It is mostly Java, AWS and delivery guidance; `CLAUDE.md` here is more specific. Use single skills by hand where they fit (accessibility review in Phase 8).
- A scheduled UESP refresh. The game's data is stable; run `scripts/refresh.py` by hand when adding content.

Still open from earlier: the four FudgeMuppet videos under Phase 6, which need a person.

## Out of scope

Mod-only builds (Requiem templates, the Ordinator Dragonborn, FudgeMuppet's modded Sand Demon, Celestial and King), ESO class conversions, and full perk templates for all 18 trees.

## Decisions (2026-11-11)

- Naming: community names become the primary names, and NPC-file names become aliases. Phase 1 adds aliases and alias search; the renames happen in Phase 2.
- Weights for new builds: set from the research (ledger A core skills) on the 1 to 4 scale, marked as not from an NPC file, with their evidence grade.
- Mod builds: excluded. The page is vanilla-friendly, so default picks use base-game options where one fits.
- Hosting: GitHub Pages from the public repo.

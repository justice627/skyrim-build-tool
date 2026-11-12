# Skyrim Build Tool

A static reference page of Skyrim character builds. NPC class weights from UESP become player builds, grouped into families, plus ten pure race builds. Python turns YAML/JSON data into one self-contained HTML page.

## Commands

```bash
pip install -r requirements.txt     # PyYAML only
python scripts/refresh.py           # refresh data from UESP, then validate and build (--offline: validate and build only)
python scripts/validate.py          # must pass before every commit
python scripts/build.py             # writes dist/index.html and dist/artifact.html
python -m http.server -d dist 8000  # preview at http://localhost:8000
```

## Layout

- `data/classes.json`: raw UESP skill and attribute weights per NPC class EditorID. Source data; do not edit by hand.
- `data/builds.yaml`: families and builds. Each build points at the class files it comes from, plus variants, inspiration and playstyle text.
- `data/races.yaml`: pure race builds. Attribute ratios here are recommendations, not game data.
- `data/stones.yaml`, `data/shouts.yaml`: lookup lists that builds reference by id.
- `data/sources.yaml`: where data came from and how much to trust it.
- `scripts/`: `common.py` (loading, skill codes), `validate.py`, `build.py`.
- `src/template.html`: the page. `__DATA__` is replaced with the built JSON. It is a fragment because claude.ai artifacts supply their own skeleton; `build.py` wraps it into a full document for `index.html`.
- `docs/roadmap.md`: the phased plan. Work in phase order.
- `docs/research/`: the community and lore build ledger and the research notes behind it. These are leads, not verified data. `lore-groups.md` is ledger G: every UESP lore faction, how it fights, and whether it became an alias, a lore pick or a gap.
- `docs/sources/`: the saved UESP class table (PDF plus a screenshot of the rows the PDF dropped), `uesp-npc-classes.json` (which named NPCs use each class), and the raw UESP text behind `stones.yaml`, `shouts.yaml` and the race bonuses.
- `data/kits.yaml`, `data/modifiers.yaml`: gear kits (ledger D) and challenge runs (ledger F1).
- `data/black_books.yaml`: the Dragonborn Black Books and their powers (sourced from UESP).
- `scripts/fetch_terms.py`: checks every `mentions` term against UESP and saves `docs/sources/uesp-terms.json`. Run it after adding or renaming a mention, before `validate.py`.
- `scripts/refresh.py`: runs fetch_npcs, fetch_gear, fetch_skill_perks, fetch_terms, validate and build in that order, stopping at the first failure. Use it instead of running the fetch scripts by hand.
- `scripts/fetch_skill_perks.py`: all 18 skill trees from UESP's skill pages (`docs/sources/uesp-skill-perks.json`): each perk's ranks, required levels and effect.
- `scripts/fetch_gear.py`: what each build's Example characters wear, from their UESP pages (`docs/sources/uesp-npc-gear.json`). Run before `fetch_terms.py`.
- `scripts/fetch_npcs.py`: refreshes `uesp-npc-classes.json` from UESP's wiki API. UESP's normal pages are blocked from cloud sessions, but `https://en.uesp.net/w/api.php` works.

## Rules

1. Run `python scripts/validate.py` before every commit, and extend it whenever a new field or file is added.
2. Never invent perks, items, weights, NPC facts or sources. Anything not read from a source is tagged `evidence: derived` and shown as such on the page.
3. `classes.json` holds UESP numbers only. Interpretation (names, groupings, attribute plans, playstyle text) goes in `builds.yaml` or `build.py`.
4. One roadmap phase per branch. Each phase ends with a working page. When the work on a branch is done and `validate.py` passes, merge it into `main` (fast-forward when possible), push `main`, then delete the branch locally and on GitHub. No pull requests unless asked; pushing `main` triggers the Pages deploy.
5. Keep it small: no framework, no bundler, no database. The page stays one self-contained HTML file.
6. Write player-facing text plainly: American English, short sentences, no em dashes.
7. Utility over strict accuracy in recommendations. Game data (class weights, examples, perks, items) stays as UESP gives it. Recommendations (descriptions, attribute plans, picks, hand-set weights) aim at how the game is actually played, even where that departs from its design, and are tagged derived when they are this tool's call. The attribute planner moving unused Magicka is the model.

## Data conventions

- Skill codes follow UESP's column headers (`ARC`, `BLO`, `HVA`, `1HD`, ... `SPE`, plus `Hea`, `Mag`, `Sta`). See `scripts/common.py`.
- Weight tiers on the page: primary is 3 or more, secondary 2, minor 1.
- A build's first class decides the weights its card shows. Classes grouped in one build or one variant must have identical weights; the validator enforces this.
- Every class in `classes.json` is used exactly once across all builds.
- Every build has `evidence` (grade of its skills), a `stone` (`early`, optional `final`) and 2 to 4 `shouts`, each block with its own `evidence` and an optional ledger `ref` such as `B7`. Optional: `lore` (ledger A, C or G picks: `name`, `ref` such as `C12` or `G40`, `changes`, `evidence`, optional `requires` and `npc`), `aliases`, `requires`, `examples` (up to 3 named NPCs; the validator checks each against `uesp-npc-classes.json`).
- Evidence grades: `sourced`, `partly-sourced`, `derived`. Requirement tags: `vanilla`, `DG`, `HF`, `DB`, `CC`, `AE`. Mod-only content is out of scope, so there is no `Mod` tag.
- Hand-set builds (family `beyond`) have `weights` instead of `classes`, plus a ledger A `ref`. Skills 1 to 4, all of Hea, Mag and Sta. Never graded `sourced`. No class variants or examples; use `lore` picks (refs may be A or C rows).
- Hand-set weights: skills a ledger row calls core get 3, secondary 2. When a row lists skills without tiers, the first two listed get 3 and the rest 2. Where that would recommend a skill that does nothing for the playstyle (Speech on a shout build), adjust it, grade the build `derived` and give the reason in a comment.
- A lore pick sits under the build it plays like. If its `changes` names 3 or more skills, at least half must be the build's primary or secondary skills, unless the text says "Adds" or "replaces". The validator enforces this. Theme alone (shouts, werewolf) is not enough.
- `mentions` (on builds and lore picks) lists every perk, item, spell or power the text names, spelled as the UESP page title. The validator rejects terms with no UESP page or that UESP lists as unobtainable. Text must not name anything that is not in `mentions`.
- Perks: class builds and variants get them automatically from `uesp-npc-classes.json` (every named NPC of the class), filtered to the card's skills. A perk is a player perk when `uesp-terms.json` gives it a `tree` (its UESP page is a skill page or Lycanthropy). Community builds may list `perks: {names, evidence, ref}`; names must be player perks in the build's skills (or the werewolf tree) and also appear in `mentions`.
- Gear kits (`data/kits.yaml`) list UESP item titles and the build ids they fit. Do not type requirement tags for kits: `build.py` reads them from each item's UESP origin (`fetch_terms.py` records `CC:<Creation>`, `DG`, `DB`, `HF` or `base`). Challenge runs (`data/modifiers.yaml`) have a rule, ledger M ref and natural `pairs`; items a rule names go in `mentions`.
- Playstyle filter tags come from `playstyles()` in `scripts/common.py`: weapon, armor and Block skills are combat, the five spell schools magic, Sneak, Pickpocket and Lockpicking stealth; Light Armor does not count. A style is tagged when its skills (weight 2 or more) hold 30% of the fighting total. "k" (Craft) is added when Smithing, Enchanting, Alchemy and Speech weigh at least as much as the biggest fighting style. A build's `playstyles` field overrides the rule; keep overrides rare and give the reason in a comment.
- Optional `play`: one or two sentences on how to actually play a build where its data misleads (too many primaries, both armors or both weapon styles, Sneak in heavy armor). Shown as "In play", always suggested. Perks or items it names go in `mentions`.
- Gear: every card shows a Gear line. `signature` (on builds, variants and lore picks) lists a group's own set as UESP titles, with a comment naming the UESP page that ties group and gear; `fetch_terms.py` checks each item and records its origin from the item's own row or section. `loadout` comes from `loadout()` in `common.py` (armor from the armor skills, hands from weapon, Block and spell skills); a `loadout: {armor, hands}` override is allowed where the characters or the In play line say otherwise, with the reason in a comment. "As worn by" comes from `scripts/fetch_gear.py` (`docs/sources/uesp-npc-gear.json`).
- Race fit: `race_fit()` in `common.py` scores each race by skill weight x race bonus (+10 signature, +5 others) over the build's skills weighted 2 or more, and shows the top two (three on a tie). It ignores racial powers and attributes; the page says so.
- Early perks: for each primary skill the card shows no perk for, `early_perks()` lists that tree's perks needing skill 30 or less (at most 4), from `uesp-skill-perks.json`. Builds with no primary skill fall back to their secondary skills (at most three trees, skipping Block without a shield and armor the loadout does not wear).
- Optional `beast_form` (`werewolf`, `vampire-lord`) and `black_book` (`{book, power, evidence, ref}`).
- Creatures and non-playable beings (Draugr, Falmer, Daedra, giants, werewolf beast forms) are deliberately left out of `classes.json`.

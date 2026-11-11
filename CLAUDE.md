# Skyrim Build Tool

A static reference page of Skyrim character builds. NPC class weights from UESP become player builds, grouped into families, plus ten pure race builds. Python turns YAML/JSON data into one self-contained HTML page.

## Commands

```bash
pip install -r requirements.txt     # PyYAML only
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
- `docs/research/`: the community and lore build ledger and the research notes behind it. These are leads, not verified data.
- `docs/sources/`: the saved UESP class table (PDF plus a screenshot of the rows the PDF dropped), `uesp-npc-classes.json` (which named NPCs use each class), and the raw UESP text behind `stones.yaml`, `shouts.yaml` and the race bonuses.
- `scripts/fetch_npcs.py`: refreshes `uesp-npc-classes.json` from UESP's wiki API. UESP's normal pages are blocked from cloud sessions, but `https://en.uesp.net/w/api.php` works.

## Rules

1. Run `python scripts/validate.py` before every commit, and extend it whenever a new field or file is added.
2. Never invent perks, items, weights, NPC facts or sources. Anything not read from a source is tagged `evidence: derived` and shown as such on the page.
3. `classes.json` holds UESP numbers only. Interpretation (names, groupings, attribute plans, playstyle text) goes in `builds.yaml` or `build.py`.
4. One roadmap phase per branch. Each phase ends with a working page. When the work on a branch is done and `validate.py` passes, merge it into `main` (fast-forward when possible), push `main`, then delete the branch locally and on GitHub. No pull requests unless asked; pushing `main` triggers the Pages deploy.
5. Keep it small: no framework, no bundler, no database. The page stays one self-contained HTML file.
6. Write player-facing text plainly: American English, short sentences, no em dashes.

## Data conventions

- Skill codes follow UESP's column headers (`ARC`, `BLO`, `HVA`, `1HD`, ... `SPE`, plus `Hea`, `Mag`, `Sta`). See `scripts/common.py`.
- Weight tiers on the page: primary is 3 or more, secondary 2, minor 1.
- A build's first class decides the weights its card shows. Classes grouped in one build or one variant must have identical weights; the validator enforces this.
- Every class in `classes.json` is used exactly once across all builds.
- Every build has `evidence` (grade of its skills), a `stone` (`early`, optional `final`) and 2 to 4 `shouts`, each block with its own `evidence` and an optional ledger `ref` such as `B7`. Optional: `aliases`, `requires`, `examples` (up to 3 named NPCs; the validator checks each against `uesp-npc-classes.json`).
- Evidence grades: `sourced`, `partly-sourced`, `derived`. Requirement tags: `vanilla`, `DG`, `HF`, `DB`, `CC`, `AE`. Mod-only content is out of scope, so there is no `Mod` tag.
- Creatures and non-playable beings (Draugr, Falmer, Daedra, giants, werewolf beast forms) are deliberately left out of `classes.json`.

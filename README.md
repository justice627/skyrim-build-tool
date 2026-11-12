# Skyrim Build Tool

A one-page reference of Skyrim character builds: https://justice627.github.io/skyrim-build-tool/

- **56 class builds**: every playable humanoid NPC class from UESP turned into a player build (skills by weight, a level 50 attribute plan, a playstyle), grouped into families, with trainer and vendor variants folded in.
- **14 community builds**: playstyles no class file can express (Pugilist, Tongue, Werewolf, Poisoner and more), with hand-set weights from the research ledger.
- **10 pure race builds** and **16 challenge runs**.
- Per build: example NPCs, stone and shouts, perks named NPCs of the class take, gear kits, and lore picks.

Every NPC, perk, item and requirement tag is checked against UESP through its wiki API. Anything worked out for the page, not read from a source, is marked "suggested". The page has playstyle and base-game filters, search, and a shareable link per build (`#thief`).

## Run it

Needs Python 3.10 or newer.

```bash
pip install -r requirements.txt
python scripts/validate.py
python scripts/build.py
python -m http.server -d dist 8000   # then open http://localhost:8000
```

`dist/index.html` is self-contained, so opening it directly in a browser also works.

## First-time setup

On Kubuntu, `sudo apt install python3-yaml` works instead of pip.

```bash
unzip skyrim-build-tool.zip && cd skyrim-build-tool
git init -b main
git add . && git commit -m "Import Skyrim build tool"
gh repo create skyrim-build-tool --public --source . --push   # or create it on github.com and push
claude                                                        # open the folder in Claude Code
```

GitHub Pages is set up: the workflow validates, builds and deploys on every push to `main`.

## Where things are

See `CLAUDE.md` for the layout and house rules, and `docs/roadmap.md` for what comes next.

## Sources

Class weights come from [UESP's Skyrim:Classes page](https://en.uesp.net/wiki/Skyrim:Classes), read through the wiki API by `scripts/fetch_classes.py`. See `data/sources.yaml` for what is sourced and what is derived.

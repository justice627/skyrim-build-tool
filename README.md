# Skyrim Build Tool

A one-page reference of Skyrim character builds. Every playable humanoid NPC class from UESP is turned into a player build (skills by weight, a level 50 attribute plan, and a playstyle), grouped into 12 families with trainer and vendor variants folded in. Ten pure race builds close the page.

Current contents: 119 NPC class files, 56 builds, 10 races.

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

To publish with GitHub Pages: in the repo's Settings > Pages, set Source to "GitHub Actions". The included workflow validates, builds and deploys on every push to `main`.

## Where things are

See `CLAUDE.md` for the layout and house rules, and `docs/roadmap.md` for what comes next.

## Sources

Class weights come from [UESP's Skyrim:Classes page](https://en.uesp.net/wiki/Skyrim:Classes). The saved copy used to read them is in `docs/sources/`. See `data/sources.yaml` for what is sourced and what is derived.

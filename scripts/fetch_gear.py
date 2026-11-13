"""What the Example characters of each build wear and wield, per their UESP pages.

Reads the "wears / wields / carries" sentences on each Example's page (builds and variants) and keeps
the armor and weapon items they link to. Writes data/uesp/uesp-npc-gear.json:
  {"retrieved", "source", "npcs": {npc name: [item titles]}}
Generic pieces (boots, plain daggers, hoods) are dropped; the card shows body armor, weapons and shields.
Links that UESP does not file as items (a shop named The Scorched Hammer) are dropped, and so are bug notes.
Run fetch_terms.py afterwards: it checks every item on UESP and records where it comes from.
"""
import re

import yaml

from common import DATA, cache, write_cache
from uesp import API, batches, get, wikitext

GEAR = re.compile(r"(?i)\b(wears?|wearing|clad in|equipped with|dressed in|wields?|carries)\b")
LINK = re.compile(r"\[\[(?:Skyrim|SR):([^|\]#]+)(?:#[^|\]]*)?(?:\|[^\]]*)?\]\]")
KEEP = re.compile(r"(?i)armor|cuirass|robes|sword|axe|mace|bow|shield|staff|hammer|greatsword|dagger of|blade")
DROP = re.compile(r"(?i)^(iron|steel|elven|orcish)? ?dagger$|boots|bracers|gauntlets|helmet|hood$|key$|^trainer"
                  r"|^(bow|sword|shield|armor|mace|war axe|greatsword|battleaxe|warhammer|staff|heavy armor|light armor)$")


def gear_in(page, limit=5):
    """Armor and weapon items linked in a page's "wears / wields / carries" sentences, in page order."""
    body = re.sub(r"\{\{NPC Summary.*?\n\}\}", "", page, flags=re.S)
    # Bug notes describe what patches changed ("His outfit was changed from Steel Armor to Wolf Armor"), not the game.
    body = re.sub(r"\n==+\s*Bugs\s*==+.*", "", body, flags=re.S)
    body = re.sub(r"\{\{Bug\|[^\n]*", "", body)
    items = []
    for sent in re.split(r"(?<=[.!?])\s", body):
        if GEAR.search(sent):
            for raw in LINK.findall(sent):
                item = raw.replace("_", " ").strip()
                if KEEP.search(item) and not DROP.search(item) and item not in items:
                    items.append(item)
    return items[:limit] if limit else items


ITEM_CATEGORY = re.compile(r"-(Items|Weapons|Armor|Clothing)\b")


def is_item(categories):
    """True when a page's UESP categories file it under items. Places do not: The Scorched Hammer is a shop."""
    return any(ITEM_CATEGORY.search(c) for c in categories)


def item_titles(titles):
    """The titles that UESP files as items: the page a title lands on is in an item category, or the title
    is one section of a shared page (Ancient Nord Armor is a section of Skyrim:Skyforge, a place)."""
    out = set()
    for batch in batches(sorted(titles)):
        d = get(action="query", prop="categories", cllimit=500, redirects=1,
                titles="|".join(f"Skyrim:{t}" for t in batch))["query"]
        norm = {n["from"]: n["to"] for n in d.get("normalized", [])}
        redir = {r["from"]: (r["to"], r.get("tofragment", "")) for r in d.get("redirects", [])}
        cats = {p["title"]: [c["title"] for c in p.get("categories", [])] for p in d["pages"].values()}
        for t in batch:
            title = norm.get(f"Skyrim:{t}", f"Skyrim:{t}")
            page, section = redir.get(title, (title, ""))
            if section or is_item(cats.get(page, [])):
                out.add(t)
    return out


def example_pages(doc):
    npcs = cache("npc-classes")["classes"]
    page = {n["name"]: n["page"] for v in npcs.values() for n in v}
    names = {n for b in doc["builds"] for n in b.get("examples", []) + [x for v in b.get("variants", []) for x in v.get("examples", [])]}
    return {n: page[n] for n in names if n in page}


def main():
    doc = yaml.safe_load((DATA / "builds.yaml").read_text())
    pages = example_pages(doc)
    text = wikitext(sorted(set(pages.values())), redirects=True)
    found = {name: gear_in(text.get(title, ""), limit=None) for name, title in sorted(pages.items())}
    real = item_titles({i for items in found.values() for i in items})
    out = {name: [i for i in items if i in real][:5] for name, items in found.items()}
    out = {name: items for name, items in out.items() if items}
    write_cache("npc-gear", API, npcs=out)
    print(f"{len(out)} Example characters with named gear")


if __name__ == "__main__":
    main()

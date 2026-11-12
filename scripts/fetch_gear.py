"""What the Example characters of each build wear and wield, per their UESP pages.

Reads the "wears / wields / carries" sentences on each Example's page (builds and variants) and keeps
the armor and weapon items they link to. Writes docs/sources/uesp-npc-gear.json:
  {"retrieved", "source", "npcs": {npc name: [item titles]}}
Generic pieces (boots, plain daggers, hoods) are dropped; the card shows body armor, weapons and shields.
Run fetch_terms.py afterwards: it checks every item on UESP and records where it comes from.
"""
import datetime
import json
import re

import yaml

from common import DATA, ROOT
from fetch_npcs import API, get

OUT = ROOT / "docs" / "sources" / "uesp-npc-gear.json"
GEAR = re.compile(r"(?i)\b(wears?|wearing|clad in|equipped with|dressed in|wields?|carries)\b")
LINK = re.compile(r"\[\[(?:Skyrim|SR):([^|\]#]+)(?:#[^|\]]*)?(?:\|[^\]]*)?\]\]")
KEEP = re.compile(r"(?i)armor|cuirass|robes|sword|axe|mace|bow|shield|staff|hammer|greatsword|dagger of|blade")
DROP = re.compile(r"(?i)^(iron|steel|elven|orcish)? ?dagger$|boots|bracers|gauntlets|helmet|hood$|key$|^trainer"
                  r"|^(bow|sword|shield|armor|mace|war axe|greatsword|battleaxe|warhammer|staff|heavy armor|light armor)$")


def example_pages(doc):
    npcs = json.loads((ROOT / "docs" / "sources" / "uesp-npc-classes.json").read_text())["classes"]
    page = {n["name"]: n["page"] for v in npcs.values() for n in v}
    names = {n for b in doc["builds"] for n in b.get("examples", []) + [x for v in b.get("variants", []) for x in v.get("examples", [])]}
    return {n: page[n] for n in names if n in page}


def main():
    doc = yaml.safe_load((DATA / "builds.yaml").read_text())
    pages = example_pages(doc)
    titles = sorted(set(pages.values()))
    text = {}
    for i in range(0, len(titles), 50):
        d = get(action="query", prop="revisions", rvprop="content", rvslots="main", titles="|".join(titles[i:i + 50]), redirects=1)["query"]
        text.update({p["title"]: p["revisions"][0]["slots"]["main"]["*"] for p in d["pages"].values() if "revisions" in p})
    out = {}
    for name, title in sorted(pages.items()):
        body = re.sub(r"\{\{NPC Summary.*?\n\}\}", "", text.get(title, ""), flags=re.S)
        items = []
        for sent in re.split(r"(?<=[.!?])\s", body):
            if GEAR.search(sent):
                for raw in LINK.findall(sent):
                    item = raw.replace("_", " ").strip()
                    if KEEP.search(item) and not DROP.search(item) and item not in items:
                        items.append(item)
        if items:
            out[name] = items[:5]
    OUT.write_text(json.dumps({"retrieved": datetime.date.today().isoformat(), "source": API, "npcs": out},
                              indent=1, ensure_ascii=False) + "\n")
    print(f"{len(out)} Example characters with named gear")


if __name__ == "__main__":
    main()

"""Every perk in the 18 skill trees, read from UESP's skill pages.

Parses the perk-tree image marks, e.g. "Armsman (5 ranks): 0/20/40/60/80 One-handed. One-Handed weapons do
20/40/60/80/100% more damage." Writes docs/sources/uesp-skill-perks.json:
  {"retrieved", "source", "trees": {skill code: [{"name", "ranks", "levels", "effect"}]}}
"""
import datetime
import json
import re

from common import ROOT, SKILLS
from fetch_npcs import API, get

OUT = ROOT / "docs" / "sources" / "uesp-skill-perks.json"
PAGE = {"1HD": "One-handed", "2HD": "Two-handed"}
# {{Image Mark|x|y|Name|<text>|...}}; the text may be named mark_alt= or "mark alt=", or be the fifth field.
MARK = re.compile(r"\{\{Image Mark\|\d+\|\d+\|[^|]+\|(?:mark[ _]alt=)?([^|}]+)")
ALT = re.compile(r"mark[ _]alt=([^|}]+)")
# The root perk of a tree may give no level ("Steel Smithing: Create Steel armor..."): that means level 0.
ENTRY = re.compile(r"^\s*(?P<name>.+?)(?:\s*\((?P<ranks>\d+) ranks?\))?:\s*(?:(?P<levels>[\d/]+)\s+[A-Za-z' -]+?\.\s*)?(?P<effect>.*)$")


def main():
    titles = {code: "Skyrim:" + PAGE.get(code, name) for code, name in SKILLS.items()}
    d = get(action="query", prop="revisions", rvprop="content", rvslots="main", titles="|".join(titles.values()), redirects=1)["query"]
    norm = {n["from"]: n["to"] for n in d.get("normalized", [])}
    text = {p["title"]: p["revisions"][0]["slots"]["main"]["*"] for p in d["pages"].values() if "revisions" in p}
    trees = {}
    for code, title in titles.items():
        perks = []
        page = text.get(norm.get(title, title), "")
        for raw in MARK.findall(page) + ALT.findall(page):
            m = ENTRY.match(raw.strip())
            if not m or any(p["name"] == m["name"] for p in perks):
                continue
            perks.append({"name": m["name"].strip(), "ranks": int(m["ranks"] or 1),
                          "levels": [int(x) for x in m["levels"].split("/")] if m["levels"] else [0], "effect": m["effect"].strip()})
        trees[code] = sorted(perks, key=lambda p: (p["levels"][0], p["name"]))
    OUT.write_text(json.dumps({"retrieved": datetime.date.today().isoformat(), "source": API, "trees": trees},
                              indent=1, ensure_ascii=False) + "\n")
    print(" ".join(f"{c}:{len(v)}" for c, v in trees.items()))


if __name__ == "__main__":
    main()

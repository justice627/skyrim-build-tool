"""Check every perk, item, spell or power named in builds.yaml `mentions` against UESP.

Writes docs/sources/uesp-terms.json: {"retrieved", "source", "terms": {term: {"page", "section", "missing"}}}.
A term resolves when Skyrim:<term> exists on UESP, directly or through a redirect (perks usually redirect
to their skill page, e.g. Fists of Steel -> Skyrim:Heavy Armor#Fists of Steel). validate.py reads this file;
run this script again after adding or renaming a mention.
"""
import datetime
import json

import yaml

from common import DATA, ROOT
from fetch_npcs import API, get

OUT = ROOT / "docs" / "sources" / "uesp-terms.json"


def mentions(doc):
    out = set()
    for b in doc["builds"]:
        out.update(b.get("mentions", []))
        for e in b.get("lore", []):
            out.update(e.get("mentions", []))
    return sorted(out)


def main():
    doc = yaml.safe_load((DATA / "builds.yaml").read_text())
    terms = mentions(doc)
    result = {}
    for i in range(0, len(terms), 50):
        batch = terms[i:i + 50]
        d = get(action="query", titles="|".join(f"Skyrim:{t}" for t in batch), redirects=1)["query"]
        norm = {n["from"]: n["to"] for n in d.get("normalized", [])}
        redir = {r["from"]: (r["to"], r.get("tofragment", "")) for r in d.get("redirects", [])}
        pages = {p["title"]: p for p in d["pages"].values()}
        for t in batch:
            title = norm.get(f"Skyrim:{t}", f"Skyrim:{t}")
            target, section = redir.get(title, (title, ""))
            p = pages.get(target, {"missing": True})
            result[t] = {"page": target, "section": section, "missing": "missing" in p}
    OUT.write_text(json.dumps({"retrieved": datetime.date.today().isoformat(), "source": API,
                               "terms": result}, indent=1, ensure_ascii=False) + "\n")
    bad = [t for t, r in result.items() if r["missing"] or r["page"] == "Skyrim:Unobtainable Items"]
    print(f"{len(result)} terms, {len(bad)} not usable: {bad}")


if __name__ == "__main__":
    main()

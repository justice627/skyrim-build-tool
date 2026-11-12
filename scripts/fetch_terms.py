"""Check every perk, item, spell or power named in builds.yaml (and every NPC perk) against UESP.

Writes docs/sources/uesp-terms.json: {"retrieved", "source", "terms": {term: {"page", "section", "missing"}}}.
Each term also gets "tree": the skill code (or "werewolf") of the perk tree its page belongs to,
or null when it is not a player perk (items, spells, NPC-only perks).
A term resolves when Skyrim:<term> exists on UESP, directly or through a redirect (perks usually redirect
to their skill page, e.g. Fists of Steel -> Skyrim:Heavy Armor#Fists of Steel). validate.py reads this file;
run this script again after adding or renaming a mention.
"""
import datetime
import json
import re

import yaml

from common import DATA, ROOT, tree_of_page
from fetch_npcs import API, get

OUT = ROOT / "docs" / "sources" / "uesp-terms.json"


def mentions(doc):
    """Every term to check: build and lore `mentions`, community `perks`, and every perk an NPC takes."""
    out = set()
    npcs = json.loads((ROOT / "docs" / "sources" / "uesp-npc-classes.json").read_text())["classes"]
    out.update(p["name"] for v in npcs.values() for n in v for p in n.get("perks", []))
    for b in doc["builds"]:
        out.update(b.get("mentions", []))
        out.update(b.get("perks", {}).get("names", []))
        for e in b.get("lore", []):
            out.update(e.get("mentions", []))
    for k in yaml.safe_load((DATA / "kits.yaml").read_text())["kits"]:
        out.update(k["items"])
        out.update(k.get("mentions", []))
    for m in yaml.safe_load((DATA / "modifiers.yaml").read_text())["modifiers"]:
        out.update(m.get("mentions", []))
    out.update(gear_items(doc))
    return sorted(out)


DLC = {"Dawnguard": "DG", "Dragonborn": "DB", "Hearthfire": "HF"}


def origin(text):
    """Where an item comes from, read from its UESP page header: "CC:<Creation>", "DG", "DB", "HF" or "base"."""
    m = re.search(r"\{\{CC Header\|([^}|]*)", text)
    if m:
        name = m.group(1).strip()
        if "=" in name or not name:  # e.g. {{CC Header|shortcut={{CC|Bow of Shadows}}
            inner = re.search(r"\{\{CC\|([^}|]+)", text)
            name = inner.group(1).strip() if inner else ""
        return DLC.get(name, f"CC:{name}")
    for dlc, tag in DLC.items():
        if f"Category:Skyrim-{dlc}" in text[:3000]:
            return tag
    return "base"


def gear_items(doc):
    """Signature gear on builds, variants and lore picks, plus what Example characters wear."""
    out = set()
    for b in doc["builds"]:
        out.update(b.get("signature", []))
        for v in b.get("variants", []) + b.get("lore", []):
            out.update(v.get("signature", []))
    worn = ROOT / "docs" / "sources" / "uesp-npc-gear.json"
    if worn.exists():
        out.update(i for items in json.loads(worn.read_text())["npcs"].values() for i in items)
    return out


def section_origin(text, anchor):
    """Origin of an item that is one row of a shared page (Indoril Armor on Skyrim:Chitin), read from the
    row's name cell only: notes columns mention Creation locations that say nothing about the item."""
    head = re.search(r"\n=+\s*" + re.escape(anchor) + r"([^\n]*?)=+\s*\n", text)
    if head:  # a section of its own, e.g. ===Indoril Armor{{CC|Ghosts of the Tribunal}}===
        cc = re.search(r"\{\{CC\|([^}|]+)", head.group(1))
        if cc:
            return DLC.get(cc.group(1).strip(), "CC:" + cc.group(1).strip())
        for dlc, tag in DLC.items():
            if "{{" + tag + "}}" in head.group(1):
                return tag
    i = text.find("Anchor|" + anchor)
    if i < 0:
        return None
    start = text.rfind("\n|", 0, i)
    end = min(x for x in (text.find("||", i), text.find("\n", i)) if x > 0)
    cell = text[start if start >= 0 else i:end]
    cc = re.search(r"\{\{CC\|([^}|]+)", cell)
    if cc:
        return DLC.get(cc.group(1).strip(), "CC:" + cc.group(1).strip())
    for dlc, tag in DLC.items():
        if "{{" + tag + "}}" in cell:
            return tag
    return None


def kit_items():
    return sorted({i for k in yaml.safe_load((DATA / "kits.yaml").read_text())["kits"] for i in k["items"]})


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
    # Perk trees: a term whose page is a skill (or Lycanthropy) page is a player perk of that tree.
    # Some perks share a title with another page (Barbarian, Ranger, Stealth, Necromage); UESP keeps
    # "<name> (perk)" redirects for those, so try that when the plain title is not a skill page.
    retry = [t for t, r in result.items() if not tree_of_page(r["page"])]
    for i in range(0, len(retry), 50):
        batch = retry[i:i + 50]
        d = get(action="query", titles="|".join(f"Skyrim:{t} (perk)" for t in batch), redirects=1)["query"]
        redir = {r["from"]: r["to"] for r in d.get("redirects", [])}
        for t in batch:
            target = redir.get(f"Skyrim:{t} (perk)")
            if target and tree_of_page(target):
                result[t]["perk_page"] = target
    for t, r in result.items():
        r["tree"] = tree_of_page(r.get("perk_page") or r["page"])
    # Origins for kit and gear items, from each item's own page header, or its own row on a shared page.
    items = sorted(set(kit_items()) | {t for t in gear_items(doc) if t in result and not result[t]["missing"]})
    for i in range(0, len(items), 50):
        batch = items[i:i + 50]
        d = get(action="query", prop="revisions", rvprop="content", rvslots="main",
                titles="|".join(result[t]["page"] for t in batch))["query"]["pages"]
        text = {p["title"]: p["revisions"][0]["slots"]["main"]["*"] for p in d.values() if "revisions" in p}
        for t in batch:
            page_text = text.get(result[t]["page"], "")
            section = result[t]["section"]
            result[t]["origin"] = (section and section_origin(page_text, section)) or origin(page_text)
    OUT.write_text(json.dumps({"retrieved": datetime.date.today().isoformat(), "source": API,
                               "terms": result}, indent=1, ensure_ascii=False) + "\n")
    named = {t for b in doc["builds"] for t in b.get("mentions", []) + [m for e in b.get("lore", []) for m in e.get("mentions", [])]}
    bad = [t for t in sorted(named) if result[t]["missing"] or result[t]["page"] == "Skyrim:Unobtainable Items"]
    perks = sum(1 for r in result.values() if r["tree"])
    print(f"{len(result)} terms ({perks} player perks); build mentions not usable: {bad or 'none'}")


if __name__ == "__main__":
    main()

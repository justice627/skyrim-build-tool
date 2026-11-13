"""Fetch which named NPCs use each class in data/classes.json, from UESP's MediaWiki API.

Writes data/uesp/uesp-npc-classes.json:
  {"retrieved": date, "source": api url, "classes": {EditorID: [{"name", "page", "size"}, ...]}}

An NPC counts for a class when its NPC Summary infobox has class_details=[[Skyrim:<EditorID>|...]],
or, without that, a class name that matches exactly one EditorID in the Skyrim:Classes table.
`perks` is the NPC Summary's perk list as UESP gives it (NPC-only perks included; build.py keeps
only perks that UESP files under a skill tree). `size` is the NPC page's length in bytes, used to list better-known NPCs first.
Pages that hold more than one NPC Summary (generic soldiers, unused NPCs) are skipped.
Run it by hand when the data needs refreshing; build.py and validate.py only read the saved file.
"""
import json
import re

from common import DATA, cache_path, write_cache
from uesp import API, batches, get, page_text

SKYRIM_NS = 134


def npc_pages():
    """Every Skyrim-namespace page that uses the NPC Summary infobox."""
    out, cont = [], {}
    while True:
        d = get(action="query", list="embeddedin", eititle="Template:NPC Summary",
                einamespace=SKYRIM_NS, eilimit=500, **cont)
        out += [e["title"] for e in d["query"]["embeddedin"]]
        if "continue" not in d:
            return out
        cont = d["continue"]


def class_names():
    """Class display name -> EditorIDs, read from the class table on Skyrim:Classes."""
    return class_names_in(page_text("Skyrim:Classes"))


def class_names_in(wikitext):
    names = {}
    for row in wikitext.split("\n|-"):
        cells = [c.strip() for c in row.strip().split("\n") if c.startswith("|")]
        if len(cells) < 2:
            continue
        name, eid = (re.sub(r"\{\{(?:Anchor\|)?([^}]*)\}\}", r"\1", c.lstrip("|")).strip() for c in cells[:2])
        name = re.sub(r"(DG|DB|HF|CC)$", "", name).strip()
        names.setdefault(name, set()).add(eid)
    return names


def pages(titles):
    """Wikitext and length for up to 50 titles at a time."""
    out = {}
    for batch in batches(titles):
        d = get(action="query", prop="revisions|info", rvprop="content", rvslots="main", titles="|".join(batch))
        for p in d["query"]["pages"].values():
            if "revisions" in p:
                out[p["title"]] = (p["revisions"][0]["slots"]["main"]["*"], p.get("length", 0))
    return out


def link_text(v):
    """'[[Skyrim:Blade (class)|Blade]]' or 'Blade' -> 'Blade'."""
    m = re.match(r"\[\[([^|\]]+)(?:\|([^\]]+))?\]\]", v)
    if m:
        v = m.group(2) or m.group(1).split(":", 1)[-1]
    return re.sub(r"\s*\(class\)$", "", v).strip()


SUMMARY = re.compile(r"\{\{NPC Summary(.*?)\n\}\}", re.S)


def summaries(text):
    for m in SUMMARY.finditer(text):
        body = m.group(1)
        name = re.search(r"\|\s*name\s*=\s*([^\n|]+)", body)
        det = re.search(r"\|\s*class_details\s*=\s*\[\[Skyrim:([^|\]]+)", body)
        cls = re.search(r"\|\s*class\s*=\s*([^\n]+)", body)
        yield ((name.group(1).strip() if name else None), (det.group(1).strip() if det else None),
               (link_text(cls.group(1).strip()) if cls else None))


def perks_of(text):
    """Perks from the NPC Summary's perks= field: [{"name", "rank"}]. "None" or empty gives []."""
    m = SUMMARY.search(text)
    f = re.search(r"\|\s*perks\s*=([^\n]*)", m.group(1)) if m else None
    out = []
    for item in (f.group(1).split(";") if f else []):
        rank = re.search(r"\((?:rank|Rank)\s*(\d+)\)", item)
        item = re.sub(r"\((?:rank|Rank)\s*\d+\)", "", item)
        name = link_text(item.strip()) if "[[" in item else re.sub(r"<[^>]+>|\{\{[^}]*\}\}", "", item).strip()
        if name and name.lower() != "none":
            out.append({"name": name, "rank": int(rank.group(1)) if rank else None})
    return out


def main():
    classes = json.loads((DATA / "classes.json").read_text())
    names = class_names()
    titles = npc_pages()
    print(f"{len(titles)} NPC pages")
    result = {eid: [] for eid in classes}
    for title, (text, size) in pages(titles).items():
        found = list(dict.fromkeys(summaries(text)))  # one NPC with two identical infoboxes counts once
        if len(found) != 1:  # pages such as "Imperial Soldier" or "Unused NPCs" describe many NPCs
            continue
        for name, detail, cname in found:
            if detail in classes:
                eid, how = detail, "class_details"
            elif not detail and cname:
                ids = [e for e in names.get(cname, ()) if e in classes]
                if len(ids) != 1:
                    continue
                eid, how = ids[0], "class name"
            else:
                continue
            result[eid].append({"name": name or title.split(":", 1)[1], "page": title, "size": size,
                                "matched_by": how, "perks": perks_of(text)})
    for found in result.values():
        found.sort(key=lambda n: (-n["size"], n["name"]))
    write_cache("npc-classes", API, classes=result)
    print("\n".join(f"{e}: {len(v)} {[n['name'] for n in v[:4]]}" for e, v in result.items()))
    print(f"Wrote {cache_path('npc-classes')}")


if __name__ == "__main__":
    main()

"""Fetch which named NPCs use each class in data/classes.json, from UESP's MediaWiki API.

Writes docs/sources/uesp-npc-classes.json:
  {"retrieved": date, "source": api url, "classes": {EditorID: [{"name", "page", "size"}, ...]}}

An NPC counts for a class when its NPC Summary infobox has class_details=[[Skyrim:<EditorID>|...]],
or, without that, a class name that matches exactly one EditorID in the Skyrim:Classes table.
`size` is the NPC page's length in bytes, used to list better-known NPCs first.
Pages that hold more than one NPC Summary (generic soldiers, unused NPCs) are skipped.
Run it by hand when the data needs refreshing; build.py and validate.py only read the saved file.
"""
import datetime
import json
import re
import time
import urllib.parse
import urllib.request

from common import DATA, ROOT

API = "https://en.uesp.net/w/api.php"
UA = "skyrim-build-tool/1.0 (static reference page; low request rate)"
OUT = ROOT / "docs" / "sources" / "uesp-npc-classes.json"
SKYRIM_NS = 134


def get(**params):
    params["format"] = "json"
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                time.sleep(0.3)
                return json.load(r)
        except Exception:
            time.sleep(2 ** (attempt + 1))
    raise RuntimeError(f"failed: {url}")


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
    d = get(action="parse", page="Skyrim:Classes", prop="wikitext")
    names = {}
    for row in d["parse"]["wikitext"]["*"].split("\n|-"):
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
    for i in range(0, len(titles), 50):
        d = get(action="query", prop="revisions|info", rvprop="content", rvslots="main",
                titles="|".join(titles[i:i + 50]))
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
                                "matched_by": how})
    for found in result.values():
        found.sort(key=lambda n: (-n["size"], n["name"]))
    OUT.write_text(json.dumps({"retrieved": datetime.date.today().isoformat(), "source": API,
                               "classes": result}, indent=1, ensure_ascii=False) + "\n")
    print("\n".join(f"{e}: {len(v)} {[n['name'] for n in v[:4]]}" for e, v in result.items()))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()

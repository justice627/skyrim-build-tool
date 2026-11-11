"""Render the data into the page.

Writes two files to dist/:
- index.html     a full HTML document for GitHub Pages or opening locally
- artifact.html  the same page without the document skeleton, for publishing as a claude.ai artifact
"""
import json
import re

from common import (ATTRS, BEAST_FORMS, ROOT, SCHOOL, SKILLS, by_id, card_weights, load, load_lookup, npc_classes,
                    weights)

LEVELS = 49  # level-ups from level 2 to 50


def tiers(w, keep):
    skills = sorted(((k, v) for k, v in w.items() if k in SKILLS), key=lambda kv: -kv[1])
    return [{"s": SKILLS[k], "w": v, "sc": SCHOOL[k]} for k, v in skills if keep(v)]


def split(ratio, total=LEVELS):
    """Spread level-ups over Health/Magicka/Stamina by ratio, largest remainders first."""
    s = sum(ratio)
    raw = [total * x / s for x in ratio]
    out = [int(x) for x in raw]
    for i in sorted(range(3), key=lambda i: -(raw[i] - out[i]))[: total - sum(out)]:
        out[i] += 1
    return out


def plan(w):
    """The player's attribute plan: the NPC ratio, moved where the NPC file wastes points."""
    h, m, s = (w.get(a, 0) for a in ATTRS)
    magic = sum(v for k, v in w.items() if k in SKILLS and SCHOOL[k] == "m")
    total = sum(v for k, v in w.items() if k in SKILLS) or 1
    if m > 0 and magic == 0:
        return [h, 0, s + m], "Magicka moved to Stamina: this class has no spells."
    if m == 0 and magic / total >= 0.4:
        return [h, s, 0], "Stamina moved to Magicka: this class is mostly spells."
    return [h, m, s], ""


def skill_line(w):
    skills = sorted(((k, v) for k, v in w.items() if k in SKILLS), key=lambda kv: -kv[1])
    return " · ".join(f"{SKILLS[k]} {v}" for k, v in skills)


def render_picks(b, stones, shouts, books):
    """Stone, shouts and requirement tags. Requirements are the build's own plus each shout's."""
    st = b["stone"]
    stone = {"early": stones[st["early"]]["name"], "early_fx": stones[st["early"]]["effect"],
             "ev": st["evidence"]}
    if st.get("final"):
        stone.update(final=stones[st["final"]]["name"], final_fx=stones[st["final"]]["effect"])
    picked = [shouts[i] for i in b["shouts"]["ids"]]
    req = set(b.get("requires", [])) | {s["requires"] for s in picked} | {stones[st["early"]]["requires"]}
    beast = book = None
    if "beast_form" in b:
        beast_name, beast_req = BEAST_FORMS[b["beast_form"]]
        beast, req = beast_name, req | {beast_req}
    if "black_book" in b:
        bb = b["black_book"]
        bk = books[bb["book"]]
        fx = next(p["effect"] for p in bk["powers"] if p["name"] == bb["power"])
        book, req = {"book": bk["name"], "power": bb["power"], "fx": fx, "ev": bb["evidence"]}, req | {bk["requires"]}
    req.discard("vanilla")
    order = ("DG", "HF", "DB", "CC", "AE")
    return {
        "stone": stone,
        "shouts": {"list": [{"n": s["name"], "fx": s["effect"], "req": s["requires"]} for s in picked],
                   "ev": b["shouts"]["evidence"]},
        "req": [r for r in order if r in req], "beast": beast, "book": book,
    }


def npc_name(page_name):
    """'Miraak (person)' -> 'Miraak': UESP disambiguates pages, the page shows the character's name."""
    return re.sub(r"\s*\([^)]*\)$", "", page_name)


def render_lore(b, build_of_npc):
    """Ledger C picks. `where` names the build the NPC's own UESP class sits in, when that is another build."""
    out = []
    for e in b.get("lore", []):
        home = build_of_npc.get(e.get("npc"))
        out.append({"n": e["name"], "ref": e["ref"], "changes": e["changes"], "ev": e["evidence"],
                    "req": e.get("requires", []), "npc": npc_name(e["npc"]) if "npc" in e else "",
                    "where": home if home and home != b["name"] else ""})
    return out


def npc_homes(doc):
    """NPC name -> name of the build that holds the NPC's class."""
    build_of_class = {}
    for b in doc["builds"]:
        for e in b.get("classes", []) + [c for v in b.get("variants", []) for c in v["classes"]]:
            build_of_class[e] = b["name"]
    return {n: build_of_class[e] for e, names in npc_classes().items() for n in names if e in build_of_class}


def render_build(b, classes, stones, shouts, books, homes):
    w = card_weights(b, classes)
    hand = "weights" in b
    # A hand-set ratio is already a player recommendation, so plan() does not adjust it.
    attrs, why = ([w[a] for a in ATTRS], "") if hand else plan(w)
    variants = []
    for v in b.get("variants", []):
        vw = weights(classes, v["classes"][0])
        variants.append({"label": v["label"], "eids": v["classes"], "skills": skill_line(vw),
                         "npcs": [npc_name(n) for n in v.get("examples", [])],
                         "attr": [vw.get(a, 0) for a in ATTRS]})
    return {
        "fam": b["family"], "name": b["name"], "insp": b["inspired_by"], "eids": b.get("classes", []),
        "hand": hand, "ref": b.get("ref", ""), "mentions": b.get("mentions", []),
        "p": tiers(w, lambda v: v >= 3), "s": tiers(w, lambda v: v == 2), "m": tiers(w, lambda v: v == 1),
        "npc": [w.get(a, 0) for a in ATTRS], "plan": attrs, "lv50": split(attrs), "why": why,
        "variants": variants, "desc": b["description"],
        "npcs": [npc_name(n) for n in b.get("examples", [])], "aka": b.get("aliases", []),
        "lore": render_lore(b, homes), "ev": b["evidence"], **render_picks(b, stones, shouts, books),
    }


def render_race(r):
    return {"race": r["race"], "sig": r["signature"], "plus5": r["plus5"], "attr": r["attributes"],
            "lv50": split(r["attributes"]), "note": r["note"], "power": r["power"]}


def page_data():
    classes, doc, races = load()
    stones, shouts = by_id(load_lookup("stones")), by_id(load_lookup("shouts"))
    homes = npc_homes(doc)
    books = by_id(load_lookup("black_books"))
    return {
        "fams": doc["families"],
        "builds": [render_build(b, classes, stones, shouts, books, homes) for b in doc["builds"]],
        "races": [render_race(r) for r in races],
    }


SKELETON = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<style>:root{{color-scheme:light;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}body{{margin:0;font:14px system-ui,-apple-system,"Segoe UI",sans-serif}}img{{max-width:100%}}[hidden]{{display:none!important}}</style>
</head>
<body>
{page}
</body>
</html>
"""


def main():
    template = (ROOT / "src" / "template.html").read_text()
    data = json.dumps(page_data(), ensure_ascii=False)
    page = template.replace("__DATA__", data)
    out = ROOT / "dist"
    out.mkdir(exist_ok=True)
    (out / "artifact.html").write_text(page)
    (out / "index.html").write_text(SKELETON.format(page=page))
    print(f"Wrote {out / 'index.html'} and {out / 'artifact.html'}")


if __name__ == "__main__":
    main()

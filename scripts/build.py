"""Render the data into the page.

Writes two files to dist/:
- index.html     a full HTML document for GitHub Pages or opening locally
- artifact.html  the same page without the document skeleton, for publishing as a claude.ai artifact
"""
import json
import re

import json as _json

from common import (ARMOR, ATTRS, BEAST_FORMS, HANDS, ROOT, SCHOOL, SKILLS, by_id, card_weights, early_perks, load,
                    load_lookup, loadout, npc_classes, playstyles, race_fit, uesp_terms, weights)

SPELL_SCHOOLS = ("ALT", "CON", "DES", "ILU", "RES")
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
    # Spell schools only: Enchanting is a magic skill but costs no Magicka to use.
    magic = sum(v for k, v in w.items() if k in SPELL_SCHOOLS)
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


def skills_of(b, classes):
    return {k: v for k, v in card_weights(b, classes).items() if k in SKILLS}


def npc_name(page_name):
    """'Miraak (person)' -> 'Miraak': UESP disambiguates pages, the page shows the character's name."""
    return re.sub(r"\s*\([^)]*\)$", "", page_name)


def render_lore(b, build_of_npc, terms):
    """Ledger C picks. `where` names the build the NPC's own UESP class sits in, when that is another build."""
    out = []
    for e in b.get("lore", []):
        home = build_of_npc.get(e.get("npc"))
        out.append({"n": e["name"], "ref": e["ref"], "changes": e["changes"], "ev": e["evidence"],
                    "req": e.get("requires", []), "npc": npc_name(e["npc"]) if "npc" in e else "",
                    "sig": [{"n": i, "tag": gear_tag(i, terms)} for i in e.get("signature", [])],
                    "where": home if home and home != b["name"] else ""})
    return out


def npc_homes(doc):
    """NPC name -> name of the build that holds the NPC's class."""
    build_of_class = {}
    for b in doc["builds"]:
        for e in b.get("classes", []) + [c for v in b.get("variants", []) for c in v["classes"]]:
            build_of_class[e] = b["name"]
    return {n: build_of_class[e] for e, names in npc_classes().items() for n in names if e in build_of_class}


def class_perks(eids, w, npcs, terms):
    """Perks that named NPCs of these classes take, kept only when UESP files the perk under a skill
    on this card. Grouped by skill (highest weight first); within a skill, perks more NPCs take come first."""
    takers = {}
    for e in eids:
        for n in npcs.get(e, []):
            for p in n.get("perks", []):
                tree = (terms.get(p["name"]) or {}).get("tree")
                if tree in w and tree in SKILLS:
                    takers.setdefault((tree, p["name"]), []).append(npc_name(n["name"]))
    return group_perks(takers, w)


def group_perks(takers, w):
    order = sorted({t for t, _ in takers}, key=lambda t: (-w.get(t, 0), list(SKILLS).index(t) if t in SKILLS else 99))
    out = []
    for t in order:
        ps = sorted(((n, by) for (tt, n), by in takers.items() if tt == t), key=lambda x: (-len(x[1]), x[0]))
        out.append({"s": SKILLS.get(t, "Werewolf"), "sc": SCHOOL.get(t, "c"),
                    "perks": [{"n": n, "by": sorted(set(by))} for n, by in ps]})
    return out


def hand_perks(b, w, terms):
    """Community builds: the perks their ledger row names, kept when they sit in a card skill or the werewolf tree."""
    pk = b.get("perks")
    if not pk:
        return []
    takers = {}
    for n in pk["names"]:
        tree = terms[n]["tree"]
        if tree in w or tree == "werewolf":
            takers[(tree, n)] = []
    return group_perks(takers, w)


def gear_tag(item, terms):
    o = terms[item].get("origin", "base")
    return "" if o == "base" else (o if not o.startswith("CC:") else "CC")


def render_gear(b, skills, terms, worn):
    """Gear line: signature sets (sourced, with DLC/CC tags), then the loadout (suggested)."""
    lo = loadout(skills, b.get("loadout"))
    sig = [{"n": i, "tag": gear_tag(i, terms), "cc": terms[i].get("origin", "")[3:] if terms[i].get("origin", "").startswith("CC:") else ""}
           for i in b.get("signature", [])]
    people = b.get("examples", []) + [n for v in b.get("variants", []) for n in v.get("examples", [])]
    seen = []
    for n in people:
        items = [i for i in worn.get(n, []) if i in terms and not terms[i]["missing"]]
        if items and len(seen) < 3:
            seen.append({"npc": npc_name(n), "items": [{"n": i, "tag": gear_tag(i, terms)} for i in items[:3]]})
    return {"armor": ARMOR[lo["armor"]], "hands": [HANDS[h] for h in lo["hands"]], "sig": sig, "worn": seen}


def tree_perks(skills, shown, trees, lo=None):
    """Early skill-tree perks for each primary skill the card shows no perk for (NPC or ledger perks).
    A build with no primary skill (Monk, Vigilant) falls back to its secondary skills, skipping Block
    without a shield and armor its loadout does not wear, at most three trees."""
    covered = {g["s"] for g in shown}
    have = {p["n"] for g in shown for p in g["perks"]}
    out = []
    floor = 3 if any(v >= 3 for v in skills.values()) else 2
    skip = set()
    if floor == 2 and lo:
        if "shield" not in lo["hands"]:
            skip.add("BLO")
        if lo["armor"] not in ("light",):
            skip.add("LTA")
        if lo["armor"] not in ("heavy", "robes-heavy"):
            skip.add("HVA")
    order = sorted(skills.items(), key=lambda kv: (-kv[1], list(SKILLS).index(kv[0])))
    for k, v in order:
        if len(out) >= 3 and floor == 2:
            break
        if v >= floor and k not in skip and SKILLS[k] not in covered:
            ps = early_perks(trees, k, have)
            if ps:
                out.append({"s": SKILLS[k], "sc": SCHOOL[k], "perks": ps})
    return out


def render_build(b, classes, stones, shouts, books, homes, npcs, terms, worn, races=None, trees=None):
    w = card_weights(b, classes)
    hand = "weights" in b
    # A hand-set ratio is already a player recommendation, so plan() does not adjust it.
    attrs, why = ([w[a] for a in ATTRS], "") if hand else plan(w)
    skills = {k: x for k, x in w.items() if k in SKILLS}
    variants = []
    for v in b.get("variants", []):
        vw = weights(classes, v["classes"][0])
        vskills = {k: x for k, x in vw.items() if k in SKILLS}
        variants.append({"label": v["label"], "eids": v["classes"], "skills": skill_line(vw),
                         "sig": [{"n": i, "tag": gear_tag(i, terms)} for i in v.get("signature", [])],
                         "perks": class_perks(v["classes"], vskills, npcs, terms),
                         "npcs": [npc_name(n) for n in v.get("examples", [])],
                         "attr": [vw.get(a, 0) for a in ATTRS]})
    return {
        "id": b["id"], "styles": b.get("playstyles") or playstyles(skills), "fam": b["family"], "name": b["name"], "insp": b["inspired_by"], "eids": b.get("classes", []),
        "hand": hand, "ref": b.get("ref", ""), "play": b.get("play", ""),
        "gear": render_gear(b, skills_of(b, classes), terms, worn),
        "races": race_fit(skills_of(b, classes), races or []), "mentions": b.get("mentions", []),
        "p": tiers(w, lambda v: v >= 3), "s": tiers(w, lambda v: v == 2), "m": tiers(w, lambda v: v == 1),
        "npc": [w.get(a, 0) for a in ATTRS], "plan": attrs, "lv50": split(attrs), "why": why,
        "variants": variants, "desc": b["description"],
        "npcs": [npc_name(n) for n in b.get("examples", [])], "aka": b.get("aliases", []),
        "lore": render_lore(b, homes, terms),
        "perks": hand_perks(b, skills, terms) if hand else class_perks(b["classes"], skills, npcs, terms),
        "tree": tree_perks(skills, hand_perks(b, skills, terms) if hand else class_perks(b["classes"], skills, npcs, terms),
                           trees or {}, loadout(skills, b.get("loadout"))),
        "perk_ev": b["perks"]["evidence"] if hand and b.get("perks") else ("sourced" if not hand else ""),
        "perk_ref": b["perks"].get("ref", "") if hand and b.get("perks") else "", "ev": b["evidence"], **render_picks(b, stones, shouts, books),
    }


def kit_tags(items, terms):
    """Requirement tags for a kit, read from where UESP says each item comes from."""
    origins = [terms[i]["origin"] for i in items]
    dlc = [o for o in ("DG", "DB", "HF") if o in origins]
    creations = sorted({o[3:] for o in origins if o.startswith("CC:")})
    return dlc, creations


def render_kits(kits, terms):
    by_build = {}
    for k in kits:
        dlc, creations = kit_tags(k["items"], terms)
        base = [i for i in k["items"] if terms[i]["origin"] == "base"]
        entry = {"n": k["name"], "ref": k["ref"], "items": k["items"], "note": k["note"], "ev": k["evidence"],
                 "dlc": dlc, "cc": creations, "base": base}
        for b in k["fits"]:
            by_build.setdefault(b, []).append(entry)
    return by_build


def render_race(r):
    code = {n: c for c, n in SKILLS.items()}
    w = {code[s]: 1 for s in r["plus5"]} | {code[r["signature"]]: 2}
    return {"styles": playstyles(w, min_weight=1), "race": r["race"], "sig": r["signature"], "plus5": r["plus5"], "attr": r["attributes"],
            "lv50": split(r["attributes"]), "note": r["note"], "power": r["power"]}


def page_data():
    classes, doc, races = load()
    stones, shouts = by_id(load_lookup("stones")), by_id(load_lookup("shouts"))
    homes = npc_homes(doc)
    kits_by_build = render_kits(load_lookup("kits"), uesp_terms())
    mods = load_lookup("modifiers")
    name_of = {b["id"]: b["name"] for b in doc["builds"]}
    books = by_id(load_lookup("black_books"))
    npcs = _json.loads((ROOT / "docs" / "sources" / "uesp-npc-classes.json").read_text())["classes"]
    terms = uesp_terms()
    worn = _json.loads((ROOT / "docs" / "sources" / "uesp-npc-gear.json").read_text())["npcs"]
    trees = _json.loads((ROOT / "docs" / "sources" / "uesp-skill-perks.json").read_text())["trees"]
    return {
        "fams": doc["families"],
        "builds": [dict(render_build(b, classes, stones, shouts, books, homes, npcs, terms, worn, races, trees),
                        kits=kits_by_build.get(b["id"], []),
                        mods=[m["name"] for m in mods if b["id"] in m["pairs"]]) for b in doc["builds"]],
        "mods": [{"n": m["name"], "rule": m["rule"], "ref": m["ref"], "ev": m["evidence"],
                  "pairs": [name_of[p] for p in m["pairs"]]} for m in mods],
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

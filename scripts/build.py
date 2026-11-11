"""Render the data into the page.

Writes two files to dist/:
- index.html     a full HTML document for GitHub Pages or opening locally
- artifact.html  the same page without the document skeleton, for publishing as a claude.ai artifact
"""
import json

from common import ATTRS, DATA, ROOT, SCHOOL, SKILLS, load, weights

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


def render_build(b, classes):
    w = weights(classes, b["classes"][0])
    attrs, why = plan(w)
    variants = []
    for v in b.get("variants", []):
        vw = weights(classes, v["classes"][0])
        variants.append({"label": v["label"], "eids": v["classes"], "skills": skill_line(vw),
                         "attr": [vw.get(a, 0) for a in ATTRS]})
    return {
        "fam": b["family"], "name": b["name"], "insp": b["inspired_by"], "eids": b["classes"],
        "p": tiers(w, lambda v: v >= 3), "s": tiers(w, lambda v: v == 2), "m": tiers(w, lambda v: v == 1),
        "npc": [w.get(a, 0) for a in ATTRS], "plan": attrs, "lv50": split(attrs), "why": why,
        "variants": variants, "desc": b["description"],
    }


def render_race(r):
    return {"race": r["race"], "sig": r["signature"], "plus5": r["plus5"], "attr": r["attributes"],
            "lv50": split(r["attributes"]), "note": r["note"], "power": r["power"]}


def page_data():
    classes, doc, races = load()
    return {
        "fams": doc["families"],
        "builds": [render_build(b, classes) for b in doc["builds"]],
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

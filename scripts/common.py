"""Shared loading and game constants for validate.py and build.py."""
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
UESP = DATA / "uesp"  # caches the fetch scripts write and the build reads

# Column codes as UESP's class table uses them, in UESP order.
SKILLS = {
    "ARC": "Archery", "BLO": "Block", "HVA": "Heavy Armor", "1HD": "One-Handed",
    "SMI": "Smithing", "2HD": "Two-Handed", "ALT": "Alteration", "CON": "Conjuration",
    "DES": "Destruction", "ENC": "Enchanting", "ILU": "Illusion", "RES": "Restoration",
    "ALC": "Alchemy", "LTA": "Light Armor", "LOC": "Lockpicking", "PIC": "Pickpocket",
    "SNK": "Sneak", "SPE": "Speech",
}
ATTRS = ("Hea", "Mag", "Sta")
# Skill school: c = combat (warrior), m = magic (mage), s = stealth (thief).
SCHOOL = {code: ("c" if i < 6 else "m" if i < 12 else "s") for i, code in enumerate(SKILLS)}
SCHOOL_BY_NAME = {SKILLS[c]: s for c, s in SCHOOL.items()}
# Requirement tags: base game, Dawnguard, Hearthfire, Dragonborn, paid Creation, Anniversary Edition.
# Mod is left out on purpose: mod-only builds are out of scope.
REQUIRES = ("vanilla", "DG", "HF", "DB", "CC", "AE")
EVIDENCE = ("sourced", "partly-sourced", "derived")
# Beast forms a build can be played in: id -> (name, requirement). Lycanthropy is base game;
# the werewolf perk tree and the Vampire Lord come with Dawnguard.
BEAST_FORMS = {"werewolf": ("Werewolf", "vanilla"), "vampire-lord": ("Vampire Lord", "DG")}
UNUSABLE_PAGES = ("Skyrim:Unobtainable Items",)


def load():
    classes = json.loads((DATA / "classes.json").read_text())
    builds = yaml.safe_load((DATA / "builds.yaml").read_text())
    races = yaml.safe_load((DATA / "races.yaml").read_text())["races"]
    return classes, builds, races


def cache(name):
    """A saved UESP read: cache("terms") is data/uesp/uesp-terms.json."""
    return json.loads(cache_path(name).read_text())


def cache_path(name):
    return UESP / f"uesp-{name}.json"


def write_cache(name, source, **body):
    """Save a UESP read with the day it was made."""
    import datetime
    doc = {"retrieved": datetime.date.today().isoformat(), "source": source, **body}
    cache_path(name).write_text(json.dumps(doc, indent=1, ensure_ascii=False) + "\n")


def load_lookup(name):
    """A list file such as stones.yaml, as a list of entries (ids may repeat; validate.py checks)."""
    return yaml.safe_load((DATA / f"{name}.yaml").read_text())[name]


def npc_classes():
    """EditorID -> names of single-NPC UESP pages using that class (data/uesp/uesp-npc-classes.json)."""
    return {eid: {n["name"] for n in npcs} for eid, npcs in cache("npc-classes")["classes"].items()}


def skills_in_text(text):
    """Skill codes named in free text such as a lore pick's `changes` ("fire Destruction" counts)."""
    low = text.lower()
    return {c for c, n in SKILLS.items() if re.search(r"\b" + re.escape(n.lower()) + r"\b", low)}


_TREE_PAGES = {f"skyrim:{n.lower()}": c for c, n in SKILLS.items()}
_TREE_PAGES["skyrim:lycanthropy"] = "werewolf"


def tree_of_page(page):
    """Skill code for a UESP skill page ("Skyrim:One-handed" -> "1HD"), "werewolf" for Lycanthropy, else None."""
    return _TREE_PAGES.get(page.lower()) if page else None


# Playstyle filter: the skills that decide how a build plays. Weapons and the armor and block that go
# with them count as combat; the five spell schools as magic; sneaking and thieving as stealth.
# Smithing, Enchanting, Alchemy, Speech and Light Armor support any style, so they are left out
# (the game files Light Armor under thief skills, which made a Barbarian read as stealth).
PLAYSTYLE = {"c": ("1HD", "2HD", "BLO", "HVA", "ARC"), "m": ("ALT", "CON", "DES", "ILU", "RES"),
             "s": ("SNK", "PIC", "LOC")}
CRAFT = ("SMI", "ENC", "ALC", "SPE")  # "Craft & trade": tagged only when it outweighs every fighting style
STYLE_CODES = ("c", "m", "s", "k")


def playstyles(w, min_weight=2, share=0.3):
    """Styles a build plays as: combat, magic or stealth when that style's skills (weight 2 or more) hold
    at least 30% of the fighting total; "k" (craft and trade) when Smithing, Enchanting, Alchemy and Speech
    weigh at least as much as the biggest fighting style. builds.yaml may override with `playstyles`."""
    sums = {st: sum(v for k, v in w.items() if k in ks and v >= min_weight) for st, ks in PLAYSTYLE.items()}
    total = sum(sums.values())
    out = [st for st, v in sums.items() if total and v / total >= share]
    craft = sum(v for k, v in w.items() if k in CRAFT and v >= min_weight)
    if craft and craft >= max(sums.values()):
        out.append("k")
    return out


ARMOR = {"heavy": "Heavy armor", "light": "Light armor", "robes": "Robes", "clothes": "Clothes",
         "robes-heavy": "Robes, steel boots and gauntlets"}
HANDS = {"one-handed": "One-handed weapon", "dual": "A weapon in each hand", "shield": "Shield",
         "two-handed": "Two-handed weapon", "bow": "Bow", "spells": "Spells", "staff": "Staff", "fists": "Fists"}


def loadout(w, override=None):
    """Recommended armor and hands from the card's skills (a suggestion, rule 7). builds.yaml may override."""
    if override:
        return {"armor": override["armor"], "hands": list(override["hands"])}
    g = lambda k: w.get(k, 0)
    spells = sum(1 for k in ("ALT", "CON", "DES", "ILU", "RES") if g(k) >= 2)
    if g("HVA") >= 2 and g("HVA") >= g("LTA"):
        armor = "heavy"
    elif g("LTA") >= 2:
        armor = "light"
    elif max(g("HVA"), g("LTA")) >= 1:
        armor = "heavy" if g("HVA") > g("LTA") else "light"
    elif spells:
        armor = "robes"
    else:
        armor = "clothes"
    hands = []
    if g("2HD") >= 2 and g("2HD") > g("1HD"):
        hands.append("two-handed")
    elif g("1HD") >= 2:
        hands.append("one-handed")
    if g("BLO") >= 2 and "two-handed" not in hands:
        hands.append("shield")
    if g("ARC") >= 3:
        hands.insert(0, "bow") if g("ARC") > max(g("1HD"), g("2HD")) else hands.append("bow")
    if spells:
        hands.append("spells") if hands else hands.insert(0, "spells")
    if not hands and g("1HD") >= 1:
        hands.append("one-handed")
    return {"armor": armor, "hands": hands}


def race_fit(w, races):
    """Races whose starting skill bonuses best match a build: score = sum of skill weight x race bonus over the
    build's skills weighted 2 or more (+10 signature, +5 others; UESP Skyrim:Races). Top two, or three on a tie.
    Returns [{"race", "boosts": [skill names]}]. Racial powers and attributes are not counted."""
    code = {n: c for c, n in SKILLS.items()}
    scored = []
    for r in races:
        bonus = {code[r["signature"]]: 10} | {code[s]: 5 for s in r["plus5"]}
        hits = [(k, v * bonus[k]) for k, v in w.items() if v >= 2 and k in bonus]
        score = sum(x for _, x in hits)
        if score:
            boosts = [SKILLS[k] for k, _ in sorted(hits, key=lambda h: -h[1])]
            scored.append((score, r["race"], boosts))
    scored.sort(key=lambda s: (-s[0], s[1]))
    if not scored:
        return []
    cut = scored[1][0] if len(scored) > 1 else scored[0][0]
    top = [s for s in scored if s[0] >= cut][:3]
    return [{"race": r, "boosts": b[:3]} for _, r, b in top]


def early_perks(trees, code, have, limit=4, max_level=30):
    """The first perks of a skill tree (needing skill 30 or less), skipping ones the card already shows."""
    out = [p for p in trees.get(code, []) if p["levels"][0] <= max_level and p["name"] not in have]
    return [{"n": p["name"], "lvl": p["levels"][0], "fx": p["effect"]} for p in out[:limit]]


def card_weights(b, classes):
    """The weights a build's card shows: hand-set `weights`, or its first class file's."""
    return b["weights"] if "weights" in b else classes[b["classes"][0]]["weights"]


def uesp_terms():
    """Term -> {page, section, missing} from data/uesp/uesp-terms.json (written by fetch_terms.py)."""
    return cache("terms")["terms"]


def by_id(entries):
    return {e["id"]: e for e in entries}


def weights(classes, editor_id):
    return classes[editor_id]["weights"]


# --- Text check: everything a card's text names must be in `mentions` (CLAUDE.md, data conventions) ---
_ITEM_NOUN = (r"Sword|Greatsword|Dagger|Blade|Oathblade|Axe|Battleaxe|Mace|Warhammer|Hammer|Bow|Crossbow|Staff|"
              r"Shield|Armor|Cuirass|Helmet|Helm|Mask|Robes|Gauntlets|Boots|Amulet|Ring|Crown|Circlet|Necklace")
_CAP = r"[A-Z][\w'’-]*"
# A capitalized name ending in an item word ("Ebony Greatsword"), or an item word plus "of ..." ("Amulet of Talos").
ITEM_SHAPED = re.compile(rf"\b(?:{_CAP} )*(?:{_ITEM_NOUN}) of (?:the )?{_CAP}(?: {_CAP})*|\b(?:{_CAP} )+(?:{_ITEM_NOUN})\b")
_LEAD = re.compile(r"^(?:The|A|An|Adds|Swaps|Keep|Train|Take|Use|Wear|Wears|With|And|Or|Its|His|Her|Their|Your|No|Some|Two) ")


def plain_form(title):
    """A UESP title as text writes it: "The Black Star (item)" -> "Black Star"."""
    return re.sub(r"^The ", "", re.sub(r"\s*\([^)]*\)$", "", title))


def named_in_text(text, known, plain=()):
    """Names a text uses that need a `mentions` entry: every term in `known` (UESP-checked terms, matched by
    case as whole words, longest first) plus anything shaped like an item name. `plain` holds names that need
    no entry: skills, and stone, shout and Black Book names, which their own lookup files check.
    A one-word term at the start of a sentence is skipped: "Fear works on..." may be the plain word."""
    found, spans = set(), []
    known = {plain_form(t): t for t in known}
    for name in plain:
        spans += [m.span() for m in re.finditer(re.escape(name), text)]
    hit = lambda a, b: any(a < y and b > x for x, y in spans)
    shaped = []
    for m in ITEM_SHAPED.finditer(text):
        raw = m.group(0)
        while _LEAD.match(raw):
            raw = _LEAD.sub("", raw, count=1)
        if " " in raw and raw not in plain and not hit(m.end() - len(raw), m.end()):
            shaped.append((m.end() - len(raw), m.end(), raw))
    for t in sorted(known, key=len, reverse=True):
        for m in re.finditer(r"(?<![\w'’-])" + re.escape(t) + r"s?(?![\w-])", text):
            if hit(*m.span()):
                continue
            spans.append(m.span())
            # "Ancient Shrouded Armor" is its own item, not the known "Shrouded Armor".
            if any(a <= m.start() and m.end() <= b and b - a > m.end() - m.start() for a, b, _ in shaped):
                continue
            start = m.start() == 0 or text[:m.start()].rstrip()[-1:] in ".:!?"
            if not (" " not in t and start):
                found.add(known[t])
            shaped = [x for x in shaped if not (m.start() <= x[0] and x[1] <= m.end())]
    return found | {raw for _, _, raw in shaped}


def unlisted(text, own, known, plain):
    """Names in `text` that its holder's `mentions` (or signature, perks, items) do not cover."""
    have = {plain_form(t) for t in own}
    return sorted(n for n in named_in_text(text, known, plain) if plain_form(n) not in have)


def text_holders(doc, kits, mods):
    """(label, text, names its text may use) for every block of player-facing text that can name game things."""
    for b in doc["builds"]:
        own = set(b.get("mentions", [])) | set(b.get("signature", [])) | set(b.get("perks", {}).get("names", []))
        yield b.get("name", b["id"]), " ".join(str(b.get(f, "")) for f in ("description", "play")), own
        for e in b.get("lore", []):
            yield (f"{b.get('name', b['id'])} [lore {e.get('name')!r}]", str(e.get("changes", "")),
                   set(e.get("mentions", [])) | set(e.get("signature", [])))
    for k in kits:
        yield f"kit {k.get('id')}", str(k.get("note", "")), set(k.get("items", [])) | set(k.get("mentions", []))
    for m in mods:
        yield f"modifier {m.get('id')}", str(m.get("rule", "")), set(m.get("mentions", []))


def plain_names(stones, shouts, books):
    """Names text may use without a `mentions` entry: skills, and the lookup lists validated on their own."""
    out = set(SKILLS.values()) | {s["name"] for s in shouts} | {b["name"] for b in books}
    out |= {p["name"] for b in books for p in b["powers"]}
    out |= {name for name, _ in BEAST_FORMS.values()}
    return out | {s["name"] for s in stones} | {f"{s['name']} Stone" for s in stones}


def ledger_rows():
    """Row ids (A1, C12, G40, M3 ...) that exist in the research ledgers under docs/research/."""
    text = "\n".join(p.read_text() for p in sorted((ROOT / "docs" / "research").glob("*.md")))
    return set(re.findall(r"^\|\s*\**([A-Z]\d+)\**\s*\|", text, re.M))


def ledger_refs(doc, kits, mods):
    """(label, ref) for every ledger reference in the data."""
    for b in doc["builds"]:
        name = b.get("name", b["id"])
        for part, blk in (("build", b), ("stone", b.get("stone")), ("shouts", b.get("shouts")),
                          ("perks", b.get("perks")), ("black_book", b.get("black_book"))):
            if blk and blk.get("ref"):
                yield f"{name} [{part}]", str(blk["ref"])
        for e in b.get("lore", []):
            if e.get("ref"):
                yield f"{name} [lore {e.get('name')!r}]", str(e["ref"])
    for kind, entries in (("kit", kits), ("modifier", mods)):
        for e in entries:
            if e.get("ref"):
                yield f"{kind} {e.get('id')}", str(e["ref"])

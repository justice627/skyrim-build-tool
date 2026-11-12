"""Shared loading and game constants for validate.py and build.py."""
import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

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


def load_lookup(name):
    """A list file such as stones.yaml, as a list of entries (ids may repeat; validate.py checks)."""
    return yaml.safe_load((DATA / f"{name}.yaml").read_text())[name]


def npc_classes():
    """EditorID -> names of single-NPC UESP pages using that class (docs/sources/uesp-npc-classes.json)."""
    doc = json.loads((ROOT / "docs" / "sources" / "uesp-npc-classes.json").read_text())
    return {eid: {n["name"] for n in npcs} for eid, npcs in doc["classes"].items()}


def skills_in_text(text):
    """Skill codes named in free text such as a lore pick's `changes` ("fire Destruction" counts)."""
    import re
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


def card_weights(b, classes):
    """The weights a build's card shows: hand-set `weights`, or its first class file's."""
    return b["weights"] if "weights" in b else classes[b["classes"][0]]["weights"]


def uesp_terms():
    """Term -> {page, section, missing} from docs/sources/uesp-terms.json (written by fetch_terms.py)."""
    return json.loads((ROOT / "docs" / "sources" / "uesp-terms.json").read_text())["terms"]


def by_id(entries):
    return {e["id"]: e for e in entries}


def weights(classes, editor_id):
    return classes[editor_id]["weights"]

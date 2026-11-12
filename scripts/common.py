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

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


def by_id(entries):
    return {e["id"]: e for e in entries}


def weights(classes, editor_id):
    return classes[editor_id]["weights"]

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


def load():
    classes = json.loads((DATA / "classes.json").read_text())
    builds = yaml.safe_load((DATA / "builds.yaml").read_text())
    races = yaml.safe_load((DATA / "races.yaml").read_text())["races"]
    return classes, builds, races


def weights(classes, editor_id):
    return classes[editor_id]["weights"]

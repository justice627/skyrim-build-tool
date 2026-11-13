# "As worn by" spot check (2026-11-13)

`scripts/fetch_gear.py` reads gear from the sentences on a character's UESP page that say "wears", "wields" or "carries", and keeps linked items whose names look like armor or weapons. That is a heuristic, so 11 of the 83 characters were compared with their UESP pages (every eighth name, alphabetically).

| Character | Stored before | UESP says | Result |
|---|---|---|---|
| Adrianne Avenicci | Steel Mace | carries a steel mace | Correct |
| Balimund | The Scorched Hammer | carries a key to The Scorched Hammer, his store | Wrong: a shop, not an item |
| Crowstooth | Forsworn Armor, Forsworn Bow, Forsworn Sword | also has the unique axe Tyrant's Bane | Correct, one item missed |
| Elrindir | Steel War Axe, Long Bow | steel war axe and long bow | Correct |
| Farkas | Steel Armor, Skyforge Steel Greatsword, Iron Greatsword, Wolf Armor | Wolf Armor appears only in a bug note about the Unofficial Patch | Wrong: Wolf Armor is not his game outfit |
| Grelka | Leather Armor | leather armor | Correct |
| Keeper Carcette | Apprentice Robes of Restoration | apprentice robes of Restoration, steel plate gauntlets and boots | Correct |
| Miraak | Miraak's Robes, Miraak's Sword, Miraak's Staff | the same | Correct |
| Ralis Sedarys | Pickaxe, Leather Armor | also carries Hoarfrost, a unique pickaxe | Correct, one item missed |
| Tolfdir | Master Robes of Alteration | the same | Correct |
| Vilkas | Banded Iron Shield | also carries his own sword | Correct, one item missed |

Two of 11 held something wrong. Both causes are fixed in `fetch_gear.py`:

- A link is kept only when UESP files its page under an item category, or the link is a section of a shared page. This drops The Scorched Hammer and nothing else.
- Bug notes and Bugs sections are not read. This drops Farkas's Wolf Armor and nothing else.

After the fix every stored item in the sample is one the character's page says they wear or carry. The list is still not a full inventory: items whose names do not look like gear (Tyrant's Bane, Hoarfrost) are missed. The page says so.

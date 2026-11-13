"""The wikitext parsers in the fetch scripts, checked against text copied from UESP (2026-11-13).

These run offline. A failure after a fetch script change means it no longer reads what UESP writes.
"""
import unittest

from tests import helpers

import build
import fetch_classes
import fetch_gear
import fetch_npcs
import fetch_skill_perks
import fetch_terms
import uesp

TABLE = (helpers.ROOT / "tests" / "fixtures" / "classes-table.wiki").read_text()


class ClassTable(unittest.TestCase):
    def test_rows(self):
        got = fetch_classes.parse(TABLE)
        self.assertEqual(got["CombatWarrior1H"], {"ARC": 2, "BLO": 2, "HVA": 3, "1HD": 3, "2HD": 1, "Hea": 4, "Sta": 2})
        self.assertEqual(got["TrainerAlchemyExpert"],
                         {"ALT": 1, "ALC": 4, "PIC": 2, "SNK": 2, "SPE": 3, "Hea": 1, "Mag": 1, "Sta": 1})
        self.assertEqual(len(got), 2)

    def test_weights_keep_uesp_column_order(self):
        self.assertEqual(list(fetch_classes.parse(TABLE)["TrainerAlchemyExpert"]),
                         ["ALT", "ALC", "PIC", "SNK", "SPE", "Hea", "Mag", "Sta"])

    def test_a_changed_header_stops_the_read(self):
        with self.assertRaises(ValueError):
            fetch_classes.parse(TABLE.replace("[[Skyrim:Block|BLO]] !! ", ""))

    def test_a_short_row_stops_the_read(self):
        with self.assertRaises(ValueError):
            fetch_classes.parse(TABLE.replace("| 2 || 2 || 3 || 3 ||", "| 2 || 2 || 3 ||"))

    def test_a_non_number_stops_the_read(self):
        with self.assertRaises(ValueError):
            fetch_classes.parse(TABLE.replace("| 2 || 2 || 3 || 3 ||", "| 2 || x || 3 || 3 ||"))

    def test_class_names(self):
        self.assertEqual(fetch_npcs.class_names_in(TABLE)["Warrior"], {"CombatWarrior1H"})


class ItemOrigin(unittest.TestCase):
    def test_creation_named_in_the_header(self):
        text = "{{CC Header|Stendarr's Hammer|shortcut={{CC|Stendarr's Hammer}}|icon=x.png}}{{Trail|Creation Club}}"
        self.assertEqual(fetch_terms.origin(text), "CC:Stendarr's Hammer")

    def test_creation_named_only_in_the_shortcut(self):
        text = "{{CC Header|shortcut={{CC|Bow of Shadows}}|icon=SR-icon-weapon-Bow of Shadows.png}}{{Trail|Creation Club}}"
        self.assertEqual(fetch_terms.origin(text), "CC:Bow of Shadows")

    def test_dlc_category(self):
        text = "<noinclude>{{Trail|Items|Artifacts}}{{Mod Header|Dawnguard}}[[Category:Skyrim-Dawnguard]]</noinclude>"
        self.assertEqual(fetch_terms.origin(text), "DG")

    def test_base_game(self):
        self.assertEqual(fetch_terms.origin("{{Trail|Items}}{{Artifact Summary\n|artifacttype=Weapon}}"), "base")

    def test_a_section_of_its_own_on_a_shared_page(self):
        chitin = ("{{Mod Note|Ghosts of the Tribunal}}\n===Indoril Armor{{CC|Ghosts of the Tribunal}} ===\n"
                  "Indoril Armor is a craftable heavy armor set.\n")
        self.assertEqual(fetch_terms.section_origin(chitin, "Indoril Armor"), "CC:Ghosts of the Tribunal")

    def test_a_table_row_reads_only_its_name_cell(self):
        gear = ("|-\n| [[File:SR-icon-weapon-BladesSword.png|48px]]\n| {{Anchor|Blades Sword}}<br>{{ID|0003aeb9|par=1}} "
                "|| One Handed Sword \n| 10 || 300 || 11\n| \n* Also sold in {{CC|Rare Curios}} shops\n")
        self.assertIsNone(fetch_terms.section_origin(gear, "Blades Sword"))

    def test_a_dlc_row(self):
        row = "|-\n| {{Anchor|Dragonbone Sword}}{{DG}} || One Handed Sword\n"
        self.assertEqual(fetch_terms.section_origin(row, "Dragonbone Sword"), "DG")

    def test_an_anchor_at_the_end_of_the_page(self):
        self.assertIsNone(fetch_terms.section_origin("| {{Anchor|Blades Sword}}", "Blades Sword"))

    def test_no_such_anchor(self):
        self.assertIsNone(fetch_terms.section_origin("nothing here", "Blades Sword"))


LYDIA = """{{NPC Summary
|race=Nord
|class=[[Skyrim:Warrior (class)|Warrior]]
|class_details=[[Skyrim:CombatWarrior1H|CombatWarrior1H]]
|perks=[[Skyrim:Bladesman|Bladesman]] (rank 2); Extra Damage 1.5; [[Skyrim:Juggernaut|Juggernaut]] (Rank 1)
|voicetype=FemaleEvenToned
}}
'''Lydia''' is a [[Skyrim:Nord|Nord]] housecarl.

She wears a set of [[Skyrim:Steel Armor|steel armor]] with [[Skyrim:Steel Boots|boots]], and wields a [[Skyrim:Steel Sword|steel sword]] and a [[Skyrim:Steel Shield|steel shield]]. She carries a [[Skyrim:Key to Breezehome|key]] to [[Skyrim:The Scorched Hammer|a shop]].

==Bugs==
{{Bug|Her outfit was changed to [[Skyrim:Wolf Armor|Wolf Armor]] by the patch.}}
She sometimes wears [[Skyrim:Daedric Armor|Daedric armor]] by mistake.
"""


class NpcPages(unittest.TestCase):
    def test_summary(self):
        self.assertEqual(list(fetch_npcs.summaries(LYDIA)), [(None, "CombatWarrior1H", "Warrior")])

    def test_perks_with_and_without_ranks(self):
        self.assertEqual(fetch_npcs.perks_of(LYDIA), [{"name": "Bladesman", "rank": 2},
                                                      {"name": "Extra Damage 1.5", "rank": None},
                                                      {"name": "Juggernaut", "rank": 1}])

    def test_no_perks(self):
        self.assertEqual(fetch_npcs.perks_of("{{NPC Summary\n|perks=None\n}}"), [])
        self.assertEqual(fetch_npcs.perks_of("{{NPC Summary\n|race=Nord\n}}"), [])

    def test_link_text(self):
        self.assertEqual(fetch_npcs.link_text("[[Skyrim:Blade (class)|Blade]]"), "Blade")
        self.assertEqual(fetch_npcs.link_text("[[Skyrim:Bard]]"), "Bard")
        self.assertEqual(fetch_npcs.link_text("Warrior (class)"), "Warrior")

    def test_gear_reads_wear_and_wield_sentences(self):
        # Boots and the key are dropped by name. The shop still passes: only UESP's categories can tell.
        self.assertEqual(fetch_gear.gear_in(LYDIA), ["Steel Armor", "Steel Sword", "Steel Shield", "The Scorched Hammer"])

    def test_gear_ignores_bug_notes(self):
        got = fetch_gear.gear_in(LYDIA, limit=None)
        self.assertNotIn("Wolf Armor", got)
        self.assertNotIn("Daedric Armor", got)

    def test_places_are_not_items(self):
        self.assertFalse(fetch_gear.is_item(["Category:Skyrim-Places", "Category:Skyrim-Places-Stores"]))
        self.assertTrue(fetch_gear.is_item(["Category:Skyrim-Items", "Category:Skyrim-Weapons"]))
        self.assertTrue(fetch_gear.is_item(["Category:Skyrim-Dragonborn-Clothing-Clothes"]))


MARKS = """{{Image Mark|436|874|Armsman|mark_alt=Armsman (5 ranks): 0/20/40/60/80 One-handed. One-Handed weapons do 20/40/60/80/100% more damage.|position=left}}
{{Image Mark|622|560|Bladesman|mark_alt=Bladesman (3 ranks): 30/60/90 One-handed. Attacks with swords have a 10/15/20% chance of doing critical damage.|position=bottomright}}
{{Image Mark|366|430|Steel Smithing|mark_alt=Steel Smithing: Create Steel armor and weapons at forges.}}
{{Image Mark|387|196|Arcane<br>Blacksmith|mark_alt=Arcane Blacksmith: 60 Smithing. Improve magical weapons and armor.|position=bottom}}
"""


class SkillPerks(unittest.TestCase):
    PERKS = {p["name"]: p for p in fetch_skill_perks.perks_in(MARKS)}

    def test_ranks_and_levels(self):
        self.assertEqual(self.PERKS["Armsman"], {"name": "Armsman", "ranks": 5, "levels": [0, 20, 40, 60, 80],
                                                 "effect": "One-Handed weapons do 20/40/60/80/100% more damage."})

    def test_a_root_perk_with_no_level_is_level_zero(self):
        self.assertEqual(self.PERKS["Steel Smithing"]["levels"], [0])
        self.assertEqual(self.PERKS["Steel Smithing"]["effect"], "Create Steel armor and weapons at forges.")

    def test_the_name_comes_from_the_text_not_the_label(self):
        self.assertEqual(self.PERKS["Arcane Blacksmith"]["levels"], [60])
        self.assertEqual(len(self.PERKS), 4)

    def test_lowest_level_first(self):
        self.assertEqual([p["name"] for p in fetch_skill_perks.perks_in(MARKS)][-1], "Arcane Blacksmith")


class BuiltPage(unittest.TestCase):
    DATA = {"builds": [{"id": "thief"}, {"id": "monk"}]}

    def page(self, data):
        import json
        return f"<script>\nconst DATA = {json.dumps(data)};\nrender();\n</script>"

    def test_a_good_page(self):
        self.assertEqual(build.self_check(self.page(self.DATA), self.DATA), [])

    def test_a_missing_build(self):
        problems = build.self_check(self.page({"builds": [{"id": "thief"}]}), self.DATA)
        self.assertIn("build monk is missing from the page", problems)

    def test_broken_data(self):
        self.assertTrue(build.self_check("<script>\nconst DATA = {oops;\n</script>", self.DATA))
        self.assertTrue(build.self_check("<p>no data</p>", self.DATA))

    def test_a_leftover_marker(self):
        self.assertTrue(build.self_check(self.page(self.DATA) + "__DATA__", self.DATA))


class Api(unittest.TestCase):
    def test_batches(self):
        self.assertEqual([len(b) for b in uesp.batches(range(120))], [50, 50, 20])
        self.assertEqual(uesp.batches([]), [])


if __name__ == "__main__":
    unittest.main()

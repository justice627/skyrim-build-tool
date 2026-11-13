"""The rules that decide what a card shows, checked against real builds.

A failure here means a rule change moved a card. Decide whether that is wanted, then update the case.
Run: python -m unittest discover -s tests
"""
import unittest

from tests import helpers  # noqa: F401  (import path)

import build
from common import (SKILLS, cache, card_weights, early_perks, load, loadout, named_in_text, plain_form, playstyles,
                    race_fit, skills_in_text, tree_of_page, unlisted)

CLASSES, DOC, RACES = load()
BUILDS = {b["name"]: b for b in DOC["builds"]}


def skills(name):
    return {k: v for k, v in card_weights(BUILDS[name], CLASSES).items() if k in SKILLS}


class Playstyles(unittest.TestCase):
    def test_real_builds(self):
        cases = {"Warrior": ["c"], "Stealth Archer": ["c", "s"], "True Mage": ["m"], "Monk": ["c", "m"],
                 "Temple priest": ["m", "k"], "Blacksmith": ["c", "k"]}
        for name, want in cases.items():
            with self.subTest(name):
                self.assertEqual(playstyles(skills(name)), want)

    def test_light_armor_is_not_stealth(self):
        self.assertEqual(playstyles({"2HD": 3, "LTA": 3}), ["c"])

    def test_minor_skills_do_not_count(self):
        self.assertEqual(playstyles({"1HD": 3, "SNK": 1, "DES": 1}), ["c"])

    def test_craft_needs_to_match_the_biggest_fighting_style(self):
        self.assertNotIn("k", playstyles({"1HD": 3, "HVA": 3, "SMI": 3}))
        self.assertIn("k", playstyles({"1HD": 2, "SMI": 3, "SPE": 3}))

    def test_no_skills(self):
        self.assertEqual(playstyles({}), [])


class Loadout(unittest.TestCase):
    def test_real_builds(self):
        cases = {"Warrior": ("heavy", ["one-handed", "shield"]), "Stealth Archer": ("light", ["bow", "spells"]),
                 "True Mage": ("robes", ["spells"]), "Monk": ("light", ["one-handed", "spells"])}
        for name, (armor, hands) in cases.items():
            with self.subTest(name):
                self.assertEqual(loadout(skills(name)), {"armor": armor, "hands": hands})

    def test_two_handed_takes_no_shield(self):
        self.assertEqual(loadout({"2HD": 3, "BLO": 2, "HVA": 3})["hands"], ["two-handed"])

    def test_heavy_wins_a_tie_with_light(self):
        self.assertEqual(loadout({"HVA": 2, "LTA": 2})["armor"], "heavy")

    def test_no_armor_skill_and_no_spells_is_clothes(self):
        self.assertEqual(loadout({"SPE": 3, "1HD": 1}), {"armor": "clothes", "hands": ["one-handed"]})

    def test_override_wins(self):
        b = BUILDS["Pugilist"]
        self.assertEqual(loadout(skills("Pugilist"), b["loadout"]), {"armor": "heavy", "hands": ["fists"]})


class RaceFit(unittest.TestCase):
    def test_real_builds(self):
        cases = {"Warrior": ["Orc", "Redguard"], "Stealth Archer": ["Bosmer", "Khajiit"],
                 "True Mage": ["Dunmer", "Imperial"]}
        for name, want in cases.items():
            with self.subTest(name):
                self.assertEqual([r["race"] for r in race_fit(skills(name), RACES)], want)

    def test_a_tie_for_second_shows_three(self):
        self.assertEqual(len(race_fit(skills("Vigilant of Stendarr"), RACES)), 3)

    def test_minor_skills_are_ignored(self):
        self.assertEqual(race_fit({"SNK": 1}, RACES), [])

    def test_boosts_name_the_matching_skills(self):
        orc = race_fit(skills("Warrior"), RACES)[0]
        self.assertEqual(orc["boosts"], ["Heavy Armor", "One-Handed", "Block"])


class AttributePlan(unittest.TestCase):
    def test_unused_magicka_moves_to_stamina(self):
        w = card_weights(BUILDS["Blacksmith"], CLASSES)
        ratio, why = build.plan(w)
        self.assertEqual(ratio, [2, 0, 3])
        self.assertIn("Magicka moved to Stamina", why)

    def test_enchanting_is_not_a_spell_school(self):
        self.assertEqual(build.plan({"ENC": 4, "Hea": 1, "Mag": 1, "Sta": 1})[0], [1, 0, 2])

    def test_a_caster_with_no_magicka_gets_its_stamina(self):
        self.assertEqual(build.plan({"DES": 3, "RES": 2, "SNK": 1, "Hea": 2, "Sta": 2})[0], [2, 2, 0])

    def test_a_working_ratio_is_left_alone(self):
        self.assertEqual(build.plan(card_weights(BUILDS["Warrior"], CLASSES)), ([4, 0, 2], ""))

    def test_split_spends_every_level(self):
        for ratio, want in (([2, 0, 1], [33, 0, 16]), ([1, 1, 1], [17, 16, 16]), ([4, 2, 0], [33, 16, 0])):
            self.assertEqual(build.split(ratio), want)
            self.assertEqual(sum(build.split(ratio)), build.LEVELS)


class EarlyPerks(unittest.TestCase):
    TREES = cache("skill-perks")["trees"]

    def test_first_perks_of_a_tree(self):
        got = early_perks(self.TREES, "1HD", set())
        self.assertEqual([p["n"] for p in got], ["Armsman", "Fighting Stance", "Bladesman", "Bone Breaker"])
        self.assertTrue(all(p["lvl"] <= 30 for p in got))

    def test_perks_already_on_the_card_are_skipped(self):
        self.assertNotIn("Armsman", [p["n"] for p in early_perks(self.TREES, "1HD", {"Armsman"})])

    def test_every_tree_starts_at_level_zero(self):
        for code in SKILLS:
            with self.subTest(code):
                self.assertEqual(early_perks(self.TREES, code, set())[0]["lvl"], 0)


class TextNames(unittest.TestCase):
    KNOWN = {"Ebonyflesh", "Shrouded Armor", "The Black Star (item)", "Fear", "Dremora Lord"}
    PLAIN = {"Heavy Armor", "Slow Time", "Lord Stone"}

    def names(self, text):
        return named_in_text(text, self.KNOWN, self.PLAIN)

    def test_known_terms_are_found(self):
        self.assertEqual(self.names("Cast Ebonyflesh before the fight."), {"Ebonyflesh"})

    def test_plurals_match(self):
        self.assertEqual(self.names("Summons two Dremora Lords."), {"Dremora Lord"})

    def test_item_shaped_names_are_found_even_when_unknown(self):
        self.assertEqual(self.names("Carries an Ebony Greatsword and the Amulet of Talos."),
                         {"Ebony Greatsword", "Amulet of Talos"})

    def test_a_longer_item_is_not_read_as_the_known_shorter_one(self):
        self.assertEqual(self.names("Wears Ancient Shrouded Armor."), {"Ancient Shrouded Armor"})

    def test_plain_names_need_no_entry(self):
        self.assertEqual(self.names("Heavy Armor, the Lord Stone and Slow Time."), set())

    def test_a_one_word_term_starting_a_sentence_is_skipped(self):
        self.assertEqual(self.names("Fear works on most enemies. Then cast Fear again."), {"Fear"})
        self.assertEqual(self.names("Fear works on most enemies."), set())

    def test_titles_match_without_the_or_a_suffix(self):
        self.assertEqual(plain_form("The Black Star (item)"), "Black Star")
        self.assertEqual(unlisted("Fill the Black Star.", {"The Black Star (item)"}, self.KNOWN, self.PLAIN), [])
        self.assertEqual(unlisted("Fill the Black Star.", set(), self.KNOWN, self.PLAIN), ["The Black Star (item)"])

    def test_skills_in_text(self):
        self.assertEqual(skills_in_text("Fire Destruction, with some sneak. Not Sneaking."), {"DES", "SNK"})

    def test_tree_of_page(self):
        self.assertEqual(tree_of_page("Skyrim:One-handed"), "1HD")
        self.assertEqual(tree_of_page("Skyrim:Lycanthropy"), "werewolf")
        self.assertIsNone(tree_of_page("Skyrim:Dawnbreaker"))
        self.assertIsNone(tree_of_page(""))


if __name__ == "__main__":
    unittest.main()

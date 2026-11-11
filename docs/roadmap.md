# Roadmap

The living version is the Skyrim Build Tool Roadmap doc on claude.ai: https://claude.ai/artifact/W3LhGStR8tJfmkiDouXJmY
This copy holds what Claude Code needs to work through the phases. The research behind it is in `docs/research/community-build-ledger.md`.

## Order

Phase 0 (move to this repo) is done; the one step left is switching Settings > Pages > Source to "GitHub Actions". Phases 1 and 2 can start in either order. Phases 3 and 5 wait on Phase 1's fields, and Phase 4 waits on Phase 2's named variants. Phase 6 runs alongside all of them.

## Phase 0: repo setup

Done when the repo is on GitHub, `validate.py` passes, and `build.py` reproduces the published page.

## Phase 1: fields that unlock the most

Add to every build: standing stone (early and final), shouts (two to four), requirements (vanilla, Dawnguard, Hearthfire, Dragonborn, Creation, AE, mod), evidence (sourced, partly sourced, derived) and aliases. Beast form and Black Book power moved to Phase 3, where the first builds that need them arrive.

- New lookup files: `data/stones.yaml`, `data/shouts.yaml`. Builds reference them by id and the validator checks that every id resolves.
- Defaults for the 56 builds come from ledger section F2 and are tagged derived.
- Done when every build shows a stone and shouts, and searching "stealth archer" finds Scout.
- Status: done. The stone and shout lists, and the race skill bonuses, were checked against UESP through its wiki API on 2026-11-11 and are tagged sourced. The per-build picks stay derived.

## Phase 2: names and named variants

Rename Cutpurse to Thief. Everything else from ledger B becomes an alias (Stealth Archer, Crusader, Witcher). Add Paladin as a variant of Vigilant of Stendarr rather than renaming it.

- Add the named-character variants from ledger C: Kodlak, Vilkas, Delphine, Karliah, Isran, Serana, Astrid, Tolfdir and the rest.
- Done when every row of ledgers B and C is applied or marked rejected.
- Status: done (2026-11-11).

| Rows | Result |
|---|---|
| B1 Cutpurse, B3 Prisoner, B7 Scout | Renamed to Thief, Crafter, Stealth Archer; old names are aliases |
| B9 Destruction mage, B12 Blade Binder | Renamed to True Mage, Bound Warrior; old names are aliases |
| B11 Housecarl | Renamed to Warrior, the class's own UESP name; Housecarl is an alias |
| B2, B6 | Variants renamed Knight and Burglar |
| B4 Vilkas, B5 Tolfdir | Kept as trainer variants; both show as Examples from UESP |
| B8 Crusader, B10 Archer, B13 Witcher, Paladin | Kept as aliases; Spellsword, Ranger, Witchblade and Vigilant keep their names |
| C12 to C37, C39, C40 | Added as lore picks under the ledger's parent build; where UESP puts the NPC's class elsewhere, the pick says so |
| C20 Bone Shepherd | Rejected: needs a mod. Mannimarco kept as a lore hook |
| C1 to C7, C10, C11, C38 | Added in Phase 3a under Tongue, Werewolf, Poisoner, Dual-wielder and Pugilist |
| C8, C9 | Deferred to Phase 3b with their parent, Druid |

## Phase 3a: the builds no class file can express

Status: done (2026-11-11). Six builds in a new family, "Beyond the class files": Pugilist (A1), Tongue (A2), Werewolf (A3), Pacifist (A4, with Puppet Master A7 as a lore pick), Poisoner (A5) and Dual-wielder (A14).

- Hand-set `weights` on the 1 to 4 scale: ledger core skills 3, secondary 2. Attribute ratios are derived. Never graded sourced.
- New fields: `beast_form` (Werewolf, Vampire Lord) and `black_book` (from `data/black_books.yaml`, sourced from UESP).
- Every perk, item, spell or power these builds name is listed in `mentions` and checked against UESP by `scripts/fetch_terms.py` and `validate.py`.
- The check corrected the ledger twice: Greybeard's Robes are unobtainable (dropped from Tongue), and the Ring of Bloodlust is Dragonborn, not Dawnguard. UESP lists 18 Black Book powers, not 21.
- Rejected: A2's "Way of the Voice" variant (needs Ordinator, a mod).

## Phase 3b: sourced extras

Spellshield (A6), Witchhunter (A8, vanilla skills only), Vampire Slayer (A9), Druid (A10, with C8 Arcane Beastmaster and C9 Warden), The Preserver (A11), The Madman (A12), Champion of Cyrodiil (A13) and Arcanist (A18). Same pattern as 3a: hand-set weights, `mentions` checked against UESP.

- Agent (A15), Pilgrim (A16) and Battlemage (A17) overlap existing builds: add them as aliases or lore picks, not builds.
- Hold: Divine Crusader (A19, AE-or-mod question unresolved) and Warrior-Poet (A20, derived, spear is a mod).
- Done when each new build has skills, stone, shouts, a playstyle and an evidence tag.

## Phase 4: perks, together with the user

For each build, the user picks one named NPC as its perk source and supplies UESP screenshots of that NPC's perks. Add key-perk chips where the research names them (Fists of Steel for Pugilist, Poisoned for Poisoner).

- New file: `data/perks.yaml`.
- Done when every primary skill on every build shows at least one sourced perk.

## Phase 5: gear kits and challenge modifiers

Attach gear kits to builds (Spell Knight Armor to Spellsword, Necromantic Grimoire to the Necromancer variant, Arcane Archer Pack to Battle archer). Add a separate picker for restriction runs (stolen items only, level 1) that pairs with any build.

- New files: `data/gear.yaml`, `data/modifiers.yaml`.
- Done when kits show on their builds and any build can be paired with a modifier.

## Phase 6: verification, alongside the rest

Done early: stones, shouts and race skill bonuses checked against UESP (2026-11-11). Still open: settle whether Chrysamere, Keening and Sunder need AE or mods. Spot-check the lore claims marked unverified in the ledger. Watch the FudgeMuppet videos for Sabre Cat, Preserver, Mechanist and Ronin.

- Done when no row is still tagged unverified.

## Out of scope

Mod-only builds (Requiem templates, the Ordinator Dragonborn, FudgeMuppet's modded Sand Demon, Celestial and King), ESO class conversions, and full perk templates for all 18 trees.

## Decisions (2026-11-11)

- Naming: community names become the primary names, and NPC-file names become aliases. Phase 1 adds aliases and alias search; the renames happen in Phase 2.
- Weights for new builds: set from the research (ledger A core skills) on the 1 to 4 scale, marked as not from an NPC file, with their evidence grade.
- Mod builds: excluded. The page is vanilla-friendly, so default picks use base-game options where one fits.
- Hosting: GitHub Pages from the public repo.

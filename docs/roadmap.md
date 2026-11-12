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

Status: done (2026-11-11). Six builds in a new family, "Community builds" (first named "Beyond the class files"): Pugilist (A1), Tongue (A2), Werewolf (A3), Pacifist (A4, with Puppet Master A7 as a lore pick), Poisoner (A5) and Dual-wielder (A14).

- Hand-set `weights` on the 1 to 4 scale: ledger core skills 3, secondary 2. Attribute ratios are derived. Never graded sourced.
- New fields: `beast_form` (Werewolf, Vampire Lord) and `black_book` (from `data/black_books.yaml`, sourced from UESP).
- Every perk, item, spell or power these builds name is listed in `mentions` and checked against UESP by `scripts/fetch_terms.py` and `validate.py`.
- The check corrected the ledger twice: Greybeard's Robes are unobtainable (dropped from Tongue), and the Ring of Bloodlust is Dragonborn, not Dawnguard. UESP lists 18 Black Book powers, not 21.
- Rejected: A2's "Way of the Voice" variant (needs Ordinator, a mod).

### Lore pick placement fix (2026-11-11)

The ledger grouped lore picks by theme, not skills, so 11 sat under builds they do not play like. Each moved to the build its skills match: Stormcrown and Jarl of the Voice to Warrior, Ash-King to Miraak, Ethereal Hunter to Ebony Warrior, Aela to Thief, Puppet Master to Mystic, Praying Mantis to Bandit chief, Cleric to Vigilant of Stendarr, Esbern to Conjurer, Oblivion Scout to Ranger, The Imperial Spectre to Rogue. Brynjolf, Mercer Frey and Astrid stay: they tweak one or two skills on their own UESP class's build. Battle Bard stays, reworded as additions to the Bard. `validate.py` now rejects picks whose skills barely overlap their build.

## Phase 3b: sourced extras

Status: done (2026-11-11). Eight more builds in "Community builds" (first named "Beyond the class files"): Spellshield (A6), Witchhunter (A8, vanilla skills only), Vampire Slayer (A9), Druid (A10), The Preserver (A11), The Madman (A12), Champion of Cyrodiil (A13, weights from FudgeMuppet's The Master) and Arcanist (A18, TheGamer's Spider Mastermind).

- Where a ledger row lists skills without saying which are core (A8, A11, A12, A13), the first two listed get 3 and the rest 2.
- Lore picks placed by skill fit, not by the ledger's parent: C8 Arcane Beastmaster under Spellshield, C9 Warden under Conjurer (neither fits Druid), A13's lore version Hero of Kvatch under Spellsword, A15 Agent under Trader, A16 Pilgrim under Blacksmith, A17 Battlemage under Bandit chief.
- Left out: Witchhunter's Purifier and Requiem template (mods). Held: Divine Crusader (A19, AE-or-mod question unresolved) and Warrior-Poet (A20, derived, spear is a mod).

## Phase 4: perks from UESP

Status: done (2026-11-12). The planned method (the user picks an NPC per build and supplies screenshots) was replaced: UESP NPC infoboxes have a `perks=` field the wiki API returns.

- Class builds and variants show the combined perks of every named NPC of their class, filtered to the skills on the card, grouped by skill, most-taken first. Tagged sourced.
- A perk counts as a player perk when its UESP page is a skill page (or Lycanthropy). Ambiguous titles (Barbarian, Ranger, Stealth, Necromage) resolve through UESP's "<name> (perk)" redirects. NPC-only perks (Extra Damage, MS02IncreaseDamage, IrilethVsDragons) are dropped.
- Coverage: 22 of 56 class builds and 9 variants. The rest have no named NPC with a perk list and say so on the card.
- Community builds show the key perks their ledger row names: Fists of Steel (Pugilist), Poisoned (Poisoner), Dual Flurry (Dual-wielder) and the werewolf tree (Werewolf). Partly sourced.
- Done criterion changed: every perk shown is sourced or marked, and gaps are visible. "Every primary skill shows a perk" is not reachable without guessing.
- Planner fix: Enchanting no longer counts as a spell school. Temple priest loses a wrong Magicka shift; Laborer, Citizen and Crafter now move their unused Magicka to Stamina.

## Phase 5: gear kits and challenge runs

Status: done (2026-11-12).

- `data/kits.yaml`: 13 kits (ledger D1 to D13) attached to builds. Every item is checked on UESP. Requirement tags are read from each item's UESP page header (`{{CC Header|<Creation>}}` or a DLC category), never typed by hand. Paid Creations show as "CC: <Creation>"; all of them ship in the Anniversary Edition bundle, so the ledger's CC versus AE split is dropped.
- The UESP check regrouped the ledger: Light of Day, Trueflame, Hopesfire, Magebane, Cleaver of St. Felms and Skull Crusher are all *Ghosts of the Tribunal*; Bloodthirst is *Dawnfang & Duskfang*; Sunder and Wraithguard are one Creation; Keening, Wuuthrad, Spellbreaker and Ring of Namira are base game.
- `data/modifiers.yaml`: 16 challenge runs (M1 to M14, with M5 split into stolen, purchased and crafted). Shown as their own section and chip, and as a line on the builds they pair with.
- Left out: D14 relic stand-ins (derived, for held builds) and D15 Black Book powers (already a field).

## Phase 6: verification, alongside the rest

Done early: stones, shouts and race skill bonuses checked against UESP (2026-11-11). Settled in Phase 5: Chrysamere, Sunder and Wraithguard are official Creations (CC), Keening is base game, so Divine Crusader (A19) can come back as a CC build. Spot-check the lore claims marked unverified in the ledger. Watch the FudgeMuppet videos for Sabre Cat, Preserver, Mechanist and Ronin.

- Done when no row is still tagged unverified.

## Out of scope

Mod-only builds (Requiem templates, the Ordinator Dragonborn, FudgeMuppet's modded Sand Demon, Celestial and King), ESO class conversions, and full perk templates for all 18 trees.

## Decisions (2026-11-11)

- Naming: community names become the primary names, and NPC-file names become aliases. Phase 1 adds aliases and alias search; the renames happen in Phase 2.
- Weights for new builds: set from the research (ledger A core skills) on the 1 to 4 scale, marked as not from an NPC file, with their evidence grade.
- Mod builds: excluded. The page is vanilla-friendly, so default picks use base-game options where one fits.
- Hosting: GitHub Pages from the public repo.

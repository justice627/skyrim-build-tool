# Roadmap

The living version is the Skyrim Build Tool Roadmap doc on claude.ai: https://claude.ai/artifact/W3LhGStR8tJfmkiDouXJmY
This copy holds what Claude Code needs to work through the phases. The research behind it is in `docs/research/community-build-ledger.md`.

## Order

Phase 0 (move to this repo) comes first. Phases 1 and 2 can start in either order. Phases 3 and 5 wait on Phase 1's fields, and Phase 4 waits on Phase 2's named variants. Phase 6 runs alongside all of them.

## Phase 0: repo setup

Done when the repo is on GitHub, `validate.py` passes, and `build.py` reproduces the published page.

## Phase 1: fields that unlock the most

Add to every build: standing stone (early and final), shouts (two to four), requirements (vanilla, Dawnguard, Hearthfire, Dragonborn, Creation, AE, mod), evidence (sourced, partly sourced, derived) and aliases. Beast form and Black Book power are optional fields.

- New lookup files: `data/stones.yaml`, `data/shouts.yaml`. Builds reference them by id and the validator checks that every id resolves.
- Defaults for the 56 builds come from ledger section F2 and are tagged derived.
- Done when every build shows a stone and shouts, and searching "stealth archer" finds Scout.

## Phase 2: names and named variants

Rename Cutpurse to Thief. Everything else from ledger B becomes an alias (Stealth Archer, Crusader, Witcher). Add Paladin as a variant of Vigilant of Stendarr rather than renaming it.

- Add the named-character variants from ledger C: Kodlak, Vilkas, Delphine, Karliah, Isran, Serana, Astrid, Tolfdir and the rest.
- Done when every row of ledgers B and C is applied or marked rejected.

## Phase 3: new builds for the five gaps

Pugilist (unarmed), Tongue (shouts), Werewolf, Pacifist with Puppet Master, and Poisoner come first, because the NPC class files cannot express them. Then the sourced extras: Witchhunter, Vampire Slayer, Druid, Madman, Spellshield.

- These have no NPC class file. They get hand-set weights on the same 1 to 4 scale, tagged derived, and the page shows that difference.
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

Settle whether Chrysamere, Keening and Sunder need AE or mods. Spot-check the lore claims marked unverified in the ledger. Watch the FudgeMuppet videos for Sabre Cat, Preserver, Mechanist and Ronin.

- Done when no row is still tagged unverified.

## Out of scope

Mod-only builds (Requiem templates, the Ordinator Dragonborn, FudgeMuppet's modded Sand Demon, Celestial and King), ESO class conversions, and full perk templates for all 18 trees.

## Open decisions before Phase 1

- Naming policy. Default: NPC-file names stay primary and community names become aliases, except Cutpurse to Thief.
- Hand-set weights for new builds. Default: same 1 to 4 scale, visibly marked as set by hand.
- Mod builds. Default: excluded.
- Hosting. GitHub Pages is free for a public repo; a private repo needs a paid GitHub plan.

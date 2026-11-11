# Elder Scrolls class archetypes from other games, recreated in Skyrim

Source access note: UESP (en., m., app., content1., pt. mirrors) and the Elder Scrolls Fandom wiki returned errors for every class page during this session (the egress proxy also refused en.uesp.net). The UESP Standing Stones and Daggerfall:Classes pages loaded once early on. Oblivion class data comes from Game8. Morrowind vanilla data could not be confirmed (see Gaps). Wherever these notes say "Skyrim NPC class", the source is the user's own `_existing_builds.md`, which was built from Skyrim's NPC class files.

## What are the major/minor skills and attributes of each Morrowind/Oblivion class, and how do they convert to Skyrim's 18 skills?

### Takeaway
I confirmed the Oblivion data for all 21 classes. One Skyrim SE mod article converts every Oblivion class into Skyrim skill sets, so the conversion pattern is documented: Marksman becomes Archery, Armorer becomes Smithing, Security becomes Lockpicking, Speechcraft and Mercantile become Speech, and Blade/Blunt become One-/Two-Handed. Athletics, Acrobatics, Hand-to-Hand and Mysticism have no Skyrim equivalent and are dropped. Of the 21 classes, 9 already exist by name in the user's tool. Most of the others can be relabelled or added as variants of existing builds. Only about four have no clear home: Crusader, Pilgrim, Witchhunter and Battlemage.

### Cited Findings

**Oblivion's 21 classes (specialization; favored attributes; 7 major skills)**, all from [Game8 Oblivion classes](https://game8.co/games/Elder-Scrolls-Oblivion/archives/515708):
- Warrior: Combat; Strength, Endurance; Armorer, Athletics, Blade, Block, Blunt, Hand-to-Hand, Heavy Armor
- Barbarian: Combat; Strength, Speed; Armorer, Athletics, Blade, Block, Blunt, Hand-to-Hand, Light Armor
- Crusader: Combat; Strength, Willpower; Athletics, Blade, Blunt, Destruction, Hand-to-Hand, Heavy Armor, Restoration
- Knight: Combat; Strength, Personality; Blade, Block, Blunt, Hand-to-Hand, Heavy Armor, Illusion, Speechcraft
- Archer: Combat; Agility, Strength; Armorer, Blade, Blunt, Hand-to-Hand, Light Armor, Marksman, Sneak
- Scout: Combat; Speed, Endurance; Acrobatics, Alchemy, Armorer, Athletics, Blade, Block, Light Armor
- Rogue: Combat; Speed, Personality; Alchemy, Athletics, Blade, Block, Illusion, Light Armor, Mercantile
- Mage: Magic; Intelligence, Willpower; Alchemy, Alteration, Conjuration, Destruction, Illusion, Mysticism, Restoration
- Sorcerer: Magic; Intelligence, Endurance; Alchemy, Alteration, Conjuration, Destruction, Heavy Armor, Mysticism, Restoration
- Battlemage: Magic; Strength, Intelligence; Alchemy, Alteration, Blade, Blunt, Conjuration, Destruction, Mysticism
- Healer: Magic; Personality, Willpower; Alchemy, Alteration, Destruction, Illusion, Mercantile, Restoration, Speechcraft
- Spellsword: Magic; Willpower, Endurance; Alteration, Blade, Block, Destruction, Heavy Armor, Illusion, Restoration
- Witchhunter: Magic; Intelligence, Agility; Alchemy, Athletics, Conjuration, Destruction, Marksman, Mysticism, Security
- Nightblade: Magic; Willpower, Speed; Acrobatics, Alteration, Athletics, Blade, Destruction, Light Armor, Restoration
- Thief: Stealth; Speed, Agility; Acrobatics, Light Armor, Marksman, Mercantile, Security, Sneak, Speechcraft
- Agent: Stealth; Personality, Agility; Acrobatics, Illusion, Marksman, Mercantile, Security, Sneak, Speechcraft
- Acrobat: Stealth; Agility, Endurance; Acrobatics, Blade, Block, Marksman, Security, Sneak, Speechcraft
- Assassin: Stealth; Speed, Intelligence; Acrobatics, Alchemy, Blade, Light Armor, Marksman, Security, Sneak
- Monk: Stealth; Agility, Willpower; Acrobatics, Alteration, Athletics, Hand-to-Hand, Marksman, Security, Sneak
- Pilgrim: Stealth; Personality, Endurance; Armorer, Block, Blunt, Light Armor, Mercantile, Security, Speechcraft
- Bard: Stealth; Personality, Intelligence; Alchemy, Blade, Block, Illusion, Light Armor, Mercantile, Speechcraft

**Morrowind class descriptions** (flavour text only; the skill tables did not come through), from [Elder Scrolls Fandom: Classes (Morrowind)](https://elderscrolls.fandom.com/wiki/Classes_(Morrowind)):
- Crusader: "heavily armored spellcaster who hunts monsters and villains"
- Knight: a chivalrous warrior "who also studies healing and enchantment"
- Pilgrim: a traveller with arms, armour and magic, "skilled in commerce and persuasion"
- Witchhunter: hunts "vampires, witches, warlocks, and necromancers" with martial, magical and stealth skills
- Agent: an operative "skilled in deception, avoidance, and self-defense"
- Acrobat: a stealthy thief who "relies on mobility and cunning"
- Healer: heals and cures disease, using "deadly force only as a last resort"

**Morrowind skill and attribute lists, from a mod's revised class table (not vanilla):** [Nexus Morrowind mod 56674 docs](https://www.nexusmods.com/morrowind/mods/56674?tab=docs). The page says its lists are the mod's revisions and that the vanilla lists had problems. Use them only to show how each class is themed. Examples:
- Crusader: Strength, Willpower; Blunt, Long Blade, Heavy Armor, Block, Destruction
- Pilgrim: Speed, Personality; Medium Armor, Marksman, Speechcraft, Restoration, Mysticism
- Witchhunter: Intelligence, Speed; Marksman, Light Armor, Mysticism, Enchant, Alchemy
- Knight: Strength, Personality; Axe, Long Blade, Heavy Armor, Block, Speechcraft
- Agent: Agility, Personality; Short Blade, Sneak, Light Armor, Speechcraft, Security
- Healer: Intelligence, Personality; Hand-to-hand, Speechcraft, Restoration, Alteration, Conjuration

**Daggerfall:** it has 18 predefined classes: Acrobat, Archer, Assassin, Barbarian, Bard, Battlemage, Burglar, Healer, Knight, Mage, Monk, Nightblade, Ranger, Rogue, Sorcerer, Spellsword, Thief, Warrior. Every class except Warrior starts with advantages and/or disadvantages, such as weaknesses, resistances, weapon or armour restrictions and spell-point changes ([UESP Daggerfall:Classes](https://en.uesp.net/wiki/Daggerfall:Classes)). Burglar and Ranger are the only names that are not among Morrowind/Oblivion's 21.

**How one mod converts the Oblivion classes to Skyrim skills.** This is the Skyrim SE class-selection article by MrVectorr; it requires a mod, and the article does not give the mod's name ([Nexus SSE article 10189](https://www.nexusmods.com/skyrimspecialedition/articles/10189)). Each class gets 6 major skills plus one ability:
- Crusader: Block, Heavy Armor, One-Handed, Two-Handed, Destruction, Restoration. Ability "Smite": +15% mace and warhammer damage.
- Knight: Block, Heavy Armor, One-Handed, Two-Handed, Illusion, Speech. Ability "Sturdy": +20% heavy armour. Bonus spell: Courage.
- Pilgrim: Block, One-Handed, Smithing, Restoration, Light Armor, Speech. Ability: +15% buying and selling.
- Witchhunter: Archery, Destruction, Enchanting, Conjuration, Alchemy, Lockpicking. Ability "Purifier": +25% damage against undead, including vampires.
- Agent: Archery, Illusion, Lockpicking, Pickpocket, Sneak, Speech. Ability: Persuasion is 20% easier.
- Acrobat: Archery, One-Handed, Lockpicking, Pickpocket, Sneak, Speech. Ability "Spry": 75% less fall damage.
- Healer: Alchemy, Alteration, Destruction, Illusion, Restoration, Speech. Ability: +10% Restoration. Bonus spell: Healing Hands.
- Battlemage: One-Handed, Alteration, Conjuration, Destruction, Enchanting, Alchemy. Ability: +10% Destruction.
- Spellsword: Heavy Armor, One-Handed, Alteration, Destruction, Enchanting, Restoration.
- Monk: Archery, Alteration, Alchemy, Lockpicking, Pickpocket, Sneak. Ability "Martial Arts": +20 unarmed damage.
- Sorcerer: Alchemy, Enchanting, Conjuration, Destruction, Restoration, Heavy Armor. Bonus spell: Bound Sword.
- Archer: Archery, Block, One-Handed, Smithing, Light Armor, Sneak.
- Scout: Block, One-Handed, Smithing, Alchemy, Light Armor, Sneak. Ability "Nimble": +10% movement.
- Rogue: Block, One-Handed, Illusion, Alchemy, Light Armor, Speech.
- Bard: One-Handed, Enchanting, Illusion, Alchemy, Light Armor, Speech.
- Thief: Archery, Light Armor, Lockpicking, Pickpocket, Sneak, Speech.
- Assassin: Archery, One-Handed, Alchemy, Light Armor, Pickpocket, Sneak.
- Nightblade: One-Handed, Light Armor, Illusion, Destruction, Alteration, Sneak.
- Mage: Enchanting, Alteration, Conjuration, Destruction, Illusion, Restoration.
- Warrior: Archery, Block, Heavy Armor, One-Handed, Smithing, Two-Handed.
- Barbarian: Archery, Block, One-Handed, Smithing, Two-Handed, Light Armor.

**A third source with unclear methodology:** [nukes2.nuxt.dev character-builds DB](https://nukes2.nuxt.dev/skyrim/db/character-builds) lists Skyrim builds named Agent, Acrobat, Crusader, Healer, Knight, Pilgrim, Witchhunter and others, each with perk counts per skill. For example, Crusader uses Heavy Armor, Block, One-Handed, Destruction and Restoration, and Pilgrim uses Block, One-Handed, Speech, Alchemy, Illusion and Restoration. The page gives no stone, race or gear, and does not say how the builds were made.

**Skyrim NPC classes with the same names, compared** (Skyrim side from the user's `_existing_builds.md`; Oblivion side from Game8 above):
- Skyrim Spellsword is Heavy Armor 3, One-Handed 3, Destruction 3, Restoration 2. That is almost exactly Oblivion's **Crusader** (Blade/Blunt, Heavy Armor, Destruction, Restoration). Oblivion's Spellsword adds Block, Alteration and Illusion.
- Skyrim Scout is Archery, Sneak, Restoration and Light Armor. Oblivion's Scout has no Marksman or Sneak; it is Blade, Block, Light Armor, Alchemy, Armorer, Acrobatics and Athletics.
- Skyrim Monk is Archery, One-Handed, Alteration, Restoration and Sneak, a weapon user. Oblivion's Monk is built on Hand-to-Hand.
- Skyrim Nightblade is Destruction, Sneak, One-Handed and Alteration. Oblivion's adds Light Armor and Restoration.
- Skyrim Bard is Speech 4 with Alteration, Illusion and Pickpocket, a non-combatant. Oblivion's Bard carries Blade, Block and Light Armor.
- Skyrim Rogue is One-Handed, Sneak, Block and Light Armor. Oblivion's Rogue is a "face" class with Illusion, Alchemy and Mercantile.
- Skyrim Barbarian and Assassin are close to their Oblivion namesakes.

### Inferences
Verdict for each class against the user's 56 builds. The skill comparisons are my own and are based on the sources above.
- **Warrior:** rename. It fits the existing Housecarl or Greatsword mercenary; the name "Warrior" is missing from the tool.
- **Barbarian:** already exists under the same name.
- **Crusader:** a better name for, or variant of, the existing **Spellsword**, since the Skyrim Spellsword NPC is mechanically the Oblivion Crusader. It also overlaps Vigilant of Stendarr. Mace focus ("Smite" in the mod). Recommendation: add Crusader as a label for the Spellsword skill set, and let Spellsword move toward the Oblivion definition (Block, Alteration, Illusion), which is close to the existing **Witchblade** (One-Handed, Destruction, Block, Illusion).
- **Knight:** a variant of Housecarl. The Housecarl's Speech journeyman trainer variant (Heavy Armor, One-Handed, Block, Speech) is almost exactly the Knight. Recommendation: rename that variant "Knight". The Requiem template adds Restoration and Enchanting.
- **Archer:** a rename of Ranger (Archery, Light Armor, One-Handed; the mod adds Smithing and Sneak).
- **Scout:** the name already exists, but the Skyrim NPC version is an archer. A melee "Oblivion Scout" (One-Handed, Block, Light Armor, Alchemy, Smithing) would be a variant.
- **Rogue:** exists. Add a "silver-tongued rogue" variant with Illusion, Alchemy and Speech.
- **Mage:** a rename of Destruction mage, or of the generalist Mystic. No build is called "Mage".
- **Sorcerer:** a variant of Conjurer with Heavy Armor added. Both the Oblivion and mod versions include Heavy Armor. It overlaps Court sorcerer.
- **Battlemage:** new name. One-/Two-Handed, Conjuration, Destruction, Alteration and Alchemy, with Heavy Armor in Requiem. The closest existing build is Blade Binder.
- **Healer:** a better name for, or variant of, Temple priest. Add Alteration, Illusion and Alchemy; Destruction is a light secondary.
- **Spellsword:** exists (see the Crusader note).
- **Witchhunter:** **new**. Archery, Conjuration (bound bow), Destruction, Alchemy, Enchanting, Lockpicking. The closest existing build is Battle archer. It is thematically distinct from the melee Vigilant of Stendarr.
- **Nightblade:** exists.
- **Thief:** a rename of Cutpurse.
- **Agent:** **new**, or a variant of Blades agent. Its core is Illusion, Speech, Sneak, Lockpicking and Pickpocket, with Archery as the weapon. This "infiltrator/face" role is not covered.
- **Acrobat:** a variant of Cutpurse at best. Skyrim has no Acrobatics skill, so the identity rests on gear and stone (light gear and Steed in Requiem) rather than skills.
- **Assassin:** exists.
- **Monk:** the name exists, but an **unarmed Monk** variant is new. Hand-to-Hand has no Skyrim skill; the usual workarounds (Khajiit claws, the Heavy Armor "Fists of Steel" perk, Alteration Mage Armor) are my inference and are not cited.
- **Pilgrim:** **new**. Speech, Smithing, Block, One-Handed (mace), Light Armor, Restoration and Lockpicking. Closest existing builds are Trader and Blacksmith, but neither is an armed traveller.
- **Bard:** exists, but the Skyrim NPC is a non-combatant. Add a "battle bard" variant (One-Handed, Block, Light Armor, Illusion, Speech).
- **Daggerfall Burglar and Ranger:** Ranger already exists. Burglar would be a rename of Cutpurse's Lockpicking variant.

### Gaps
- The vanilla Morrowind specializations, favored attributes and major/minor skills could not be confirmed. Every UESP and Fandom route failed, and the only full table (the Nexus 56674 mod) is a revised version. To fill this, re-fetch https://en.uesp.net/wiki/Morrowind:Classes when it is reachable.
- I could not retrieve Daggerfall's per-class skills or advantages and disadvantages (the UESP table loaded with empty skill columns).
- I could not retrieve Skyrim's NPC class list from UESP (Skyrim:Classes), so the NPC comparison relies on the user's file.
- The name of the mod behind Nexus article 10189 is not given on the page.

## How do community guides recreate ESO classes in Skyrim?

### Takeaway
I found **no community guide that converts ESO classes to Skyrim**. Searches for Templar, Dragonknight, Warden and Arcanist "in Skyrim" returned only ESO builds. The mappings below are my own, based on each ESO class's three skill lines and on vanilla and DLC spells.

### Cited Findings
- ESO class skill lines, from [Fextralife ESO Class Skills](https://elderscrollsonline.wiki.fextralife.com/Class_Skills):
  - Dragonknight: Ardent Flame, Draconic Power, Earthen Heart
  - Templar: Aedric Spear, Dawn's Wrath, Restoring Light
  - Sorcerer: Dark Magic, Daedric Summoning, Storm Calling
  - Nightblade: Assassination, Shadow, Siphoning
  - Warden: Animal Companions, Green Balance, Winter's Embrace
  - Necromancer: Grave Lord, Bone Tyrant, Living Death
  - Arcanist: Soldier of Apocrypha, Herald of the Tome, Curative Runeforms
- ESO class roles ([Fextralife ESO Classes](https://elderscrollsonline.wiki.fextralife.com/Classes)): Dragonknight is fire damage, battle buffs and high survivability. Templar is light-based attacks and healing. Sorcerer is summons plus lightning. Nightblade is stealth and crits. Warden is nature magic with frost, for healing and damage. Necromancer is death magic, "protect yourself with flesh and bone". Arcanist is Apocryphal runes for offense, defense and healing.
- ESO role summaries ([ESO-Hub classes](https://eso-hub.com/en/classes)): Templar is "the strongest healer"; Warden is an excellent tank and healer that uses netch pets; Dragonknight is a strong tank and melee damage dealer.
- Searches for Skyrim versions of the ESO classes returned only ESO-side builds, for example [AlcastHQ Dragonknight builds](https://alcasthq.com/eso-dragonknight/) and [ESO-Hub Templar](https://eso-hub.com/en/classes/templar).
- Skyrim's Dawnguard DLC sun-themed Restoration spells, which suit a Templar: [UESP Skyrim:Sun Damage](https://content2.uesp.net/wiki/Skyrim:Sun_Damage), [UESP Stendarr's Aura](https://content2.uesp.net/wiki/Skyrim:Stendarr%27s_Aura), [UESP Sun Fire](https://app.uesp.net/wiki/Skyrim:Sun_Fire). These URLs appeared in search results; the pages themselves were not fetched.

### Inferences
These are mappings I built from the skill lines above, not community guides.
- **Templar** (spear, sun, healing): Restoration-led, with Dawnguard sun spells, One-Handed or a spear (no vanilla spears, so the spear needs a mod) and Heavy Armor. Verdict: a variant of Vigilant of Stendarr, or a new "Templar" label for it.
- **Dragonknight** (fire, dragon power, earth armor): Heavy Armor, One-/Two-Handed, fire Destruction, plus Shouts and the Lord stone. Verdict: a new name; mechanically close to Spellsword.
- **ESO Sorcerer** (dark magic, Daedric summons, storm): Conjuration plus shock Destruction. Verdict: a variant of Conjurer, or of the shock version of Destruction mage.
- **ESO Nightblade** (assassination, shadow, siphon): exists as Nightblade. Lean on Illusion invisibility and the Shadow stone.
- **Warden** (animal companions, nature heals, frost): frost Destruction, Restoration, Conjuration (Conjure Familiar) and Light Armor. Verdict: **new**. Closest existing builds are Forsworn shaman and Hedge wizard.
- **Necromancer:** exists as the Conjurer's "Necromancer" variant. The Ritual stone fits.
- **Arcanist** (Hermaeus Mora tomes, runes, healing runes): rune-based Destruction, Restoration and Alteration, with a Dragonborn DLC Black Book / Miraak theme. Verdict: **new**. It is the archetype furthest from anything in the tool.

### Gaps
- No Reddit, Steam or YouTube "ESO class in Skyrim" guide was found in the searches I ran.
- Unverified: whether ESO-style spear or rune mechanics exist in Skyrim without mods. Vanilla Skyrim has rune spells (Fire Rune and others) but no spears.

## Which standing stones pair with which archetypes in community guides?

### Takeaway
UESP documents what each vanilla stone does. The only class-to-stone pairings I found come from the **Requiem mod** community wiki. It uses Lord for armoured classes, Mage, Thief or Warrior as the leveling stone, Steed for Acrobat, and Lover/Tower for Pilgrim. Requiem renames Light Armor to "Evasion", so its builds need translating back to vanilla.

### Cited Findings
- Vanilla stone effects ([UESP Skyrim:Standing Stones](https://en.uesp.net/wiki/Skyrim:Standing_Stones)):
  - Warrior: combat skills (except Archery) improve 20% faster.
  - Mage: magic skills improve 20% faster.
  - Thief: stealth skills, including Archery, improve 20% faster.
  - Apprentice: faster Magicka regeneration, but weaker against magic.
  - Atronach: absorbs some spell damage and adds Magicka, but Magicka regenerates more slowly.
  - Lady: faster Health and Stamina regeneration.
  - Lord: more resistance to magic and physical damage.
  - Lover: all skills improve 15% faster.
  - Ritual: once a day, reanimate nearby corpses.
  - Serpent: once a day, a ranged paralyzing poison.
  - Shadow: once a day, invisibility.
  - Steed: worn armour weighs nothing and causes no slowdown; +100 carry weight (+50 in Survival).
  - Tower: once a day, open any lock up to Expert.
  - The Aetherial Crown lets you have two stones at once.
- Requiem build templates ([r/skyrimrequiem wiki builds overview](https://www.reddit.com/r/skyrimrequiem/wiki/builds/overview), read via [mirror](https://axebps-redlib.hf.space/r/skyrimrequiem/wiki/builds/overview); **Requiem mod required**; the page says Requiem has no class system and these are templates). Format is major skills / minor skills / race / stone:
  - Crusader: One-Handed, Heavy Armor, Restoration / Block, Destruction, Alchemy / Imperial or Breton / Lord or Mage
  - Knight: One-Handed, Heavy Armor, Block / Speech, Restoration, Enchanting / Imperial or Breton / Lord or Warrior. Tip: a mage follower covers magic damage.
  - Healer: Restoration, Alteration, Alchemy / Speech, Illusion, a weapon / Altmer or Imperial / Mage or Apprentice
  - Battlemage: Destruction, Conjuration, Heavy Armor / Alteration, Restoration, a weapon / Imperial or Dunmer / Mage or Lady. Tip: battlestaves.
  - Spellsword: One-Handed, Destruction, Evasion or Heavy Armor / Restoration, Block, Enchanting / Dunmer or Imperial / Mage or Warrior
  - Witchhunter: Marksmanship, Conjuration, Alchemy / Sneak, Evasion, Enchanting / Bosmer or Breton / Mage or Thief. Tip: elemental ammunition and bound weapons.
  - Agent: One-Handed, Evasion, Sneak / Speech, Pickpocket, Lockpicking / Imperial or Breton / Thief or Lord. Tip: common or noble clothing to blend in.
  - Acrobat: Marksmanship, Evasion, Sneak / Pickpocket, Lockpicking, Speech / Khajiit or Bosmer / Thief or Steed. Tip: as light as possible, light bow or crossbow.
  - Monk: One-/Two-Handed, Evasion, Sneak / Alteration, Restoration, Marksmanship / Khajiit or Argonian / Mage or Lord. Tip: robes plus Mage Armor.
  - Pilgrim: Speech, Alchemy, Enchanting / Smithing, Lockpicking, Evasion / Imperial or Orsimer / Lover or Tower. Tip: light armour, shield, staves, scrolls, backup mace or crossbow.
- The Nexus SSE class article lists 13 birthsigns separately and does not tie any of them to a class ([Nexus SSE article 10189](https://www.nexusmods.com/skyrimspecialedition/articles/10189)).

### Inferences
Pairings for the vanilla tool, extrapolated from the Requiem templates and the stone effects; these are not community-sourced for vanilla.
- **Lord:** Crusader, Knight, Dragonknight. **Ritual:** Necromancer. **Shadow:** Nightblade and Agent. **Tower:** Thief, Pilgrim, Acrobat. **Steed:** Acrobat, or any heavy-armour build. **Lover:** Pilgrim and Bard, the generalists. **Atronach:** Sorcerer and Arcanist. **Lady:** Battlemage and Warden, the hybrids. **Serpent:** Witchhunter and Assassin.
- Skyrim's stones are the old birthsigns, not classes. As stand-alone "archetypes" they are better treated as a stone field on each build than as builds of their own. The three guardian stones (Warrior, Mage, Thief) match the three Oblivion specializations, Combat, Magic and Stealth, which Game8 lists per class. The exception is Archery: Skyrim puts it under the Thief stone.

### Gaps
- I found no vanilla, non-Requiem community guide that systematically pairs stones with Morrowind/Oblivion/ESO class names.
- Not checked: Reddit r/skyrimbuilds, YouTube and Steam guides. Searches turned up no relevant hits, and I stopped at the tool-call budget.

"""Check the data files before any build. Exits 1 with a list of problems if anything is off.

Rules:
- every class in classes.json has only known skill/attribute codes with whole-number weights 1-9
- every build names a known family, a description and an inspiration
- every class a build or variant references exists
- classes grouped in one build (or one variant) have identical weights, so merging them hides nothing
- every class in classes.json is used exactly once across all builds
- races use real skill names and a three-part attribute ratio
- stones.yaml and shouts.yaml entries have unique ids, a name, an effect, a known requirement and evidence grade
- every lore pick (ledger C) has a name, a C-row ref, changes text, a known evidence grade and requirements,
  and any npc it names exists in the saved UESP NPC data
- hand-set builds (no class file) have weights 1-4, a ledger A ref, and are never graded sourced
- beast forms and Black Book powers resolve; every `mentions` term exists on UESP and is not unobtainable
- lore picks that list 3+ skills share at least half of them with their build (unless they say "adds")
- community `perks` are UESP player perks in the build's skills (or the werewolf tree), named in mentions
- gear kits and challenge runs have ledger refs, known builds, and items/mentions that exist on UESP
- every example NPC on a build or variant uses one of that group's classes, per the saved UESP NPC data
- every build has a skill evidence grade, a stone (early, optional final) and 2 to 4 shouts that resolve,
  known evidence grades and requirements, and aliases that clash with no build name or other alias
"""
import re
import sys
from collections import Counter

from common import (ATTRS, BEAST_FORMS, EVIDENCE, REQUIRES, SKILLS, STYLE_CODES, UNUSABLE_PAGES, by_id, card_weights,
                    load, load_lookup, npc_classes, skills_in_text, uesp_terms, weights)

LEDGER_REF = re.compile(r"[A-F]\d+")


def check_lookup(kind, entries, errors):
    ids = Counter(e.get("id") for e in entries)
    errors += [f"{kind} id {i} is used {n} times" for i, n in ids.items() if n > 1]
    for e in entries:
        for field in ("id", "name", "effect"):
            if not str(e.get(field, "")).strip():
                errors.append(f"{kind} {e.get('id')}: missing {field}")
        if e.get("requires") not in REQUIRES:
            errors.append(f"{kind} {e.get('id')}: unknown requires {e.get('requires')!r}")
        if e.get("evidence") not in EVIDENCE:
            errors.append(f"{kind} {e.get('id')}: unknown evidence {e.get('evidence')!r}")


LORE_REF = re.compile(r"[ACG]\d+")  # G = lore groups ledger (docs/research/lore-groups.md)
HAND_REF = re.compile(r"A\d+")


def check_mentions(label, terms, known, errors):
    for t in terms:
        r = known.get(t)
        if r is None:
            errors.append(f"{label}: {t!r} is not in uesp-terms.json; run scripts/fetch_terms.py")
        elif r["missing"]:
            errors.append(f"{label}: {t!r} has no UESP page")
        elif r["page"] in UNUSABLE_PAGES:
            errors.append(f"{label}: {t!r} is listed on UESP as {r['page']}, not a usable item")


def check_hand_set(name, b, errors):
    """Builds with no class file: hand-set weights from a ledger A row, never graded sourced."""
    w = b["weights"]
    for k, v in w.items():
        if k in SKILLS and not (isinstance(v, int) and 1 <= v <= 4):
            errors.append(f"{name}: hand-set weight {k}={v!r} is not 1-4")
        elif k in ATTRS and not (isinstance(v, int) and 0 <= v <= 9):
            errors.append(f"{name}: attribute {k}={v!r} is not 0-9")
        elif k not in SKILLS and k not in ATTRS:
            errors.append(f"{name}: unknown code {k}")
    if not any(k in SKILLS for k in w) or any(a not in w for a in ATTRS) or not sum(w.get(a, 0) for a in ATTRS):
        errors.append(f"{name}: hand-set weights need at least one skill and all of Hea, Mag, Sta")
    if not HAND_REF.fullmatch(str(b.get("ref", ""))):
        errors.append(f"{name}: hand-set build needs a ledger A ref")
    if b.get("evidence") == "sourced":
        errors.append(f"{name}: hand-set weights cannot be graded sourced")
    if b.get("variants") or b.get("examples"):
        errors.append(f"{name}: variants and examples need class files; use lore picks instead")


def check_perks(name, b, terms, errors):
    """Community builds may list key perks from their ledger row: each must be a UESP perk in one of the
    build's skills or the werewolf tree, and also appear in `mentions` (the text names it)."""
    pk = b.get("perks")
    if not pk:
        return
    if "weights" not in b:
        errors.append(f"{name}: class builds get perks from UESP NPC data, not a perks field")
        return
    if pk.get("evidence") not in EVIDENCE or not HAND_REF.fullmatch(str(pk.get("ref", ""))):
        errors.append(f"{name}: perks need an evidence grade and a ledger A ref")
    for n in pk.get("names", []):
        tree = (terms.get(n) or {}).get("tree")
        if not tree:
            errors.append(f"{name}: perk {n!r} is not a player perk on UESP; run scripts/fetch_terms.py")
        elif tree != "werewolf" and tree not in b["weights"]:
            errors.append(f"{name}: perk {n!r} is in the {tree} tree, which this build does not use")
        if n not in b.get("mentions", []):
            errors.append(f"{name}: perk {n!r} must also be in mentions")


def check_layers(build_ids, terms, errors):
    """Gear kits (ledger D) and challenge runs (ledger F1)."""
    kits, mods = load_lookup("kits"), load_lookup("modifiers")
    for kind, entries, ref_re, link in (("kit", kits, r"D\d+", "fits"), ("modifier", mods, r"M\d+", "pairs")):
        ids = Counter(e.get("id") for e in entries)
        errors += [f"{kind} id {i} is used {n} times" for i, n in ids.items() if n > 1]
        for e in entries:
            label = f"{kind} {e.get('id')}"
            for f in ("name", "note" if kind == "kit" else "rule"):
                if not str(e.get(f, "")).strip():
                    errors.append(f"{label}: missing {f}")
            if not re.fullmatch(ref_re, str(e.get("ref", ""))):
                errors.append(f"{label}: ref {e.get('ref')!r} is not a ledger row")
            if e.get("evidence") not in EVIDENCE:
                errors.append(f"{label}: unknown evidence {e.get('evidence')!r}")
            errors += [f"{label}: unknown build {b!r} in {link}" for b in e.get(link, []) if b not in build_ids]
            check_mentions(label, e.get("items", []) + e.get("mentions", []), terms, errors)
            for i in e.get("items", []):
                if i in terms and "origin" not in terms[i]:
                    errors.append(f"{label}: no origin recorded for {i!r}; run scripts/fetch_terms.py")
        if kind == "kit":
            errors += [f"{label}: a kit needs at least one build in fits" for e in entries if not e.get("fits")
                       for label in [f"kit {e.get('id')}"]]
    return len(kits), len(mods)


def check_extras(name, b, books, errors):
    if "beast_form" in b and b["beast_form"] not in BEAST_FORMS:
        errors.append(f"{name}: unknown beast form {b['beast_form']!r}")
    bb = b.get("black_book")
    if bb:
        book = books.get(bb.get("book"))
        if not book:
            errors.append(f"{name}: unknown Black Book {bb.get('book')!r}")
        elif bb.get("power") not in {p["name"] for p in book["powers"]}:
            errors.append(f"{name}: {bb.get('power')!r} is not a power of {book['name']}")
        if bb.get("evidence") not in EVIDENCE:
            errors.append(f"{name}: black_book has unknown evidence {bb.get('evidence')!r}")


def check_lore_fit(name, b, classes, errors):
    """A lore pick that lists 3+ skills must share at least half of them with the build's primary and
    secondary skills, unless it says it adds or replaces skills. Keeps picks under the build they play like."""
    core = {k for k, v in card_weights(b, classes).items() if k in SKILLS and v >= 2}
    for e in b.get("lore", []):
        text = e.get("changes", "")
        named = skills_in_text(text)
        if len(named) < 3 or "adds" in text.lower() or "replaces" in text.lower():
            continue
        if len(named & core) * 2 < len(named):
            errors.append(f"{name} [lore {e['name']!r}]: its skills {sorted(named)} barely overlap the build's "
                          f"{sorted(core)}; move it to the build it plays like")


def check_lore(name, b, known_npcs, terms, errors):
    names = Counter(str(e.get("name", "")).strip() for e in b.get("lore", []))
    errors += [f"{name}: lore pick {n!r} appears {k} times" for n, k in names.items() if k > 1]
    for e in b.get("lore", []):
        label = f"{name} [lore {e.get('name')!r}]"
        if not str(e.get("name", "")).strip() or not str(e.get("changes", "")).strip():
            errors.append(f"{label}: needs a name and changes")
        if not LORE_REF.fullmatch(str(e.get("ref", ""))):
            errors.append(f"{label}: ref {e.get('ref')!r} is not a ledger A, C or G row")
        if e.get("evidence") not in EVIDENCE:
            errors.append(f"{label}: unknown evidence {e.get('evidence')!r}")
        errors += [f"{label}: unknown requires {r!r}" for r in e.get("requires", []) if r not in REQUIRES]
        check_mentions(label, e.get("mentions", []), terms, errors)
        if "npc" in e and e["npc"] not in known_npcs:
            errors.append(f"{label}: npc {e['npc']!r} is not in the UESP NPC data")


def check_picks(name, b, stones, shouts, errors):
    if b.get("evidence") not in EVIDENCE:
        errors.append(f"{name}: unknown evidence {b.get('evidence')!r}")
    for r in b.get("requires", []):
        if r not in REQUIRES:
            errors.append(f"{name}: unknown requires {r!r}")
    st = b.get("stone") or {}
    if not st.get("early"):
        errors.append(f"{name}: missing stone.early")
    for key in ("early", "final"):
        if st.get(key) and st[key] not in stones:
            errors.append(f"{name}: unknown stone {st[key]!r}")
    sh = b.get("shouts") or {}
    ids = sh.get("ids") or []
    if not 2 <= len(ids) <= 4 or len(set(ids)) != len(ids):
        errors.append(f"{name}: needs 2 to 4 different shouts, has {ids}")
    errors += [f"{name}: unknown shout {i!r}" for i in ids if i not in shouts]
    for label, block in (("stone", st), ("shouts", sh)):
        if block.get("evidence") not in EVIDENCE:
            errors.append(f"{name}: {label} has unknown evidence {block.get('evidence')!r}")
        if "ref" in block and not LEDGER_REF.fullmatch(str(block["ref"])):
            errors.append(f"{name}: {label} ref {block['ref']!r} is not a ledger row id")


def main():
    classes, doc, races = load()
    stone_list, shout_list = load_lookup("stones"), load_lookup("shouts")
    stones, shouts = by_id(stone_list), by_id(shout_list)
    npcs = npc_classes()
    all_npcs = set().union(*npcs.values())
    terms = uesp_terms()
    book_list = load_lookup("black_books")
    books = by_id(book_list)
    for bk in book_list:
        if bk.get("requires") not in REQUIRES or bk.get("evidence") not in EVIDENCE or len(bk.get("powers", [])) != 3:
            errors.append(f"black book {bk.get('id')}: needs requires, evidence and three powers")
    errors = []
    check_lookup("stone", stone_list, errors)
    check_lookup("shout", shout_list, errors)
    known = set(SKILLS) | set(ATTRS)

    for eid, c in classes.items():
        if c.get("source") not in ("uesp-pdf", "uesp-screenshot", "uesp"):
            errors.append(f"class {eid}: unknown source {c.get('source')!r}")
        for k, v in c["weights"].items():
            if k not in known:
                errors.append(f"class {eid}: unknown code {k}")
            if not isinstance(v, int) or not 1 <= v <= 9:
                errors.append(f"class {eid}: weight {k}={v!r} is not 1-9")

    families = {f["id"] for f in doc["families"]}
    ids = Counter(b["id"] for b in doc["builds"])
    errors += [f"build id {i} is used {n} times" for i, n in ids.items() if n > 1]

    used = []
    names = Counter()
    for b in doc["builds"]:
        names[b.get("name", "").lower()] += 1
        for a in b.get("aliases", []):
            names[str(a).lower()] += 1
    for b in doc["builds"]:
        name = b.get("name", b["id"])
        check_picks(name, b, stones, shouts, errors)
        check_lore(name, b, all_npcs, terms, errors)
        if "classes" in b or "weights" in b:
            check_lore_fit(name, b, classes, errors)
        check_extras(name, b, books, errors)
        check_perks(name, b, terms, errors)
        if "play" in b and not (isinstance(b["play"], str) and b["play"].strip()):
            errors.append(f"{name}: play must be a non-empty line")
        bad = [s for s in b.get("playstyles", []) if s not in STYLE_CODES]
        if bad or ("playstyles" in b and not b["playstyles"]):
            errors.append(f"{name}: playstyles override must list codes from {STYLE_CODES}")
        check_mentions(name, b.get("mentions", []), terms, errors)
        if ("classes" in b) == ("weights" in b):
            errors.append(f"{name}: needs either classes or hand-set weights, not both or neither")
            continue
        if "weights" in b:
            check_hand_set(name, b, errors)
            continue
        for a in b.get("aliases", []):
            if not isinstance(a, str) or not a.strip():
                errors.append(f"{name}: empty alias")
            elif names[a.lower()] > 1:
                errors.append(f"{name}: alias {a!r} repeats another build name or alias")
        if b["family"] not in families:
            errors.append(f"{name}: unknown family {b['family']}")
        for field in ("description", "inspired_by"):
            if not str(b.get(field, "")).strip():
                errors.append(f"{name}: missing {field}")
        groups = [("main", b["classes"], b.get("examples", []))]
        groups += [(v["label"], v["classes"], v.get("examples", [])) for v in b.get("variants", [])]
        for label, eids, examples in groups:
            known_npcs = set().union(*(npcs.get(e, set()) for e in eids))
            if len(set(examples)) != len(examples) or len(examples) > 3:
                errors.append(f"{name} [{label}]: examples must be up to 3 different NPCs")
            errors += [f"{name} [{label}]: {n!r} does not use these classes in the UESP NPC data"
                       for n in examples if n not in known_npcs]
            missing = [e for e in eids if e not in classes]
            errors += [f"{name} [{label}]: class {e} not in classes.json" for e in missing]
            present = [e for e in eids if e in classes]
            if any(weights(classes, e) != weights(classes, present[0]) for e in present[1:]):
                errors.append(f"{name} [{label}]: grouped classes have different weights {present}")
            used += eids

    n_kits, n_mods = check_layers({b["id"] for b in doc["builds"]}, terms, errors)

    counts = Counter(used)
    errors += [f"class {e} is used {n} times" for e, n in counts.items() if n > 1]
    errors += [f"class {e} is not used by any build" for e in classes if e not in counts]

    skill_names = set(SKILLS.values())
    for r in races:
        for s in [r["signature"], *r["plus5"]]:
            if s not in skill_names:
                errors.append(f"race {r['race']}: unknown skill {s}")
        if len(set(r["plus5"])) != 5 or r["signature"] in r["plus5"]:
            errors.append(f"race {r['race']}: needs five different +5 skills besides the signature skill")
        a = r["attributes"]
        if len(a) != 3 or not all(isinstance(x, int) and x >= 0 for x in a) or not sum(a):
            errors.append(f"race {r['race']}: attributes must be three non-negative ints")

    if errors:
        print(f"{len(errors)} problem(s):")
        print("\n".join(f"  - {e}" for e in errors))
        return 1
    print(f"OK: {len(classes)} classes, {len(doc['builds'])} builds, {len(races)} races, "
          f"{len(stones)} stones, {len(shouts)} shouts, {len(books)} Black Books, "
          f"{n_kits} kits, {n_mods} challenges, {len(terms)} checked terms")
    return 0


if __name__ == "__main__":
    sys.exit(main())

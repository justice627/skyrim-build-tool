"""Check the data files before any build. Exits 1 with a list of problems if anything is off.

Rules:
- every class in classes.json has only known skill/attribute codes with whole-number weights 1-9
- every build names a known family, a description and an inspiration
- every class a build or variant references exists
- classes grouped in one build (or one variant) have identical weights, so merging them hides nothing
- every class in classes.json is used exactly once across all builds
- races use real skill names and a three-part attribute ratio
- stones.yaml and shouts.yaml entries have unique ids, a name, an effect, a known requirement and evidence grade
- every example NPC on a build or variant uses one of that group's classes, per the saved UESP NPC data
- every build has a skill evidence grade, a stone (early, optional final) and 2 to 4 shouts that resolve,
  known evidence grades and requirements, and aliases that clash with no build name or other alias
"""
import re
import sys
from collections import Counter

from common import ATTRS, EVIDENCE, REQUIRES, SKILLS, by_id, load, load_lookup, npc_classes, weights

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
          f"{len(stones)} stones, {len(shouts)} shouts")
    return 0


if __name__ == "__main__":
    sys.exit(main())

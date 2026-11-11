"""Check the data files before any build. Exits 1 with a list of problems if anything is off.

Rules:
- every class in classes.json has only known skill/attribute codes with whole-number weights 1-9
- every build names a known family, a description and an inspiration
- every class a build or variant references exists
- classes grouped in one build (or one variant) have identical weights, so merging them hides nothing
- every class in classes.json is used exactly once across all builds
- races use real skill names and a three-part attribute ratio
"""
import sys
from collections import Counter

from common import ATTRS, SKILLS, load, weights


def main():
    classes, doc, races = load()
    errors = []
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
    for b in doc["builds"]:
        name = b.get("name", b["id"])
        if b["family"] not in families:
            errors.append(f"{name}: unknown family {b['family']}")
        for field in ("description", "inspired_by"):
            if not str(b.get(field, "")).strip():
                errors.append(f"{name}: missing {field}")
        groups = [("main", b["classes"])] + [(v["label"], v["classes"]) for v in b.get("variants", [])]
        for label, eids in groups:
            missing = [e for e in eids if e not in classes]
            errors += [f"{name} [{label}]: class {e} not in classes.json" for e in missing]
            present = [e for e in eids if e in classes]
            if any(weights(classes, e) != weights(classes, present[0]) for e in present[1:]):
                errors.append(f"{name} [{label}]: grouped classes have different weights {present}")
            used += eids

    counts = Counter(used)
    errors += [f"class {e} is used {n} times" for e, n in counts.items() if n > 1]
    errors += [f"class {e} is not used by any build" for e in classes if e not in counts]

    names = set(SKILLS.values())
    for r in races:
        for s in [r["signature"], *r["plus5"]]:
            if s not in names:
                errors.append(f"race {r['race']}: unknown skill {s}")
        a = r["attributes"]
        if len(a) != 3 or not all(isinstance(x, int) and x >= 0 for x in a) or not sum(a):
            errors.append(f"race {r['race']}: attributes must be three non-negative ints")

    if errors:
        print(f"{len(errors)} problem(s):")
        print("\n".join(f"  - {e}" for e in errors))
        return 1
    print(f"OK: {len(classes)} classes, {len(doc['builds'])} builds, {len(races)} races")
    return 0


if __name__ == "__main__":
    sys.exit(main())

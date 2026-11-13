"""Read every class's skill and attribute weights from UESP's Skyrim:Classes table (wiki API).

Writes data/classes.json: {EditorID: {"source": "uesp", "weights": {code: weight}}}, weights in UESP's
column order, empty cells left out. Classes listed in data/excluded_classes.yaml are skipped. The script
stops without writing when the table holds a class that is in neither file, when a class already in
classes.json has left the table, or when a row does not parse: each of those needs a person to decide.
"""
import json
import re
import sys

import yaml

from common import ATTRS, DATA, SKILLS
from uesp import page_text

OUT = DATA / "classes.json"
# The table's 24 cells per row: three blocks of six skills, then the attributes, with a spacer after each block.
CODES = list(SKILLS)
COLUMNS = CODES[:6] + [None] + CODES[6:12] + [None] + CODES[12:] + [None] + list(ATTRS)


def parse(wikitext):
    """EditorID -> weights, from the table's rows. Raises ValueError on a row it cannot read."""
    head = re.search(r"\n!([^\n]*\[\[Skyrim:Archery\|ARC\]\][^\n]*)", wikitext)
    found = [re.sub(r".*\|(\w+)\]\]", r"\1", c.strip()) or None for c in head.group(1).split("!!")] if head else []
    if found != COLUMNS:
        raise ValueError(f"the table's columns changed: {found}")
    out = {}
    for row in wikitext.split("\n|-"):
        lines = [l for l in row.strip().split("\n") if l.startswith("|") and not l.startswith("|}")]
        if len(lines) < 4 or "{{ID|" not in lines[2]:
            continue
        eid = re.sub(r"\{\{(?:Anchor\|)?([^}]*)\}\}", r"\1", lines[1].lstrip("|")).strip()
        cells = [c.strip() for c in lines[3][1:].split("||")]
        if len(cells) != len(COLUMNS) or not all(c == "" or c.isdigit() for c in cells) or eid in out:
            raise ValueError(f"cannot read the row for {eid!r}: {lines[3]!r}")
        out[eid] = {code: int(c) for code, c in zip(COLUMNS, cells) if code and c}
    return out


def main():
    live = parse(page_text("Skyrim:Classes"))
    groups = yaml.safe_load((DATA / "excluded_classes.yaml").read_text())["excluded"]
    excluded = {e for ids in groups.values() for e in ids}
    old = json.loads(OUT.read_text()) if OUT.exists() else {}
    problems = [f"{e} is on UESP but in neither classes.json nor excluded_classes.yaml"
                for e in sorted(set(live) - excluded - set(old))] if old else []
    problems += [f"{e} is in classes.json but no longer on UESP" for e in sorted(set(old) - set(live))]
    problems += [f"{e} is excluded but not on UESP" for e in sorted(excluded - set(live))]
    if problems:
        print("\n".join(problems))
        return 1
    keep = sorted(set(old) or set(live) - excluded)
    new = {e: {"source": "uesp", "weights": live[e]} for e in keep}
    changed = [e for e in keep if e in old and old[e]["weights"] != live[e]]
    OUT.write_text(json.dumps(new, indent=1) + "\n")
    print(f"{len(new)} classes from UESP ({len(live)} in the table, {len(excluded)} excluded); "
          f"weights changed: {changed or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

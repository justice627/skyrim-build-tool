"""Refresh everything in the right order, stopping at the first failure.

    python scripts/refresh.py            fetch from UESP, then validate and build
    python scripts/refresh.py --offline  validate and build only (UESP unreachable, or nothing to fetch)

Order matters: NPC classes and perks feed the gear fetch; NPC perks, gear and skill trees feed the term
check; the validator reads every cache; the build reads everything.
"""
import subprocess
import sys

from common import ROOT

FETCH = ["fetch_npcs.py", "fetch_gear.py", "fetch_skill_perks.py", "fetch_terms.py"]
CHECK = ["validate.py", "build.py"]


def run(script):
    print(f"--- {script}", flush=True)
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT / "scripts")
    if r.returncode:
        print(f"!!! {script} failed (exit {r.returncode}); stopping.")
        sys.exit(r.returncode)


def main():
    offline = "--offline" in sys.argv[1:]
    for script in ([] if offline else FETCH) + CHECK:
        run(script)
    print("--- changes in docs/sources since the last commit:")
    subprocess.run(["git", "diff", "--stat", "--", "docs/sources"], cwd=ROOT)


if __name__ == "__main__":
    main()

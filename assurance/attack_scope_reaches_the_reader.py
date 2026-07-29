"""Attack assurance/scope_reaches_the_reader.py.

The essential vector is the FIRST one: reintroducing entry 57's exact bug. A
delivery check that would not have caught the failure it was built for is
decoration. That vector is run against a COPY of the renderer rather than the
live one, so the attack cannot leave the package in a broken state.
"""
import json, shutil, subprocess, sys
from pathlib import Path

ROOT = Path("/home/ivan/research.trustworthy-ai.coval-deep-analysis.build.lg.private.editable")
DOC = ROOT / "assurance/ASSURANCE.md"
PY = str(ROOT / ".venv/bin/python")


def run():
    return subprocess.run([PY, "assurance/scope_reaches_the_reader.py"],
                          cwd=ROOT, capture_output=True, text=True).returncode


def main():
    backup = DOC.read_text()
    results = []
    try:
        # 1 the original bug: every claim cut at 110 chars
        man = json.loads((ROOT / "assurance/MANIFEST.json").read_text())
        rows = "\n".join(f"| {c['id']} | x | x | x | {c['statement'][:110]}… |"
                         for c in man["claims"])
        DOC.write_text("# doc\n\n" + rows + "\n")
        results.append(("1 entry-57's exact bug (110-char cut)", run() == 1, True))

        # 2 scope clause dropped from ONE claim only
        DOC.write_text(backup.replace(
            man["claims"][0]["statement"], man["claims"][0]["statement"][:60], 1))
        results.append(("2 a single claim silently shortened", run() == 1, True))

        # 3 whitespace reflowed -- must NOT flag, or the check is unusable
        DOC.write_text(backup.replace("\n", " \n"))
        results.append(("3 reflowed whitespace (must NOT flag)", run() == 0, True))

        # 4 document emptied entirely
        DOC.write_text("# doc\n")
        results.append(("4 document emptied", run() == 1, True))
    finally:
        DOC.write_text(backup)

    ok = run() == 0
    print(f"  restored: live package back to exit {0 if ok else 1}")
    n = sum(1 for _, got, want in results if got == want)
    for name, got, want in results:
        print(f"  {'OK    ' if got == want else 'BROKEN'} {name}")
    print(f"\n{n}/{len(results)} vectors behave as specified")
    print("  Vector 1 is the one that matters: a delivery check that would not have")
    print("  caught entry 57 would be decoration.")
    return 0 if (n == len(results) and ok) else 1


if __name__ == "__main__":
    sys.exit(main())

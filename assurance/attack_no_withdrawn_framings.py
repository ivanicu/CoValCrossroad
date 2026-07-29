"""Attack assurance/no_withdrawn_framings.py.  Five vectors, actually run.

A lock never attacked is a lock never tested, and the fix is where the new hole
is.  Each vector plants a withdrawn framing that a real round could plausibly
emit, then asks whether the check finds it.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path("/home/ivan/research.trustworthy-ai.coval-deep-analysis.build.lg.private.editable")
TMP = ROOT / "rounds" / "_attack_tmp" / "results"
PY = str(ROOT / ".venv/bin/python")

VECTORS = [
    ("1 case variation",
     "v1.json", {"verdict": "Core Launders Post-Choice Polarity Into Text."}),
    ("2 conclusion under an unlisted field name",
     "v2.json", {"interpretation": "This shows the rubric measures values only partly."}),
    ("3 claim field holding a LIST of strings",
     "v3.json", {"verdict": ["step one", "the result is not leakage at all"]}),
    ("4 results file one directory deeper",
     "nested/v4.json", {"verdict": "core launders polarity into the criterion text"}),
    ("5 unhyphenated / line-broken phrasing",
     "v5.json", {"verdict": "the value carrying share of the headline shrinks"}),
]


def run():
    r = subprocess.run([PY, "assurance/no_withdrawn_framings.py"],
                       cwd=ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout


def main():
    if TMP.parent.exists():
        shutil.rmtree(TMP.parent)
    results = []
    try:
        for name, rel, doc in VECTORS:
            shutil.rmtree(TMP.parent, ignore_errors=True)
            p = TMP / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(doc, indent=1))
            rc, out = run()
            caught = rc == 1
            results.append((name, caught))
            print(f"  {'CAUGHT ' if caught else 'MISSED '} {name}")
            if not caught:
                print(f"      planted: {json.dumps(doc)[:100]}")
    finally:
        shutil.rmtree(TMP.parent, ignore_errors=True)
    rc, out = run()
    print(f"\n  cleanup verified: repo scan back to exit {rc}")
    n = sum(c for _, c in results)
    print(f"\n{n}/{len(results)} vectors caught")
    return 0 if n == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())

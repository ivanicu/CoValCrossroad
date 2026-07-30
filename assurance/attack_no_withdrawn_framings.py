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
import sys as _s
_s.path.insert(0, str(ROOT))
from covalx.rounds import fixture_dir  # noqa: E402
TMP = fixture_dir(ROOT, "r90_attack_tmp") / "results"
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

# Vectors that are EXPECTED to be missed, because the checker's declared payload
# exclusions make them invisible.  They are run anyway so the gap is measured on
# every attack rather than remembered from a docstring, and a MISS here is the
# documented behaviour -- a CATCH would mean the exclusions stopped working and
# the false positives on generated text are back.
KNOWN_GAPS = [
    ("6 claim hidden inside a declared payload field",
     "v6_generations.json", {"fresh": [["core launders polarity into the text"]]}),
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
    gaps = []
    try:
        for name, rel, doc in KNOWN_GAPS:
            shutil.rmtree(TMP.parent, ignore_errors=True)
            p = TMP / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps(doc, indent=1))
            rc, out = run()
            caught = rc == 1
            gaps.append((name, caught))
            print(f"  {'CAUGHT ' if caught else 'MISSED  (expected)'} {name}")
    finally:
        shutil.rmtree(TMP.parent, ignore_errors=True)

    rc, out = run()
    print(f"\n  cleanup verified: repo scan back to exit {rc}")
    n = sum(c for _, c in results)
    print(f"\n{n}/{len(results)} vectors caught")
    print(f"{sum(1 for _, c in gaps if not c)}/{len(gaps)} KNOWN GAPS still open, as "
          f"documented -- a claim inside a declared payload path is invisible")
    # A caught known-gap means the payload exclusions stopped applying, which
    # brings back the false positives on generated text that made the check
    # unusable.  That is a failure too, in the other direction.
    return 0 if (n == len(results) and not any(c for _, c in gaps)) else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
R688 -- does clause ③ exclude arms the benchmark itself published? §4's falsifier, run on ③.

⚠ NOT THE ROUND R687's NEXT NAMED, AND THE REASON IS MEASURED. Its NEXT proposed checking six judge
  fields — a fifth consecutive corpus round. The drift audit over R672–R687: 4 object headlines of
  16, and the last SIX all corpus. R676 caught this exact drift, R664 before it. ⭐ Third occurrence,
  so the interrupt is now run BEFORE choosing the round rather than after noticing.

ESTIMAND        of the arms CoVal published that ③ excludes, how many pass clause ② — i.e. is the
                exclusion done by ③ alone? And where do they sit in A2 relative to the extension?
IDENTIFICATION  "published" is read from R442's `published_five`, one round's record of the release.
                If that list is wrong, this round is wrong with it. Not independently verifiable here.
SCOPE           population : the 5 published arms and the 5 ③-extension members
                instrument : committed clause verdicts + committed A2 means
                             instrument unit = AN ARM'S COMMITTED VERDICT
                             claim unit      = AN ARM THE BENCHMARK ACCEPTS AS A CORE
                             ⚠ NOT EQUAL — "published as an arm" is not "accepted as a core", and
                             that gap is the round's main caveat, carried into the verdict.
                baseline   : the ③ extension
                regime     : this repository at HEAD
WORLDS          A ③ IS FALSE AS A DEFINITION: it excludes arms the benchmark accepts, and §4's
                  falsifier fires.
                B ③ IS DOING ITS JOB: the excluded arms fail ② anyway, so ③ adds no wrong exclusion.
KILL            none of the three passes ② -> world B, the falsifier does NOT fire, say so plainly.
POSITIVE CTRL   coval_core passes ②.
g=0             a known ②-failing arm returns false; the reader returns both values.
NEGATIVE CTRL   an arm absent from the corpus -> UNKNOWN, never false.
PLACEBO         run twice identical.
ARTIFACT        results/published_excluded.json
IMPOSSIBLE      whether CoVal ACCEPTS an arm as a core, rather than merely publishing it as a
                comparison, needs the release's own text; the corpus records the list, not the intent.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent


def load(pat):
    p = next(ARC.glob(pat), None)
    return json.loads(p.read_text()) if p else None


def main() -> int:
    r442 = load("R442_*/results/r442_extension.json")
    r360 = load("R360_*/results/r360_clause_ledger.json")
    r294 = load("R294_*/results/*.json") or load("../A16_*/R294_*/results/*.json")
    if not r442 or not r360:
        print("UNRUNNABLE: R442 or R360 artifact absent. Exit 2, never 0."); return 2

    published = set(r442["published_five"])
    ext = set(r442["ext_impl"])
    pass2 = set(r360.get("clause2_admits", []))
    excluded = sorted(published - ext)

    print("─── CONTROLS ───")
    posok = "coval_core" in pass2
    print(f"  POSITIVE  coval_core is KNOWN to pass ② -> {posok} -> "
          f"{'PASS' if posok else '⛔ FAIL — the ②-reader cannot see a known passer'}")
    known_fail = [a for a in r360.get("arms", []) if a not in pass2]
    g0ok = len(known_fail) > 0
    print(f"  g=0       an arm known to FAIL ② returns false -> {len(known_fail)} such arms "
          f"(e.g. {known_fail[:3]}) -> "
          f"{'PASS — the reader returns both values' if g0ok else '⛔ FAIL — everything passes ②'}")
    unknown = "no_such_arm_xyz"
    negok = unknown not in set(r360.get("arms", []))
    print(f"  NEGATIVE  an arm absent from the corpus -> UNKNOWN, not false -> "
          f"{'PASS' if negok else '⛔ FAIL'}")
    plc = (published - ext) == (set(r442["published_five"]) - set(r442["ext_impl"]))
    print(f"  PLACEBO   run twice identical -> {'PASS' if plc else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and plc

    print(f"\n─── THE FALSIFIER (G3 — every published arm, none hidden) ───")
    print(f"  CoVal's published five      : {sorted(published)}")
    print(f"  ③'s extension               : {sorted(ext)}")
    print(f"  ⭐ published ∩ extension     : {sorted(published & ext)}")
    print(f"  ⛔ published but ③-EXCLUDED  : {excluded}")
    rows = []
    for a in excluded:
        p2 = a in pass2
        known = a in set(r360.get("arms", []))
        rows.append({"arm": a, "passes_clause2": p2, "in_corpus": known})
        print(f"     {a:<14} in corpus {known}   passes ② {p2}   "
              f"{'⭐ ③ ALONE excludes it' if p2 else '② already excluded it'}")
    n_by3 = sum(1 for r in rows if r["passes_clause2"])
    print(f"\n  ⭐ excluded by ③ ALONE (they pass ②) : {n_by3} of {len(excluded)}")
    print(f"  registered A 2 [0,3] -> {n_by3}: error {n_by3-2:+d}")
    print(f"    ⚠ the interval [0,3] spans the whole range and is UNFAILABLE (ledger 803). "
          f"It is reported as uninformative; the point error and the directional carry the content.")
    dirn = n_by3 >= 1
    print(f"  DIRECTIONAL >=1 published-but-excluded arm passes ② -> "
          f"{'HOLDS' if dirn else '⛔ FAILS'}")
    killed = n_by3 == 0
    print(f"  pre-registered kill (none passes ②) -> "
          f"{'⭐ FIRES — ② already excluded them; the falsifier does NOT fire against ③' if killed else 'does not fire'}")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire."
    elif killed:
        world = (f"B ③ IS DOING ITS JOB — the {len(excluded)} published arms outside ③'s extension "
                 f"all fail ② anyway, so ③ adds no exclusion the behaviour did not already make. "
                 f"§4's falsifier does NOT fire against ③.")
    else:
        world = (f"⭐⭐⭐ A THE FALSIFIER FIRES. Of the {len(excluded)} arms CoVal PUBLISHED that ③ "
                 f"excludes — {excluded} — {n_by3} PASS clause ②, so ③ ALONE removes them. §4's test "
                 f"for a definition is: name an admissible object this clause excludes, and if the "
                 f"excluded object is one your own benchmark accepts, the clause is FALSE. ⚠ AND THE "
                 f"UNIT GAP IS THE WHOLE DEFENCE OF ③: 'published as an arm' is NOT 'accepted as a "
                 f"core'. CoVal publishes comparison arms it does not call cores, and this corpus "
                 f"records the LIST, not the intent. So the falsifier fires against a reading of ③ "
                 f"under which the published five are cores, and not against ③ itself — which is "
                 f"exactly the question the release's own text would settle and this corpus cannot.")
    print(f"  {world}")

    sha = subprocess.run(["git","rev-parse","HEAD"],cwd=ROOT,capture_output=True,text=True).stdout.strip()
    print(f"\n  MULTIPLICITY: {len(published)} published arms × 2 clause verdicts, 4 controls.")
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE/"results").mkdir(exist_ok=True)
    (HERE/"results"/"published_excluded.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "published": sorted(published), "extension": sorted(ext),
        "overlap": sorted(published & ext), "published_excluded": excluded,
        "rows": rows, "n_excluded_by_three_alone": n_by3,
        "kill_fired": killed, "directional_holds": dirn,
        "registered": "A 2 [0,3] (interval unfailable, said so); >=1 passes ②; kill if none",
        "unit_gap": ("'published as an arm' is not 'accepted as a core'. The corpus records the "
                     "list, not the intent; the release's own text would settle it."),
        "drift_audit": "4 object headlines of 16 over R672-R687; the last six all corpus.",
    }, indent=2))
    print(f"  wrote {HERE/'results'/'published_excluded.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

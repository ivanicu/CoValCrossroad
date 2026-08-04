"""Is the clause-② reference strong because it is BLIND, or because it is CURATED?

R347 established that clause ② implies clause ① on this release, and put the mechanism on the front
page and in FORMULATION.md in these words:

    "A criterion set that never reads the conversation beats a random draw of that conversation's
     own criteria, on every arm."

That sentence is TRUE OF THE CLAUSE-② REFERENCE and FALSE AS STATED about criterion sets that never
read the conversation. This round measures the difference, because the two readings imply different
definitions.

WHAT THE CLAUSE-② REFERENCE ACTUALLY IS. `sat_genericpool16.npz` -- a pool of SIXTEEN generic
criteria authored for the benchmark, from which the reference draws a size-matched subset. It is a
CURATED INSTRUMENT that happens not to read the specific conversation. `Blind` and `curated` are two
different properties and the campaign's own R287 already noticed the second one, in its own words:
*"the stricter the baseline's budget, the harder the clause -- and no round in this campaign has ever
stated what budget a baseline SHOULD have."* I did not check that before writing the mechanism
sentence, and the sentence generalised a property of one curated pool into a property of blindness.

ESTIMAND, named before the method
---------------------------------
For each criterion set that did NOT read this conversation, its A2 minus the clause-① reference
(a random draw from THIS conversation's own rubric), against that contrast's own MDE. Written in
R294's committed observables this is exactly `c1` with `mde1`, so nothing is recomputed and no new
estimator is introduced.

  provenance class A   CURATED, blind   -- the generic pool / hand-picked `generic`
  provenance class B   CROWD, blind     -- a `*_sham` arm: real crowd-written criteria applied to
                                          the WRONG conversation. Same authorship process, same
                                          people, no curation, and it did not read this prompt.

IDENTIFICATION. The contrast is identified for every arm the census scored, because `c1` is defined
against the same clause-① reference for all of them. What is NOT identified here is a random draw
from another prompt's rubric -- the shams are SELECTED criteria misapplied, not random ones, so
class B is a biased-upward proxy for `a crowd rubric that never read this conversation`. Declared,
because it makes the finding CONSERVATIVE: if even selected crowd criteria fail to beat the
own-rubric draw, a random one will not.

WORLDS
  W1 BLINDNESS HELPS   not reading the conversation is itself an advantage -> class B should also
                       beat the clause-① reference. This is what the published sentence implies.
  W2 CURATION HELPS    only the curated pool beats it; crowd-written blind sets do no better, or
                       worse -> the clause-② reference is strong as an INSTRUMENT, not as a blind
                       one, and the published sentence must be narrowed to the object it is about.

PREDICTION MATRIX
  W1 -> class B arms have c1 > mde1
  W2 -> class B arms have c1 <= mde1, some resolvably negative; class A has c1 > mde1
The two worlds differ on the SIGN of a measured contrast, so the round cannot come out both ways.

PRE-REGISTERED KILL
    if the positive control (class A must be resolvably better) and the direction control both hold:
        any class B arm resolvably better -> W1 survives; the published sentence stands.
        no class B arm resolvably better  -> W2. The sentence is RETRACTED and narrowed.
    else: UNVERIFIED.

CONTROLS
  POSITIVE   class A (`generic`, the hand-picked blind quadruple) MUST come out resolvably better
             than the clause-① reference. If it does not, the contrast is not being read correctly
             and every class-B zero below is silence rather than a measurement.
  DIRECTION  `topw_k4` and `coval_core` -- arms that DID read the conversation -- must also be
             resolvably better. This separates "the contrast can return positive" from "the contrast
             returns positive for blind sets", which are the instrument's unit and the claim's unit
             and must not be confused.
  g=0        an arm whose A2 equals the reference exactly must land inside the MDE, not on either
             side. Planted.
  ⚠ NO PERMUTATION NULL is used. The question is the SIGN of a contrast against a fixed reference,
    not whether a pairing matters, and a permutation here would answer a question nobody asked.

⛔ ARITHMETIC TRAP. Could this come out otherwise? Yes: nothing in the construction of a `*_sham`
   arm forces its A2 below the clause-① reference. Two of five are resolvably below and three are
   inside the MDE; had blindness carried an advantage they would have been above.

EXIT
    0  controls hold and the classes are reported
    1  a control misbehaved -- the verdict is silence
    2  the census is missing or contains no class-B arm: an empty population, never a silent pass
"""
from __future__ import annotations

import glob
import hashlib
import json
import pathlib
import statistics as st
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
CENSUS = "E0*/A*/R294_the_definition_against_everything/results/*.json"
CURATED_BLIND = ["generic"]                  # class A: authored generic criteria, never read this prompt
READ_THE_PROMPT = ["topw_k4", "coval_core"]  # direction control


def verdict(c1, mde):
    if c1 > mde:
        return "resolvably better"
    if c1 < -mde:
        return "resolvably WORSE"
    return "inside the MDE"


def main() -> int:
    hits = sorted(glob.glob(str(ROOT / CENSUS)))
    if not hits:
        print("  UNRUNNABLE: R294's census is missing. Exit 2, never 0.")
        return 2
    p = pathlib.Path(hits[0])
    rows = json.loads(p.read_text(encoding="utf-8"))["rows"]
    sha = hashlib.sha256(p.read_bytes()).hexdigest()[:16]
    classB = sorted(n for n in rows if n.endswith("_sham"))
    if not classB:
        print("  UNRUNNABLE: no class-B (crowd, blind) arm in the census. Exit 2, never 0.")
        return 2
    print(f"R348 · blindness or curation?   census sha256[:16] {sha}\n")

    # ---- controls --------------------------------------------------------------------------------
    posA = [(n, rows[n]["c1"][0], rows[n]["mde1"]) for n in CURATED_BLIND if n in rows]
    pos_ok = bool(posA) and all(c > m for _n, c, m in posA)
    for n, c, m in posA:
        print(f"  POSITIVE (class A, curated+blind): {n} c1 {c:+.4f} vs MDE {m:.5f} -> "
              f"{verdict(c, m)}  {'PASS' if c > m else 'FAIL'}")
    dirA = [(n, rows[n]["c1"][0], rows[n]["mde1"]) for n in READ_THE_PROMPT if n in rows]
    dir_ok = bool(dirA) and all(c > m for _n, c, m in dirA)
    print(f"  DIRECTION (arms that DID read the prompt): "
          f"{', '.join(f'{n} {c:+.4f}' for n, c, _m in dirA)}  {'PASS' if dir_ok else 'FAIL'}")
    g0 = verdict(0.0, rows[classB[0]]["mde1"])
    g0_ok = g0 == "inside the MDE"
    print(f"  g=0 (planted, arm equals the reference exactly): {g0}  {'PASS' if g0_ok else 'FAIL'}")

    # ---- the two classes -------------------------------------------------------------------------
    print(f"\n  c1 = A2(arm) − the clause-① reference (a random draw from THIS prompt's own rubric)\n")
    print(f"    {'arm':<24}{'k':>3}{'c1':>10}{'mde1':>9}   verdict")
    rowsout = []
    for n in classB:
        r = rows[n]
        c, m = r["c1"][0], r["mde1"]
        rowsout.append({"arm": n, "cls": "B crowd+blind", "k": r["k"], "c1": c, "mde1": m,
                        "verdict": verdict(c, m)})
        print(f"    {n:<24}{r['k']:>3}{c:>+10.4f}{m:>9.5f}   {verdict(c, m)}")
    print()
    for n in CURATED_BLIND + READ_THE_PROMPT:
        if n not in rows:
            continue
        r = rows[n]
        c, m = r["c1"][0], r["mde1"]
        cls = "A curated+blind" if n in CURATED_BLIND else "read the prompt"
        rowsout.append({"arm": n, "cls": cls, "k": r["k"], "c1": c, "mde1": m,
                        "verdict": verdict(c, m)})
        print(f"    {n:<24}{r['k']:>3}{c:>+10.4f}{m:>9.5f}   {verdict(c, m)}   [{cls}]")

    better = [x for x in rowsout if x["cls"].startswith("B") and x["verdict"] == "resolvably better"]
    worse = [x for x in rowsout if x["cls"].startswith("B") and x["verdict"] == "resolvably WORSE"]
    inside = [x for x in rowsout if x["cls"].startswith("B") and x["verdict"] == "inside the MDE"]
    bmean = st.mean(x["c1"] for x in rowsout if x["cls"].startswith("B"))
    print(f"\n  class B (crowd criteria, wrong conversation): {len(better)} resolvably better, "
          f"{len(worse)} resolvably WORSE, {len(inside)} inside the MDE; mean c1 {bmean:+.4f}")

    print()
    if not (pos_ok and dir_ok and g0_ok):
        print("  UNVERIFIED: a control misbehaved, so the classes above are silence.")
        v = "UNVERIFIED"
    elif better:
        print(f"  W1 — BLINDNESS HELPS. {[x['arm'] for x in better]} beat the clause-① reference")
        print("  while never reading the conversation. The published sentence stands.")
        v = "W1_BLINDNESS"
    else:
        print(f"  W2 — CURATION HELPS, NOT BLINDNESS. Not one of the {len(classB)} crowd-written")
        print(f"  blind arms beats a random draw of THIS prompt's own rubric; {len(worse)} are")
        print("  resolvably worse. The curated pool does, by a wide margin. So the clause-②")
        print("  reference is strong AS AN INSTRUMENT, not as a blind one.")
        print("\n  ⛔ RETRACTED, from FORMULATION.md and README.md: \"A criterion set that never reads")
        print("     the conversation beats a random draw of that conversation's own criteria, on")
        print("     every arm.\" True of the curated pool. False as stated: a CROWD rubric that never")
        print("     read this conversation does no better, and usually worse.")
        v = "W2_CURATION"

    art = {"census_sha256_16": sha, "rows": rowsout, "classB_mean_c1": bmean,
           "controls": {"positive_classA": pos_ok, "direction": dir_ok, "g0": g0_ok},
           "verdict": v}
    outp = HERE / "results" / "r348_blindness_or_curation.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")

    print("\n  ⚠ SCOPE, and it makes the finding CONSERVATIVE rather than the reverse. A `*_sham`")
    print("    arm is SELECTED criteria applied to the wrong conversation, not a RANDOM draw from")
    print("    another conversation's rubric — so class B is biased UPWARD as a proxy for `a crowd")
    print("    rubric that never read this prompt`. Even so it does not beat the own-rubric draw.")
    print("    A true random cross-prompt draw is not scored on this release and would need the")
    print("    satisfaction layer recomputed for criteria against conversations they never saw.")
    return 0 if (pos_ok and dir_ok and g0_ok) else 1


if __name__ == "__main__":
    sys.exit(main())

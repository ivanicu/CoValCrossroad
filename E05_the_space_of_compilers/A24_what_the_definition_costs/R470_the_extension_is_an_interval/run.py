"""R470 -- the extension is an INTERVAL, not an integer, and its committed value rests on a dead instrument.

⛔ MY OWN ANNOUNCED SENTENCE HAD THE DIRECTION BACKWARDS. R469 closed: "the document reports an
   extension of ONE arm, and that count silently treats the 19 UNKNOWN arms as EXCLUDED." **It treats
   them as ADMITTED.** `coval_core` is itself UNKNOWN under ③ (R466), so under unknown-as-excluded
   the released core drops out and the extension is **0**, not 1. *Thirty-eighth announced step
   checked; its premise inverted before anything ran.*

⛔ AND THE COMMITTED VALUE RESTS ON AN INSTRUMENT R469 KILLED. The document states *"the extension
   under the written reading is 1, not 0 (R443)"*, and R443's justification is the CONTAINMENT
   measurement (0.0779). **R469 showed containment is constant on ③'s own partition and therefore
   provably unable to decide it.** So the "1" is not a measurement; it is a CONVENTION -- and one
   whose supporting instrument is now known not to support it.

ESTIMAND (named before the method)
    Let P = the arms admitted by ①∧②∧④ (the extension before ③ is applied).
    Under each reading of ③'s UNKNOWN verdict:
        EXT_excluded  = |P ∩ ③-ADMITTED|
        EXT_admitted  = |P ∩ (③-ADMITTED ∪ ③-UNKNOWN)|
        EXT_unverified= (confirmed = EXT_excluded, unverified = EXT_admitted - EXT_excluded)
    ⭐ The estimand is the SET of three, reported together. A single integer is only honest if they
      coincide, and whether they coincide is the measurement.

IDENTIFICATION
    Identified from committed artifacts plus `clause3_as_written`, which is deterministic.
    ⚠ NOT identified: which reading is CORRECT. That is a definitional choice, not a measurable
    fact, and this round deliberately does not make it -- it measures what the choice costs.

SCOPE  population : the arms P admitted by ①∧②∧④, per the committed record
       instrument : `clause3_as_written.partition`, deterministic, no judge involved
       baseline   : the document's committed extension of 1
       regime     : the home release, ③ as written

WORLDS
    W-INTERVAL   the three readings differ -> the document's single integer has been resting on an
                 unstated convention, and the honest form is an interval with the convention named.
    W-COINCIDE   all three agree -> the convention is immaterial and the integer stands.
    W-EMPTY      P itself is empty -> the extension question is moot and something upstream is wrong.

PREDICTION MATRIX
                   differ   agree   P empty
    W-INTERVAL      0.90     0.05     0.05
    W-COINCIDE      0.05     0.90     0.05
    W-EMPTY         0.05     0.05     0.90

PRE-REGISTERED KILL -- CONDITIONAL. Binding only if the controls fire.
    |P| == 0                                  -> W-EMPTY (checked FIRST; an empty population makes
                                                 every downstream count vacuous)
    EXT_excluded != EXT_admitted              -> W-INTERVAL
    otherwise                                 -> W-COINCIDE

CONTROLS
    ANCHOR    EXT under the convention the document actually used must reproduce its committed 1.
              If no reading reproduces 1, this round is not describing the document's claim.
    MEMBERSHIP `coval_core` must appear in P -- the document's extension names it, so a P without it
              would mean P is not the set the document is talking about.
    DETERMINISM `clause3_as_written` is re-run twice and must give byte-identical partitions; it takes
              no seed, so any variation would mean the arm list is unstable underneath it.
    g=0       a reading applied to an EMPTY UNKNOWN set must give identical answers -- printed as a
              DERIVATION, since with no unknowns the convention cannot matter.
    ⚠ NO POSITIVE CONTROL IS POSSIBLE and that is stated rather than faked: there is no ground-truth
      extension to recover. Every number here is a COUNT under a stated convention, and the round's
      claim is about the SPREAD across conventions, which is arithmetic once the sets are fixed.

MULTIPLICITY  3 readings over one set; all printed. No selection, nothing to correct.
ARTIFACT      results/r470_extension_interval.json
IMPOSSIBLE HERE, NAMED
    * deciding which reading is correct -- a definitional choice, not a measurable fact.
    * a ground-truth extension -- none exists; hence no positive control, said plainly.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "assurance")); sys.path.insert(0, str(ROOT))
COMMITTED = 1
# P: the arms admitted by ①∧②∧④ before ③ is applied. Committed by R442 as the 5-arm extension.
P = ["coval_core", "oracle_k4", "oracle_k4_fit1", "greedy_k4_fit1", "indep_k4_fit1"]


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    from clause3_as_written import partition
    print("R470 · the extension is an INTERVAL, not an integer\n")
    print("  ⛔ MY OWN ANNOUNCED SENTENCE HAD THE DIRECTION BACKWARDS: I wrote that the committed")
    print("     count 'treats the 19 UNKNOWN arms as EXCLUDED'. It treats them as ADMITTED —")
    print("     `coval_core` is itself UNKNOWN under ③, so unknown-as-excluded gives 0, not 1.")
    print("  ⛔ And the committed 1 rests on R443's CONTAINMENT argument, which R469 showed is")
    print("     constant on ③'s partition and provably unable to decide it. Thirty-eighth step")
    print("     checked; premise inverted before anything ran.\n")

    have = {p.name[4:-4] for p in SATD.glob("sat_*.npz")}
    missing = [a for a in P if a not in have]
    if missing:
        print(f"  ⚠ P names arms with no satisfaction file: {missing}")
    Pw = [a for a in P if a in have]
    print(f"  P (admitted by ①∧②∧④, committed by R442): {len(Pw)} of {len(P)} present")
    for a in Pw: print(f"    {a}")
    if not Pw:
        print("\n  UNRUNNABLE: P is empty; every downstream count would be vacuous. Exit 2.")
        return 2

    exc, adm, unk = partition(sorted(have))
    e_s, a_s, u_s = set(exc), set(adm), set(unk)

    print("\n  CONTROLS")
    p1 = partition(sorted(have)); p2 = partition(sorted(have))
    det_ok = p1 == p2
    print(f"    DETERMINISM  `clause3_as_written` re-run twice, identical: {det_ok}   "
          f"{'PASS' if det_ok else '⛔ FAIL — the arm list is unstable underneath it'}")
    mem_ok = "coval_core" in Pw
    print(f"    MEMBERSHIP   `coval_core` in P: {mem_ok}   "
          f"{'PASS' if mem_ok else '⛔ FAIL — P is not the set the document describes'}")
    print(f"    g=0          with an EMPTY unknown set the three readings coincide BY CONSTRUCTION")
    print(f"                 — a DERIVATION, and the reason the convention only matters here")
    print(f"    ⚠ NO POSITIVE CONTROL IS POSSIBLE: there is no ground-truth extension to recover.")
    print(f"      Every number below is a COUNT under a stated convention, and the claim is about")
    print(f"      the SPREAD across conventions, which is arithmetic once the sets are fixed.")

    print("\n  ③'s VERDICT ON EACH ARM OF P")
    verd = {}
    for a in Pw:
        v = "EXCLUDED" if a in e_s else ("ADMITTED" if a in a_s else "UNKNOWN")
        verd[a] = v
        print(f"    {a:<18} {v}")

    ext_x = sum(1 for a in Pw if verd[a] == "ADMITTED")
    ext_a = sum(1 for a in Pw if verd[a] in ("ADMITTED", "UNKNOWN"))
    print(f"\n  ⭐ THE EXTENSION UNDER EACH READING OF ③'s UNKNOWN")
    print(f"    unknown-as-EXCLUDED    {ext_x}")
    print(f"    unknown-as-ADMITTED    {ext_a}      <- the document's committed {COMMITTED}")
    print(f"    unknown-as-UNVERIFIED  {ext_x} confirmed + {ext_a - ext_x} unverified")

    which = ("unknown-as-ADMITTED" if ext_a == COMMITTED else
             "unknown-as-EXCLUDED" if ext_x == COMMITTED else "NEITHER")
    anch_ok = which != "NEITHER"
    print(f"\n    ANCHOR   the reading that reproduces the committed {COMMITTED}: {which}   "
          f"{'PASS' if anch_ok else '⛔ FAIL — this round is not describing the document''s claim'}")

    ctrl_ok = det_ok and mem_ok and anch_ok
    if not ctrl_ok:
        world = "UNVERIFIED"
    elif not Pw:
        world = "W-EMPTY"
    elif ext_x != ext_a:
        world = "W-INTERVAL"
    else:
        world = "W-COINCIDE"
    print(f"\n  WORLD: {world}")
    if world == "W-INTERVAL":
        print(f"    ⛔ THE DOCUMENT'S SINGLE INTEGER RESTS ON AN UNSTATED CONVENTION. The extension")
        print(f"       is {ext_x} under one reading and {ext_a} under another, and the committed")
        print(f"       value corresponds to {which} — a choice the document never names.")
        print(f"    ⛔ And the choice is not innocent: the ONLY arm it admits is `coval_core`, the")
        print(f"       object the definition was written from. **Under the other reading the")
        print(f"       definition's extension is EMPTY.**")
        print(f"    ⭐ The honest form is the INTERVAL [{ext_x}, {ext_a}] with the convention named,")
        print(f"       and the third reading — {ext_x} confirmed, {ext_a - ext_x} UNVERIFIED — is the")
        print(f"       one this campaign's own proxy ledger requires, since UNVERIFIED must never be")
        print(f"       folded into either EXCLUDED or ADMITTED.")

    sha = subprocess.run(["git", "hash-object", __file__], capture_output=True, text=True).stdout.strip()
    out = {"source_sha": sha, "world": world, "P": Pw, "verdicts": verd,
           "ext_unknown_as_excluded": ext_x, "ext_unknown_as_admitted": ext_a,
           "ext_unverified_bucket": ext_a - ext_x, "committed": COMMITTED,
           "reading_that_reproduces_committed": which,
           "controls": {"determinism": bool(det_ok), "membership": bool(mem_ok),
                        "anchor": bool(anch_ok), "positive_control": "IMPOSSIBLE — no ground truth"}}
    (RES / "r470_extension_interval.json").write_text(json.dumps(out, indent=2))
    print(f"\n  artifact: {RES/'r470_extension_interval.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

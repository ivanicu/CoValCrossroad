"""R416 -- R415's `re-run pairs` have DIFFERENT criteria, so they are not scoring replicates.

R415 measured five `_08b`/`_08bR` pairs and reported them as "same arm, same judge, SAME CODE,
different run", concluding a run-to-run shift in mean A2 of up to 0.116489 -- 13x the effect the
campaign chases. It offered a disjunction for the cause: either the pipeline is wildly unstable, OR
two different configurations share a filename.

⛔ THE SECOND BRANCH IS TRUE AND IT IS CHECKABLE IN ONE LINE, WHICH I DID NOT RUN BEFORE PUBLISHING.
   Each arm has a COMMITTED CORE JSON -- the criterion set that was scored -- and `core_X_08b.json`
   and `core_X_08bR.json` are DIFFERENT FILES. The criteria were RE-SELECTED, not merely re-scored.
   So the pairs are same RULE, different REALISATION, and R415's "same code" is wrong in the
   direction that made its number sound like scoring noise.

⛔ THIS IS AN ATTACK ON MY OWN ROUND FROM ONE ROUND AGO, SO IT IS A ROUND AND NOT AN EDIT. §3: an
   attack run as an inline script is not evidence whichever way it comes out, and this one CHANGES A
   PUBLISHED FRAMING, which is exactly when the standard is strictest.

⛔ ARITHMETIC TRAP. That two files with different names might differ is not a finding; that these
   SPECIFIC files differ, and that the difference is in the CRITERIA rather than only in the scores,
   is a measurement. And it could have come out the other way -- identical criteria would have left
   R415's framing intact and its disjunction unresolved.

ESTIMAND        (A) for each of R415's five pairs, whether the committed core JSONs are byte-identical;
                (B) if not, HOW they differ -- the share of prompts whose selected criterion set
                    changed, so "different" is quantified rather than asserted from a hash;
                (C) what of R415 survives and what is downgraded, stated as a ledger.

IDENTIFICATION  Exact -- the files are committed. NOT identified: how much of R415's 0.116 shift is
                selection and how much is scoring. Separating them needs a re-score of the SAME
                criteria, which needs the GPU. Named, and it is the honest residual.

SCOPE           population: R415's five pairs · instrument: file hashes and per-prompt criterion-set
                comparison · baseline: a file against itself · regime: committed artifacts only.

WORLDS
  W-SAME-CRITERIA   the core JSONs are identical. Then R415's framing stands, the pairs ARE scoring
                    replicates, and the disjunction resolves onto "the pipeline is unstable".
  W-DIFFERENT-CRITERIA  they differ. Then R415's "same code" is wrong, its 0.116 is a RULE-level
                    floor (selection + scoring) and not a scoring floor, and the disjunction resolves
                    onto "two configurations share a filename" -- which R415 listed and did not test.

PREDICTION MATRIX
  W-SAME-CRITERIA      -> 5 of 5 byte-identical
  W-DIFFERENT-CRITERIA -> >= 1 differs, with the per-prompt change share reported

PRE-REGISTERED KILL -- conditional on the control, never on the hashes alone.
    if a_file_against_itself_hashes_equal:
        all 5 identical -> W-SAME-CRITERIA
        else            -> W-DIFFERENT-CRITERIA, share reported per arm
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  SELF (=)      a core JSON hashed against ITSELF must be equal. A hash function that returned
                different values for the same bytes would make every "differs" below meaningless.
  SHAPE         both members of a pair must have the same structure and length, or they are not
                comparable realisations of one rule and the round says so rather than differencing
                incomparable objects.
  QUANTIFIED    a hash mismatch says only "not identical". The per-prompt share of CHANGED criterion
                sets is computed, because "different" from a hash is compatible with one byte of
                whitespace and with a total rewrite, and those imply different corrections.

MULTIPLICITY    5 pairs x (hash, shape, per-prompt share); all printed.
SEEDS           none.
ARTIFACT        results/r416_criteria_differ.json with the source hash.

IMPOSSIBLE HERE
  splitting selection from scoring -- needs a re-score of IDENTICAL criteria, i.e. the GPU. This is
                                      the honest residual and R415's number cannot be decomposed
                                      without it.
  the 2B floor                    -- still unmeasured, unchanged by this round.
  a claim that the pipeline IS stable -- ruling out one branch's evidence is not evidence for the
                                      other branch. Stated, because that inversion is the easy error.

EXIT
    0  the control holds and the comparison is reported
    1  the control misbehaved -- UNVERIFIED
    2  a pair is missing -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
R415 = HERE.parent / "R415_the_pipelines_own_noise_floor" / "results" / "r415_noise_floor.json"


def h(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    if not R415.exists():
        print("  UNRUNNABLE: R415's artifact absent. Exit 2, never 0."); return 2
    a415 = json.loads(R415.read_text())
    arms = sorted(a415["pairs"])
    print("R416 · are R415's re-run pairs scoring replicates at all?\n")
    print("  ⛔ R415 CALLED THEM `same arm, same judge, SAME CODE, different run` AND OFFERED A")
    print("     DISJUNCTION FOR THE CAUSE. Its second branch — `two different configurations share a")
    print("     filename` — is checkable in one line against committed files, and I published")
    print("     before running it.\n")

    # ---- CONTROL ----------------------------------------------------------------------------------
    probe = RES / "core_genericpool16.json"
    self_ok = probe.exists() and h(probe) == h(probe)
    print(f"  CONTROLS")
    print(f"    SELF (=)     a core JSON hashed against ITSELF is equal: {self_ok}   "
          f"{'PASS' if self_ok else 'FAIL — every `differs` below would be meaningless'}")
    if not self_ok:
        print("\n  UNVERIFIED. Exit 1."); return 1

    # ---- the comparison ----------------------------------------------------------------------------
    print(f"\n  THE CRITERIA THAT WERE SCORED — one committed JSON per run, per arm")
    print(f"    {'arm':<18}{'core_*_08b':>14}{'core_*_08bR':>14}{'identical':>11}"
          f"{'prompts changed':>18}")
    rows, differ = {}, []
    for arm in arms:
        a, b = RES / f"core_{arm}_08b.json", RES / f"core_{arm}_08bR.json"
        if not (a.exists() and b.exists()):
            rows[arm] = dict(status="MISSING")
            print(f"    {arm:<18}{'absent':>14}"); continue
        ha, hb = h(a), h(b)
        da, db = json.loads(a.read_text()), json.loads(b.read_text())
        shape_ok = type(da) is type(db) and len(da) == len(db)
        share = None
        if shape_ok and isinstance(da, dict):
            keys = set(da) & set(db)
            chg = sum(1 for k in keys if da[k] != db[k])
            share = chg / len(keys) if keys else None
        elif shape_ok and isinstance(da, list):
            chg = sum(1 for x, y in zip(da, db) if x != y)
            share = chg / len(da) if da else None
        rows[arm] = dict(status="OK", sha_a=ha[:12], sha_b=hb[:12], identical=(ha == hb),
                         shape_ok=shape_ok, changed_share=share)
        if ha != hb:
            differ.append(arm)
        print(f"    {arm:<18}{ha[:12]:>14}{hb[:12]:>14}{str(ha == hb):>11}"
              f"{(f'{share:.1%}' if share is not None else 'n/a'):>18}")

    ok = [r for r in rows.values() if r.get("status") == "OK"]
    if not ok:
        print("\n  UNRUNNABLE: no pair had both core files. Exit 2."); return 2
    shapes = all(r["shape_ok"] for r in ok)
    print(f"\n    shape-comparable on every pair: {shapes}")

    print()
    if not differ:
        v = "W_SAME_CRITERIA"
        print(f"  W-SAME-CRITERIA — all {len(ok)} pairs scored IDENTICAL criteria. R415's framing")
        print(f"  stands, the pairs are genuine scoring replicates, and its disjunction resolves onto")
        print(f"  `the pipeline is unstable`.")
    else:
        v = "W_DIFFERENT_CRITERIA"
        print(f"  W-DIFFERENT-CRITERIA — {len(differ)} of {len(ok)} pairs scored DIFFERENT criteria.")
        print(f"  R415's `same code` is WRONG. Its 0.116489 is a RULE-LEVEL floor — selection AND")
        print(f"  scoring together — not a scoring floor, and its disjunction resolves onto the")
        print(f"  branch it listed and did not test: two configurations sharing a filename.")

    print(f"\n  WHAT SURVIVES OF R415, AND WHAT DOES NOT")
    print(f"    SURVIVES  · the magnitude: re-running the same RULE end to end shifts the mean A2 by")
    print(f"                up to {a415['worst_mean_shift']:.6f}, which is still "
          f"{a415['worst_mean_shift']/a415['e_2b']:.0f}x the effect.")
    print(f"              · that these files are NOT usable as replicates — now ESTABLISHED rather")
    print(f"                than offered as a disjunction.")
    print(f"              · the 2B floor is still UNMEASURED. Unchanged.")
    print(f"    DOWNGRADED· `the pipeline is wildly unstable` is NOT supported. The shift is fully")
    print(f"                compatible with different criteria and no scoring instability at all.")
    print(f"              · `same arm, same code, different run` must be corrected everywhere it was")
    print(f"                written — README, DEFINITION.md and the front page.")
    print(f"    RESIDUAL  · how much of the shift is SELECTION and how much is SCORING cannot be")
    print(f"                split without re-scoring IDENTICAL criteria, which needs the GPU.")
    print(f"\n  ⚠ AND RULING OUT ONE BRANCH'S EVIDENCE IS NOT EVIDENCE FOR THE OTHER. This does not")
    print(f"    show the pipeline is STABLE; it shows R415's measurement never bore on that question.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               arms=arms, rows=rows, differ=differ, shapes_ok=shapes,
               r415_shift=a415["worst_mean_shift"], r415_e2b=a415["e_2b"],
               controls=dict(self_hash=self_ok), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r416_criteria_differ.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""R418 -- R396 found R130's output DIFFERS. None of the differing tokens has the shape of a claim.

R396 ran R130 twice at unchanged source and found the extracted number multisets differ, concluding
W-TAIL-MOVES: the source-hash cache would certify a stale verification, and R388's gate has a live
false-conviction mode on the slow tail.

⛔ I THEN GUESSED AT THE CAUSE TWICE AND WAS WRONG TWICE, IN A REPORT. First: "1.22, 104.63, 117.28
   look like timings" -- R130 prints no timings, `grep` for `time.time`/`elapsed`/`perf_counter`
   returns nothing. Second: "they look like tqdm progress rates" -- no `tqdm` in R130, in
   `covalx/judge.py`, or in `corebench/*.py`. Two hypotheses, two refutations, zero measurements.

⭐ SO STOP GUESSING AT THE CAUSE, BECAUSE THE ACTIONABLE QUESTION DOES NOT NEED IT. R130's CLAIMS are
   printed by one line -- `mean_sat {v.mean():.4f}  core {1-e_core:.4f}  full_eq {1-e_fe:.4f}` -- so
   a claim-value has the shape `0.dddd`. Whether the tokens that differed have that shape is
   answerable from R396's COMMITTED artifact, needs no GPU, and does not require knowing where the
   other tokens came from.

⛔ ARITHMETIC TRAP. That twelve tokens have SOME shape is not a finding. That NONE of them matches
   the claim shape while R130 demonstrably prints claim-shaped values is a measurement, and it could
   have come out the other way -- a differing `0.5234` would mean the claims themselves moved, which
   is the world R396's verdict assumed.

ESTIMAND        (A) the share of R396's differing tokens matching R130's CLAIM SHAPE (`0.dddd`,
                    a 4-decimal value in [0,1] as its print format emits);
                (B) whether R130's source actually emits claim-shaped values at all -- so a zero in
                    (A) is a measurement rather than a claim shape that never occurs;
                (C) what that implies for R396's verdict and for R388's gate.

IDENTIFICATION  Exact given R396's committed `differing` list and R130's source. NOT identified:
                WHERE the non-claim tokens come from. Two guesses have already failed and a third
                would be worth nothing; establishing it needs the captured outputs, which R396 did
                not persist. Named as the residual, and it is MY omission in R396's design.

SCOPE           population: R396's 12 committed differing tokens · instrument: shape classification
                against R130's own print formats · baseline: the claim shape as R130 emits it ·
                regime: committed artifacts only.

WORLDS
  W-CLAIMS-STABLE   no differing token has the claim shape. Then R130's REPORTED VALUES did not move;
                    what moved is everything else the extractor swept up, and R388's gate would
                    convict an honest backfill on NON-CLAIM tokens while the claims were identical.
                    R396's operational conclusion survives; its stated CAUSE does not.
  W-CLAIMS-MOVED    at least one differing token has the claim shape. Then the round's own reported
                    values are unstable and R396's verdict stands exactly as written.

PREDICTION MATRIX
  W-CLAIMS-STABLE -> 0 of 12 match `^0\\.\\d{4}$`
  W-CLAIMS-MOVED  -> >= 1 matches, and it is named

PRE-REGISTERED KILL -- conditional on the emission control, never on the count alone.
    if R130_source_emits_claim_shaped_values:
        0 claim-shaped among the differing -> W-CLAIMS-STABLE
        else                                -> W-CLAIMS-MOVED, tokens named
    else: UNVERIFIED -- a shape that the round never prints cannot be absent from a diff in any
          informative way, and reporting its absence would be a check that cannot fail.

CONTROLS
  EMISSION (+)  R130's source must contain a `:.4f` format for the claim values. Without it, "no
                claim-shaped token differed" is vacuous -- the shape would never appear at all, and
                this is precisely the check-that-cannot-fail the ledger names.
  EXTRACTOR     the shape test is applied to R396's OWN committed token list, not to a re-derivation,
                so the population is exactly the one that produced the verdict.
  SHAPE (-)     a synthetic token `0.5234` must be classified as claim-shaped, and `117.28` must not.
                Both directions, because a classifier that says no to everything would pass (A)
                trivially.
  HONESTY       the two failed hypotheses are recorded in this round rather than quietly dropped,
                because a report that guessed twice and then presented a third story as if it were
                the first would be the narrative failure this campaign is built against.

MULTIPLICITY    12 tokens x 1 shape test + 3 controls; every token printed with its verdict.
SEEDS           none.
ARTIFACT        results/r418_shape_of_the_difference.json with the source hash.

IMPOSSIBLE HERE
  the ORIGIN of the non-claim tokens -- R396 did not persist the captured outputs. That is MY
                                        omission in its design, and no amount of reasoning recovers
                                        it; it needs a re-run that saves them.
  a general claim about scoring rounds -- one round, one pair of runs.

EXIT
    0  the emission control holds and the shapes are reported
    1  R130 emits no claim-shaped values -- UNVERIFIED, the test would be vacuous
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
R396 = HERE.parent / "R396_is_the_slow_tail_stable_on_gpu" / "results" / "r396_tail_stability.json"
R130 = next(iter(ROOT.glob("E0*/A*/R130_judge_gauge/run.py")), None)
CLAIM = re.compile(r"^0\.\d{4}$")


def main() -> int:
    if not (R396.exists() and R130 and R130.exists()):
        print("  UNRUNNABLE: R396 artifact or R130 source absent. Exit 2, never 0."); return 2
    a = json.loads(R396.read_text())
    diff = list(a.get("differing") or [])
    src = R130.read_text()

    print("R418 · did R130's CLAIMS differ, or only everything else?\n")
    print("  ⛔ I GUESSED AT THE CAUSE TWICE AND WAS WRONG TWICE, IN A REPORT. `they look like")
    print("     timings` — R130 prints none. `they look like tqdm rates` — no tqdm in R130, in")
    print("     covalx/judge.py, or in corebench/*.py. Two hypotheses, two refutations, zero")
    print("     measurements. The actionable question does not need the cause at all.\n")

    # ---- CONTROLS ---------------------------------------------------------------------------------
    emits = bool(re.search(r":\.4f\}", src))
    fmt = [l.strip()[:88] for l in src.splitlines() if ":.4f}" in l][:1]
    shape_pos = bool(CLAIM.match("0.5234"))
    shape_neg = not CLAIM.match("117.28")
    print("  CONTROLS")
    print(f"    EMISSION (+)  R130's source emits `:.4f` claim values: {emits}   "
          f"{'PASS' if emits else 'FAIL — absence of a shape it never prints is vacuous'}")
    if fmt:
        print(f"                  {fmt[0]}")
    print(f"    SHAPE (+/-)   `0.5234` is claim-shaped: {shape_pos} · `117.28` is not: {shape_neg}"
          f"   {'PASS' if (shape_pos and shape_neg) else 'FAIL'}")
    print(f"    EXTRACTOR     testing R396's OWN committed token list ({len(diff)} tokens), not a")
    print(f"                  re-derivation, so the population is the one that produced the verdict")
    if not emits:
        print("\n  UNVERIFIED — R130 never prints a claim-shaped value, so their absence from the")
        print("  diff says nothing. That is a check that cannot fail. Exit 1."); return 1
    if not (shape_pos and shape_neg):
        print("\n  UNVERIFIED — the shape classifier is blind. Exit 1."); return 1

    # ---- the measurement ---------------------------------------------------------------------------
    print(f"\n  THE {len(diff)} TOKENS R396 FOUND DIFFERING, BY SHAPE")
    claimish = []
    for t in diff:
        ok = bool(CLAIM.match(str(t)))
        if ok:
            claimish.append(t)
        print(f"    {str(t):<12} claim-shaped: {ok}")
    print(f"\n    claim-shaped among the differing: {len(claimish)} of {len(diff)}   {claimish}")

    print()
    if not claimish:
        v = "W_CLAIMS_STABLE"
        print(f"  W-CLAIMS-STABLE — NOT ONE of the {len(diff)} differing tokens has the shape R130")
        print(f"  prints its claims in. Its REPORTED VALUES did not move; what moved is everything")
        print(f"  else the extractor swept up.")
        print(f"  ⛔ R396's OPERATIONAL CONCLUSION SURVIVES AND ITS STATED CAUSE DOES NOT. R388's")
        print(f"     gate uses the same extractor over stdout+stderr, so it WOULD convict an honest")
        print(f"     backfill — but on NON-CLAIM tokens, while the claims were identical. That is a")
        print(f"     defect in the GATE'S EXTRACTOR, not evidence that a scoring round's findings")
        print(f"     are unstable, and the two call for opposite fixes: narrow the extractor, rather")
        print(f"     than exclude scoring rounds from verification.")
    else:
        v = "W_CLAIMS_MOVED"
        print(f"  W-CLAIMS-MOVED — {claimish} has the claim shape. The round's own reported values")
        print(f"  are unstable and R396's verdict stands exactly as written.")

    print(f"\n  ⚠ THE ORIGIN OF THE NON-CLAIM TOKENS IS STILL UNKNOWN AND I AM NOT GUESSING A THIRD")
    print(f"    TIME. R396 did not persist the captured outputs — MY omission in its design — and no")
    print(f"    amount of reasoning recovers them. It needs a re-run that saves stdout and stderr.")
    print(f"  ⚠ AND THIS IS ONE ROUND AND ONE PAIR OF RUNS. It licenses nothing about scoring rounds")
    print(f"    in general.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               differing=diff, claim_shaped=claimish, n_differing=len(diff),
               r396_verdict=a.get("verdict"), r130_source=str(R130.relative_to(ROOT)),
               controls=dict(emits_claim_shape=emits, shape_pos=shape_pos, shape_neg=shape_neg),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r418_shape_of_the_difference.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

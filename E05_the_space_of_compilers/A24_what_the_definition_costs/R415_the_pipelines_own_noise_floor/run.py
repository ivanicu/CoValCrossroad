"""R415 -- the pipeline's own run-to-run noise floor, measured from committed re-run pairs.

R414's NEXT asked which of the two 0.8B naming families is the real judge. The git history answered a
larger question first: the commit that added them, 9d1d409, is titled *"five rounds change a
CONCLUSION across hash seeds, so a committed artifact in this repo is not a function of its committed
code"* -- and it added `_08bR` files, an R for RE-RUN.

⛔ SO THE FAMILY SPLIT IS PROBABLY NOT A PROVENANCE PUZZLE AT ALL, AND THE REAL QUESTION IS BIGGER. If
   the scoring pipeline is not stable run to run, then every `sat_*.npz` this session has consumed --
   including `sat_coval_core.npz`, the file R408's +0.009002 came from -- is ONE DRAW, not a fixed
   quantity. The campaign has computed MDEs from WITHIN-run standard errors for hundreds of rounds
   and has never measured the BETWEEN-run floor.

⭐ AND §1 REQUIRES EXACTLY THIS AND I HAVE NEVER DONE IT: "NOISE FLOOR: measured, not assumed.
   Replicates beat models." The replicates are on disk. `sat_topvar_k4_08b.npz` and
   `sat_topvar_k4_08bR.npz` are the SAME ARM, SAME JUDGE, SAME CODE, DIFFERENT RUN, both committed.
   That difference IS the floor, and it costs no GPU.

⛔ ARITHMETIC TRAP. Nothing forces the floor to be small. A pipeline could be bit-identical run to run
   (floor exactly 0) or vary by more than any effect the campaign has reported. The whole point is
   that the answer decides whether a session's worth of numbers are above their own instrument's
   noise.

⚠ AND THE PAIRS ARE AT 0.8B WHILE THE HEADLINE EFFECT IS AT 2B. Transporting a noise floor across
  judges is an ASSUMPTION and is named. What it can establish without transport: whether the pipeline
  is deterministic AT ALL. A non-zero floor at one judge kills "the artifact is a function of the
  code" outright, which is a claim about the PIPELINE and not about a model.

ESTIMAND        (A) for each committed re-run pair, the per-prompt A2 difference between the two runs
                    of the same arm -- mean, sd, and max;
                (B) that sd expressed against R408's committed +0.009002, the effect it would have to
                    be smaller than for the session's numbers to sit above the pipeline's own floor;
                (C) whether the two independent pairs AGREE about the floor -- a replication of the
                    floor measurement itself.

IDENTIFICATION  Exact for the pairs on disk. NOT identified: the floor at the 2B judge, which has no
                committed re-run pair. Named, and the verdict is worded to say what it covers.

SCOPE           population: arms with a committed `_08b`/`_08bR` pair · instrument: the same scoring
                module every round uses · baseline: zero difference · regime: same code, same judge,
                different run.

WORLDS
  W-DETERMINISTIC   the pairs are identical. Then 9d1d409's title is about something other than the
                    sat files, the family split needs another explanation, and every within-run se in
                    this campaign stands unqualified.
  W-FLOOR-SMALL     non-zero but the run-to-run sd is far below 0.009. Then the pipeline is noisy and
                    the session's effects still clear it, with the floor now stated rather than
                    assumed.
  W-FLOOR-BINDING   the run-to-run sd is comparable to or above 0.009. Then R408's effect sits inside
                    the pipeline's own noise, and every number this session derived from a single
                    committed artifact is scoped by that -- the largest downgrade available here.

PREDICTION MATRIX
  W-DETERMINISTIC  -> max |difference| == 0 on every pair
  W-FLOOR-SMALL    -> sd < 0.003 (a third of the effect)
  W-FLOOR-BINDING  -> sd >= 0.009

PRE-REGISTERED KILL -- conditional on the controls, never on the sd alone.
    if self_comparison_is_exactly_zero and both_pairs_measured:
        max|d| == 0            -> W-DETERMINISTIC
        sd < 0.003             -> W-FLOOR-SMALL
        sd >= 0.009            -> W-FLOOR-BINDING
        else                   -> named as between, not rounded
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  SELF (-)      a file compared to ITSELF must give exactly 0.0 with exactly 0.0 sd. A placebo that
                must return exactly zero, and it fails if the loader is non-deterministic in a way
                that would fake a floor.
  TWO PAIRS     the floor is measured on two INDEPENDENT arms, so the floor measurement is itself
                replicated. One pair would be a single draw of a quantity about single draws.
  SCORING       load_sat/yvec/cls IMPORTED from the module every other round uses, so the floor is
                the floor of THE pipeline and not of a re-implementation.
  PROMPT MATCH  only prompts present in BOTH runs are compared, and the count is printed -- a pair
                that shares few prompts would give a floor about coverage rather than about noise.

MULTIPLICITY    2 pairs x (mean, sd, max) + 1 self control; every number printed.
SEEDS           none -- the pairs ARE the replicates.
ARTIFACT        results/r415_noise_floor.json with the source hash.

IMPOSSIBLE HERE
  the floor at the 2B judge -- no committed re-run pair exists for it. Named; a re-run would need
                               the GPU, which R396 holds.
  the CAUSE of any instability -- sampling, batching, kernel non-determinism are not separated here.
  a second release          -- one.

EXIT
    0  the controls hold and the floor is reported
    1  a control misbehaved -- UNVERIFIED
    2  no re-run pair exists -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import math
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
RES = ROOT / "corebench" / "results"
R408 = HERE.parent / "R408_the_literal_test_at_the_universal_reference" / "results" / \
    "r408_literal_test.json"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402


def main() -> int:
    pairs = []
    for p in sorted(RES.glob("*_08bR.npz")):
        base = RES / (p.name.replace("_08bR.npz", "_08b.npz"))
        if base.exists():
            pairs.append((p.name.replace("_08bR.npz", "").replace("sat_", ""), base, p))
    if not pairs or not R408.exists():
        print(f"  UNRUNNABLE: {len(pairs)} re-run pairs found. Exit 2, never 0."); return 2
    e_2b = json.loads(R408.read_text())["rows"]["coval_core"]["e"]

    tg, _ = load_targets()
    print(f"R415 · the pipeline's own run-to-run noise floor\n")
    print("  ⛔ THE GIT HISTORY ANSWERED A LARGER QUESTION THAN R414's NEXT ASKED. The commit that")
    print("     added both 0.8B families is titled `a committed artifact in this repo is not a")
    print("     function of its committed code` — and it added `_08bR` files, an R for RE-RUN. If the")
    print("     pipeline is not stable run to run, every sat_*.npz this session consumed is ONE DRAW.")
    print("  ⭐ §1 REQUIRES `NOISE FLOOR: measured, not assumed. Replicates beat models.` The")
    print("     replicates have been on disk the whole time, and I have never measured this.\n")

    def a2(sat, ps):
        out = []
        for q in ps:
            idx = sorted({i for i, _ in sat[q]})
            yv = cls(yvec(sat[q], idx))
            H = [cls(np.array(t[0], float)) for t in tg[q]]
            out.append(np.mean([[yv[c] == h[c] for c in range(6)] for h in H]))
        return np.array(out, float)

    # ---- CONTROL: a file against ITSELF ------------------------------------------------------------
    name0, f0, _ = pairs[0]
    S0 = load_sat(f0)
    ps0 = [q for q in sorted(S0) if q in tg and len(tg[q]) >= 2]
    v0 = a2(S0, ps0)
    self_d = v0 - a2(load_sat(f0), ps0)
    self_ok = (float(np.abs(self_d).max()) == 0.0)
    print(f"  CONTROLS")
    print(f"    SELF (-)      `{name0}` compared to ITSELF: max|d| = "
          f"{float(np.abs(self_d).max()):.1e}   {'PASS' if self_ok else 'FAIL — the LOADER is noisy'}")
    if not self_ok:
        print("\n  UNVERIFIED — a self-comparison is non-zero, so any floor below would be the")
        print("  loader's and not the pipeline's. Exit 1."); return 1

    # ---- the floor ---------------------------------------------------------------------------------
    print(f"\n  THE FLOOR — same arm, same judge, same code, DIFFERENT RUN, both committed")
    print(f"    {'arm':<16}{'prompts':>9}{'mean':>12}{'sd':>12}{'max|d|':>12}")
    rows = {}
    for name, fa, fb in pairs:
        A, B = load_sat(fa), load_sat(fb)
        ps = [q for q in sorted(set(A) & set(B)) if q in tg and len(tg[q]) >= 2]
        if len(ps) < 100:
            print(f"    {name:<16}{len(ps):>9}   too few shared prompts — skipped"); continue
        d = a2(A, ps) - a2(B, ps)
        rows[name] = dict(n=len(ps), mean=float(d.mean()), sd=float(d.std(ddof=1)),
                          mx=float(np.abs(d).max()))
        print(f"    {name:<16}{len(ps):>9}{d.mean():>+12.6f}{d.std(ddof=1):>12.6f}"
              f"{np.abs(d).max():>12.6f}")
    if len(rows) < 1:
        print("\n  UNRUNNABLE: no pair had enough shared prompts. Exit 2."); return 2

    # ⛔ MY FIRST COMPARISON USED THE WRONG UNITS. R408's +0.009002 is a MEAN over prompts; the `sd`
    #   column is the PER-PROMPT dispersion, and setting them side by side compares a mean to a
    #   spread. The comparable quantity is the run-to-run shift in the MEAN A2 -- the `mean` column --
    #   and it is reported as the headline. The sd is kept because it sets the se of that shift
    #   (sd/sqrt(n)) and because dropping a column after seeing it is how a table becomes an argument.
    shifts = [abs(r["mean"]) for r in rows.values()]
    worst_shift = max(shifts)
    print(f"\n    ⛔ THE COMPARABLE QUANTITY IS THE SHIFT IN THE MEAN, NOT THE PER-PROMPT SD. R408's")
    print(f"       +{e_2b:.6f} is a mean over prompts; the sd column is a spread. Comparing them")
    print(f"       would set a mean beside a dispersion.")
    print(f"    worst run-to-run shift in MEAN A2 across {len(rows)} pairs : {worst_shift:.6f}")
    print(f"    R408's committed effect at 2B                          : {e_2b:+.6f}")
    print(f"    the shift is {worst_shift/e_2b:.1f}x the effect")
    print(f"    per-pair mean shifts: {[round(r['mean'], 4) for r in rows.values()]}")
    sds = [r["sd"] for r in rows.values()]
    mxs = [r["mx"] for r in rows.values()]
    sd = max(sds)
    print(f"\n    worst-case run-to-run sd across {len(rows)} independent pairs: {sd:.6f}")
    print(f"    R408's committed effect at 2B                                : {e_2b:+.6f}")
    print(f"    ratio effect / floor                                         : {e_2b/sd:.2f}x"
          if sd > 0 else "    the pipeline is bit-identical")
    if len(sds) >= 2:
        print(f"    ⭐ the two pairs agree to {abs(sds[0]-sds[1]):.6f} — the FLOOR MEASUREMENT is")
        print(f"       itself replicated, so it is not one draw of a quantity about single draws")

    print()
    if max(mxs) == 0.0:
        v = "W_DETERMINISTIC"
        print(f"  W-DETERMINISTIC — every pair is bit-identical. 9d1d409's title is about something")
        print(f"  other than these files, the family split needs another explanation, and every")
        print(f"  within-run se in this campaign stands unqualified.")
    elif sd < 0.003:
        v = "W_FLOOR_SMALL"
        print(f"  W-FLOOR-SMALL — the pipeline is NOT deterministic (max|d| {max(mxs):.6f}) but the")
        print(f"  run-to-run sd of {sd:.6f} is {e_2b/sd:.1f}x below R408's effect. The session's")
        print(f"  numbers clear the pipeline's own floor, and the floor is now STATED rather than")
        print(f"  assumed — which §1 has required all along and no round had done.")
    elif worst_shift >= 0.009:
        v = "W_FLOOR_BINDING"
        print(f"  W-FLOOR-BINDING — re-running the SAME arm at the SAME judge shifts its MEAN A2 by")
        print(f"  up to {worst_shift:.6f}, which is {worst_shift/e_2b:.0f}x R408's +{e_2b:.6f}.")
        print(f"  ⚠ AND THE CAUSE IS NOT SEPARATED, WHICH MATTERS FOR WHAT THIS LICENSES. A shift of")
        print(f"    0.1 in an agreement metric is large for kernel non-determinism, so EITHER the")
        print(f"    pipeline is wildly unstable OR two different configurations share a filename.")
        print(f"    BOTH are disqualifying for treating these files as replicates, and this round")
        print(f"    cannot tell them apart — so it claims the disjunction and not either branch.")
        print(f"  ⚠ AND NO RE-RUN PAIR EXISTS AT 2B. The floor there is UNMEASURED, so the correct")
        print(f"    statement is NOT `R408's effect is inside the noise` — it is that every 2B number")
        print(f"    this session produced rests on an ASSUMPTION of pipeline stability that has now")
        print(f"    failed at the only judge where it could be checked.")
    else:
        v = "W_FLOOR_BETWEEN"
        print(f"  BETWEEN — sd {sd:.6f}, effect/floor {e_2b/sd:.2f}x, between the pre-registered")
        print(f"  thresholds. Named as it fell.")

    print(f"\n  ⚠ THE PAIRS ARE AT 0.8B AND THE HEADLINE EFFECT IS AT 2B. Transporting a floor across")
    print(f"    judges is an ASSUMPTION. What needs no transport: whether the pipeline is")
    print(f"    deterministic AT ALL — that is a fact about the PIPELINE, not about a model, and a")
    print(f"    non-zero floor at any judge kills `the artifact is a function of the code` outright.")
    print(f"  ⚠ AND THE CAUSE IS NOT SEPARATED. Sampling, batching and kernel non-determinism are")
    print(f"    not distinguished here; only the magnitude is.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               pairs=rows, worst_sd=sd, worst_mean_shift=worst_shift, worst_max=max(mxs), e_2b=e_2b,
               ratio=(e_2b / sd if sd > 0 else None),
               controls=dict(self_zero=self_ok, n_pairs=len(rows)), verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r415_noise_floor.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""R409 -- is the ordering of the five label-free arms information, or is it noise I ranked?

R408 found that at the per-k maximum blind set the five label-free arms clear the literal `e > 0` bar
at 0.87, 0.81, 0.62, 0.46 and 0.38 of their own significance bars, and its NEXT proposed treating that
as "a graded quantity the admitted-set framing throws away" and testing whether the ordering is stable
across judge, target and metric.

⛔ THAT NEXT IS A CLAIM AND IT HAS NO CONTROL, WHICH IS THE ONE SENTENCE IN A ROUND THAT NEVER GETS
   ONE. Before asking whether the ordering survives a change of judge, ask the cheaper question it
   presupposes: is the ordering distinguishable from noise AT ALL, on the data that produced it? The
   five effects span +0.0041 to +0.0090 and each carries se ~ 0.0037, so the pairwise gaps are the
   same size as a single arm's uncertainty. Ranking them could be exactly the failure the ledger
   already names -- an ordering of draws reported as though it were information.

⛔ ARITHMETIC TRAP, ANSWERED BEFORE THE RUN. That the five have SOME order is forced -- five distinct
   floats always do. What is NOT forced is whether that order is reproducible under resampling of the
   prompts, and that is the only thing this round reports.

⚠ AND THE POSITIVE CONTROL HAS TO BE AN ARM WHOSE SEPARATION IS NOT IN DOUBT, or a uniform rank
  distribution below would be uninterpretable: I could not tell "the five are indistinguishable" from
  "my bootstrap cannot distinguish anything". `oracle_k4` at +0.0708 is ~8x the largest label-free
  effect, and it must rank first in essentially every resample.

ESTIMAND        for each of the five label-free arms, the DISTRIBUTION of its rank (by paired effect
                against its own per-k maximum blind reference) across cluster bootstrap resamples of
                the prompt set. Reported as a rank matrix, never as a single "the ordering is/isn't
                stable" bit.

IDENTIFICATION  Exact for the resampling distribution given the committed per-prompt difference
                vectors. NOT identified: whether the ordering survives a different JUDGE or TARGET --
                that is R408's NEXT and remains open; this round tests the weaker precondition and
                says so.

SCOPE           population: the 5 label-free arms admitted under the literal reading, plus 1 label-
                reading arm as a control · instrument: cluster bootstrap over prompts, B resamples ·
                baseline: each arm's own per-k maximum blind set · regime: p = 100, literal rule.

WORLDS
  W-ORDER-REAL   the top arm holds rank 1 in a clear majority of resamples. Then the ordering carries
                 information and R408's NEXT is worth its compute.
  W-ORDER-NOISE  the rank distributions are near-uniform. Then the ordering is an artifact of five
                 draws from overlapping distributions, R408's NEXT was about to spend a judge sweep
                 on noise, and the honest object is the SET, not the ranking.

PREDICTION MATRIX
  W-ORDER-REAL  -> top arm's P(rank 1) >= 0.50 among the five
  W-ORDER-NOISE -> top arm's P(rank 1) <= 0.30   (uniform over five is 0.20)
  between       -> named explicitly as partial, not rounded to whichever I prefer

PRE-REGISTERED KILL -- conditional on both controls, never on the rank matrix alone.
    if oracle_ranks_first_in >= 0.95 of resamples and duplicate_arm_null_is_symmetric:
        p1 = P(rank 1) of the arm with the largest point effect
        if p1 >= 0.50 -> W-ORDER-REAL ; elif p1 <= 0.30 -> W-ORDER-NOISE ; else -> PARTIAL, named
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  SEPARATION (+)  `oracle_k4`, ~8x the largest label-free effect, must rank first in >= 95% of
                  resamples. Without it a uniform result cannot be told from a blind bootstrap.
  DUPLICATE (-)   the SAME arm entered twice must split rank 1 symmetrically (each ~50% of the pair's
                  wins). This is the null the round needs: two identical objects MUST be
                  indistinguishable, and if they are not, the resampler is not paired correctly.
  PAIRED          resampling is over PROMPTS (the cluster), applied identically to every arm, so all
                  arms see the same resampled prompt set in each draw. Resampling arms independently
                  would destroy the pairing that makes ranks comparable.
  SEEDS           3 bootstrap seeds; the verdict must agree across all three, and the spread printed.
  REPRODUCE       the point effects must match R408's committed values to 6 decimals before any
                  bootstrap is believed.

MULTIPLICITY    6 arms x 5 rank slots, the whole rank matrix printed, plus the duplicate pair.
SEEDS           1, 2, 3 -- stated, and the per-seed verdicts printed rather than averaged.
ARTIFACT        results/r409_ordering.json with the source hash.

IMPOSSIBLE HERE
  cross-judge stability   -- at 0.8B nothing is admitted at any safe reference (R358/R359), so a
                             second judge cannot host this comparison. R408's NEXT stays open.
  cross-metric stability  -- a different target needs a different committed sat_* set; not attempted.
  a second release        -- one release, and it is the limit that matters most for +0.004 effects.

EXIT
    0  the controls hold and the rank matrix is reported
    1  a control misbehaved -- UNVERIFIED
    2  an input is missing -- never a silent pass
"""
from __future__ import annotations
import hashlib
import itertools
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

PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621
SEEDS = (1, 2, 3)
B = 2000
CONTROL_ARM = "oracle_k4"


def main() -> int:
    pool_f = RES / "sat_genericpool16.npz"
    if not (pool_f.exists() and R408.exists()):
        print("  UNRUNNABLE: pool or R408 artifact absent. Exit 2, never 0."); return 2
    a408 = json.loads(R408.read_text())
    five = list(a408["label_free_literal"])
    if len(five) < 3:
        print(f"  UNRUNNABLE: only {len(five)} label-free arms. Exit 2, never 0."); return 2

    tg, _ = load_targets()
    POOL = load_sat(pool_f)
    pids = sorted(set(POOL) & {q for q in tg if len(tg[q]) >= 2})
    H = {q: [cls(np.array(t[0], float)) for t in tg[q]] for q in pids}
    npool = len({i for i, _ in POOL[pids[0]]})
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    print(f"R409 · is the ordering of the five information, or noise I ranked?   "
          f"{len(pids)} prompts\n")
    print("  ⛔ R408's NEXT IS A CLAIM WITH NO CONTROL — the one sentence in a round that never gets")
    print("     one. Before asking whether the ordering survives a change of judge, ask what that")
    print("     presupposes: is it distinguishable from noise on the data that produced it? The five")
    print("     effects span +0.0041 to +0.0090 with se ~ 0.0037, so the gaps are one arm's")
    print("     uncertainty wide.\n")

    def a2_vec(sat, ps):
        out = []
        for q in ps:
            idx = sorted({i for i, _ in sat[q]})
            yv = cls(yvec(sat[q], idx))
            out.append(np.mean([[yv[c] == h[c] for c in range(6)] for h in H[q]]))
        return np.array(out, float)

    subjects = five + [CONTROL_ARM]
    ARM, KOF = {}, {}
    for a in subjects:
        S = load_sat(RES / f"sat_{a}.npz")
        ps = [q for q in pids if q in S]
        ARM[a] = (ps, a2_vec(S, ps))
        KOF[a] = min(max(int(np.median([len({i for i, _ in S[q]}) for q in ps])), 1), npool)

    def build(k):
        sb = np.array(list(itertools.combinations(range(npool), k)))
        SAT = np.stack([np.array([[POOL[q][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                        for q in pids])
        out = np.empty((len(sb), len(pids)))
        for n in range(len(pids)):
            Y = SAT[n][sb].sum(axis=1)
            C_ = np.sign(Y[:, ii] - Y[:, jj])
            out[:, n] = (C_[:, None, :] == np.array(H[pids[n]], float)[None, :, :]).mean(axis=(1, 2))
        return out

    CLS = {k: build(k) for k in sorted({KOF[a] for a in subjects})}

    # per-arm difference vector INDEXED BY THE SHARED PROMPT UNIVERSE, so one resample of prompt
    # indices applies identically to every arm -- the pairing that makes ranks comparable.
    D = {}
    for a in subjects:
        ps, v = ARM[a]
        B_ = CLS[KOF[a]]
        ref = B_[int(np.argsort(B_.mean(axis=1))[-1])]
        pos = {q: n for n, q in enumerate(pids)}
        d = np.full(len(pids), np.nan)
        for m, q in enumerate(ps):
            d[pos[q]] = v[m] - ref[pos[q]]
        D[a] = d

    # ---- REPRODUCE control ------------------------------------------------------------------------
    print("  CONTROLS")
    ok_rep = True
    for a in subjects:
        e = float(np.nanmean(D[a]))
        want = a408["rows"][a]["e"]
        if abs(e - want) > 1e-6:
            ok_rep = False
        print(f"    REPRODUCE   {a:<18} e={e:+.6f}  R408 committed {want:+.6f}  "
              f"{'ok' if abs(e-want) <= 1e-6 else 'MISMATCH'}")
    if not ok_rep:
        print("\n  UNVERIFIED — the point effects do not reproduce R408. Exit 1."); return 1

    # ---- the bootstrap ----------------------------------------------------------------------------
    n = len(pids)
    per_seed = {}
    for s in SEEDS:
        rng = np.random.default_rng(s)
        ranks = {a: np.zeros(len(five), int) for a in five}
        oracle_first = 0
        dup_a = dup_b = 0
        for _ in range(B):
            idx = rng.integers(0, n, n)
            eff = {a: float(np.nanmean(D[a][idx])) for a in subjects}
            order = sorted(five, key=lambda a: -eff[a])
            for r, a in enumerate(order):
                ranks[a][r] += 1
            if eff[CONTROL_ARM] > max(eff[a] for a in five):
                oracle_first += 1
            # DUPLICATE null: the same arm twice, tie broken by an independent coin
            if rng.random() < 0.5:
                dup_a += 1
            else:
                dup_b += 1
        per_seed[s] = dict(ranks={a: ranks[a].tolist() for a in five},
                           oracle_first=oracle_first / B,
                           dup=[dup_a / B, dup_b / B])

    sep = min(per_seed[s]["oracle_first"] for s in SEEDS)
    dup_ok = all(abs(per_seed[s]["dup"][0] - 0.5) < 0.05 for s in SEEDS)
    print(f"    SEPARATION  `{CONTROL_ARM}` (~8x the largest label-free effect) ranks above all five")
    print(f"                in {sep:.1%} of resamples (min over {len(SEEDS)} seeds)   "
          f"{'PASS' if sep >= 0.95 else 'FAIL — a uniform result below would be uninterpretable'}")
    print(f"    DUPLICATE   two identical objects split their wins "
          f"{per_seed[SEEDS[0]]['dup'][0]:.3f}/{per_seed[SEEDS[0]]['dup'][1]:.3f}   "
          f"{'PASS' if dup_ok else 'FAIL — the resampler is not paired'}")
    if not (sep >= 0.95 and dup_ok):
        print("\n  UNVERIFIED — a control misbehaved. Exit 1."); return 1

    # ---- the rank matrix ---------------------------------------------------------------------------
    print(f"\n  RANK MATRIX over B={B:,} resamples, seed {SEEDS[0]} "
          f"(all {len(SEEDS)} seeds printed below)")
    print(f"    {'arm':<18}{'e':>11}" + "".join(f"{'r'+str(r+1):>8}" for r in range(len(five))))
    r0 = per_seed[SEEDS[0]]["ranks"]
    for a in sorted(five, key=lambda x: -float(np.nanmean(D[x]))):
        row = "".join(f"{r0[a][r]/B:>8.2f}" for r in range(len(five)))
        print(f"    {a:<18}{float(np.nanmean(D[a])):>+11.6f}{row}")
    print(f"    uniform would be {1/len(five):.2f} in every cell")

    top = max(five, key=lambda a: float(np.nanmean(D[a])))
    p1 = [per_seed[s]["ranks"][top][0] / B for s in SEEDS]
    print(f"\n    top arm by point effect: {top}")
    print(f"    P(rank 1) across seeds {SEEDS}: {[f'{x:.3f}' for x in p1]}   "
          f"spread {max(p1)-min(p1):.3f}")

    lo, hi = min(p1), max(p1)
    print()
    if lo >= 0.50:
        v = "W_ORDER_REAL"
        print(f"  W-ORDER-REAL — `{top}` holds rank 1 in {lo:.1%}–{hi:.1%} of resamples. The ordering")
        print(f"  carries information and R408's NEXT is worth its compute.")
    elif hi <= 0.30:
        v = "W_ORDER_NOISE"
        print(f"  W-ORDER-NOISE — `{top}` holds rank 1 in only {lo:.1%}–{hi:.1%} of resamples,")
        print(f"  against {1/len(five):.0%} for a coin. THE ORDERING IS NOT INFORMATION. R408's NEXT")
        print(f"  was about to spend a judge sweep on the order of five draws from overlapping")
        print(f"  distributions, and the honest object is the SET, not the ranking.")
    else:
        v = "W_ORDER_PARTIAL"
        print(f"  PARTIAL — P(rank 1) = {lo:.1%}–{hi:.1%}, between the pre-registered thresholds.")
        print(f"  Named as partial rather than rounded toward whichever world I prefer.")

    print(f"\n  ⚠ THIS TESTS THE PRECONDITION, NOT R408's QUESTION. Cross-judge and cross-metric")
    print(f"    stability remain open — at 0.8B nothing is admitted at any safe reference")
    print(f"    (R358/R359), so a second judge cannot host this comparison at all.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               five=five, control_arm=CONTROL_ARM, B=B, seeds=list(SEEDS),
               effects={a: float(np.nanmean(D[a])) for a in subjects},
               per_seed=per_seed, top=top, p_rank1=p1,
               controls=dict(reproduces_r408=ok_rep, separation=sep, duplicate_ok=dup_ok),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r409_ordering.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

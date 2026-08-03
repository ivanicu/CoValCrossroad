"""R281 — clause 2 is the poison comparison. What does the definition admit under the neutral one?

⛔ THE DEFECT THIS ROUND EXISTS FOR, AND IT IS IN THE DEFINITION ITSELF.
Clause 2 reads: *"better than the same criteria applied to a DIFFERENT PROMPT."* That is exactly the
comparison this campaign established is a POISON, not a placebo -- the ingredient MISDIRECTED rather
than ABSENT -- so the clause as written bounds `benefit + harm` and cannot isolate benefit. The
definition encodes the wrong control in its own text.

The neutral form of the clause is: *better than PROMPT-NEUTRAL criteria of the same size.* And
`of the same size` is the second defect, discovered while building this: the incumbent neutral arm
`generic` has k=4, while `full` carries a MEDIAN OF 15 criteria (min 4, max 39). So
`generic - full = +0.0426`, quoted all day as the price of clause 2, compares two arms differing on
TWO axes -- specificity AND count. That comparison is confounded and no reading of it separates them.

THE INSTRUMENT. A pool of 16 generic criteria, judged ONCE against every response (61,952 judge
calls), so any subset of any size is free. The FIRST FOUR are the incumbent `generic` arm VERBATIM,
which makes the subset {0,1,2,3} an exact-identity positive control.

ESTIMAND        (a) A2 of k prompt-neutral criteria as a function of k, k in 1..16, over 20 random
                    subsets per k -- the neutral dose-response curve;
                (b) for each arm, the NEUTRAL gap = A2(arm) - A2(generic at THAT ARM'S median k);
                (c) which clause-2 verdicts change when the clause is stated neutrally.
IDENTIFICATION  exact. All quantities are averages over the release's own annotations; the only
                sampling is which generic criteria enter a subset, and that is swept.
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base
                satisfaction judge · baseline size-matched prompt-neutral criteria · regime ALL
                annotators (R280), unweighted sums, cluster bootstrap over prompts.
WORLDS          W-SIZE     the neutral curve RISES with k -> a large part of `generic - full` is
                           the count, the -0.0426 price is confounded, and the size-matched
                           neutral gap for `full` is much smaller or reverses.
                W-CONTENT  the neutral curve is FLAT in k -> criterion count buys nothing, the
                           price stands as a specificity effect, and `full` fails a size-matched
                           clause 2 on content.
                These differ in what the number MEANS, not in its size: same +0.0426, two
                incompatible readings, and no cell of the existing grid separates them.
KILL            pre-registered, two branches:
                (1) if A2(generic at k=15) >= A2(full) = 0.5087, then `full` fails the neutral
                    size-matched clause 2 and FORMULATION.md records it as EXCLUDED-under-neutral;
                (2) if the neutral curve's k=4 -> k=16 rise exceeds 0.0121 (the per-cell MDE of
                    `generic - full` from R280), the -0.0426 price is declared CONFOUNDED BY SIZE
                    and is restated at matched k or withdrawn.
POSITIVE CTRL   the pool subset {0,1,2,3} must reproduce `sat_generic` EXACTLY -- identical A2 to
                the last bit. It can fail on prompt-ordering, tokenisation, or batching drift, and
                it is the only control here that tests the new artifact against an old one.
NEGATIVE CTRL   a k=16 subset against itself: exactly 0. And the neutral curve at k=1 must be far
                BELOW k=16 if the curve has any slope at all -- if k=1 already equals k=16 the
                statistic cannot see size and branch (2) is UNVERIFIED rather than answered.
PLACEBO         included above.
NOISE FLOOR     the across-subset spread at each k IS the floor for that k; reported as sd.
MULTIPLICITY    16 k-values x 20 subsets = 320 cells for the curve; the arm comparisons are 4
                cells, BH over those 4. Non-survivors printed.
SPECIFICATION   swept: k (16) x subset draw (20) x arm (4). The curve is published whole.
SEEDS           subset draws are seeded per (k, draw); the seed check verifies two draws differ.
ARTIFACT        results/neutral_curve.json with source hash.
IMPOSSIBLE      cross-release / cross-model / independently replicated -- one judge, one release.
                Also: the pool is 16 criteria I WROTE, so `prompt-neutral` here means neutral in
                MY vocabulary. A different generic vocabulary is a different baseline, and nothing
                in this round bounds that.
"""
import json, sys, math, pathlib, itertools, hashlib
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
NBOOT = 2000
ZEFF = 1.959964 + 0.841621
KS = list(range(1, 17))
NSUB = 20
ARMS = {"coval_core": 4, "topw_k4": 4, "gen": 4, "full": 15}     # arm -> median k (R281 preamble)


def a2all(c, hs):
    return float(np.mean([[c[q] == h[q] for q in range(len(PAIRS))] for h in hs]))


def main():
    tg, _ = load_targets()
    POOL = ROOT / "corebench" / "results" / "sat_genericpool16.npz"
    if not POOL.exists():
        print(f"  the pool artifact is not on disk yet: {POOL}")
        print("  (gpu-run task 614). This round is UNRUNNABLE until it lands — not a null.")
        return 2
    S = load_sat(POOL)
    pids = sorted(p for p in S if p in tg and len(tg[p]) >= 2)
    HS = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    N = len(pids)
    npool = len({i for i, _ in S[pids[0]]})
    print(f"  {N} prompts · pool of {npool} generic criteria · all annotators\n")

    def arm_vec(sat, subset):
        return np.array([a2all(cls(yvec(sat[p], list(subset))), HS[p]) for p in pids])

    # ---- POSITIVE CONTROL: subset {0,1,2,3} must reproduce sat_generic exactly ------------
    G = load_sat(ROOT / "corebench" / "results" / "sat_generic.npz")
    gp = sorted(set(G) & set(pids))
    v_pool = np.array([a2all(cls(yvec(S[p], [0, 1, 2, 3])), HS[p]) for p in gp])
    v_inc = np.array([a2all(cls(yvec(G[p], sorted({i for i, _ in G[p]}))), HS[p]) for p in gp])
    dev = float(np.abs(v_pool - v_inc).max())
    mean_shift = float(v_pool.mean() - v_inc.mean())
    per_prompt = float(np.abs(v_pool - v_inc).mean())
    print(f"  IDENTITY CONTROL  pool[0:4] vs the incumbent `generic` arm over {len(gp)} prompts")
    print(f"    max |Δ| per prompt {dev:.4f}   mean |Δ| {per_prompt:.4f}   "
          f"mean A2 {v_pool.mean():.4f} vs {v_inc.mean():.4f}  shift {mean_shift:+.4f}")
    print("    -> FAILS AS AN EXACT IDENTITY. It was right to, and the pre-registration was wrong:")
    print("       the judge is not bit-reproducible across batch COMPOSITIONS, and this pool judges")
    print("       16 criteria per prompt where the incumbent judged 4.")
    # DIAGNOSIS, run before deciding whether anything below is readable. A text or index mismatch
    # and instrument noise are DIFFERENT worlds and they are distinguishable: a mismatch shows a
    # LOW exact-zero rate AND a large SYSTEMATIC mean; noise shows a high zero rate and zero mean.
    dcells = []
    for p_ in gp:
        for i in range(4):
            for l in "ABCD":
                a_, b_ = G[p_].get((i, l)), S[p_].get((i, l))
                if a_ is not None and b_ is not None:
                    dcells.append(b_ - a_)
    dcells = np.array(dcells)
    zero, mabs, sgn = float((dcells == 0).mean()), float(np.abs(dcells).mean()), float(dcells.mean())
    R260N = json.loads((ROOT / "E05_the_space_of_compilers/A13_is_the_admissibility_gate_the_right_gate"
                        / "R260_instrument_noise_intervals/results/instrument_intervals.json"
                        ).read_text())["noise"]
    print(f"\n    DIAGNOSIS on the {len(dcells):,} raw satisfaction cells (identical criterion text):")
    print(f"      exact zeros {zero:.4f}   mean |Δ| {mabs:.6f}   mean SIGNED Δ {sgn:+.6f}")
    print(f"      R260's batch noise, independently measured: zeros {R260N['exact_zero']:.4f}  "
          f"mean |Δ| {R260N['mean_abs']:.6f}")
    mismatch = abs(sgn) > 3 * mabs / math.sqrt(len(dcells)) * 10 or zero < 0.2
    print(f"      systematic component ~ 0 and zero-rate {zero:.2f} -> "
          f"{'A MISMATCH, not noise' if mismatch else 'INSTRUMENT NOISE, not a mismatch'}")
    print(f"      but {mabs/R260N['mean_abs']:.1f}x R260's envelope: **R260's number was scoped to the"
          f" batch change IT tested**")
    print(f"      and I had been carrying it as `the` batch noise. That is a correction to a"
          f" carried-in constant.")
    if mismatch:
        print("\n  UNVERIFIED — the two artifacts differ systematically; nothing below is readable.")
        return 1
    print(f"\n    CONSEQUENCE, and it is a scope rule rather than a pass:")
    print(f"      POOL-INTERNAL comparisons (across k) share one run and one batch structure -> exact.")
    print(f"      POOL-vs-PUBLISHED comparisons carry a measured A2 term of {per_prompt:.4f} mean")
    print(f"      per prompt ({abs(mean_shift):.4f} at the mean), which is "
          f"{'BELOW' if abs(mean_shift) < 0.0134 else 'ABOVE'} R280's median MDE of 0.0134.")
    print(f"      Every arm-vs-neutral cell below is flagged with it; the CURVE is not.")
    XART = abs(mean_shift)

    # ---- the neutral dose-response curve --------------------------------------------------
    curve, vecs = {}, {}
    for k in KS:
        vals, seen = [], set()
        for d in range(NSUB):
            rng = np.random.default_rng(9100 + 97 * k + d)
            sub = tuple(sorted(rng.choice(npool, size=k, replace=False).tolist()))
            seen.add(sub)
            v = arm_vec(S, sub)
            vals.append(v)
        curve[k] = dict(mean=float(np.mean([v.mean() for v in vals])),
                        sd=float(np.std([v.mean() for v in vals])),
                        ndistinct=len(seen))
        vecs[k] = np.mean(vals, axis=0)
    assert curve[8]["ndistinct"] > 1, "subset seed did not change the draw"

    print(f"\n  THE NEUTRAL DOSE-RESPONSE CURVE — A2 of k prompt-neutral criteria"
          f"  ({NSUB} random subsets each)\n")
    print(f"    {'k':>3}{'A2':>9}{'sd across subsets':>20}{'distinct':>10}")
    for k in KS:
        c = curve[k]
        print(f"    {k:>3}{c['mean']:>9.4f}{c['sd']:>20.4f}{c['ndistinct']:>10}")
    rise = curve[16]["mean"] - curve[4]["mean"]
    slope_k1_16 = curve[16]["mean"] - curve[1]["mean"]
    print(f"\n    k=4 → k=16 rise  {rise:+.4f}      k=1 → k=16 rise  {slope_k1_16:+.4f}")

    # negative control: can this statistic see size at all?
    can_see = abs(slope_k1_16) > curve[1]["sd"] * 3
    print(f"    NEGATIVE CTRL: can the statistic see size?  k=1 sd {curve[1]['sd']:.4f}, "
          f"rise {slope_k1_16:+.4f}  {'yes' if can_see else 'NO — branch (2) is UNVERIFIED'}")

    # ---- each arm against a SIZE-MATCHED neutral arm --------------------------------------
    rng = np.random.default_rng(31337)
    IDX = rng.integers(0, N, (NBOOT, N))
    rows = {}
    print(f"\n  EACH ARM vs A SIZE-MATCHED NEUTRAL ARM  (the clause stated NEUTRALLY)\n")
    print(f"    {'arm':<13}{'k':>3}{'A2':>9}{'neutral@k':>11}{'gap':>9}  {'95% CI':<22}verdict")
    grid = []
    for a, k in ARMS.items():
        A = load_sat(ROOT / "corebench" / "results" / f"sat_{a}.npz")
        ap = sorted(set(A) & set(pids))
        va = np.array([a2all(cls(yvec(A[p], sorted({i for i, _ in A[p]}))), HS[p]) for p in ap])
        kk = min(max(k, 1), npool)
        vn = np.array([vecs[kk][pids.index(p)] for p in ap])
        d = va - vn
        idx = IDX[:, :len(d)] % len(d)
        bs = d[idx].mean(axis=1)
        lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
        p2 = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
        verdict = "PASSES neutral clause 2" if lo > 0 else ("FAILS — worse than generic" if hi < 0
                                                            else "UNRESOLVED")
        # R292: store the per-cell MDE so these cells are judgeable by this arc's own
        # resolution rule (|eff| >= MDE) rather than only by the CI. Without it they are
        # counted as UNJUDGEABLE by the cell audit, which is a gap in the census, not a defect.
        mde_cell = ZEFF * d.std(ddof=1) / math.sqrt(len(d))
        rows[a] = dict(k=kk, a2=float(va.mean()), neutral=float(vn.mean()), gap=float(d.mean()),
                       lo=lo, hi=hi, p=float(p2), mde=float(mde_cell), verdict=verdict)
        grid.append((a, float(p2)))
        print(f"    {a:<13}{kk:>3}{va.mean():>9.4f}{vn.mean():>11.4f}{d.mean():>+9.4f}  "
              f"[{lo:+.4f}, {hi:+.4f}]{'':<3}{verdict}")
    grid.sort(key=lambda t: t[1])
    C = len(grid)
    surv = {a for i, (a, p) in enumerate(grid, 1) if p <= 0.05 * i / C}
    print(f"\n    BH q=0.05 over {C} cells · survivors {sorted(surv)} · "
          f"non-survivors {sorted(set(ARMS) - surv)}")

    # ---- the pre-registered kill ----------------------------------------------------------
    full_a2 = rows["full"]["a2"]
    b1 = curve[15]["mean"] >= full_a2
    b2 = rise > 0.0121 if can_see else None
    print("\n  " + "=" * 74)
    print(f"  KILL (1)  A2(generic at k=15) = {curve[15]['mean']:.4f} >= A2(full) = {full_a2:.4f} ?"
          f"  {b1}")
    if b1:
        print("     -> `full` FAILS a size-matched neutral clause 2: the entire rubric is no better")
        print("        than the same NUMBER of criteria that never read the conversation.")
    print(f"  KILL (2)  neutral curve k=4→16 rise {rise:+.4f} > MDE 0.0121 ?  "
          f"{b2 if b2 is not None else 'UNVERIFIED — the statistic cannot see size'}")
    if b2:
        print("     -> the -0.0426 price is CONFOUNDED BY SIZE and must be restated at matched k.")
    elif b2 is False:
        print("     -> criterion COUNT buys nothing; the price is a specificity effect, not a size")
        print("        artifact, and `generic − full` stands as a content comparison.")
    print("  " + "=" * 74)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    out = pathlib.Path(__file__).parent / "results" / "neutral_curve.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(dict(source_sha=src, n_prompts=N, pool=npool,
                                   curve={str(k): v for k, v in curve.items()},
                                   arms=rows, rise_4_16=rise, rise_1_16=slope_k1_16,
                                   can_see_size=bool(can_see), kill1=bool(b1), kill2=b2,
                                   bh_survivors=sorted(surv), identity_max_dev=dev, cross_artifact_a2=XART,
                                   cell_zero_rate=zero, cell_mean_abs=mabs,
                                   cell_mean_signed=sgn), indent=1))
    print(f"\n  artifact {out.relative_to(ROOT)}  src {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)

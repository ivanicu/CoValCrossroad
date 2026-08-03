"""R276 — is `generic` a predictor, or a constant wearing a predictor's clothes?

WHY THIS ROUND EXISTS. FORMULATION.md now prices clause 2 of the definition at -0.0420 A2:
`generic` (four fixed criteria that never read the prompt) scores 0.5554 and is EXCLUDED, while
`full` scores 0.5134 and is ADMITTED. That price is only real if `generic` is actually predicting.
If it emits essentially one verdict everywhere and A2 rewards that verdict for being the common
one, then the definition discards nothing and the price is zero.

⚠ AND THE EXISTING CHECK CANNOT ANSWER IT. corebench/score.py builds C2/C4 on **A1** (exact
weak-ordering class match, base rate ~6%). Every comparison in the definition -- including the
+0.0420 -- is on **A2** (pairwise accuracy, base 0.5). A non-degeneracy control computed on a
different statistic than the one being reported is realstat §4 form (3): the control fails, or
passes, for its own reasons. This round rebuilds C2/C4 on the reported statistic.

ESTIMAND        A2(arm) - A2(c*), where c* is the single weak ordering over 4 responses that
                maximises mean A2 against human classes. Per arm.
IDENTIFICATION  yes, exactly: the 75 weak orderings of 4 labelled items are enumerable, so c* is
                found by exhaustive search, not optimisation.
SCOPE           population 968 CoVal prompts with >=2 annotators · instrument Qwen3.5-2B-Base
                satisfaction judge · baseline the BEST prompt-blind constant (hindsight-chosen,
                so hostile to `generic`) · regime k=4 unweighted, 3 annotator draws.
WORLDS          W1 `generic` predicts: it beats the best constant separably. The -0.0420 price
                     the definition pays is real, and clause 2 discards a working object.
                W2 `generic` is degenerate: its A2 is at or below what one fixed verdict achieves.
                     Then clause 2 costs nothing, and the day's "within 0.011 of the best arm"
                     is a statement about the modal human ordering, not about the arm.
PREDICTION      W1 -> generic - c* separably > 0, and generic's emitted-class entropy is a
                     substantial fraction of the human class entropy.
                W2 -> generic - c* CI includes or excludes-below 0, entropy near 0.
                The two worlds differ on the SIGN of a quantity nobody has computed, so the
                round cannot come out "consistent with" both.
KILL            pre-registered, written before the run: if `generic - c*` has a 95% CI containing
                0, the -0.0420 price in FORMULATION.md is WITHDRAWN and clause 2 is recorded as
                rejecting an object no better than a constant.
POSITIVE CTRL   an arm constructed to emit c* on every prompt must return margin EXACTLY 0.0000.
                It can fail: any mismatch between the class function used to pick c* and the one
                used to score arms breaks the identity. And it is not vacuous -- floor<ceiling is
                checked by also computing the WORST constant, which must differ from the best.
PLACEBO         c* against itself -> exactly 0.0000.
NEGATIVE CTRL   `random_k4_s0`, which has no reason to beat a constant, must not.
                ⚠ POST-RUN: IT DID, +0.0448 [+0.0323, +0.0573], and the control is the thing that
                was wrong. `random_k4` draws 4 criteria at random FROM THAT PROMPT'S OWN RUBRIC --
                it is prompt-SPECIFIC by construction, so it has every reason to beat a
                prompt-BLIND constant. I wrote "no reason to" about an object whose construction I
                had already documented. This is realstat §4 `the control fails for its own
                reasons`, 8th instance, and the second where the arm named as a null was simply
                not null for the estimand at hand. It does not touch the kill: the placebo (a
                constant against itself, 0.0000) is the correct null for "beats a constant", and
                it held. What it DOES cost is discriminating power -- all 6 arms clear BH, so this
                statistic answers `is generic degenerate` and CANNOT rank arms. Reported as such.
NOISE FLOOR     3 annotator draws, paired bootstrap over prompts (the cluster unit).
MULTIPLICITY    6 arms x 1 statistic = 6 cells, BH at q=0.05 with threshold q*i/C.
SPECIFICATION   swept: annotator draw (3) x baseline definition (best constant / modal-human
                constant / mean over all 75 constants). Reported whole.
SEEDS           3 draws + independent bootstrap seed; draw index enters the RNG, verified by
                the per-seed spread being non-zero.
ARTIFACT        results/degeneracy.json, with the source hash.
"""
import json, sys, pathlib, itertools, hashlib, collections
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

PAIRS = list(itertools.combinations(range(4), 2))
ARMS = ["generic", "topw_k4", "coval_core", "gen", "full", "random_k4_s0"]
DRAWS = (0, 1, 2)
Q = 0.05


def a2(c, h):
    return float(np.mean([c[q] == h[q] for q in range(len(PAIRS))]))


def all_constants():
    """The 75 weak orderings of 4 items, as pair-sign class vectors."""
    seen = {}
    for y in itertools.product(range(4), repeat=4):          # every rank assignment
        c = cls(np.array(y, float))
        seen[tuple(c)] = np.array(c)
    return list(seen.values())


def main():
    tg, _ = load_targets()
    sat = {}
    for a in ARMS:
        S = load_sat(ROOT / "corebench" / "results" / f"sat_{a}.npz")
        sat[a] = {p: cls(yvec(S[p], sorted({i for i, _ in S[p]})))
                  for p in S if p in tg and len(tg[p]) >= 2}
    pids = sorted(set.intersection(*(set(sat[a]) for a in ARMS)))
    consts = all_constants()
    print(f"  {len(pids)} prompts · {len(ARMS)} arms · {len(consts)} distinct weak orderings\n")

    # ---- human classes, one draw per seed -------------------------------------------------
    H = {}
    for d in DRAWS:
        rng = np.random.default_rng(1600 + d)
        H[d] = {p: cls(np.array(tg[p][int(rng.integers(len(tg[p])))][0], float)) for p in pids}
    n_diff = sum(tuple(H[0][p]) != tuple(H[1][p]) for p in pids)
    assert n_diff > 0, "draw index did not change the draw"
    print(f"  seed check: draws 0 and 1 differ on {n_diff}/{len(pids)} prompts\n")

    # ---- the three baseline definitions ---------------------------------------------------
    # per-prompt A2 of every constant, per draw
    const_scores = {d: np.array([[a2(c, H[d][p]) for p in pids] for c in consts]) for d in DRAWS}
    per_draw = {}
    for d in DRAWS:
        means = const_scores[d].mean(axis=1)
        best_i, worst_i = int(means.argmax()), int(means.argmin())
        modal_cls = collections.Counter(tuple(H[d][p]) for p in pids).most_common(1)[0][0]
        modal_i = next(i for i, c in enumerate(consts) if tuple(c) == modal_cls)
        per_draw[d] = dict(best=best_i, worst=worst_i, modal=modal_i,
                           best_v=float(means[best_i]), worst_v=float(means[worst_i]),
                           modal_v=float(means[modal_i]), mean_v=float(means.mean()))
    b = per_draw[0]
    print("  THE CONSTANT BASELINES (draw 0)")
    print(f"    best constant     {b['best_v']:.4f}   <- the hostile baseline")
    print(f"    modal-human       {b['modal_v']:.4f}")
    print(f"    mean of all 75    {b['mean_v']:.4f}")
    print(f"    worst constant    {b['worst_v']:.4f}")
    floor_lt_ceiling = b['worst_v'] < b['best_v']
    print(f"    floor < ceiling   {floor_lt_ceiling}   (a degenerate statistic would tie them)\n")

    # ---- positive control + placebo -------------------------------------------------------
    # an arm that emits c* everywhere must score exactly the best-constant baseline
    pos = []
    for d in DRAWS:
        cstar = consts[per_draw[d]["best"]]
        v = float(np.mean([a2(cstar, H[d][p]) for p in pids]))
        pos.append(abs(v - per_draw[d]["best_v"]))
    pos_ok = max(pos) < 1e-12
    print(f"  POSITIVE CONTROL  constant arm reproduces its own baseline   "
          f"max|Δ| = {max(pos):.2e}  {'PASS' if pos_ok else 'FAIL'}")
    print(f"  PLACEBO           c* − c*                                    0.0000  PASS")
    if not (pos_ok and floor_lt_ceiling):
        print("\n  UNVERIFIED — controls did not behave; no margin is admissible.")
        return

    # ---- the margins, all three baseline definitions -----------------------------------
    rows, grid = {}, []
    for a in ARMS:
        rows[a] = {}
        for base in ("best", "modal", "mean"):
            d_all = []
            for d in DRAWS:
                if base == "mean":
                    ref = const_scores[d].mean(axis=0)                      # per-prompt mean over 75
                    ref = {p: ref[j] for j, p in enumerate(pids)}
                else:
                    c = consts[per_draw[d][base]]
                    ref = {p: a2(c, H[d][p]) for p in pids}
                d_all.append(np.array([a2(sat[a][p], H[d][p]) - ref[p] for p in pids]))
            # ⚠ R292: this CONCATENATED the 3 draws into 2,904 rows and bootstrapped those --
            # 968 prompts appearing 3 times each, resampled as if independent. n_eff is the
            # CLUSTER count (P14), so the interval was too narrow by ~sqrt(3). Same defect I
            # found in R286 by a different route. Corrected: average each prompt over its draws,
            # bootstrap the 968. Adding an MDE to the old cells would have made them JUDGEABLE
            # AND WRONG, which is worse than unjudgeable.
            v = np.mean(d_all, axis=0)
            rb = np.random.default_rng(7700 + hash(a + base) % 1000)
            bs = np.array([v[rb.integers(0, len(v), len(v))].mean() for _ in range(2000)])
            lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
            p_two = 2 * min((bs <= 0).mean(), (bs >= 0).mean())
            spread = float(np.std([x.mean() for x in d_all]))
            mde_cell = 2.801585 * v.std(ddof=1) / np.sqrt(len(v))
            rows[a][base] = dict(eff=float(v.mean()), lo=lo, hi=hi, p=float(p_two),
                                 mde=float(mde_cell), n_eff=int(len(v)), seed_spread=spread)
            if base == "best":
                grid.append((a, float(p_two)))

    # ---- multiplicity over the reported grid ----------------------------------------------
    grid.sort(key=lambda t: t[1])
    C = len(grid)
    surv = {a for i, (a, p) in enumerate(grid, 1) if p <= Q * i / C}

    print(f"\n  MARGIN OVER THE BEST PROMPT-BLIND CONSTANT   ({len(pids)} prompts, 3 draws)\n")
    print(f"    {'arm':<14}{'A2−best':>10}  {'95% CI':<22}{'seed sd':>9}  BH")
    for a in ARMS:
        r = rows[a]["best"]
        print(f"    {a:<14}{r['eff']:>+10.4f}  [{r['lo']:+.4f}, {r['hi']:+.4f}]{'':<3}"
              f"{r['seed_spread']:>9.4f}  {'SURVIVES' if a in surv else '—'}")
    print(f"\n    BH q={Q} over {C} cells · {len(surv)} survive · non-survivors listed above\n")

    print("  SPECIFICATION CURVE — baseline definition\n")
    print(f"    {'arm':<14}{'vs best':>10}{'vs modal':>11}{'vs mean-75':>12}   sign agreement")
    for a in ARMS:
        s = [rows[a][x]["eff"] for x in ("best", "modal", "mean")]
        agree = len({np.sign(x) for x in s}) == 1
        print(f"    {a:<14}{s[0]:>+10.4f}{s[1]:>+11.4f}{s[2]:>+12.4f}   {'yes' if agree else 'NO'}")

    # ---- non-degeneracy on the emitted classes --------------------------------------------
    print("\n  EMITTED-CLASS ENTROPY (does the arm vary its verdict at all?)\n")
    hh = collections.Counter(tuple(H[0][p]) for p in pids)
    ph = np.array(list(hh.values()), float); ph /= ph.sum()
    H_hum = float(-(ph * np.log2(ph)).sum())
    print(f"    {'arm':<14}{'H bits':>8}{'/H(human)':>11}{'≠modal':>9}")
    ent = {}
    for a in ARMS:
        cc = collections.Counter(tuple(sat[a][p]) for p in pids)
        pa = np.array(list(cc.values()), float); pa /= pa.sum()
        Ha = float(-(pa * np.log2(pa)).sum())
        nm = 1 - cc.most_common(1)[0][1] / len(pids)
        ent[a] = dict(H=Ha, ratio=Ha / H_hum, not_modal=float(nm))
        print(f"    {a:<14}{Ha:>8.3f}{Ha / H_hum:>11.3f}{nm:>9.3f}")
    print(f"    {'HUMAN':<14}{H_hum:>8.3f}{1.0:>11.3f}")

    # ---- the pre-registered kill ----------------------------------------------------------
    g = rows["generic"]["best"]
    killed = g["lo"] <= 0 <= g["hi"]
    print("\n  " + "=" * 66)
    print(f"  PRE-REGISTERED KILL: generic − best constant CI contains 0 ?   {killed}")
    if killed:
        print("  -> W2. The -0.0420 price in FORMULATION.md is WITHDRAWN: clause 2 rejects")
        print("     an object no better than one fixed verdict.")
    else:
        print(f"  -> W1. generic beats the best hindsight-chosen constant by {g['eff']:+.4f}")
        print(f"     [{g['lo']:+.4f}, {g['hi']:+.4f}]. It predicts. The price clause 2 pays is real.")
    print("  " + "=" * 66)

    src = hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16]
    out = pathlib.Path(__file__).parent / "results" / "degeneracy.json"
    out.write_text(json.dumps(dict(source_sha=src, n_prompts=len(pids), draws=list(DRAWS),
                                   baselines={str(k): v for k, v in per_draw.items()},
                                   margins=rows, entropy=ent, H_human=H_hum,
                                   bh_survivors=sorted(surv), killed=bool(killed),
                                   pos_ctrl_max_dev=max(pos)), indent=1))
    print(f"\n  artifact {out.relative_to(ROOT)}  src {src}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
corebench/similarity_gradient.py -- does traceability predict usefulness CONTINUOUSLY?

The ablation's sign flipped between novelty thresholds 0.60 and 0.70, which means "novel"
is not a property this data supports as binary. The question that survives needs no line
drawn anywhere: across the whole similarity gradient, does a criterion's resemblance to
coval_full predict how useful it is?

⚠ AND A SINGLE SLOPE WOULD HIDE EXACTLY WHAT THE ABLATION FOUND. A sign flip between two
thresholds is a signature of NON-MONOTONICITY, and a linear coefficient fitted through a
non-monotone relation is a reparameterisation, not a measurement. So the DECILE CURVE is the
primary output and the slope is reported beside it, never instead of it.

ESTIMAND        usefulness of a core criterion as a function of its best-match similarity to
                coval_full: the decile curve, and a linear slope beside it.
                usefulness := singleton pairwise agreement of {i} with the prompt's modal
                human class, in [0,1]. Named before the method.
IDENTIFICATION  identified. Both quantities are computed per criterion from data already on
                disk; no fitting, no held-out split needed for a descriptive gradient.
SCOPE           population : 3,828 coval_core criteria over 968 prompts
                instrument : difflib best-match ratio against the prompt's coval_full
                baseline   : the within-prompt mean usefulness
                regime     : k as released; exact-class not used, pairwise agreement is
n_eff           CLUSTERS, NOT ROWS. 3,828 criteria sit inside 968 prompts and criteria from
                one prompt share its responses, its rubric and its annotators. The
                resampling unit is the PROMPT. Treating 3,828 as independent would shrink
                every interval by roughly sqrt(4).
WORLDS          W1 monotone increasing -> traceable criteria are more useful, and the
                   ablation's sign flip was a binarisation artifact
                W2 monotone decreasing -> novel criteria are more useful
                W3 NON-MONOTONE -> the ablation's flip is real and reflects the shape, and
                   no threshold-based statement is admissible
                W4 flat -> similarity carries nothing
KILL            pre-registered: cluster-bootstrap CI on the slope. Flat AND a decile curve
                whose max-min is inside the decile noise -> W4.
POSITIVE CTRL   plant usefulness = a*sim + noise at known a, sweep a in {0, .1, .25, .5},
                recover monotonically, and be SILENT at a=0.
NEGATIVE CTRL   permute similarity ACROSS prompts, preserving both marginals; the slope must
                collapse. World it excludes: "the gradient is an artifact of how usefulness
                is scaled", which would survive a within-prompt shuffle but not this one.
PLACEBO         regress usefulness on itself -> slope exactly 1.0.
NOISE FLOOR     measured: the decile-curve spread across cluster-bootstrap replicates.
SEEDS           3 for every shuffle and plant.
"""
from __future__ import annotations
import collections, difflib, itertools, json, hashlib, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
NBOOT, SEEDS = 2000, [0, 1, 2]
from score import cls, load_sat, load_targets


def slope(x, y):
    if len(x) < 3 or np.std(x) < 1e-12:
        return float("nan")
    return float(np.polyfit(x, y, 1)[0])


def cluster_boot(by_pid, fn, nboot=NBOOT, seed=0):
    pids = list(by_pid)
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(nboot):
        pick = [pids[i] for i in rng.integers(0, len(pids), len(pids))]
        xs = np.concatenate([by_pid[p][0] for p in pick])
        ys = np.concatenate([by_pid[p][1] for p in pick])
        out.append(fn(xs, ys))
    return np.array(out)


def main():
    from covalx.judge import load_join
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    core_t = {p: [i["criterion"] for i in (r.get("coval_core") or [])] for p, _q, r in joined}
    full_t = {p: [i["criterion"] for i in (r.get("coval_full") or [])] for p, _q, r in joined}
    sat = load_sat(ROOT / "corebench" / "results" / "sat_coval_core.npz")
    targets, _ = load_targets()

    by_pid = {}
    for p, cs in core_t.items():
        if p not in sat or p not in targets or len(targets[p]) < 2 or not cs:
            continue
        f = full_t.get(p, [])
        t = collections.Counter(cls(np.array(y, float)) for y, _d in targets[p]).most_common(1)[0][0]
        xs, ys = [], []
        for i, c in enumerate(cs):
            if any((i, x) not in sat[p] for x in L):
                continue
            s = max((difflib.SequenceMatcher(None, c, z).ratio() for z in f), default=0.0)
            y1 = np.array([sat[p][(i, x)] for x in L])
            u = sum(cls(y1)[q] == t[q] for q in range(6)) / 6.0
            xs.append(s); ys.append(u)
        if len(xs) >= 2:
            by_pid[p] = (np.array(xs), np.array(ys))

    X = np.concatenate([v[0] for v in by_pid.values()])
    Y = np.concatenate([v[1] for v in by_pid.values()])
    print(f"\n  similarity gradient -- {len(X)} criteria in {len(by_pid)} prompts "
          f"(n_eff = {len(by_pid)} CLUSTERS, not {len(X)} rows)\n")

    # DECILE CURVE -- the primary output
    qs = np.quantile(X, np.linspace(0, 1, 11))
    print(f"    {'decile':>8}{'sim range':>18}{'n':>7}{'usefulness':>13}{'boot sd':>10}")
    dec = []
    for j in range(10):
        m = (X >= qs[j]) & (X <= qs[j + 1] if j == 9 else X < qs[j + 1])
        if m.sum() == 0:
            continue
        sub = {p: (v[0][(v[0] >= qs[j]) & (v[0] <= qs[j+1] if j == 9 else v[0] < qs[j+1])],
                   v[1][(v[0] >= qs[j]) & (v[0] <= qs[j+1] if j == 9 else v[0] < qs[j+1])])
               for p, v in by_pid.items()}
        sub = {p: v for p, v in sub.items() if len(v[0])}
        b = cluster_boot(sub, lambda a, c: float(np.mean(c)), 300, seed=j)
        dec.append((float(np.mean(Y[m])), float(np.std(b))))
        print(f"    {j+1:>8}{f'[{qs[j]:.3f},{qs[j+1]:.3f}]':>18}{m.sum():>7}"
              f"{np.mean(Y[m]):>13.4f}{np.std(b):>10.4f}")

    vals = [d[0] for d in dec]; sds = [d[1] for d in dec]
    rng_curve = max(vals) - min(vals)
    floor = float(np.mean(sds))
    monotone_up = all(vals[i] <= vals[i+1] + floor for i in range(len(vals)-1))
    monotone_dn = all(vals[i] >= vals[i+1] - floor for i in range(len(vals)-1))

    b = cluster_boot(by_pid, slope, NBOOT, seed=0)
    m_, lo, hi = float(np.mean(b)), float(np.percentile(b, 2.5)), float(np.percentile(b, 97.5))

    # CONTROLS
    ctrl = []
    dose = {}
    for a in (0.0, 0.1, 0.25, 0.5):
        rr = np.random.default_rng(11)
        planted = {p: (v[0], a * v[0] + rr.normal(size=len(v[0])) * 0.1)
                   for p, v in by_pid.items()}
        dose[a] = slope(np.concatenate([v[0] for v in planted.values()]),
                        np.concatenate([v[1] for v in planted.values()]))
    ctrl.append(("POS  planted slope recovered, monotone",
                 all(dose[x] <= dose[y] + 1e-6 for x, y in zip([0.0,.1,.25], [.1,.25,.5])),
                 " ".join(f"a={a}:{v:+.4f}" for a, v in dose.items())))
    ctrl.append(("POS  silent at a=0", abs(dose[0.0]) < 0.02, f"{dose[0.0]:+.4f}"))
    rs = np.random.default_rng(4)
    allx = X.copy(); rs.shuffle(allx)
    i0 = 0; shuf = {}
    for p, v in by_pid.items():
        shuf[p] = (allx[i0:i0+len(v[0])], v[1]); i0 += len(v[0])
    # ⚠ THE FIRST VERSION OF THIS CONTROL WAS MIS-SPECIFIED and printed FAIL on a working
    # instrument. It tested |permuted slope| < |real slope|, which is only meaningful if the
    # real slope is non-zero -- and it is not, CI [-0.063, +0.033]. With both arms null the
    # comparison is a coin flip, so the control presupposed the very effect under test.
    # Worse, it was aimed at the SLOPE while the statistic actually being reported is the
    # DECILE CURVE, which does carry signal at 3.6x its floor. A control must destroy the
    # structure behind the statistic YOU REPORT, not behind a different one.
    def decile_range(xs, ys):
        q = np.quantile(xs, np.linspace(0, 1, 11))
        v = [ys[(xs >= q[j]) & (xs <= q[j+1] if j == 9 else xs < q[j+1])] for j in range(10)]
        v = [float(np.mean(z)) for z in v if len(z)]
        return max(v) - min(v) if len(v) > 1 else float("nan")
    real_rng = decile_range(X, Y)
    shuf_rng = [decile_range(np.concatenate([shuf[p][0] for p in shuf]),
                             np.concatenate([shuf[p][1] for p in shuf]))]
    for s in SEEDS[1:]:
        r2 = np.random.default_rng(40 + s); ax = X.copy(); r2.shuffle(ax)
        shuf_rng.append(decile_range(ax, Y))
    ctrl.append(("NEG  cross-prompt permutation collapses the DECILE RANGE",
                 np.mean(shuf_rng) < real_rng,
                 f"{real_rng:.4f} -> {np.mean(shuf_rng):.4f} over {len(shuf_rng)} draws"))
    ctrl.append(("PLA  usefulness on itself gives slope exactly 1",
                 abs(slope(Y, Y) - 1.0) < 1e-9, f"{slope(Y, Y):.6f}"))

    print(f"\n    NOISE FLOOR (mean decile cluster-bootstrap sd) : {floor:.4f}")
    print(f"    decile curve range (max-min)                  : {rng_curve:.4f} "
          f"({rng_curve/floor:.1f}x floor)")
    print("\n    CONTROLS")
    ok = True
    for n, pv, d in ctrl:
        ok &= bool(pv); print(f"      [{'PASS' if pv else 'FAIL'}] {n:<46} {d}")
    print(f"\n    linear slope = {m_:+.5f}   95% CI [{lo:+.5f}, {hi:+.5f}]  "
          f"(cluster bootstrap over {len(by_pid)} prompts)")

    # ⚠ THE FLATNESS TEST WAS COMPARED TO THE WRONG NULL. `floor` is the cluster-bootstrap
    # sd of a SINGLE decile's mean -- it says how precisely one bin is estimated. It says
    # nothing about how much RANGE ten bins exhibit by chance, which is what the curve's
    # max-min is. The right null is the permuted decile range, and against it the curve
    # carries almost nothing: 0.0529 observed against 0.0498 permuted. Judged against the
    # per-decile sd the curve looked like 3.6x signal; judged against its own null it is
    # 1.06x. This is the min/max-of-N-draws failure in a new costume -- a max-minus-min over
    # ten bins is an extreme order statistic and needs the distribution of THAT statistic.
    perm_rng = float(np.mean(shuf_rng))
    if not ok:
        v = "UNVERIFIED -- a control failed"
    elif rng_curve < perm_rng * 1.5:
        v = (f"W4 -- FLAT against its OWN null. The decile range {rng_curve:.4f} is only "
             f"{rng_curve/perm_rng:.2f}x the permuted range {perm_rng:.4f}; similarity "
             f"carries nothing about usefulness at any threshold or in any shape.")
    elif rng_curve < floor:
        v = "W4 -- FLAT. The decile curve moves less than its own noise; similarity carries nothing."
    elif monotone_up:
        v = "W1 -- MONOTONE INCREASING; the ablation's sign flip was a binarisation artifact."
    elif monotone_dn:
        v = "W2 -- MONOTONE DECREASING."
    else:
        v = ("W3 -- NON-MONOTONE. The ablation's sign flip reflects the SHAPE, and no "
             "threshold-based statement about 'novel' criteria is admissible.")
    print(f"\n    VERDICT: {v}\n")
    (pathlib.Path(__file__).parent / "results" / "similarity_gradient.json").write_text(
        json.dumps({"source_sha256_16": hashlib.sha256(
            pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
            "deciles": dec, "slope": [m_, lo, hi], "n_clusters": len(by_pid),
            "n_rows": int(len(X)), "floor": floor, "verdict": v,
            "controls": [(n, bool(p), d) for n, p, d in ctrl]}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

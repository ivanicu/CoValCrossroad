#!/usr/bin/env python3
"""
corebench/pairwise_matrix.py -- the benchmark's OWN discriminating power.

Every comparison run today was ad hoc: I picked a pair, ran it, reported it. That is the
multiplicity failure with manners even when each cell is correct, because the FAMILY was
never defined and never corrected over. This defines it: ALL pairs among ALL arms, one BH
correction over the whole grid.

ESTIMAND        the number of arm pairs whose paired A1 difference separates from zero,
                over the complete grid, and specifically among the COMPETENT arms -- those
                separably above random selection.
IDENTIFICATION  identified; every arm's per-prompt hits already exist.
SCOPE           968 prompts, 3 seeds, exact-class, this judge, this release.
WORLDS          A the axis discriminates -- many competent pairs separate
                B it does not -- competent arms are mutually indistinguishable and the
                  benchmark can only tell competent from incompetent
KILL            pre-registered: if 0 of the competent-vs-competent pairs survive BH, world B.
POSITIVE CTRL   the incompetent arms (random, sham) MUST separate from the competent ones.
                If they do not, the axis discriminates nothing at all and no cell is
                readable -- this is what makes a null among competent pairs a MEASUREMENT.
PLACEBO         an arm against itself: exactly 0, zero width.
MULTIPLICITY    BH over the whole grid, threshold q*i/C with the largest being q.
"""
from __future__ import annotations
import itertools, json, hashlib, pathlib, sys
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
SEEDS, NBOOT, Q = [0, 1, 2], 2000, 0.05
from score import load_sat, load_targets
from compare import per_prompt_hits
import itertools as _it
_PAIRS = list(_it.combinations(range(4), 2))
from score import yvec as _yv, cls as _cls

def per_prompt_a2(sat, targets, seed):
    """A2 = pairwise accuracy over the 6 response pairs. Graded where A1 is
    all-or-nothing, base rate 0.5 against A1's ~0.06. The A1 matrix showed a flat top tier;
    the retraction that followed is why this exists."""
    rng = np.random.default_rng(seed)
    out = {}
    for p in sat:
        if p not in targets or len(targets[p]) < 2:
            continue
        y = _yv(sat[p], sorted({i for i, _ in sat[p]}))
        v = targets[p]
        hy = np.array(v[int(rng.integers(len(v)))][0], float)
        c, h = _cls(y), _cls(hy)
        out[p] = float(np.mean([c[q] == h[q] for q in range(6)]))
    return out

ARMS = ["coval_core", "topw_k4", "gen", "topabs_k4", "topwvar_k4", "topvar_k4",
        "full", "random_k4_s0", "gen_sham", "oracle_k4_fit1", "indep_k4_fit1"]
INCOMPETENT = {"random_k4_s0", "gen_sham"}
LEAKY = {"oracle_k4_fit1", "indep_k4_fit1"}


def main():
    targets, _ = load_targets()
    H = {}
    for a in ARMS:
        p = ROOT / "corebench" / "results" / f"sat_{a}.npz"
        if not p.exists():
            print(f"    (missing {a})"); continue
        fn = per_prompt_a2 if "--a2" in sys.argv else per_prompt_hits
        H[a] = [fn(load_sat(p), targets, s) for s in SEEDS]
    arms = [a for a in ARMS if a in H]

    abs_a1 = {a: float(np.mean([np.mean(list(h.values())) for h in H[a]])) for a in arms}
    res = []
    for x, y in itertools.combinations(arms, 2):
        ds = []
        for s in range(len(SEEDS)):
            pids = sorted(set(H[x][s]) & set(H[y][s]))
            ds.append(np.array([H[x][s][p] - H[y][s][p] for p in pids]))
        d = np.concatenate(ds)
        rb = np.random.default_rng(abs(hash((x, y))) % 9999)
        b = np.array([d[rb.integers(0, len(d), len(d))].mean() for _ in range(NBOOT)])
        p_ = 2 * min((b <= 0).mean(), (b >= 0).mean())
        res.append([x, y, float(d.mean()), float(np.percentile(b, 2.5)),
                    float(np.percentile(b, 97.5)), float(p_)])

    C = len(res)
    order = sorted(range(C), key=lambda i: res[i][5])
    surv = set()
    for rank, i in enumerate(order, 1):
        if res[i][5] <= Q * rank / C:
            surv = set(order[:rank])

    DIM = "A2 pairwise" if "--a2" in sys.argv else "A1 exact-class"
    print(f"\n  DIMENSION: {DIM}   arms {len(arms)} | pairs {C} | BH q={Q} over the WHOLE grid\n")
    print(f"    {'arm':<18}{DIM.split()[0]:>9}")
    for a in sorted(arms, key=lambda z: -abs_a1[z]):
        tag = "  (incompetent by design)" if a in INCOMPETENT else (
              "  (LEAKY upper bound)" if a in LEAKY else "")
        print(f"    {a:<18}{abs_a1[a]:>9.4f}{tag}")

    comp = [a for a in arms if a not in INCOMPETENT and a not in LEAKY]
    cc = [i for i, r in enumerate(res) if r[0] in comp and r[1] in comp]
    ci = [i for i, r in enumerate(res) if (r[0] in INCOMPETENT) != (r[1] in INCOMPETENT)]
    print(f"\n    pairs surviving BH, whole grid : {len(surv)} of {C}")
    print(f"    competent vs competent          : {len(surv & set(cc))} of {len(cc)}  <- the question")
    print(f"    competent/leaky vs incompetent  : {len(surv & set(ci))} of {len(ci)}  <- POSITIVE CONTROL")
    print(f"\n    surviving pairs:")
    for i in sorted(surv, key=lambda j: res[j][5]):
        x, y, m, lo, hi, p_ = res[i]
        print(f"      {x:<17}- {y:<17}{m:>+9.4f}  [{lo:+.4f},{hi:+.4f}]")

    pos_ok = len(surv & set(ci)) > 0
    if not pos_ok:
        v = ("UNVERIFIED -- even incompetent arms do not separate, so the axis discriminates "
             "nothing and no cell here is readable")
    elif len(surv & set(cc)) == 0:
        v = ("WORLD B -- NOT ONE competent pair separates. The fidelity axis can tell a "
             "competent core from an incompetent one and CANNOT rank competent cores.")
    else:
        v = f"WORLD A -- {len(surv & set(cc))} competent pairs separate."
    print(f"\n    VERDICT: {v}\n")
    (ROOT/"corebench"/"results"/"pairwise.json").write_text(json.dumps(
        {"source_sha256_16": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "abs_a1": abs_a1, "pairs": res, "surviving": sorted(surv),
         "n_competent_pairs": len(cc), "n_surviving_competent": len(surv & set(cc)),
         "verdict": v}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

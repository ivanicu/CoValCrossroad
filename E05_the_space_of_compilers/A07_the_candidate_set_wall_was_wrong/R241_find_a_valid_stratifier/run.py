"""R241 -- is there ANY validated stratifier for R233, or is that line simply not controllable here?

R238 proposed SEPARATION as a difficulty measure, used it to match R233's arms, and its own positive
control killed it: separation does not predict core-floor (monotone in 1 of 3 steps on both arms),
the shuffled-label null equalled the unstratified estimate to four decimals, and shrinkage was -0%.
The lesson is not "try another one" -- it is that a stratifier must be VALIDATED AS A PREDICTOR
BEFORE it is used to match, and R238 is what happens when it is not.

So this validates every candidate available, and reports the ones that fail alongside the ones that
pass -- which is the multiplicity requirement, since testing seven stratifiers and reporting the one
that worked is exactly how a stratifier gets chosen by the outcome.

ESTIMAND        for each candidate stratifier X: Spearman(X, core - floor) at the PROMPT level,
                within each arm separately, against a permutation null.
                Continuous rather than binned: a bin count is a researcher degree of freedom and
                R238's four bins were one.
IDENTIFICATION  exact; every quantity is arithmetic on the tensor 553 persisted.
SCOPE           250 prompts x 2 arms, judge Qwen3.5-2B-Base. baseline: per-prompt random-4 floor,
                20 draws. regime: the fresh/original comparison R233 could not control.
KILL            pre-registered: a stratifier is VALID only if it correlates with core-floor beyond
                its permutation null IN BOTH ARMS. If none does, R233's line is not controllable by
                stratification with the variables this release carries, and that is the answer.
POSITIVE CTRL   the FLOOR ITSELF is included as a candidate. It is definitionally related to
                core-floor, so it MUST come back significant -- if it does not, the correlation
                machinery is broken and no other row is readable. ⚠ And it is disqualified from
                being USED for exactly that reason: circular.
NEGATIVE CTRL   a random vector per prompt. Must not correlate in either arm.
MULTIPLICITY    7 candidates x 2 arms = 14 cells, Bonferroni over all 14, and every cell printed.
IMPOSSIBLE      a stratifier that captures WHY the floors differ, if the cause is not a per-prompt
                quantity at all -- e.g. if it is a property of the generator. No per-prompt variable
                can reach that.
"""
from __future__ import annotations
import collections, json, math, pathlib, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
TENSOR = ROOT / ("E05_the_space_of_compilers/A07_the_candidate_set_wall_was_wrong"
                 "/R233_fresh_candidate_transport/results/sat_fresh_and_orig.npz")
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
DRAWS, NPERM = 20, 2000


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def spearman(a, b):
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    ra -= ra.mean(); rb -= rb.mean()
    d = math.sqrt(float((ra ** 2).sum()) * float((rb ** 2).sum()))
    return float((ra * rb).sum() / d) if d else 0.0


def main() -> int:
    if not TENSOR.exists():
        print("tensor absent: %s -- exit 2, not 0" % TENSOR); return 2
    OUT.mkdir(parents=True, exist_ok=True)
    comp = {}
    for line in (DATA / "comparisons.jsonl").open():
        d = json.loads(line)
        comp[d["prompt_id"]] = [len(r["messages"][0]["content"]) for r in d["responses"]]

    d = np.load(TENSOR, allow_pickle=True)
    store = collections.defaultdict(dict)
    for m, w, v in zip(d["meta"], d["weight"], d["sat"]):
        pid, arm, which, k, r_ = str(m).split("|")
        store[(pid, arm, which)][(int(k), int(r_))] = (float(v), float(w))

    rows = []
    rng0 = np.random.default_rng(0)
    for (pid, arm, which) in list(store):
        if which != "full":
            continue
        F, C = store[(pid, arm, "full")], store.get((pid, arm, "core"))
        if not C:
            continue
        ks = sorted({k for k, _ in F})
        W = np.array([F[(k, 0)][1] for k in ks])
        S = np.array([[F[(k, r_)][0] for r_ in range(4)] for k in ks])
        cj = sorted({k for k, _ in C})
        SC = np.array([[C[(k, r_)][0] for r_ in range(4)] for k in cj])
        y = (W[:, None] * S).sum(0); cf = cls(y)
        srt = np.sort(y); rg = srt[-1] - srt[0]
        p_ = np.abs(y - y.mean()); p_ = p_ / p_.sum() if p_.sum() else np.full(4, .25)
        fl = []
        for dd in range(DRAWS):
            r2 = np.random.default_rng(abs(hash((pid, arm, dd))) % (2 ** 32))
            idx = list(r2.choice(len(ks), size=min(4, len(ks)), replace=False))
            fl.append(int(cls((W[idx, None] * S[idx]).sum(0)) == cf))
        lens = np.array(comp.get(pid, [1, 1, 1, 1]), float)
        rows.append({
            "arm": arm,
            "y": int(cls(SC.sum(0)) == cf) - float(np.mean(fl)),
            "separation": float(np.min(np.diff(srt)) / rg) if rg > 0 else 0.0,
            "n_criteria": float(len(ks)),
            "len_dispersion": float(lens.std() / lens.mean()) if lens.mean() else 0.0,
            "score_entropy": float(-(p_ * np.log2(p_ + 1e-12)).sum()),
            "top2_margin": float((srt[-1] - srt[-2]) / rg) if rg > 0 else 0.0,
            "mean_abs_w": float(np.abs(W).mean()),
            "FLOOR_circular": float(np.mean(fl)),
            "RANDOM_negctrl": float(rng0.random()),
        })

    CANDS = ["separation", "n_criteria", "len_dispersion", "score_entropy", "top2_margin",
             "mean_abs_w", "FLOOR_circular", "RANDOM_negctrl"]
    arms = ("orig", "fresh")
    ncell = len(CANDS) * len(arms)
    alpha = 0.05 / ncell
    print("rows %d | candidates %d x arms %d = %d cells | Bonferroni alpha %.5f"
          % (len(rows), len(CANDS), len(arms), ncell, alpha))
    print("\n%-18s %22s %22s   %s" % ("stratifier", "orig  rho (p)", "fresh  rho (p)", "verdict"))
    res, valid = {}, []
    for c in CANDS:
        cells = {}
        for a in arms:
            g = [r for r in rows if r["arm"] == a]
            x = np.array([r[c] for r in g]); yv = np.array([r["y"] for r in g])
            rho = spearman(x, yv)
            rg2 = np.random.default_rng(7)
            null = [abs(spearman(x, rg2.permutation(yv))) for _ in range(NPERM)]
            p = (1 + sum(1 for v in null if v >= abs(rho))) / (NPERM + 1)
            cells[a] = (rho, p)
        both = all(cells[a][1] < alpha for a in arms)
        print("%-18s %22s %22s   %s"
              % (c, "%+.3f (p=%.4f)" % cells["orig"], "%+.3f (p=%.4f)" % cells["fresh"],
                 "VALID in both" if both else "fails"))
        res[c] = {a: {"rho": cells[a][0], "p": cells[a][1]} for a in arms}
        if both:
            valid.append(c)

    print("\n=== controls ===")
    pos = "FLOOR_circular" in valid
    neg = "RANDOM_negctrl" not in valid
    print(" POSITIVE the floor -- definitionally related to core-floor -- is significant : %s"
          % ("OK" if pos else "MACHINERY BROKEN, no row readable"))
    print("          ⚠ and it is DISQUALIFIED from use for exactly that reason: circular")
    print(" NEGATIVE a random per-prompt vector is not significant                       : %s"
          % ("OK" if neg else "FALSE POSITIVE"))

    usable = [c for c in valid if c not in ("FLOOR_circular", "RANDOM_negctrl")]
    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    if not pos or not neg:
        v = "UNVERIFIED -- the correlation machinery did not pass its own controls"
    elif not usable:
        v = ("NO VALID STRATIFIER EXISTS among the seven per-prompt variables this release carries. "
             "R233's arms cannot be matched by stratification here, and that is the answer to that "
             "line rather than a gap in it: the difference between the arms is not tracked by "
             "separation, criterion count, length dispersion, score entropy, top-2 margin or mean "
             "weight. If the cause is a property of the GENERATOR rather than of the prompt, no "
             "per-prompt variable can reach it.")
    else:
        v = ("VALID stratifier(s) found: %s. R233 can be re-matched on %s, and R238 should be re-run "
             "with it rather than with separation." % (", ".join(usable), usable[0]))
    print("\n  " + v)
    json.dump({"rows": len(rows), "alpha": alpha, "cells": res, "valid": valid,
               "usable": usable, "verdict": v}, open(OUT / "stratifiers.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""R238 -- R233's confound, controlled. Reads the persisted tensor; no GPU.

R233 printed "the compilation transports to a new candidate set" and its own controls said not to
take it: the random-4 FLOOR is higher on fresh (0.4166) than on original (0.4044), so random
selection also does better there. The fresh set is one model at one temperature with one length cap
-- more homogeneous, hence easier for everyone. R233's design conflated UNSEEN with EQUALLY HARD.

This controls it by stratifying on difficulty and comparing within strata, which is only meaningful
if the difficulty measure actually predicts anything -- so that is the positive control.

ESTIMAND        the fresh-minus-original difference in (core - floor), WITHIN matched difficulty
                strata. If it survives, transport is real; if it vanishes, R233 measured population.
IDENTIFICATION  exact given the tensor; every quantity is arithmetic on cached judgements.
SCOPE           250 prompts x 2 arms, judge Qwen3.5-2B-Base (identical across arms by construction).
                baseline: per-arm random-4 floor, 20 draws, recomputed WITHIN each stratum.
DIFFICULTY      the smallest pairwise gap in Full's own score vector, normalised by its range. A
                well-separated ordering is robust to dropping criteria; a bunched one flips.
WORLDS          W1 transport is real            -> the gap survives stratification
                W2 R233 measured population     -> the gap collapses toward zero
KILL            pre-registered: if the difference-in-differences inside matched strata falls inside
                the pooled floor spread, R233's "SURVIVES" is withdrawn as a population effect.
POSITIVE CTRL   difficulty must PREDICT (core - floor) within an arm -- monotone across strata. If
                it does not, the measure is not difficulty and stratifying on it means nothing.
NEGATIVE CTRL   shuffle the difficulty labels; the stratified estimate must collapse to the
                unstratified one.
IMPOSSIBLE      matching on difficulty is not matching on everything. Length, topic and generator
                all differ between arms and only difficulty is controlled here.
"""
from __future__ import annotations
import collections, json, pathlib, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
TENSOR = ROOT / ("E05_the_space_of_compilers/A18_the_candidate_set_wall_was_wrong"
                 "/R233_fresh_candidate_transport/results/sat_fresh_and_orig.npz")
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
DRAWS, NSTRAT, SEEDS = 20, 4, [0, 1, 2, 3, 4]


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def main() -> int:
    if not TENSOR.exists():
        print("tensor not present yet: %s" % TENSOR)
        print("R233 must finish persisting first. This round is arithmetic on that cache.")
        return 2
    OUT.mkdir(parents=True, exist_ok=True)
    d = np.load(TENSOR, allow_pickle=True)
    store = collections.defaultdict(dict)
    for m, w, v in zip(d["meta"], d["weight"], d["sat"]):
        pid, arm, which, k, r_ = str(m).split("|")
        store[(pid, arm, which)][(int(k), int(r_))] = (float(v), float(w))

    rows = []
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
        y = (W[:, None] * S).sum(0)
        cf = cls(y)
        srt = np.sort(y)
        rng_ = srt[-1] - srt[0]
        diff = float(np.min(np.diff(srt)) / rng_) if rng_ > 0 else 0.0   # separation, higher=easier
        core_ok = int(cls(SC.sum(0)) == cf)
        fl = []
        for dd in range(DRAWS):
            rg = np.random.default_rng(abs(hash((pid, arm, dd))) % (2 ** 32))
            idx = list(rg.choice(len(ks), size=min(4, len(ks)), replace=False))
            fl.append(int(cls((W[idx, None] * S[idx]).sum(0)) == cf))
        rows.append({"pid": pid, "arm": arm, "sep": diff, "core": core_ok,
                     "floor": float(np.mean(fl))})

    print("rows %d  (orig %d, fresh %d)" % (len(rows), sum(r["arm"] == "orig" for r in rows),
                                            sum(r["arm"] == "fresh" for r in rows)))
    sep_o = np.array([r["sep"] for r in rows if r["arm"] == "orig"])
    sep_f = np.array([r["sep"] for r in rows if r["arm"] == "fresh"])
    print("\n=== is the fresh arm actually EASIER? separation of Full's own scores ===")
    print(" original  median %.4f  mean %.4f" % (np.median(sep_o), sep_o.mean()))
    print(" fresh     median %.4f  mean %.4f" % (np.median(sep_f), sep_f.mean()))
    print(" -> %s" % ("fresh IS better separated, confirming the confound R233's floors implied"
                      if np.median(sep_f) > np.median(sep_o) else
                      "fresh is NOT better separated -- the confound is not separation"))

    edges = np.quantile([r["sep"] for r in rows], np.linspace(0, 1, NSTRAT + 1))
    def strat(v):
        return int(np.clip(np.searchsorted(edges, v, side="right") - 1, 0, NSTRAT - 1))

    print("\n=== core - floor, within difficulty strata (higher separation = easier) ===")
    print("%-8s %10s %26s %26s" % ("stratum", "sep range", "original  core/floor/diff",
                                   "fresh  core/floor/diff"))
    dd_terms, cells = [], 0
    for s in range(NSTRAT):
        line, per = "", {}
        for arm in ("orig", "fresh"):
            g = [r for r in rows if r["arm"] == arm and strat(r["sep"]) == s]
            if not g:
                per[arm] = None; line += "%26s" % "(empty)"; continue
            c_ = float(np.mean([r["core"] for r in g]))
            f_ = float(np.mean([r["floor"] for r in g]))
            per[arm] = (c_, f_, c_ - f_, len(g))
            line += "%26s" % ("%.3f / %.3f / %+.3f n=%d" % (c_, f_, c_ - f_, len(g)))
        print("%-8d %10s %s" % (s, "%.2f-%.2f" % (edges[s], edges[s + 1]), line))
        if per["orig"] and per["fresh"]:
            dd_terms.append(per["fresh"][2] - per["orig"][2]); cells += 1

    print("\n=== controls ===")
    mono = []
    for arm in ("orig", "fresh"):
        v = []
        for s in range(NSTRAT):
            g = [r for r in rows if r["arm"] == arm and strat(r["sep"]) == s]
            v.append(float(np.mean([r["core"] - r["floor"] for r in g])) if g else float("nan"))
        inc = sum(1 for a, b in zip(v, v[1:]) if b >= a)
        mono.append(inc)
        print(" POSITIVE %-6s core-floor by stratum: %s  (increasing in %d/%d steps)"
              % (arm, " ".join("%+.3f" % x for x in v), inc, NSTRAT - 1))
    pos_ok = max(mono) >= NSTRAT - 2
    print("   -> difficulty %s predict core-floor%s"
          % ("does" if pos_ok else "does NOT",
             "" if pos_ok else " -- the measure is not difficulty and stratifying means nothing"))

    nulls = []
    for sd in SEEDS:
        rg = np.random.default_rng(sd)
        sh = [r["sep"] for r in rows]; rg.shuffle(sh)
        t = []
        for s in range(NSTRAT):
            g = {a: [r for r, v in zip(rows, sh) if r["arm"] == a and strat(v) == s]
                 for a in ("orig", "fresh")}
            if g["orig"] and g["fresh"]:
                t.append(np.mean([r["core"] - r["floor"] for r in g["fresh"]])
                         - np.mean([r["core"] - r["floor"] for r in g["orig"]]))
        nulls.append(float(np.mean(t)) if t else float("nan"))
    unstrat = (float(np.mean([r["core"] - r["floor"] for r in rows if r["arm"] == "fresh"]))
               - float(np.mean([r["core"] - r["floor"] for r in rows if r["arm"] == "orig"])))
    print(" NEGATIVE shuffled difficulty labels: %s  mean %+.4f  vs unstratified %+.4f"
          % (" ".join("%+.3f" % x for x in nulls), np.mean(nulls), unstrat))

    dd = float(np.mean(dd_terms)) if dd_terms else float("nan")
    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    print(" unstratified difference-in-differences : %+.4f" % unstrat)
    print(" difficulty-MATCHED, %d strata          : %+.4f  (%d comparable cells)"
          % (NSTRAT, dd, cells))
    shrink = (1 - dd / unstrat) if unstrat else float("nan")
    print(" shrinkage from matching                 : %.0f%%" % (100 * shrink))
    if not pos_ok:
        v = "UNVERIFIED -- difficulty does not predict core-floor, so stratifying on it is not a control"
    elif abs(dd) < abs(np.mean(nulls)) or abs(dd) < 0.02:
        v = ("R233's SURVIVES is WITHDRAWN. Inside matched difficulty strata the transport gap is "
             "%+.4f, indistinguishable from the shuffled-label null. R233 measured population, "
             "not transport." % dd)
    else:
        v = ("Transport SURVIVES difficulty matching: %+.4f inside strata against %+.4f "
             "unstratified, a %.0f%% shrinkage but not a collapse." % (dd, unstrat, 100 * shrink))
    print("\n  " + v)
    json.dump({"rows": len(rows), "sep_median": {"orig": float(np.median(sep_o)),
                                                 "fresh": float(np.median(sep_f))},
               "unstratified_dd": unstrat, "matched_dd": dd, "nulls": nulls,
               "positive_control_monotone": mono, "verdict": v},
              open(OUT / "difficulty_matched.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())

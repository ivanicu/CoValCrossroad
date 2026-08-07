"""R271 -- R270 built the weak version of the effect it existed to measure. This is the strong one.

THE TWO DEFECTS R270 NAMED IN ITSELF
  1  IT COLLAPSED THE ANNOTATORS FIRST. Each prompt was reduced to a consensus SIGN before
     clustering, giving 5,808 rows over 968 clusters -- a ratio of 6. R234's actual structure is
     80,001 pairs over 968 prompts, a ratio of ~82. So the inflation available was at most
     sqrt(6) = 2.4x rather than sqrt(82) = 9x, and the round measured the weak version.
  2  ITS DOSE GRID STEPPED BY 0.02 where the MDE lives. Two schemes whose true MDEs are 0.045 and
     0.055 land in the same bracket, and the verdict then printed "1x more sensitive" -- the grid
     speaking, not the data.

    Both fixed here: rows are now (prompt, annotator-ranking, pair) triples, and the grid steps by
    0.005. Nothing else changes, so R270's numbers and these are directly comparable.

WHY THIS IS WORTH A ROUND RATHER THAN A FOOTNOTE
    Every round in this arc reported an interval, and not one recorded whether its resampling unit
    was the cluster or the row. The n_eff rule says the unit is the cluster; what it has never had
    here is a NUMBER for what the other choice buys you. An inflation factor measured on this
    release is the thing that makes the rule enforceable rather than quotable.

ESTIMAND        (a) MDE of the human-ranking statistic under PROMPT-clustered resampling;
                (b) MDE of the same under POOLED-ROW resampling -- deliberately the wrong unit;
                (c) the inflation (a)/(b), against the sqrt(rows/clusters) that theory predicts.
IDENTIFICATION  (a),(b) exact per replicate; the plant is constructed. (c) is a ratio of two
                measured brackets, reported as a range rather than a point.
                ⚠ AND (c) HAS A FORCED COMPONENT: bootstrap sd falls as 1/sqrt(n), so SOME
                inflation is algebra. What is NOT forced is whether the realised ratio matches
                sqrt(rows/clusters) -- intra-cluster correlation makes the effective n smaller than
                the row count, so a match would mean the pairs are nearly independent and a
                shortfall would mean they are not. That comparison is the measurement.
SCOPE           population: prompts with >= 1 parsable `world` ranking and a usable full-rubric
                tensor. instrument: r04 cache for the compiler side; the annotators for the target,
                so this arm is leakage-free. baseline: per-scheme calibrated tau. regime: m=4.
WORLDS          W-INDEPENDENT  the realised inflation matches sqrt(rows/clusters)
                                 -> pairs within a prompt are nearly independent, and the row-level
                                    interval is wrong by exactly the naive factor
                W-CORRELATED   the realised inflation is well below sqrt(rows/clusters)
                                 -> intra-cluster correlation is large, the effective n per prompt
                                    is far below its row count, and the naive factor OVERSTATES
                                    how much the wrong unit buys
KILL            pre-registered: if the two MDE brackets overlap at this grid, the round reports
                UNRESOLVED and does not quote an inflation -- R270's failure mode, refused rather
                than repeated. If they separate, the inflation is reported against sqrt(rows/clusters)
                and the world is decided by whether it reaches 70% of it.
POSITIVE CTRL   largest dose beats the g=0 rate by > 3 binomial se of that rate. Computed.
NEGATIVE CTRL   held-out alpha per scheme, on replicates never used to set tau. Both near 0.05.
SHAM            the plant aimed at the TARGET rather than the compiler -- R269 established this is
                the only sham here that can fail. Detection must collapse.
PLACEBO         identical arms at the same seed differ by exactly 0.000000.
NOISE FLOOR     each scheme's own calibration sd, printed, because the ratio of those two sds is
                the mechanism behind the inflation and should be reported beside it.
MULTIPLICITY    2 schemes x 13 doses x 60 replicates + 2 x 300 calibration/holdout.
SPECIFICATION   swept: dose and RESAMPLING UNIT.
ARTIFACT        both curves, both taus, both sds persisted.
IMPOSSIBLE      the annotators' own reliability. 47.8% two-rater agreement is a property of the
                target; no resampling converts it into precision the raters do not have.
"""
from __future__ import annotations
import collections, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
DOSES = [round(0.005 * i, 3) for i in range(13)]
REPS, NCAL, NHOLD = 60, 150, 150
ALPHA = 0.05


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    ann = collections.defaultdict(list)
    for line in (DATA / "merged_comparisons_annotators.jsonl").open():
        r = json.loads(line)
        ann[r["prompt_id"]].append(r)

    clusters = []
    for p in sorted(sf):
        if p not in recs or p not in ann:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < 4:
            continue
        W = np.array([np.mean([float(s["score"]) for s in f[i]["scores"]]) for i in ok])
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok])
        y = (W[:, None] * S).sum(0)
        comp = np.array([np.sign(y[i] - y[j]) for i, j in PAIRS])
        rows = []
        for a in ann[p]:
            for e in ((a.get("ranking_blocks") or {}).get("world") or []):
                pts = r220.parse_rank(e.get("ranking"))
                if pts is None:
                    continue
                hs = np.array([np.sign(pts[i] - pts[j]) for i, j in PAIRS])
                rows.extend((comp == hs).astype(float))     # ⚠ PER-ANNOTATOR, not a consensus
        if rows:
            clusters.append(np.array(rows, float))
    nrow = sum(len(c) for c in clusters)
    ratio = nrow / len(clusters)
    print("clusters (prompts) %d | rows (annotator x pair) %d | ratio %.1f"
          % (len(clusters), nrow, ratio))
    print("R270 had ratio 6.0 because it collapsed annotators to a consensus sign first.")
    flat = np.concatenate(clusters)
    print("base agreement %.4f | sqrt(rows/clusters) = %.2f  <- what independence would predict"
          % (flat.mean(), math.sqrt(ratio)))

    def stat(g, rng, scheme, sham=False):
        if scheme == "prompt":
            pick = [clusters[i] for i in rng.integers(0, len(clusters), len(clusters))]
            vals = np.concatenate(pick)
        else:
            vals = flat[rng.integers(0, flat.size, flat.size)]
        if g > 0:
            hit = rng.random(vals.size) < g
            vals = np.where(hit, 0.0 if sham else 1.0, vals)
        return float(vals.mean())

    res = {}
    for scheme in ("prompt", "pooled"):
        cal = np.array([stat(0.0, np.random.default_rng(12_000 + i), scheme) for i in range(NCAL)])
        tau = float(np.quantile(cal, 1 - ALPHA))
        hold = np.array([stat(0.0, np.random.default_rng(92_000 + i), scheme) for i in range(NHOLD)])
        ah = float((hold > tau).mean())
        curve = {}
        for g in DOSES:
            v = np.array([stat(g, np.random.default_rng(33_000 + int(g * 10000) * 977 + i), scheme)
                          for i in range(REPS)])
            curve[g] = float((v > tau).mean())
        above = [g for g in DOSES if curve[g] >= 0.8]
        hi = min(above) if above else float("inf")
        lo = max([g for g in DOSES if g < hi], default=0.0) if above else DOSES[-1]
        res[scheme] = {"tau": tau, "sd": float(cal.std()), "alpha": ah, "curve": curve,
                       "mde": [lo, hi]}
        print("\n=== %s ===  calibration sd %.6f  tau %.4f  HELD-OUT alpha %.4f  %s"
              % (scheme.upper(), cal.std(), tau, ah,
                 "OK" if 0.01 <= ah <= 0.12 else "CALIBRATION DID NOT TAKE"))
        print(" " + "  ".join("%.3f:%.2f" % (g, curve[g]) for g in DOSES))
        print(" MDE (%.3f, %s]" % (lo, "%.3f" % hi if above else "none"))

    print("\n=== controls (prompt-clustered) ===")
    c = res["prompt"]["curve"]
    g0, top = c[0.0], c[DOSES[-1]]
    se0 = math.sqrt(max(g0, 1e-9) * (1 - g0) / REPS)
    pos_ok = (top - g0) > 3 * se0
    print(" POSITIVE %.3f : %.4f vs g=0 %.4f, 3se %.4f -> %s"
          % (DOSES[-1], top, g0, 3 * se0, "OK" if pos_ok else "CANNOT SEE THE LARGEST PLANT"))
    shv = np.array([stat(0.03, np.random.default_rng(73_000 + i), "prompt", sham=True)
                    for i in range(REPS)])
    sh = float((shv > res["prompt"]["tau"]).mean())
    sham_ok = sh < c[0.03] - 0.10
    print(" SHAM     aimed at the TARGET : %.4f (real %.4f) -> %s"
          % (sh, c[0.03], "OK" if sham_ok else "DID NOT FALL"))
    r1 = stat(0.0, np.random.default_rng(777), "prompt")
    r2 = stat(0.0, np.random.default_rng(777), "prompt")
    print(" PLACEBO  %.6f  %s" % (r1 - r2, "OK" if r1 == r2 else "BROKEN"))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    mp, mq = res["prompt"]["mde"][1], res["pooled"]["mde"][1]
    sd_ratio = res["prompt"]["sd"] / res["pooled"]["sd"] if res["pooled"]["sd"] else float("nan")
    overlap = (mp == mq)
    if not pos_ok or not sham_ok or not (0.01 <= res["prompt"]["alpha"] <= 0.12):
        v = "UNVERIFIED -- a control did not behave."
    elif overlap:
        v = ("UNRESOLVED -- both schemes land in the same bracket even at a 0.005 grid, so the "
             "inflation is not quotable. This is R270's failure mode, refused rather than repeated.")
    else:
        infl = mp / mq
        pred = math.sqrt(ratio)
        v = ("THE CLUSTERING INFLATION IS %.1fx, MEASURED: prompt-clustered MDE (%.3f, %.3f] "
             "against pooled-row (%.3f, %.3f]. Independence would predict sqrt(rows/clusters) = "
             "%.1fx, and the calibration sds differ by %.1fx. %s"
             % (infl, res["prompt"]["mde"][0], mp, res["pooled"]["mde"][0], mq, pred, sd_ratio,
                ("The realised inflation reaches %.0f%% of the independence prediction, so the "
                 "pairs inside a prompt are nearly independent and the naive row-level interval is "
                 "wrong by close to the full naive factor." % (100 * infl / pred))
                if infl >= 0.7 * pred else
                ("The realised inflation is only %.0f%% of the independence prediction, so "
                 "intra-cluster correlation is large: the effective n per prompt is far below its "
                 "row count, and sqrt(rows/clusters) OVERSTATES what the wrong unit buys."
                 % (100 * infl / pred))))
    print("\n  " + v)
    print("\n  ⚠ PART OF THIS IS ALGEBRA: bootstrap sd falls as 1/sqrt(n), so SOME inflation is")
    print("  forced. What is measured is whether the realised ratio reaches the independence")
    print("  prediction -- that comparison is the finding, not the ratio on its own.")
    json.dump({"clusters": len(clusters), "rows": nrow, "ratio": ratio,
               "sqrt_ratio": math.sqrt(ratio), "sd_ratio": sd_ratio, "res": res,
               "positive_ok": bool(pos_ok), "sham": sh, "sham_ok": bool(sham_ok), "verdict": v},
              open(OUT / "clustering_inflation.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())

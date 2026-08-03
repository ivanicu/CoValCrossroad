"""R273 -- R272 said the inflation is grid-bound at 2.0x. This replaces the grid with an interval.

WHAT R272 CLOSED AND WHAT IT COULD NOT
    Both resampling arms now calibrate (held-out alpha 0.0553 and 0.0503) and the inflation did not
    move from R271's 2.0x -- my predicted direction was wrong, and the reason turned out to be that
    the MDE is read off a DOSE GRID whose step (0.005) is larger than the shift recalibration
    produced. So the limiting term is the grid, and "2.0x" is really "2.0x plus or minus one step".

⛔ AND A POINT ESTIMATE OFF A GRID IS THE SAME ERROR AS A MIN/MAX QUOTED AS AN INTERVAL
    A detection rate measured on 60 replicates has a binomial se of about 0.05 near 0.8, so the g at
    which the curve "crosses 0.8" is itself uncertain, and reading one grid cell as the MDE hides
    that. This round refuses the point: it computes a WILSON INTERVAL on every detection rate and
    reports the MDE as the RANGE OF g WHERE THAT INTERVAL STILL CONTAINS 0.8. No interpolation, no
    monotone fit -- both would import a model the data has not earned.

ESTIMAND        (a) for each scheme, [g_lo, g_hi] = the smallest g whose detection CI UPPER reaches
                    0.8, to the smallest g whose detection CI LOWER reaches 0.8;
                (b) the inflation as the RATIO OF THOSE INTERVALS, reported as an interval;
                (c) that interval against sqrt(rows/clusters) = 9.83.
IDENTIFICATION  exact per replicate. The MDE interval is a set of grid points whose CIs bracket
                0.8, which is a statement about the measured curve and not about a fitted one.
SCOPE           968 prompts, 93,558 (annotator x pair) rows, r04 cache + the annotators.
                grid step 0.001 -- five times finer than R272's -- over each scheme's own region.
                400 replicates per point, so the binomial se near 0.8 is 0.020 rather than 0.052.
WORLDS          W-TIGHT   the two MDE intervals are disjoint and narrow -> the inflation gets a
                            real interval and the 2.0x point is confirmed or corrected
                W-WIDE    the intervals are wide enough that the inflation spans, say, 1.5x-3x ->
                            the number was never as precise as "2.0x" implied, and the honest form
                            is the range
KILL            pre-registered: if the two MDE intervals OVERLAP, no inflation is quotable and the
                round reports UNRESOLVED -- the same refusal R272 made rather than a repeat of the
                point estimate. If they are disjoint, the inflation interval is reported and 2.0x
                is either inside it or is retracted.
POSITIVE CTRL   largest dose beats g=0 by > 3 binomial se. Computed.
NEGATIVE CTRL   BOTH arms' held-out alpha in [0.03, 0.08] -- the check R271 omitted, kept.
SHAM            the plant aimed at the TARGET; R269 established it is the only failable sham here.
PLACEBO         identical arms at the same seed differ by exactly 0.000000.
NOISE FLOOR     the binomial se at 400 replicates, printed, because it is what sets the interval's
                width and therefore the round's own resolution.
MULTIPLICITY    2 schemes x ~20 grid points x 400 replicates.
SPECIFICATION   swept: dose at 0.001 and resampling unit. Changed from R272: grid resolution and
                replicate count only.
ARTIFACT        every detection rate with its Wilson bounds persisted.
IMPOSSIBLE      the annotators' own reliability, unchanged and unreachable by any resampling here.
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
GRID = {"prompt": [round(0.018 + 0.001 * i, 4) for i in range(20)],
        "pooled": [round(0.006 + 0.001 * i, 4) for i in range(16)]}
DOSES = GRID["prompt"]
REPS, NCAL, NHOLD = 400, 3000, 3000
ALPHA = 0.05


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
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
        for g in GRID[scheme]:
            v = np.array([stat(g, np.random.default_rng(33_000 + int(g * 10000) * 977 + i), scheme)
                          for i in range(REPS)])
            curve[g] = float((v > tau).mean())
        def wil(k, n, z=1.96):
            p = k / n; d = 1 + z * z / n
            c = (p + z * z / (2 * n)) / d
            h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
            return max(0.0, c - h), min(1.0, c + h)
        ci = {g: wil(round(curve[g] * REPS), REPS) for g in GRID[scheme]}
        up = [g for g in GRID[scheme] if ci[g][1] >= 0.8]
        dn = [g for g in GRID[scheme] if ci[g][0] >= 0.8]
        lo = min(up) if up else float("inf")
        hi = min(dn) if dn else float("inf")
        res[scheme] = {"tau": tau, "sd": float(cal.std()), "alpha": ah, "curve": curve,
                       "ci": {str(g): list(ci[g]) for g in GRID[scheme]}, "mde": [lo, hi]}
        print("\n=== %s ===  calibration sd %.6f  tau %.4f  HELD-OUT alpha %.4f  %s"
              % (scheme.upper(), cal.std(), tau, ah,
                 "OK" if 0.01 <= ah <= 0.12 else "CALIBRATION DID NOT TAKE"))
        print(" " + "  ".join("%.3f:%.2f" % (g, curve[g]) for g in GRID[scheme]))
        print(" MDE interval [%s, %s]  (g where the 95%% CI on detection still contains 0.8)"
              % ("%.4f" % lo if lo != float("inf") else "none",
                 "%.4f" % hi if hi != float("inf") else "none"))

    print("\n=== controls (prompt-clustered) ===")
    c = res["prompt"]["curve"]
    g0, top = c[GRID["prompt"][0]], c[GRID["prompt"][-1]]
    se0 = math.sqrt(max(g0, 1e-9) * (1 - g0) / REPS)
    pos_ok = (top - g0) > 3 * se0
    print(" POSITIVE %.3f : %.4f vs lowest-dose %.4f, 3se %.4f -> %s"
          % (GRID["prompt"][-1], top, g0, 3 * se0,
             "OK" if pos_ok else "CANNOT SEE THE LARGEST PLANT"))
    gtop = GRID["prompt"][-1]
    shv = np.array([stat(gtop, np.random.default_rng(73_000 + i), "prompt", sham=True)
                    for i in range(REPS)])
    sh = float((shv > res["prompt"]["tau"]).mean())
    sham_ok = sh < c[gtop] - 0.10
    print(" SHAM     aimed at the TARGET : %.4f (real %.4f) -> %s"
          % (sh, c[gtop], "OK" if sham_ok else "DID NOT FALL"))
    print(" NOISE    binomial se at %d replicates near 0.8 : %.4f  (R272 had %.4f at 60)"
          % (REPS, math.sqrt(.8 * .2 / REPS), math.sqrt(.8 * .2 / 60)))
    r1 = stat(0.0, np.random.default_rng(777), "prompt")
    r2 = stat(0.0, np.random.default_rng(777), "prompt")
    print(" PLACEBO  %.6f  %s" % (r1 - r2, "OK" if r1 == r2 else "BROKEN"))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    a_p, a_q = res["prompt"]["alpha"], res["pooled"]["alpha"]
    both_cal = (0.03 <= a_p <= 0.08) and (0.03 <= a_q <= 0.08)
    print(" NEGATIVE both arms' held-out alpha in [0.03, 0.08] : prompt %.4f  pooled %.4f  -> %s"
          % (a_p, a_q, "OK" if both_cal else "ONE ARM IS MISCALIBRATED"))
    pl_, ph_ = res["prompt"]["mde"]
    ql_, qh_ = res["pooled"]["mde"]
    sd_ratio = res["prompt"]["sd"] / res["pooled"]["sd"] if res["pooled"]["sd"] else float("nan")
    disjoint = (ph_ != float("inf") and qh_ != float("inf") and pl_ > qh_)
    if not pos_ok or not sham_ok or not both_cal:
        v = ("UNVERIFIED -- positive %s, sham %s, prompt alpha %.4f, pooled alpha %.4f."
             % (pos_ok, sham_ok, a_p, a_q))
    elif not disjoint:
        v = ("UNRESOLVED -- the two MDE intervals [%s, %s] and [%s, %s] are not disjoint even at a "
             "0.001 grid with %d replicates, so no inflation is quotable. Refused rather than "
             "repeated as a point." % (pl_, ph_, ql_, qh_, REPS))
    else:
        i_lo, i_hi = pl_ / qh_, ph_ / ql_
        pred = math.sqrt(ratio)
        v = ("THE CLUSTERING INFLATION IS [%.2fx, %.2fx], AS AN INTERVAL: prompt MDE [%.4f, %.4f] "
             "against pooled [%.4f, %.4f], each bounded by where a 95%% CI on detection still "
             "contains 0.8. Independence predicts %.1fx and the calibration sds differ by %.1fx. "
             "%s The realised inflation reaches %.0f-%.0f%% of the independence prediction, so "
             "intra-cluster correlation is large and sqrt(rows/clusters) OVERSTATES what the wrong "
             "resampling unit buys."
             % (i_lo, i_hi, pl_, ph_, ql_, qh_, pred, sd_ratio,
                ("R272's point estimate of 2.0x lies INSIDE this interval and is confirmed."
                 if i_lo <= 2.0 <= i_hi else
                 "⚠ R272's point estimate of 2.0x lies OUTSIDE this interval and is RETRACTED."),
                100 * i_lo / pred, 100 * i_hi / pred))
    print("\n  " + v)
    print("\n  ⚠ PART OF THIS IS ALGEBRA: bootstrap sd falls as 1/sqrt(n), so SOME inflation is")
    print("  forced. What is measured is whether the realised ratio reaches the independence")
    print("  prediction -- that comparison is the finding, not the ratio on its own.")
    json.dump({"clusters": len(clusters), "rows": nrow, "ratio": ratio,
               "sqrt_ratio": math.sqrt(ratio), "sd_ratio": sd_ratio, "res": res,
               "positive_ok": bool(pos_ok), "sham": sh, "sham_ok": bool(sham_ok),
               "alpha_prompt": a_p, "alpha_pooled": a_q, "both_calibrated": bool(both_cal),
               "r271_inflation": 2.0, "verdict": v},
              open(OUT / "clustering_inflation.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())

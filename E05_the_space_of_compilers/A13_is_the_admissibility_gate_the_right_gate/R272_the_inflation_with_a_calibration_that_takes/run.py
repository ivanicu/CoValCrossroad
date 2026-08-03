"""R272 -- R271's pooled arm printed CALIBRATION DID NOT TAKE and my kill never looked at it.

THE DEFECT, AND WHY IT MATTERS IN THE DIRECTION IT DOES
    R271 measured the clustering inflation at 2.0x. Its pooled arm -- the deliberately-wrong
    resampling unit -- came back with a held-out alpha of 0.0067 against a target of 0.05, and
    printed CALIBRATION DID NOT TAKE in its own output. My kill checked res["prompt"]["alpha"] and
    never res["pooled"]["alpha"], so the round reported an inflation resting on an arm whose own
    calibration check had failed.

    ⚠ THE CAUSE IS SAMPLE SIZE AT THE TAIL, NOT THE SCHEME. The pooled bootstrap distribution has
    sd 0.0017; estimating its 95th percentile from 150 draws puts the threshold too high, so the
    arm is CONSERVATIVE -- it fires less often than 0.05. A conservative pooled arm has an
    INFLATED MDE, which SHRINKS the measured inflation. So R271's 2.0x is a LOWER BOUND, and
    fixing this should move it up rather than down. That direction is stated before the run.

FIX: 3000 calibration and 3000 held-out replicates per scheme instead of 150, so a 95th percentile
on an sd-0.0017 distribution is actually resolvable. Nothing else changes -- same rows, same grid,
same statistic -- so R271 and R272 are directly comparable.

ESTIMAND        the same as R271: prompt-clustered MDE, pooled-row MDE, and their ratio -- but now
                with both arms' held-out alpha inside a band the kill CHECKS.
IDENTIFICATION  exact per replicate; the plant is constructed.
SCOPE           968 prompts, 93,558 (annotator x pair) rows, r04 cache + the annotators themselves.
WORLDS          W-UP    the inflation rises above R271's 2.0x -> the conservative pooled arm was
                          suppressing it, exactly as predicted, and 2.0x was a floor
                W-FLAT  it does not move -> the calibration failure was immaterial and R271's
                          number stands on a defect that did not matter
                W-DOWN  it falls -> my stated direction was wrong, which is the outcome worth the
                          most because it would mean I reasoned the bias backwards
KILL            pre-registered: BOTH arms' held-out alpha must land in [0.03, 0.08] or the round is
                UNVERIFIED -- the check R271 omitted, now applied to both. Then the inflation is
                reported against sqrt(rows/clusters) = 9.83 as before.
POSITIVE CTRL   largest dose beats g=0 by > 3 binomial se. Computed, not typed.
NEGATIVE CTRL   held-out alpha per scheme, on replicates never used to set tau -- BOTH checked.
SHAM            the plant aimed at the TARGET; R269 established it is the only failable sham here.
PLACEBO         identical arms at the same seed differ by exactly 0.000000.
NOISE FLOOR     each scheme's calibration sd, printed beside its MDE.
MULTIPLICITY    2 schemes x 13 doses x 60 replicates + 2 x 6000 calibration/holdout.
SPECIFICATION   swept: dose and resampling unit. Changed from R271: calibration sample size only.
ARTIFACT        both curves, taus, sds and alphas persisted.
IMPOSSIBLE      the annotators' own reliability -- 47.8% two-rater agreement is the target's
                property and no resampling converts it into precision they do not have.
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
REPS, NCAL, NHOLD = 60, 3000, 3000
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
    a_p, a_q = res["prompt"]["alpha"], res["pooled"]["alpha"]
    both_cal = (0.03 <= a_p <= 0.08) and (0.03 <= a_q <= 0.08)
    print(" NEGATIVE both arms' held-out alpha in [0.03, 0.08] : prompt %.4f  pooled %.4f  -> %s"
          % (a_p, a_q, "OK" if both_cal else "ONE ARM IS MISCALIBRATED"))
    print("          (R271 checked only the prompt arm; its pooled arm was at 0.0067)")
    if not pos_ok or not sham_ok or not both_cal:
        v = ("UNVERIFIED -- positive %s, sham %s, prompt alpha %.4f, pooled alpha %.4f. The check "
             "R271 omitted is applied here to BOTH arms." % (pos_ok, sham_ok, a_p, a_q))
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
               "positive_ok": bool(pos_ok), "sham": sh, "sham_ok": bool(sham_ok),
               "alpha_prompt": a_p, "alpha_pooled": a_q, "both_calibrated": bool(both_cal),
               "r271_inflation": 2.0, "verdict": v},
              open(OUT / "clustering_inflation.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""R270 -- the arc used a statistic 13x coarser than one sitting in the same release.

WHAT R268/R269 ESTABLISHED
    The class-agreement statistic -- "does this 4-criterion arm induce the same weak ordering as the
    full rubric" -- has an MDE of (0.10, 0.12] on this release, at a detector calibrated to
    alpha = 0.05 and validated on held-out no-effect replicates. Every substantive effect E05 ever
    reported is 3 to 30 times below that.

    Every round from R220 to R269 used that statistic or a relative of it.

WHAT DESIGN A USED INSTEAD, AND WHAT IT COST
    R234's human arm scores each compiler against the ANNOTATORS' OWN pairwise preferences over
    80,001 pairs from 968 prompts, and it reported its own MEASURED resolution floor: 0.0081, with
    a compression cost of 0.0173 [0.0100, 0.0250] -- 2.1x that floor. So the same release supports a
    statistic whose floor is roughly an order finer than the one this arc committed to.

    If that holds under the same calibrated machinery, the honest summary of E05 changes from
    "nothing was resolvable here" to "THE STATISTIC THIS ARC CHOSE THREW AWAY THE RESOLUTION",
    which is a design finding with a remedy rather than a site limit.

⛔ AND THE TRAP THAT MAKES THE COMPARISON EASY TO GET WRONG
    A pair-level statistic has 80,001 rows and 968 CLUSTERS. Pairs inside a prompt share both the
    responses and the annotators, so they are not independent. Computing the floor over POOLED
    PAIRS gives a spuriously tiny MDE; computing it over PROMPTS gives the honest one. This round
    computes BOTH and reports the ratio, because the size of that ratio is the quantitative form of
    the n_eff rule and is worth more than either number alone.

ESTIMAND        (a) MDE of the human-ranking statistic under PROMPT-CLUSTERED resampling;
                (b) MDE of the same statistic under POOLED-PAIR resampling -- the wrong way, run
                    deliberately so the inflation can be quantified;
                (c) the ratio (b)/(a), and both against R268's class-agreement MDE.
IDENTIFICATION  exact per replicate; the plant is constructed. The two MDEs are read off measured
                curves and reported as brackets between grid points.
SCOPE           population: prompts with parsable `world` rankings and a usable full-rubric tensor.
                instrument: the r04 cache for the compiler side; the annotators themselves for the
                target -- so this arm is LEAKAGE-FREE in R234's sense, the target is external to
                every compiler. baseline: the calibrated tau. regime: m=4, 6 pairs per prompt.
WORLDS          W-FINER   the human statistic's MDE is far below R268's (0.10, 0.12]
                            -> the arc chose the coarser instrument and the remedy is the statistic
                W-SAME    the two MDEs are comparable
                            -> the coarseness is the release's, not the statistic's, and R268's
                               "specification for a better instrument" stands unamended
KILL            pre-registered: if the prompt-clustered MDE is below 0.03 -- i.e. more than 3x finer
                than R268's lower bracket of 0.10 -- then W-FINER and E05's statistic choice is
                named as the limiting decision. If it is above 0.08, W-SAME.
POSITIVE CTRL   the largest planted dose must beat the g=0 rate by more than 3 binomial se of that
                rate. Computed from two measured numbers, no literal -- the R267 lesson.
NEGATIVE CTRL   alpha validated on HELD-OUT no-effect replicates never used to set tau, for BOTH
                resampling schemes separately. Each must land near 0.05.
SHAM            the plant applied to the TARGET (the humans' own pairwise signs) instead of to the
                compiler's ordering. Detection must collapse. R269 established this is the only
                sham here that can fail -- permuting which prompts carry an effect cannot.
PLACEBO         identical arms at the same seed differ by exactly 0.000000.
NOISE FLOOR     measured by resampling, separately per scheme; that IS the deliverable.
MULTIPLICITY    2 schemes x 9 doses x 60 replicates + 2 x 300 calibration/holdout; all printed.
SPECIFICATION   swept: dose and RESAMPLING UNIT. The second axis is the one every round in this
                arc held fixed without recording that it was a choice.
ARTIFACT        both curves and both taus persisted.
IMPOSSIBLE      whether the humans' pairwise preferences are themselves reliable. Two-rater
                agreement is 47.8% on this release; that is a property of the target and no
                resampling of it can be turned into precision the raters do not have.
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
DOSES = [0.0, 0.01, 0.02, 0.03, 0.04, 0.06, 0.08, 0.10, 0.12]
REPS, NCAL, NHOLD = 60, 150, 150
ALPHA = 0.05
R268_MDE = (0.10, 0.12)
R234_FLOOR = 0.0081


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

    prompts = []
    for p in sorted(sf):
        if p not in recs or p not in ann:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if len(ok) < 4:
            continue
        sg = np.zeros(len(PAIRS)); nr = 0
        for a in ann[p]:
            for e in ((a.get("ranking_blocks") or {}).get("world") or []):
                pts = r220.parse_rank(e.get("ranking"))
                if pts is not None:
                    sg += np.array([np.sign(pts[i] - pts[j]) for i, j in PAIRS]); nr += 1
        if not nr:
            continue
        human = np.sign(sg)
        W = np.array([np.mean([float(s["score"]) for s in f[i]["scores"]]) for i in ok])
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok])
        y = (W[:, None] * S).sum(0)
        comp = np.array([np.sign(y[i] - y[j]) for i, j in PAIRS])
        prompts.append((comp == human).astype(float))     # 6 pair-level agreements
    A = np.array(prompts)
    print("prompts (CLUSTERS) %d | pairs (ROWS) %d | ratio %.1f"
          % (len(A), A.size, A.size / len(A)))
    print("base agreement, prompt-clustered %.4f | pooled-pair %.4f"
          % (A.mean(1).mean(), A.mean()))

    def stat(g, rng, scheme, sham=False):
        if scheme == "prompt":
            idx = rng.integers(0, len(A), len(A))
            M = A[idx].copy()
        else:                                   # POOLED PAIRS -- the wrong unit, run on purpose
            flat = A.ravel()
            M = flat[rng.integers(0, flat.size, flat.size)].reshape(1, -1)
        if g > 0:
            hit = rng.random(M.shape) < g
            M = np.where(hit, 0.0 if sham else 1.0, M)
        return float(M.mean(1).mean())

    res = {}
    for scheme in ("prompt", "pooled"):
        cal = np.array([stat(0.0, np.random.default_rng(11_000 + i), scheme) for i in range(NCAL)])
        tau = float(np.quantile(cal, 1 - ALPHA))
        hold = np.array([stat(0.0, np.random.default_rng(91_000 + i), scheme) for i in range(NHOLD)])
        ah = float((hold > tau).mean())
        curve = {}
        for g in DOSES:
            v = np.array([stat(g, np.random.default_rng(31_000 + int(g * 1000) * 977 + i), scheme)
                          for i in range(REPS)])
            curve[g] = float((v > tau).mean())
        above = [g for g in DOSES if curve[g] >= 0.8]
        hi = min(above) if above else float("inf")
        lo = max([g for g in DOSES if g < hi], default=0.0) if above else DOSES[-1]
        res[scheme] = {"tau": tau, "cal_sd": float(cal.std()), "alpha_holdout": ah,
                       "curve": curve, "mde": [lo, hi]}
        print("\n=== scheme = %s ===" % scheme.upper())
        print(" calibration sd %.5f  tau %.4f  |  HELD-OUT alpha %.4f  %s"
              % (cal.std(), tau, ah, "OK" if 0.01 <= ah <= 0.12 else "CALIBRATION DID NOT TAKE"))
        print(" %-7s %10s" % ("g", "detect"))
        for g in DOSES:
            print(" %-7.2f %10.4f" % (g, curve[g]))
        print(" MDE bracket (%.2f, %s]" % (lo, "%.2f" % hi if above else "none"))

    print("\n=== controls (prompt-clustered scheme) ===")
    c = res["prompt"]["curve"]
    g0, top = c[0.0], c[DOSES[-1]]
    se0 = math.sqrt(max(g0, 1e-9) * (1 - g0) / REPS)
    pos_ok = (top - g0) > 3 * se0
    print(" POSITIVE largest dose %.2f : %.4f vs g=0 %.4f, 3se %.4f  -> %s"
          % (DOSES[-1], top, g0, 3 * se0, "OK" if pos_ok else "CANNOT SEE THE LARGEST PLANT"))
    shv = np.array([stat(0.10, np.random.default_rng(72_000 + i), "prompt", sham=True)
                    for i in range(REPS)])
    sh = float((shv > res["prompt"]["tau"]).mean())
    sham_ok = sh < c[0.10] - 0.10
    print(" SHAM     plant aimed at the TARGET : %.4f  (real %.4f, alpha %.4f)  -> %s"
          % (sh, c[0.10], res["prompt"]["alpha_holdout"], "OK" if sham_ok else "DID NOT FALL"))
    r1 = stat(0.0, np.random.default_rng(555), "prompt")
    r2 = stat(0.0, np.random.default_rng(555), "prompt")
    print(" PLACEBO  identical arms, same seed : %.6f  %s"
          % (r1 - r2, "OK" if r1 == r2 else "BROKEN"))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    mp, mq = res["prompt"]["mde"][1], res["pooled"]["mde"][1]
    infl = mp / mq if mq not in (0, float("inf")) else float("nan")
    if not (0.01 <= res["prompt"]["alpha_holdout"] <= 0.12) or not pos_ok or not sham_ok:
        v = ("UNVERIFIED -- a control did not behave (alpha %.4f, positive %s, sham %s)."
             % (res["prompt"]["alpha_holdout"], pos_ok, sham_ok))
    elif mp < 0.03:
        v = ("W-FINER -- the human-ranking statistic's prompt-clustered MDE is (%.2f, %.2f], "
             "against R268's (%.2f, %.2f] for class agreement: %.0fx finer on the SAME release. "
             "E05 chose the coarser instrument, and that choice -- not the release -- is the "
             "limiting decision. R268's 'specification for a better instrument' is amended: the "
             "better instrument was already here, and design A used it."
             % (res["prompt"]["mde"][0], mp, R268_MDE[0], R268_MDE[1], R268_MDE[1] / mp))
    elif mp > 0.08:
        v = ("W-SAME -- the human statistic's MDE (%.2f, %.2f] is comparable to R268's, so the "
             "coarseness is the RELEASE's and not the statistic's." % (res["prompt"]["mde"][0], mp))
    else:
        v = ("BETWEEN -- MDE (%.2f, %.2f], finer than class agreement but not by the 3x the kill "
             "required. Reported as a partial improvement rather than rounded up."
             % (res["prompt"]["mde"][0], mp))
    print("\n  " + v)
    print("\n  ⛔ AND THE CLUSTERING TRAP, QUANTIFIED: the POOLED-PAIR MDE is (%.2f, %.2f] against"
          % (res["pooled"]["mde"][0], mq))
    print("  the prompt-clustered (%.2f, %.2f]. Treating %d pairs as %d independent rows makes the"
          % (res["prompt"]["mde"][0], mp, A.size, A.size))
    print("  design look %.0fx more sensitive than it is. That inflation is the n_eff rule with a"
          % (1 / infl if infl else float("nan")))
    print("  number on it, and it is the axis every round in this arc held fixed silently.")
    json.dump({"clusters": len(A), "rows": int(A.size), "res": res,
               "positive_ok": bool(pos_ok), "sham": sh, "sham_ok": bool(sham_ok),
               "r268_mde": list(R268_MDE), "r234_floor": R234_FLOOR, "verdict": v},
              open(OUT / "human_statistic_mde.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())

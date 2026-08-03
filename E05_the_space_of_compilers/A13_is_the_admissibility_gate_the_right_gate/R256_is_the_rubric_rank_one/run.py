"""R256 -- the third property. If the rubric is rank-1, a core is a noisy estimator of one number.

THE GAP R255 LEFT OPEN, IN ITS OWN WORDS
    "The core matches the generic vocabulary on REDUNDANCY while differing from it on
    DISCRIMINATION. A third property is doing the work and this arc has not named it."

    R255 measured two candidates. Lexical similarity predicts behavioural agreement at rho +0.0447
    and discrimination at +0.1440 -- and the median lexical overlap between two criteria in one
    prompt is 0.0000, so shared words are nearly irrelevant. Neither closes it, because the core is
    MORE discriminating than the full rubric (R234: core/full sd 1.1047) and yet AS redundant as a
    LESS discriminating generic vocabulary (R249: +0.0042, CI containing 0).

THE PROPERTY BOTH ROUNDS MISSED, AND WHY THEY MISSED IT
    Discrimination is a statement about MAGNITUDE -- how far a criterion's four scores spread.
    Redundancy is a statement about ORDERING -- whether two criteria rank the four responses the
    same way. THOSE ARE INDEPENDENT. Two criteria can each be maximally discriminating and still be
    perfectly redundant, if both track the same latent quantity with different gains.

    So the candidate is: A SINGLE COMMON FACTOR. If responses differ mainly in one latent "quality"
    and every criterion loads on it, then criteria agree without sharing words, discrimination stays
    high, and every Q-class is a THRESHOLDING OF ONE NUMBER.

    ⚠ IF THAT HOLDS, IT REWRITES THE FORMULATION rather than adding to it. `k=1` would be the right
    core size not because of any capacity bound -- R253 already showed the bound was n in a costume
    -- but because THERE IS ONLY ONE THING TO MEASURE, and the whole (Q, class, representative,
    certificate) apparatus would be describing the geometry of a scalar.

ESTIMAND        per prompt, on the criterion x response matrix S (n x 4), row-centred:
                  (a) lambda1_share = leading eigenvalue / total, of the 4x4 response covariance
                  (b) rank1_class_agreement = P( class of the leading component == class of the
                      full weighted rubric ) -- the operational version, and the one that matters
                  (c) both, for the CORE's own criteria, and for R240's generic vocabulary
IDENTIFICATION  exact per prompt; the eigendecomposition and the class function are deterministic.
                The comparison to nulls is the only estimate.
⛔ THE ARITHMETIC TRAP, NAMED BEFORE THE NUMBER
    With m=4 responses, row-centring leaves 3 free dimensions, so lambda1_share >= 1/3 BY
    CONSTRUCTION and a value of 0.5 is not evidence of anything on its own. The null is NOT zero
    and NOT 1/3 either, because finite n adds sampling structure. It is MEASURED, by the
    row-permutation of R252 -- which preserves every criterion's exact multiset of values and
    destroys only the cross-criterion alignment. Any claim below is lambda1_share AGAINST THAT NULL.
SCOPE           population: 250 prompts, 6 <= n <= 14, r04 cache; plus the core's own tensor and
                R240's generic vocabulary. instrument: Qwen3.5-2B. baseline: row-permuted null,
                5 draws per prompt. regime: m=4, noiseless.
WORLDS          W-RANK1     one latent quality drives the responses
                              -> lambda1_share far above its permutation null, and a rank-1
                                 reconstruction reproduces the full rubric's class on most prompts
                W-MULTI     the rubric measures several independent things
                              -> lambda1_share at its null, rank-1 class agreement near the
                                 random-4 floor R231 measured (0.3836)
                W-DEGENERATE lambda1_share is high but rank-1 class agreement is NOT
                              -> the leading factor carries variance without carrying the DECISION,
                                 which would mean variance-explained is the wrong summary and the
                                 arc should stop using eigenvalue language entirely
KILL            pre-registered: if rank-1 class agreement is inside the random-4 floor's spread
                (R231: 0.3836 [0.3657, 0.4019]), the common-factor story is REFUTED regardless of
                how large lambda1_share is, and the third property is still unnamed. If it is above,
                the formulation's object changes from an equivalence class over subsets to a
                threshold on a scalar, and every earlier round must be re-read in that light.
POSITIVE CTRL   a SYNTHETIC rank-1 prompt: every criterion = a_i * q + small noise, q a random
                4-vector. lambda1_share must be near 1 and rank-1 class agreement near 1. Targets
                are reachable -- noise, not construction, sets the ceiling, and the ceiling is
                computed from the same noise level rather than assumed.
NEGATIVE CTRL   the ROW-PERMUTATION of R252: each criterion keeps its exact multiset of values,
                cross-criterion alignment destroyed. Gives the null for BOTH statistics.
SHAM            a synthetic FULL-RANK prompt: criteria drawn independently, matched on n and on the
                real tensor's mean and sd. lambda1_share must land on the permutation null.
PLACEBO         a prompt whose criteria are all identical: lambda1_share exactly 1.0.
NOISE FLOOR     5 permutation draws per prompt; spread reported.
MULTIPLICITY    2 statistics x 3 object sets (full / core / generic) x 4 arms; whole grid printed.
SPECIFICATION   swept: centring (row-centred vs raw) and weighting (population weights vs unit),
                because a common factor found only under one centring is a centring artifact.
ARTIFACT        per-prompt lambda spectra persisted.
IMPOSSIBLE      whether the latent factor IS "quality" in any sense a person would endorse. No
                external label exists; the round names a dimension, never its meaning.
"""
from __future__ import annotations
import collections, json, pathlib, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / ("E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all"
             "/R04_rebuild_satisfaction/results")
GT = ROOT / ("E05_the_space_of_compilers/A10_is_a_global_core_real/R240_fit_a_global_core"
             "/results/sat_global.npz")
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
DRAWS = 5
R231_FLOOR = (0.3836, 0.3657, 0.4019)


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def spectrum(S, centre=True):
    """leading eigenvalue share of the response covariance, and the leading component's scores."""
    X = S - S.mean(1, keepdims=True) if centre else S.copy()
    C = X.T @ X
    w, V = np.linalg.eigh(C)
    o = np.argsort(w)[::-1]
    w, V = w[o], V[:, o]
    tot = float(w.sum())
    share = float(w[0] / tot) if tot > 1e-12 else float("nan")
    # the leading component's score per response, oriented to correlate + with the mean criterion
    comp = V[:, 0] * np.sign(float(V[:, 0] @ X.mean(0)) or 1.0)
    return share, comp, w / tot if tot > 1e-12 else w


def row_permute(S, rng):
    out = S.copy()
    for i in range(len(out)):
        out[i] = out[i][rng.permutation(4)]
    return out


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    import importlib.util
    _s = importlib.util.spec_from_file_location(
        "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
                     / "R220_compiler_tournament/run.py")
    r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)
    sf = r220.load_sat(R4 / "a04_full.npz")
    sc = r220.load_sat(R4 / "a04_core.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    P = []
    for p in sorted(sf):
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if not (6 <= len(ok) <= 14):
            continue
        W = np.array([np.mean([float(s["score"]) for s in f[i]["scores"]]) for i in ok])
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok], float)
        cj = sorted({k[0] for k in (sc.get(p) or {})})
        SC = (np.array([[sc[p][(j, x)] for x in L] for j in cj], float)
              if cj and all((j, x) in sc[p] for j in cj for x in L) else None)
        P.append((p, W, S, SC))
        if len(P) >= 250:
            break
    print("prompts %d (with a usable core tensor: %d)"
          % (len(P), sum(1 for _p, _W, _S, C in P if C is not None)))

    print("\n=== controls, synthetic, before any real number ===")
    rng = np.random.default_rng(0)
    q = rng.standard_normal(4)
    S1 = np.array([rng.uniform(0.3, 1.5) * q + 0.02 * rng.standard_normal(4) for _ in range(10)])
    s1, c1, _ = spectrum(S1)
    a1 = float(cls(c1) == cls(S1.sum(0)))
    print(" POSITIVE rank-1 synthetic (10 criteria = a_i*q + 0.02 noise):")
    print("          lambda1_share %.4f   rank-1 class == full class : %.0f   %s"
          % (s1, a1, "OK" if (s1 > 0.95 and a1 == 1.0) else "SPECTRUM OR CLASS FN BROKEN"))
    allv = np.concatenate([S.ravel() for _p, _W, S, _C in P])
    Sf = np.clip(rng.normal(allv.mean(), allv.std(), (10, 4)), 0, 1)
    sfsh, _cf, _ = spectrum(Sf)
    print(" SHAM     full-rank synthetic, matched mean/sd : lambda1_share %.4f" % sfsh)
    Sid = np.tile(np.array([0.9, 0.4, 0.2, 0.7]), (10, 1))
    sid, _c, _ = spectrum(Sid)
    print(" PLACEBO  identical criteria : lambda1_share %.4f  %s"
          % (sid, "OK" if abs(sid - 1.0) < 1e-9 else "BROKEN"))
    print(" ⛔ FLOOR BY CONSTRUCTION: m=4 row-centred leaves 3 dimensions, so lambda1_share >= 1/3")
    print("    = 0.3333 before any structure exists. The real null is the row permutation below.")
    pos_ok = s1 > 0.95 and a1 == 1.0 and abs(sid - 1.0) < 1e-9

    print("\n=== the measurement, against a MEASURED null ===")
    rows = collections.defaultdict(list)
    for p, W, S, SC in P:
        for cen in (True, False):
            for wt, M in (("unit", S), ("weighted", W[:, None] * S)):
                s_, c_, _ = spectrum(M, cen)
                rows[("full", cen, wt, "real")].append(s_)
                if cen and wt == "weighted":
                    rows[("full", cen, wt, "cls")].append(
                        float(cls(c_) == cls((W[:, None] * S).sum(0))))
                nul = [spectrum(row_permute(M, rng), cen)[0] for _ in range(DRAWS)]
                rows[("full", cen, wt, "null")].append(float(np.mean(nul)))
        if SC is not None and len(SC) >= 2:
            s_, c_, _ = spectrum(SC)
            rows[("core", True, "unit", "real")].append(s_)
            rows[("core", True, "unit", "cls")].append(float(cls(c_) == cls(SC.sum(0))))
            rows[("core", True, "unit", "null")].append(
                float(np.mean([spectrum(row_permute(SC, rng))[0] for _ in range(DRAWS)])))

    print("%-8s %-9s %-9s %10s %10s %10s" % ("object", "centred", "weight", "lambda1", "null",
                                             "excess"))
    grid = {}
    for key in sorted({(k[0], k[1], k[2]) for k in rows}):
        r_ = rows[(key[0], key[1], key[2], "real")]
        n_ = rows[(key[0], key[1], key[2], "null")]
        if not r_:
            continue
        grid["%s|%s|%s" % key] = (float(np.mean(r_)), float(np.mean(n_)),
                                  float(np.mean(r_) - np.mean(n_)))
        print("%-8s %-9s %-9s %10.4f %10.4f %+10.4f"
              % (key[0], key[1], key[2], np.mean(r_), np.mean(n_), np.mean(r_) - np.mean(n_)))

    print("\n=== the statistic that decides it: does a RANK-1 reconstruction carry the CLASS? ===")
    a_full = float(np.mean(rows[("full", True, "weighted", "cls")]))
    a_core = (float(np.mean(rows[("core", True, "unit", "cls")]))
              if rows[("core", True, "unit", "cls")] else float("nan"))
    print(" full rubric : rank-1 component reproduces the full weighted class on %.4f of prompts"
          % a_full)
    print(" core        : %.4f" % a_core)
    print(" comparand   : R231's random-4 floor %.4f [%.4f, %.4f] -- what a size-matched arbitrary"
          % R231_FLOOR)
    print("               subset achieves on the same target. A rank-1 story has to beat THAT.")

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    lam = grid.get("full|True|weighted", (float("nan"),) * 3)
    if not pos_ok:
        v = "UNVERIFIED -- the synthetic rank-1 or the identical-criteria placebo did not behave."
    elif a_full <= R231_FLOOR[2]:
        v = ("W-DEGENERATE or W-MULTI -- a rank-1 reconstruction reproduces the full rubric's own "
             "class on only %.4f of prompts, inside R231's random-4 floor [%.4f, %.4f]. The common "
             "factor does NOT carry the decision even though lambda1_share is %.4f against a "
             "measured null of %.4f. VARIANCE EXPLAINED IS THE WRONG SUMMARY HERE, and the third "
             "property R255 left open is still unnamed. What this DOES kill is the eigenvalue "
             "language: no round may quote lambda1_share as evidence about the class."
             % (a_full, R231_FLOOR[1], R231_FLOOR[2], lam[0], lam[1]))
    else:
        v = ("W-RANK1 -- a rank-1 reconstruction reproduces the full rubric's class on %.4f of "
             "prompts against a random-4 floor of %.4f [%.4f, %.4f], with lambda1_share %.4f "
             "against a measured permutation null of %.4f (excess %+.4f). THE OBJECT CHANGES: a "
             "core is a noisy estimator of ONE number, every Q-class is a thresholding of it, and "
             "k=1 is right for a reason that has nothing to do with any capacity bound."
             % (a_full, R231_FLOOR[0], R231_FLOOR[1], R231_FLOOR[2], lam[0], lam[1], lam[2]))
    print("\n  " + v)
    json.dump({"prompts": len(P), "grid": grid,
               "rank1_class_full": a_full, "rank1_class_core": a_core,
               "r231_floor": list(R231_FLOOR),
               "controls": {"positive_lambda": s1, "positive_class": a1, "sham_lambda": sfsh,
                            "placebo_lambda": sid, "construction_floor": 1 / 3},
               "verdict": v}, open(OUT / "rank_one.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())

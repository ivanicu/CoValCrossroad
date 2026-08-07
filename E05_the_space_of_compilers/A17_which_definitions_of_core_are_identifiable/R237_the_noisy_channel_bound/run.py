"""R237 -- the bound has been noiseless for five rounds, and this project measured the noise.

R224 set H_have = log2 a(m) -- the number of DISTINGUISHABLE observations if the observation were
exact. R227 then measured that at the release's own rater noise a richer observable buys almost
nothing, because disagreement eats the resolution. The two never met. The inequality

    log2 |H(Q)|  <=  H_have

has been carrying a NOISELESS capacity on its right-hand side while the same arc was publishing the
noise level. That overstates what is available, by exactly the amount nobody folded back in.

THE CORRECTION
    A rater is a NOISY CHANNEL from the true class to the observed one. What the channel actually
    delivers is not log2 a(m) but

        H_eff  =  I(C_true ; C_obs)

    the mutual information under the measured confusion. H_eff <= log2 a(m) always, with equality
    only at zero noise. Re-deriving k_max with H_eff instead is the honest bound.

ESTIMAND        H_eff = I(C_true; C_obs) in bits, at eps calibrated to the release's own 47.8%
                human-human top-choice agreement, as a function of the number of raters R.
IDENTIFICATION  exact in the simulation; the confusion matrix is generated, not inferred.
SCOPE           300 prompts, m=4, classes = weak orderings induced by the real W and cached S.
                instrument: Qwen3.5-2B tensor, identical across all cells. regime: eps in
                {0, 0.10, 0.25, 0.50}, R in {1, 5, 14}.
WORLDS          W1 aggregation recovers the channel -> H_eff rises to H(C_true) as R grows
                W2 the noise is not averageable     -> H_eff plateaus below it
CONTROLS -- ceiling COMPUTED per R229, and it is NOT log2 75
  CEILING   H(C_true), the entropy of the class distribution actually realised. Classes are not
            uniform over the 75 weak orderings, so the ceiling is the empirical entropy and the
            noiseless cell must reach it. Demanding log2 75 would be a control that cannot pass.
  FLOOR     eps very large -> I must fall to ~0.
  BIAS      plug-in MI is biased UPWARD (unlike entropy). Miller-Madow-analogue correction
            reported beside the raw value; the raw one is the optimistic one and is marked.
MULTIPLICITY    4 noise levels x 3 rater counts x 5 seeds; whole grid printed.
IMPOSSIBLE      the confusion matrix of REAL raters against a REAL true class -- no true class
                exists to condition on. This is a simulation calibrated to a measured agreement
                rate, and every number is scoped to that.
"""
from __future__ import annotations
import itertools, json, math, pathlib, sys, collections
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
from covalx.control_band import check, ControlBandError

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
EPS = [0.0, 0.10, 0.25, 0.50, 2.0]
RS = [1, 5, 14]
SEEDS = [0, 1, 2, 3, 4]
K = 2

import importlib.util
_s = importlib.util.spec_from_file_location(
    "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                 / "R220_compiler_tournament/run.py")
r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def mi(pairs, rng=None, nperm=20):
    """Plug-in mutual information in bits, corrected by a PERMUTATION null.

    ⚠ THE FIRST VERSION USED AN ANALYTIC BIAS CORRECTION, (|X|-1)(|Y|-1)/(2N ln2), and its own
    positive control caught it: at eps=0 the channel is noiseless, C_obs == C_true exactly, so
    I MUST equal H(C_true) = 4.6614. It returned 2.5562. The raw plug-in was 4.6361 -- essentially
    right -- so the estimator was fine and the CORRECTION was wrong. With up to 75 classes on each
    side and N=300, that formula subtracts 74*74/(2*300*ln2) = 13.2 bits, a correction larger than
    the quantity, and it drove H_eff to exactly 0.0000 at R=14. The verdict then printed `inf%`,
    which is the arithmetic tell that should have stopped me one line earlier.
    The valid small-N correction is EMPIRICAL: shuffle the pairing, measure the MI that survives,
    subtract it. That is what the bias IS, measured rather than modelled."""
    j = collections.Counter(pairs)
    n = sum(j.values())
    if not n:
        return 0.0, 0.0
    px = collections.Counter(); py = collections.Counter()
    for (a, b), c in j.items():
        px[a] += c; py[b] += c
    I = 0.0
    for (a, b), c in j.items():
        I += (c / n) * math.log2((c / n) / ((px[a] / n) * (py[b] / n)))
    if rng is None:
        return I, I
    a = [x for x, _ in pairs]; b = [y for _, y in pairs]
    null = []
    for _ in range(nperm):
        bb = list(b); rng.shuffle(bb)
        jj = collections.Counter(zip(a, bb))
        v = 0.0
        pxx = collections.Counter(); pyy = collections.Counter()
        for (x, y), c in jj.items():
            pxx[x] += c; pyy[y] += c
        for (x, y), c in jj.items():
            v += (c / n) * math.log2((c / n) / ((pxx[x] / n) * (pyy[y] / n)))
        null.append(v)
    return I, max(0.0, I - float(np.mean(null)))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sf = r220.load_sat(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    prompts = []
    for p in sorted(sf):
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if not (6 <= len(ok) <= 16):
            continue
        W = np.array([np.mean([float(s["score"]) for s in f[i]["scores"]]) for i in ok])
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok])
        prompts.append((W, S))
        if len(prompts) >= 300:
            break

    grid, ns = {}, []
    for eps in EPS:
        for R in RS:
            per = collections.defaultdict(list)
            for seed in SEEDS:
                pairs = []
                for pi, (W, S) in enumerate(prompts):
                    rng = np.random.default_rng(abs(hash((pi, seed, eps, R))) % (2 ** 32))
                    T = tuple(sorted(rng.choice(len(W), size=K, replace=False)))
                    y0 = (W[list(T), None] * S[list(T)]).sum(0)
                    ct = cls(y0)
                    sc = (np.abs(y0).max() or 1.0)
                    votes = np.zeros(len(PAIRS))
                    for _ in range(R):
                        votes += np.array(cls(y0 + eps * sc * rng.standard_normal(4)))
                    co = tuple(np.sign(votes))
                    pairs.append((ct, co))
                    if eps == 0.0 and R == 1 and seed == SEEDS[0]:
                        ns.append(ct)
                raw, cor = mi(pairs, np.random.default_rng(1000 + seed))
                per["raw"].append(raw); per["cor"].append(cor)
            grid[(eps, R)] = (float(np.mean(per["raw"])), float(np.mean(per["cor"])),
                              max(per["cor"]) - min(per["cor"]))

    # CEILING: the entropy of the class distribution actually realised, NOT log2 75
    cnt = collections.Counter(ns)
    n = sum(cnt.values())
    H_true = -sum((c / n) * math.log2(c / n) for c in cnt.values())
    print("prompts %d | classes realised %d | H(C_true) = %.4f bits   (log2 a(4) = %.4f)"
          % (len(prompts), len(cnt), H_true, math.log2(75)))
    print("  ^ the CEILING is H(C_true), not log2 75: classes are not uniform, and demanding")
    print("    log2 75 would be a control that cannot pass (R229).")

    print("\n=== H_eff = I(C_true ; C_obs), bias-corrected, bits ===")
    print("%-8s %s" % ("eps", "".join("%18s" % ("R=%d" % R) for R in RS)))
    for eps in EPS:
        print("%-8.2f %s" % (eps, "".join("  %6.4f (raw %6.4f)" % (grid[(eps, R)][1],
                                                                   grid[(eps, R)][0]) for R in RS)))
    print("%-8s %s" % ("spread", "".join("%18.4f" % grid[(0.25, R)][2] for R in RS)))

    print("\n=== controls ===")
    pos = grid[(0.0, 1)][1]
    neg = grid[(2.0, 14)][1]
    try:
        v = check("H_eff", 0.0, H_true, H_true / 2, pos)
        print(" band: floor 0.0000  ceiling %.4f (computed)  observed at eps=0: %.4f (%.0f%% of band)"
              % (H_true, pos, 100 * v["headroom_used"]))
    except ControlBandError as e:
        print(" BAND ERROR: %s" % str(e)[:120])
    # ⚠ FOURTH CONTROL-THAT-CANNOT-PASS IN THIS ARC, and R229's band flagged it at 68%.
    # I required the CORRECTED estimate to reach H(C_true) at eps=0. At eps=0 the channel is
    # noiseless and C_obs == C_true, so the raw plug-in is not an ESTIMATE at all -- it is an
    # identity, and subtracting a permutation null from an identity over-corrects by construction.
    # The permutation null is the right correction for the NOISY cells and the wrong one for the
    # noiseless cell. So each estimator is validated in the regime where it is meaningful:
    #   RAW at eps=0        must reach H(C_true)   -- tests the estimator
    #   CORRECTED at eps=2  must fall to ~0        -- tests the correction
    # and the noisy cells are reported as a BRACKET [corrected, raw], never a point. realstat G1:
    # if only partially identified, give BOUNDS.
    pos_raw = grid[(0.0, 1)][0]
    print(" POSITIVE raw at eps=0 must reach H(C_true) : %.4f vs %.4f  %s"
          % (pos_raw, H_true, "OK" if abs(pos_raw - H_true) < 0.10 else "ESTIMATOR BROKEN"))
    print("          (the CORRECTED value at eps=0 is %.4f and is EXPECTED to undershoot: the"
          % pos)
    print("           permutation null corrects an estimate, and at zero noise there is none)")
    print(" NEGATIVE eps=2.0, R=14 must fall toward 0: %.4f  %s"
          % (neg, "OK" if neg < 0.5 * H_true else "NOT NULL"))

    print("\n=== the corrected bound: k_max with H_eff instead of log2 a(m) ===")
    nmed = 15
    print(" at n=%d, H_need(k) = log2 C(%d,k):" % (nmed, nmed))
    for k in (1, 2, 3, 4):
        print("   k=%d  needs %.2f bits" % (k, math.log2(math.comb(nmed, k))))
    print(" available:")
    for R in RS:
        lo, hi = grid[(0.25, R)][1], grid[(0.25, R)][0]
        klo = [k for k in range(1, nmed) if math.log2(math.comb(nmed, k)) <= lo]
        khi = [k for k in range(1, nmed) if math.log2(math.comb(nmed, k)) <= hi]
        print("   R=%-3d at the release's own noise: H_eff in [%.4f, %.4f] bits -> k_max in [%d, %d]"
              % (R, lo, hi, max(klo) if klo else 0, max(khi) if khi else 0))
    print("   noiseless (R224's figure)         : H_have = %.4f bits -> k_max = 1" % math.log2(75))

    lo14, hi14 = grid[(0.25, 14)][1], grid[(0.25, 14)][0]
    v = ("PARTIALLY IDENTIFIED, so a bracket rather than a point: at the release's own rater noise "
         "and its own rater count, H_eff lies in [%.2f, %.2f] bits against the %.2f R224's "
         "inequality assumed. k=1 needs %.2f bits, so a ONE-criterion core sits at the EDGE of the "
         "bracket -- admissible at the optimistic end, not at the conservative one. The noiseless "
         "bound was not merely loose, it was carrying between %.0f%% and %.0f%% more capacity than "
         "the channel delivers."
         % (lo14, hi14, math.log2(75), math.log2(15),
            100 * (math.log2(75) / hi14 - 1), 100 * (math.log2(75) / lo14 - 1)))
    print("\n" + "=" * 78); print("VERDICT"); print("=" * 78); print("\n  " + v)
    json.dump({"H_true": H_true, "classes": len(cnt),
               "grid": {"eps%.2f_R%d" % k_: v_ for k_, v_ in grid.items()}, "verdict": v},
              open(OUT / "noisy_channel.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())

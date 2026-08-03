"""R227 -- R226's price list mixed two currencies, and it does the richer observable's claim a favour.

THE ERROR, ONE ROUND OLD AND MINE
    R226 priced per-criterion satisfaction at 60 bits against the ordering's 5.96 and wrote "closes
    the gap ten times over". Those are bits about DIFFERENT UNKNOWNS.

        T  = which criteria the norm actually uses          -- a VALUE question
        S  = which criteria each response satisfies         -- a FACT question

    H_need = log2 C(n,k) is bits needed to identify T. A ranking carries bits about T, because T
    generated it. Per-criterion satisfaction carries bits about S. In this repository S is ALREADY
    reconstructed -- every round since r04 uses the cached tensor -- so a human-reported S would
    REPLACE THE JUDGE, not add identification power for T. The 60 bits are real and they buy
    something real; they do not buy what H_need is denominated in.

    => "closes the gap ten times over" is WITHDRAWN. Per-criterion satisfaction belongs on the
       instrument axis, not the identification axis.

WHAT IS ACTUALLY TESTABLE, AND WHAT R226 ASSERTED FROM CAPACITY ALONE
    The graded-score and pairwise-confidence rows ARE in the right currency: they are richer
    observations of the same object the ranking observes. But R226 priced them by CAPACITY and
    never checked the bits are USABLE. Capacity present is not recovery achieved.

ESTIMAND        recovery rate of a planted subset T as a function of observable richness g.
IDENTIFICATION  exact -- T is planted, so the truth is known.
SCOPE           300 prompts, 6<=n<=16, K=2, 5 seeds. instrument: cached Qwen3.5-2B tensor for S,
                which is held FIXED and identical across every arm, so nothing here is about S.
WORLDS          W1 the ranking's 6 bits are the binding constraint -> recovery rises with g
                W2 something else binds                            -> recovery flat in g
KILL            if recovery at g=10 does not exceed recovery at the ranking by more than the seed
                spread, R226's "a 10-point score closes the gap" is REFUTED as a usability claim.
POSITIVE CTRL   g=inf (the exact real-valued score) must recover near-perfectly. If the richest
                possible observable cannot recover T, the instrument is broken and all cells void.
NEGATIVE CTRL   g=1 (a constant) must sit at chance = 1/C(n,K).
NOISE FLOOR     5 seeds, spread reported per cell.
MULTIPLICITY    6 richness levels x 3 noise levels x 5 seeds; whole grid printed.
IMPOSSIBLE      whether a HUMAN could supply a 10-level score reliably -- that is a measurement
                error question about people and needs new elicitation, not a rerun.
"""
from __future__ import annotations

import itertools, json, math, pathlib, sys, collections
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
L = "ABCD"
K = 2
LEVELS = ["const", "rank", "g3", "g5", "g10", "exact"]
EPS = [0.0, 0.10, 0.25, 0.50]
SEEDS = [0, 1, 2, 3, 4]

import importlib.util
_s = importlib.util.spec_from_file_location(
    "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                 / "R220_compiler_tournament/run.py")
r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)

PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]


def encode(y, level):
    """The OBSERVABLE a person supplies, at richness `level`. S is never part of this -- it is
    known and identical in every arm, which is the whole point of the round."""
    if level == "const":
        return np.zeros(4)
    if level == "rank":
        return np.array([float(np.sign(y[i] - y[j])) for i, j in PAIRS])
    if level == "exact":
        rng_ = y.max() - y.min()
        return (y - y.min()) / rng_ if rng_ > 0 else np.zeros(4)
    g = int(level[1:])
    rng_ = y.max() - y.min()
    z = (y - y.min()) / rng_ if rng_ > 0 else np.zeros(4)
    return np.round(z * (g - 1)) / (g - 1)


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

    grid, chance = {}, []
    for W, S in prompts:
        chance.append(1.0 / math.comb(len(W), K))
    for eps in EPS:
        for lev in LEVELS:
            per = collections.defaultdict(list)
            for seed in SEEDS:
                for pi, (W, S) in enumerate(prompts):
                    rng = np.random.default_rng(abs(hash((pi, seed, eps, lev))) % (2 ** 32))
                    T = tuple(sorted(rng.choice(len(W), size=K, replace=False)))
                    y = (W[list(T), None] * S[list(T)]).sum(0)
                    y = y + eps * (np.abs(y).max() or 1.0) * rng.standard_normal(4)
                    obs = encode(y, lev)
                    best, hits = None, []
                    for c in itertools.combinations(range(len(W)), K):
                        idx = list(c)
                        e = encode((W[idx, None] * S[idx]).sum(0), lev)
                        d = float(np.abs(e - obs).sum())
                        if best is None or d < best - 1e-12:
                            best, hits = d, [c]
                        elif abs(d - best) <= 1e-12:
                            hits.append(c)
                    # a tie is not a recovery: credit 1/|ties| so ties cannot be cashed as skill
                    per[seed].append((1.0 / len(hits)) if T in hits else 0.0)
            v = [float(np.mean(per[s])) for s in SEEDS]
            grid[(eps, lev)] = (float(np.mean(v)), max(v) - min(v))

    # ⚠ CALIBRATE eps TO REAL HUMAN NOISE BEFORE READING ANY ROW. The gain from a richer
    # observable collapses as eps rises (+0.54 at 0, +0.03 at 0.25), so which row is the
    # RECOMMENDATION depends entirely on where real raters sit. The release's own human-human
    # agreement on the top choice is 47.8% (README, r179). Find the eps that reproduces it.
    print("=== calibrating eps to the release's own human-human agreement (47.8% on top choice) ===")
    cal = {}
    for eps in [0.0, 0.1, 0.25, 0.5, 0.75, 1.0, 1.5, 2.0]:
        agree = []
        for seed in SEEDS:
            for pi, (W, S) in enumerate(prompts):
                rng = np.random.default_rng(abs(hash((pi, seed, eps, "cal"))) % (2 ** 32))
                y0 = (W[:, None] * S).sum(0)
                sc = (np.abs(y0).max() or 1.0)
                a = np.argmax(y0 + eps * sc * rng.standard_normal(4))
                b = np.argmax(y0 + eps * sc * rng.standard_normal(4))
                agree.append(a == b)
        cal[eps] = float(np.mean(agree))
        print("   eps=%-5.2f  two independent raters pick the same top choice %.1f%%"
              % (eps, 100 * cal[eps]))
    eps_star = min(cal, key=lambda e: abs(cal[e] - 0.478))
    print("   -> the release's 47.8%% corresponds to eps ~ %.2f" % eps_star)

    ch = float(np.mean(chance))
    print("prompts %d (6<=n<=16) | K=%d | %d seeds | chance = 1/C(n,K) = %.4f"
          % (len(prompts), K, len(SEEDS), ch))
    print("\n=== recovery of the planted subset, by observable richness ===")
    print("%-8s %s" % ("eps", "".join("%12s" % l for l in LEVELS)))
    for eps in EPS:
        print("%-8.2f %s" % (eps, "".join("%12.4f" % grid[(eps, l)][0] for l in LEVELS)))
    print("%-8s %s" % ("spread", "".join("%12.4f" % grid[(0.10, l)][1] for l in LEVELS)))

    print("\n=== controls ===")
    c_neg = grid[(0.0, "const")][0]
    c_pos = grid[(0.0, "exact")][0]
    print(" NEGATIVE  const observable -> %.4f  vs chance %.4f   %s"
          % (c_neg, ch, "OK" if abs(c_neg - ch) < 0.02 else "NOT AT CHANCE"))
    print(" POSITIVE  exact score      -> %.4f                    %s"
          % (c_pos, "OK" if c_pos > 0.9 else "INSTRUMENT BROKEN -- all cells void"))

    print("\n" + "=" * 78)
    print("KILL: is a richer response-level observable USABLE, not merely larger?")
    print("=" * 78)
    res = {"chance": ch, "grid": {"eps%.2f_%s" % k: v for k, v in grid.items()}}
    if c_pos <= 0.9 or abs(c_neg - ch) >= 0.02:
        v = "UNVERIFIED -- controls did not behave"
    else:
        rows = []
        for eps in EPS:
            r_, s_ = grid[(eps, "rank")]
            g_, sg = grid[(eps, "g10")]
            rows.append((eps, g_ - r_, max(s_, sg), g_ - r_ > max(s_, sg)))
        fired = sum(1 for _, _, _, f_ in rows if f_)
        for eps, d, sp, f_ in rows:
            print(" eps=%.2f  g10 - rank = %+0.4f   seed spread %.4f   %s"
                  % (eps, d, sp, "OUTSIDE" if f_ else "inside"))
        print("\n CALIBRATED READING -- the row that is the recommendation:")
        near = min(EPS, key=lambda e: abs(e - eps_star))
        print("   at eps ~ %.2f (the release's own rater noise), g10 - rank = %+0.4f"
              % (near, grid[(near, "g10")][0] - grid[(near, "rank")][0]))
        print("   against %+0.4f in the noiseless regime -- a %.0fx difference, and the noiseless"
              % (grid[(0.0, "g10")][0] - grid[(0.0, "rank")][0],
                 (grid[(0.0, "g10")][0] - grid[(0.0, "rank")][0])
                 / max(grid[(near, "g10")][0] - grid[(near, "rank")][0], 1e-9)))
        print("   row is the one R226's capacity argument implicitly assumed.")
        if fired == len(rows):
            v = ("SUPPORTED at every noise level: a 10-level score recovers the planted subset "
                 "more often than a ranking, by more than seed noise. R226's capacity claim is "
                 "usable, not merely arithmetic.")
        elif fired == 0:
            v = ("REFUTED: a 10-level score does not beat the ranking beyond seed noise. R226 "
                 "priced capacity that is not usable for recovering T.")
        else:
            v = ("PARTIAL: the richer observable helps in %d of %d noise levels." % (fired, len(rows)))
    print("\n  " + v)
    print("\n  and separately, WITHDRAWN from R226: per-criterion satisfaction was priced at 60")
    print("  bits against the ordering's 5.96 and called 'ten times over'. Those are bits about S,")
    print("  a FACT question, while H_need is denominated in bits about T, a VALUE question. S is")
    print("  already reconstructed and held identical in every arm above. A human-reported S would")
    print("  REPLACE THE JUDGE -- a real and large benefit, on the instrument axis, not this one.")
    res["verdict"] = v
    res["withdrawn"] = ("R226's 'per-criterion satisfaction closes the gap ten times over' -- "
                        "bits about S are not bits about T")
    (OUT / "two_currencies.json").write_text(json.dumps(res, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

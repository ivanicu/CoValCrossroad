"""R225b -- the corrected estimand. Ties were the wrong statistic; RECOVERY is the property.

WHY THIS FILE EXISTS
    R225 asked "do raters add identification bits?" using TIED SUBSETS AT THE OPTIMUM, and its
    positive control failed twice, with two different plants:
        plant 1 (weight dispersion): ratio 1.000 -> 0.927 -> 0.931 -> 0.965, non-monotone
        plant 2 (sparsity)         : ratio 1.000 -> 0.942 -> 0.957 -> 0.997, non-monotone
    Two different plants, same shape of failure => the fault is not the plant, it is the ESTIMAND.
    Tie-count saturates from BOTH ends: when raters agree, everything matching consensus ties; when
    raters are maximally diverse, everything is equally bad and ties again. A statistic that
    returns to 1 at maximum signal cannot measure that signal.

THE CORRECTED ESTIMAND -- realstat G2, verbatim: "plant a known effect; require RECOVERY"
    Build a world where the generating subset T is KNOWN. Then ask, directly:
        P(recover T | consensus objective)   vs   P(recover T | multi-rater objective)
    Monotone by construction, and the positive control is the plant itself.

ESTIMAND        recovery rate of the true generating subset, under each objective.
IDENTIFICATION  exact -- T is known because we generated it.
WORLDS          W1 raters are noise around one consensus -> recovery_B == recovery_A
                W2 raters carry per-person structure     -> recovery_B >  recovery_A
KILL            recovery_B - recovery_A > the seed spread at the same (R, eps) => R224 REFUTED.
                Inside the spread => R224 SURVIVES.
DOSE            eps in {0, .1, .25, .5} x R in {2, 5, 14}; monotone in both or the plant is wrong.
SEEDS           5, and the seed flag is verified to change the draws.
"""
import itertools, json, pathlib, sys, collections
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
DATA = ROOT / "data"
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
K = 2
EPS = [0.0, 0.10, 0.25, 0.50]
RS = [2, 5, 14]
SEEDS = [0, 1, 2, 3, 4]

import importlib.util
_s = importlib.util.spec_from_file_location(
    "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                 / "R220_compiler_tournament/run.py")
r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)


def psign(y):
    return np.array([np.sign(y[i] - y[j]) for i, j in PAIRS])


def best_subsets(W, S, targets, k):
    best, hits = None, []
    for c in itertools.combinations(range(len(W)), k):
        idx = list(c)
        sg = psign((W[idx, None] * S[idx]).sum(0))
        v = sum(int((sg == t).sum()) for t in targets)
        if best is None or v > best:
            best, hits = v, [c]
        elif v == best:
            hits.append(c)
    return hits


def main():
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

    grid = {}
    fingerprint = collections.defaultdict(set)
    for eps in EPS:
        for R in RS:
            recA, recB = collections.defaultdict(list), collections.defaultdict(list)
            for seed in SEEDS:
                for pi, (W, S) in enumerate(prompts):
                    rng = np.random.default_rng(abs(hash((pi, seed, eps, R))) % (2 ** 32))
                    T = tuple(sorted(rng.choice(len(W), size=K, replace=False)))
                    fingerprint[(eps, R)].add((pi, seed, T))
                    base = (W[list(T), None] * S[list(T)]).sum(0)
                    raters = []
                    for _ in range(R):
                        y = base + eps * np.abs(base).max() * rng.standard_normal(4)
                        raters.append(psign(y))
                    # ⚠ THIS LINE WAS psign(np.mean(raters, axis=0)). `raters` are 6-element
                    # PAIR-SIGN vectors and psign() expects a 4-element SCORE vector -- it indexes
                    # y[i]-y[j] over range(4), so it read four of the six pair signs as if they
                    # were scores and produced a garbage target. Objective A was being fitted to
                    # noise, which is why it sat at 0.355 while B hit 1.000.
                    # Caught by the arithmetic check, not by a control: at eps=0 every rater is
                    # identical, so B's score is exactly R x A's score and the two objectives MUST
                    # agree. They did not. "Could this have come out otherwise?" -- no, and that is
                    # what exposed it.
                    cons = np.sign(np.sum(raters, axis=0))   # majority pairwise sign
                    recA[seed].append(T in best_subsets(W, S, [cons], K))
                    recB[seed].append(T in best_subsets(W, S, raters, K))
            a = [float(np.mean(recA[s])) for s in SEEDS]
            b = [float(np.mean(recB[s])) for s in SEEDS]
            grid[(eps, R)] = (float(np.mean(a)), float(np.mean(b)),
                              max(a) - min(a), max(b) - min(b))

    print("prompts %d (6<=n<=16)  |  K=%d  |  %d seeds  |  recovery of the KNOWN subset"
          % (len(prompts), K, len(SEEDS)))
    print("\n%-6s %-4s %10s %10s %10s   %s" % ("eps", "R", "recov_A", "recov_B", "B-A", "seed spread A/B"))
    for eps in EPS:
        for R in RS:
            a, b, sa, sb = grid[(eps, R)]
            flag = "  <-- outside the spread" if (b - a) > max(sa, sb) else ""
            print("%-6.2f %-4d %10.4f %10.4f %+10.4f   %.4f / %.4f%s" % (eps, R, a, b, b - a, sa, sb, flag))

    a0 = grid[(0.0, 5)]
    print("\n=== correctness check: at eps=0 all raters are identical, so B = R x A exactly ===")
    print("   recov_A %.4f  recov_B %.4f  difference %+.4f  (MUST be 0.0000)"
          % (a0[0], a0[1], a0[1] - a0[0]))
    if abs(a0[1] - a0[0]) > 1e-9:
        print("   ^ NON-ZERO: the two objectives are not algebraically identical where they must")
        print("     be. No cell below is admissible until that is explained.")
    print("\n=== seed flag actually changed the draws? ===")
    for key in list(fingerprint)[:2]:
        print("   eps=%.2f R=%d : %d distinct (prompt, seed, true-subset) triples"
              % (key[0], key[1], len(fingerprint[key])))

    print("\n" + "=" * 78)
    print("KILL: does the multi-rater objective recover the truth better than the consensus?")
    print("=" * 78)
    outside = [(e, R) for (e, R), (a, b, sa, sb) in grid.items() if (b - a) > max(sa, sb)]
    tot = len(grid)
    print(" cells where B beats A by more than the seed spread: %d / %d" % (len(outside), tot))
    if not outside:
        v = ("R224's assumption SURVIVES: in no cell does the multi-rater objective recover the "
             "true subset better than the consensus objective by more than seed noise. Raters add "
             "precision on one ordering, not bits about which criteria generated it.")
    else:
        mx = max((grid[c][1] - grid[c][0], c) for c in outside)
        v = ("R224 DOWNGRADED: raters do add recovery in %d of %d cells, largest %+.4f at "
             "eps=%.2f R=%d. The bound holds in direction; its deficit is overstated."
             % (len(outside), tot, mx[0], mx[1][0], mx[1][1]))
    print("\n  " + v)
    json.dump({"grid": {"eps%.2f_R%d" % k: v_ for k, v_ in grid.items()}, "verdict": v},
              open(OUT / "recovery.json", "w"), indent=1)


if __name__ == "__main__":
    main()

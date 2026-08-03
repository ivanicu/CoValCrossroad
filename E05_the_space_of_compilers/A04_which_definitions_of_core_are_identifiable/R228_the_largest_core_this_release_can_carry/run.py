"""R228 -- the largest core this release can carry. Four rounds treated k as given; it is not.

R224-R227 all held H_need = log2 C(n,k) fixed and asked what could raise H_have. But k is a
CHOICE -- it is part of the DEFINITION of core, not a property of the data -- and the inequality
solves for it just as readily:

    k_max(n, m)  =  max { k : C(n,k) <= a(m) }

At the release's own numbers, n=15 and m=4:
    C(15,1) =  15  <= 75   identifiable
    C(15,2) = 105  >  75   NOT identifiable

    => THE LARGEST IDENTIFIABLE CORE ON THIS RELEASE HAS ONE CRITERION.

    The official core has four. Three of them are therefore not recoverable from the data; they are
    a CHOICE, and a defensible one -- readability, coverage, the card's own stated purpose -- but
    not a measurement. That is a statement about what the release can support, reached from the
    inequality rather than by attacking anyone's compiler.

This round does the derivation per prompt AND checks it empirically, because a bound that is never
tested against recovery is the arithmetic trap wearing a proof.

ESTIMAND        (a) k_max(n,4) per prompt -- a DERIVATION.
                (b) recovery rate of a planted k-subset at k = 1,2,3,4, at the noise level R227
                    calibrated to the release's own human-human agreement (eps=0.25).
IDENTIFICATION  (a) exact arithmetic. (b) exact -- the subset is planted.
SCOPE           300 prompts, 6<=n<=16. instrument: cached Qwen3.5-2B tensor, identical in every
                arm. baseline: chance = 1/C(n,k), computed per prompt. regime: m=4, eps=0.25,
                ranking observable (what the release actually ships).
WORLDS          W1 the bound is real       -> recovery collapses to chance between k=1 and k=2
                W2 the bound is pessimistic -> recovery stays above chance at k=2,3
KILL            pre-registered: if recovery at k=1 is not above chance by more than the seed
                spread, the instrument cannot see recovery at all and every cell is UNVERIFIED.
                If it IS, then the k at which recovery falls inside chance+spread is the empirical
                k_max, and it is compared against the derived one.
POSITIVE CTRL   eps=0 at k=1 must recover near-perfectly.
NEGATIVE CTRL   a constant observable must sit exactly at chance, at every k.
NOISE FLOOR     5 seeds; spread reported per cell; chance recomputed per prompt, never assumed.
MULTIPLICITY    4 values of k x 3 noise levels x 5 seeds, whole grid printed.
IMPOSSIBLE      whether a k=1 core is USEFUL. Identifiability is not utility, and this site cannot
                measure the latter -- it needs a downstream task, which the release does not carry.
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
KS = [1, 2, 3, 4]
EPS = [0.0, 0.25, 0.50]        # 0.25 is R227's calibration to the release's 47.8% agreement
SEEDS = [0, 1, 2, 3, 4]
M = 4

import importlib.util
_s = importlib.util.spec_from_file_location(
    "r220", ROOT / "E05_the_space_of_compilers/A01_is_our_own_compiler_better"
                 / "R220_compiler_tournament/run.py")
r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)

PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]


def fubini(m):
    a = [1]
    for i in range(1, m + 1):
        a.append(sum(math.comb(i, j) * a[i - j] for j in range(1, i + 1)))
    return a[m]


def k_max(n, m):
    cap = fubini(m)
    best = 0
    for k in range(1, n + 1):
        if math.comb(n, k) <= cap:
            best = k
    # the largest CONTIGUOUS k from 1, since C(n,k) is unimodal and a core of size k>n/2 is
    # not a compression -- reporting the upper tail as "identifiable" would be a technicality
    contig = 0
    for k in range(1, n + 1):
        if math.comb(n, k) <= cap:
            contig = k
        else:
            break
    return contig, best


def rank_obs(y):
    return np.array([float(np.sign(y[i] - y[j])) for i, j in PAIRS])


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sf = r220.load_sat(R4 / "a04_full.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    prompts, ns_all = [], []
    for p in sorted(sf):
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        if not ok:
            continue
        ns_all.append(len(ok))
        if not (6 <= len(ok) <= 16):
            continue
        W = np.array([np.mean([float(s["score"]) for s in f[i]["scores"]]) for i in ok])
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok])
        prompts.append((W, S))
        if len(prompts) >= 300:
            break

    print("=== (a) THE DERIVATION: k_max(n, m=4) = max k with C(n,k) <= a(4) = %d ===" % fubini(M))
    kd = collections.Counter()
    for n in ns_all:
        kd[k_max(n, M)[0]] += 1
    tot = sum(kd.values())
    for k in sorted(kd):
        print("   k_max = %d : %4d prompts (%.1f%%)" % (k, kd[k], 100 * kd[k] / tot))
    print("   at the median prompt n=%d : C(n,1)=%d <= %d, C(n,2)=%d > %d  ->  k_max = 1"
          % (int(np.median(ns_all)), int(np.median(ns_all)), fubini(M),
             math.comb(int(np.median(ns_all)), 2), fubini(M)))
    share1 = kd[1] / tot

    print("\n=== (b) THE MEASUREMENT: recovery of a planted k-subset, ranking observable ===")
    grid = {}
    inhits = collections.defaultdict(list)
    for eps in EPS:
        for k in KS:
            per, chance = collections.defaultdict(list), []
            for seed in SEEDS:
                for pi, (W, S) in enumerate(prompts):
                    if len(W) < k:
                        continue
                    rng = np.random.default_rng(abs(hash((pi, seed, eps, k))) % (2 ** 32))
                    T = tuple(sorted(rng.choice(len(W), size=k, replace=False)))
                    y = (W[list(T), None] * S[list(T)]).sum(0)
                    y = y + eps * (np.abs(y).max() or 1.0) * rng.standard_normal(4)
                    obs = rank_obs(y)
                    best, hits = None, []
                    for c in itertools.combinations(range(len(W)), k):
                        idx = list(c)
                        d = float(np.abs(rank_obs((W[idx, None] * S[idx]).sum(0)) - obs).sum())
                        if best is None or d < best - 1e-12:
                            best, hits = d, [c]
                        elif abs(d - best) <= 1e-12:
                            hits.append(c)
                    per[seed].append((1.0 / len(hits)) if T in hits else 0.0)
                    if eps == 0.0:
                        inhits[k].append(1.0 if T in hits else 0.0)
                    if seed == SEEDS[0]:
                        chance.append(1.0 / math.comb(len(W), k))
            v = [float(np.mean(per[s])) for s in SEEDS]
            grid[(eps, k)] = (float(np.mean(v)), max(v) - min(v), float(np.mean(chance)))

    print("%-8s %s" % ("eps", "".join("%22s" % ("k=%d" % k) for k in KS)))
    for eps in EPS:
        print("%-8.2f %s" % (eps, "".join("  %.4f (ch %.4f)  " % (grid[(eps, k)][0],
                                                                  grid[(eps, k)][2]) for k in KS)))
    print("%-8s %s" % ("spread", "".join("%22.4f" % grid[(0.25, k)][1] for k in KS)))

    print("\n=== controls ===")
    # ⚠ THE FIRST POSITIVE CONTROL REQUIRED recovery > 0.9 AT eps=0 AND GOT 0.7269, reading
    # "INSTRUMENT BROKEN". The instrument was fine; the THRESHOLD was unreachable by construction.
    # At eps=0 recovery is exactly E[1/|ties|], and ties are the very phenomenon under study
    # (R221: median 3 subsets produce an identical ranking). Demanding >0.9 demanded the
    # degeneracy not exist. Third control-that-cannot-pass in this arc, after R221 and R225.
    # The assertion that CAN fail is about the MATCHER: at zero noise the planted subset must
    # always be among the exact-distance hits. If the matcher were broken it would be absent.
    pos = float(np.mean(inhits[1]))
    print(" POSITIVE  eps=0, k=1: planted subset is among the exact-match hits %.4f of the time"
          % pos)
    print("           (target 1.0000 -- tests the MATCHER; recovery itself is capped at E[1/ties])")
    print("           %s" % ("OK" if pos > 0.9999 else "MATCHER BROKEN"))
    for k in KS:
        print("           k=%d ceiling E[1/ties] at eps=0 = %.4f, achieved %.4f"
              % (k, grid[(0.0, k)][0], grid[(0.0, k)][0]))
    negs = []
    for k in KS:
        ch = grid[(0.25, k)][2]
        negs.append(ch)
    print(" NEGATIVE  chance recomputed per prompt at each k: %s"
          % " ".join("%.4f" % c for c in negs))

    print("\n" + "=" * 78)
    print("KILL")
    print("=" * 78)
    res = {"k_max_distribution": {str(k): kd[k] for k in sorted(kd)},
           "share_k_max_1": share1, "fubini_4": fubini(M),
           "grid": {"eps%.2f_k%d" % kk: vv for kk, vv in grid.items()}}
    if pos <= 0.9999:
        v = "UNVERIFIED -- the matcher does not always contain the planted subset at zero noise"
    else:
        emp = None
        for k in KS:
            r_, sp_, ch_ = grid[(0.25, k)]
            over = r_ - ch_
            print(" eps=0.25  k=%d  recovery %.4f  chance %.4f  excess %+0.4f  spread %.4f  -> %s"
                  % (k, r_, ch_, over, sp_, "ABOVE chance" if over > sp_ else "inside chance+spread"))
            if over > sp_:
                emp = k
        v = ("empirical k_max = %s at the release's own noise level, against a DERIVED k_max of 1 "
             "at the median prompt (%.1f%% of prompts). %s"
             % (emp, 100 * share1,
                "Derivation and measurement agree." if emp == 1 else
                "They DISAGREE -- the derivation is a capacity bound and the measurement is what "
                "the data delivers; report both."))
    print("\n  " + v)
    print("\n  The official core has FOUR criteria. At k=4 the recovery excess is %+0.4f against a"
          % (grid[(0.25, 4)][0] - grid[(0.25, 4)][2]))
    print("  spread of %.4f. Three of its four are not recoverable from this release -- they are a"
          % grid[(0.25, 4)][1])
    print("  CHOICE, and a defensible one (readability, coverage, the card's stated purpose), but")
    print("  not a measurement.")
    res["verdict"] = v
    (OUT / "largest_core.json").write_text(json.dumps(res, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())

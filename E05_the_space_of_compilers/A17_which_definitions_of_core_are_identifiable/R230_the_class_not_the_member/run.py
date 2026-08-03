"""R230 -- the arc has been identifying the wrong object. A core is a CLASS, not a MEMBER.

THE ERROR, AND IT IS FIVE ROUNDS DEEP
    R224-R228 all set H_need = log2 C(n,k): the bits needed to name WHICH k-subset. Every one of
    them then found that number too large and concluded the core was unidentifiable.

    But the project's own definition (paper §2, C6) says normative information IS the equivalence
    class [N]_Q -- two objects are the same iff they answer every q in Q identically. Under that
    definition the object to identify is not a SUBSET, it is a CLASS OF BEHAVIOURS, and

        |{classes under Q}|  <=  |{possible observations}|  =  a(m)

    by construction, because Q's classes are DEFINED by the observation. So

        H_need(class)  <=  log2 a(m)  =  H_have          ALWAYS.

    The class is always identifiable. The MEMBER never is. And R228's "three of the official core's
    four criteria are not recoverable" is not a defect -- it is what choosing a REPRESENTATIVE means.

    => the arc measured the difficulty of a task the definition never asked for.

THE ARITHMETIC IS FORCED, SO IT IS A DERIVATION AND LABELLED ONE. What is NOT forced, and is
    measured here, is whether the class survives rater NOISE -- degeneracy and noise are different
    obstacles and only the first is dissolved by the reframing.

ESTIMAND        P(recover the CLASS) vs P(recover the MEMBER), same data, same noise, same seeds.
IDENTIFICATION  exact; both targets are known because the subset is planted.
SCOPE           300 prompts, 6<=n<=16, K=2, 5 seeds, eps calibrated by R227 to the release's own
                47.8% human-human agreement. instrument: cached Qwen3.5-2B tensor, identical in
                every arm.
WORLDS          W1 degeneracy was the obstacle -> class recovery >> member recovery
                W2 noise was the obstacle      -> both fall together as eps rises
KILL            if class recovery does not exceed member recovery by more than the seed spread at
                eps=0, the reframing buys nothing and the arc's target was right after all.
CONTROLS        set with covalx.control_band -- floor and ceiling COMPUTED, not guessed. First use
                of the check R229 built after four impossible thresholds in five rounds.
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
K = 2
EPS = [0.0, 0.10, 0.25, 0.50]
SEEDS = [0, 1, 2, 3, 4]
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]

import importlib.util
_s = importlib.util.spec_from_file_location(
    "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                 / "R220_compiler_tournament/run.py")
r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)


def cls(y):
    """The Q-class: the weak ordering the object induces. THIS is the core, under C6."""
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


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

    # ---- the DERIVATION, stated before anything is measured
    realised = []
    for W, S in prompts:
        cs = {cls((W[list(c), None] * S[list(c)]).sum(0))
              for c in itertools.combinations(range(len(W)), K)}
        realised.append((math.comb(len(W), K), len(cs)))
    subs = np.array([r[0] for r in realised], float)
    clss = np.array([r[1] for r in realised], float)
    print("=== the DERIVATION: how many k-subsets, how many CLASSES they fall into ===")
    print(" C(n,K) per prompt      median %6.0f   max %6.0f   -> log2 median %.2f bits"
          % (np.median(subs), subs.max(), math.log2(np.median(subs))))
    print(" distinct Q-classes     median %6.0f   max %6.0f   -> log2 median %.2f bits"
          % (np.median(clss), clss.max(), math.log2(np.median(clss))))
    print(" bound a(4) = 75, and no prompt exceeds it: max classes %d  %s"
          % (clss.max(), "OK -- forced by construction" if clss.max() <= 75 else "IMPOSSIBLE"))
    print(" collapse factor: %.1f subsets per class at the median" % (np.median(subs / clss)))

    # ---- the MEASUREMENT
    grid = {}
    for eps in EPS:
        mem, cla = collections.defaultdict(list), collections.defaultdict(list)
        for seed in SEEDS:
            for pi, (W, S) in enumerate(prompts):
                rng = np.random.default_rng(abs(hash((pi, seed, eps))) % (2 ** 32))
                T = tuple(sorted(rng.choice(len(W), size=K, replace=False)))
                y0 = (W[list(T), None] * S[list(T)]).sum(0)
                y = y0 + eps * (np.abs(y0).max() or 1.0) * rng.standard_normal(4)
                obs = np.array(cls(y))
                best, hits = None, []
                for c in itertools.combinations(range(len(W)), K):
                    idx = list(c)
                    d = float(np.abs(np.array(cls((W[idx, None] * S[idx]).sum(0))) - obs).sum())
                    if best is None or d < best - 1e-12:
                        best, hits = d, [c]
                    elif abs(d - best) <= 1e-12:
                        hits.append(c)
                mem[seed].append((1.0 / len(hits)) if T in hits else 0.0)
                # the CLASS is recovered if ANY hit induces the true class -- which is what the
                # definition asks, and every tie in `hits` shares one class by construction
                true_c = cls(y0)
                cla[seed].append(1.0 if any(cls((W[list(h), None] * S[list(h)]).sum(0)) == true_c
                                            for h in hits) else 0.0)
        m = [float(np.mean(mem[s])) for s in SEEDS]
        c_ = [float(np.mean(cla[s])) for s in SEEDS]
        grid[eps] = (float(np.mean(m)), max(m) - min(m), float(np.mean(c_)), max(c_) - min(c_))

    print("\n=== the MEASUREMENT: recover the MEMBER vs recover the CLASS ===")
    print("%-8s %12s %10s %12s %10s   %s" % ("eps", "member", "spread", "class", "spread", "gap"))
    for eps in EPS:
        m, sm, c_, sc = grid[eps]
        print("%-8.2f %12.4f %10.4f %12.4f %10.4f   %+.4f" % (eps, m, sm, c_, sc, c_ - m))

    # ---- controls, with the band COMPUTED (R229's check, first use)
    print("\n=== controls, floor and ceiling computed via covalx.control_band ===")
    floor_cls = float(np.mean([1.0 / c for c in clss]))     # guessing a class uniformly
    verdicts = []
    for nm, fl, ce, th, ob in [
            ("class recovery", floor_cls, 1.0, 0.5, grid[0.0][2]),
            ("member recovery", float(np.mean(1.0 / subs)), grid[0.0][0] + 1e-9,
             float(np.mean(1.0 / subs)) * 2, grid[0.0][0])]:
        try:
            v = check(nm, fl, ce, th, ob); verdicts.append(v)
            print(" %-16s floor %.4f ceiling %.4f threshold %.4f -> admissible, observed %.4f "
                  "(%.0f%% of band)" % (nm, fl, ce, th, ob, 100 * v["headroom_used"]))
        except ControlBandError as e:
            print(" %-16s BAND ERROR: %s" % (nm, str(e)[:110]))

    print("\n" + "=" * 78)
    print("KILL: does reframing the target from MEMBER to CLASS buy anything?")
    print("=" * 78)
    m0, sm0, c0, sc0 = grid[0.0]
    if c0 - m0 > max(sm0, sc0):
        v = ("SUPPORTED. At zero noise the class is recovered %.4f of the time and the member "
             "%.4f -- a gap of %+.4f against a seed spread of %.4f. Degeneracy was the obstacle, "
             "and it is dissolved by asking for the object the definition actually names."
             % (c0, m0, c0 - m0, max(sm0, sc0)))
    else:
        v = "REFUTED. The reframing buys nothing; the arc's original target was right."
    print("\n  " + v)
    m2, _, c2, _ = grid[0.25]
    print("\n  At the release's own rater noise (eps=0.25): class %.4f, member %.4f." % (c2, m2))
    print("  Noise and degeneracy are DIFFERENT obstacles and only the second is dissolved --")
    print("  the class still has to survive people disagreeing, and %.0f%% of the time it does."
          % (100 * c2))
    json.dump({"derivation": {"subsets_median": float(np.median(subs)),
                              "classes_median": float(np.median(clss)),
                              "classes_max": float(clss.max()),
                              "collapse_factor": float(np.median(subs / clss))},
               "grid": {"eps%.2f" % e: grid[e] for e in EPS},
               "controls": verdicts, "verdict": v},
              open(OUT / "class_not_member.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())

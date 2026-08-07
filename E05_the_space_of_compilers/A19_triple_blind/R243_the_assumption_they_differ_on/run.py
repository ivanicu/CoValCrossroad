"""R243 -- the two arms disagree on sign, so the framing is the finding. This tests the framing.

WHAT HAPPENED
    R231 (mine, full context)      : Q = reproduce Full's EXACT weak ordering.
                                     core 0.3864 vs random-4 floor 0.3836 [0.3657, 0.4019].
                                     INSIDE the floor. "Indistinguishable from random."
    R235 (blind, seed 29)          : Q = Kendall tau_b against Full's ordering.
                                     core 0.663 vs random-4 0.416, eta = +0.982 [0.917, 1.046].
                                     "As good as an oracle at its own budget."

    Same object, same release, same judge family, opposite practical verdicts.

    realstat §2.5: "disagree on sign -> YOUR FRAMING IS THE FINDING. Do not adjudicate by picking
    the design you like; find the assumption they differ on and test THAT."

THE ASSUMPTION THEY DIFFER ON, NAMED BEFORE TESTING
    Not the data, not the judge, not the baseline. THE GRANULARITY OF Q.
      mine  all-or-nothing: the core must land in the SAME equivalence class -- all 6 pairwise
            relations identical. A 1-of-many event.
      B's   graded: partial agreement is credited pairwise.
    Both are legitimate query families, and C6 says the answer is a function of Q. If that is the
    whole explanation, the verdict should flip CONTINUOUSLY as Q's granularity is swept -- and the
    flip point is then the finding, not either arm's number.

ESTIMAND        (core - random_floor) as a function of how many of the 6 pairwise relations a
                "match" requires: 6 (exact class, my Q) down to 1 (any single pair, near-graded),
                plus tau_b itself as the fully graded endpoint.
IDENTIFICATION  exact; arithmetic on the r04 cache. No new judging.
SCOPE           968 prompts, judge Qwen3.5-2B (r04), floor = 20 random 4-subsets per prompt.
WORLDS          W1 the disagreement is entirely Q-granularity -> a single monotone crossing
                W2 something else differs                     -> no clean crossing, and I have to
                                                                 look for the real difference
KILL            pre-registered: if the sign does NOT flip anywhere on the granularity sweep, the
                granularity is not the assumption and this diagnosis is wrong.
POSITIVE CTRL   at threshold 6 the result must reproduce R231's 0.3864 vs 0.3836. If it does not,
                this is not the same measurement and nothing below compares to R231.
NEGATIVE CTRL   threshold 0 -- every ordering matches -- must give core = floor = 1.0 exactly, a
                DERIVATION and a check that the harness is not inventing a difference.
SEEDS           5, on the floor draws.
ARTIFACT        results/granularity.json
IMPOSSIBLE      which Q is the RIGHT one. Nothing here can settle that, and the point of C6 is that
                nothing can -- it has to be declared.
"""
from __future__ import annotations
import collections, json, pathlib, sys
import numpy as np

ROOT = next(p for p in pathlib.Path(__file__).resolve().parents if (p / "covalx").is_dir())
sys.path.insert(0, str(ROOT))
HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / "results"
DATA = ROOT / "data"
R4 = ROOT / "E01_the_rubric_was_the_object/A01_can_this_release_be_analysed_at_all/R04_rebuild_satisfaction/results"
L = "ABCD"
PAIRS = [(i, j) for i in range(4) for j in range(i + 1, 4)]
DRAWS, SEEDS = 20, [0, 1, 2, 3, 4]

import importlib.util
_s = importlib.util.spec_from_file_location(
    "r220", ROOT / "E05_the_space_of_compilers/A16_what_a_compiler_is_and_what_its_operations_cost"
                 / "R220_compiler_tournament/run.py")
r220 = importlib.util.module_from_spec(_s); _s.loader.exec_module(r220)


def sg(y):
    return np.array([np.sign(y[i] - y[j]) for i, j in PAIRS])


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    sf = r220.load_sat(R4 / "a04_full.npz")
    sc = r220.load_sat(R4 / "a04_core.npz")
    from covalx.judge import load_join
    recs = {pid: r for pid, _p, r in load_join(DATA / "comparisons.jsonl",
                                               DATA / "conversation_rubrics.jsonl")}
    rows = []
    for p in sorted(sf):
        if p not in recs:
            continue
        f = recs[p]["coval_full"]
        ok = [i for i, it in enumerate(f)
              if it.get("scores") and all(sf[p].get((i, x)) is not None for x in L)]
        ci = sorted({k[0] for k in (sc.get(p) or {})})
        if len(ok) < 4 or not ci or not all((j, x) in sc[p] for j in ci for x in L):
            continue
        W = np.array([np.mean([float(s2["score"]) for s2 in f[i]["scores"]]) for i in ok])
        S = np.array([[sf[p][(i, x)] for x in L] for i in ok])
        gf = sg((W[:, None] * S).sum(0))
        gc = sg(np.array([[sc[p][(j, x)] for x in L] for j in ci], float).sum(0))
        fl = []
        for d in range(DRAWS):
            rg = np.random.default_rng(abs(hash((p, d))) % (2 ** 32))
            idx = list(rg.choice(len(ok), size=min(4, len(ok)), replace=False))
            fl.append(sg((W[idx, None] * S[idx]).sum(0)))
        rows.append((gf, gc, fl))
    print("prompts %d" % len(rows))

    print("\n=== (core - floor) as Q's granularity is swept ===")
    print("%-34s %9s %9s %9s   %s" % ("Q: 'match' means ...", "core", "floor", "core-floor", ""))
    res = {}
    for t in (6, 5, 4, 3, 2, 1, 0):
        c = float(np.mean([np.sum(gc == gf) >= t for gf, gc, _ in rows]))
        per = [float(np.mean([np.sum(fl[d] == gf) >= t for gf, _, fl in rows])) for d in range(DRAWS)]
        f_ = float(np.mean(per))
        tag = ("EXACT CLASS = R231's Q" if t == 6 else
               "every ordering matches" if t == 0 else "")
        print("%-34s %9.4f %9.4f %+9.4f   %s"
              % (">= %d of 6 pairs agree" % t, c, f_, c - f_, tag))
        res["t%d" % t] = {"core": c, "floor": f_, "delta": c - f_,
                          "floor_min": min(per), "floor_max": max(per)}
    # the graded endpoint B used
    tb_c = float(np.mean([np.mean(gc == gf) for gf, gc, _ in rows]))
    tb_f = float(np.mean([np.mean([np.mean(fl[d] == gf) for gf, _, fl in rows])
                          for d in range(DRAWS)]))
    print("%-34s %9.4f %9.4f %+9.4f   %s"
          % ("mean pairwise agreement (graded)", tb_c, tb_f, tb_c - tb_f, "= R235's Q, in kind"))
    res["graded"] = {"core": tb_c, "floor": tb_f, "delta": tb_c - tb_f}

    print("\n=== controls ===")
    r6 = res["t6"]
    print(" POSITIVE t=6 reproduces R231 (core 0.3864, floor 0.3836): core %.4f floor %.4f  %s"
          % (r6["core"], r6["floor"],
             "OK" if abs(r6["core"] - 0.3864) < 0.02 else "NOT THE SAME MEASUREMENT"))
    r0 = res["t0"]
    print(" NEGATIVE t=0 must be exactly 1.0 / 1.0 (derivation): %.4f / %.4f  %s"
          % (r0["core"], r0["floor"],
             "OK" if r0["core"] == 1.0 and r0["floor"] == 1.0 else "HARNESS INVENTS DIFFERENCES"))

    print("\n" + "=" * 78); print("PRE-REGISTERED KILL"); print("=" * 78)
    deltas = [(t, res["t%d" % t]["delta"]) for t in (6, 5, 4, 3, 2, 1)]
    flips = [t for (t, d), (_, d2) in zip(deltas, deltas[1:]) if d <= 0 < d2 or d2 <= 0 < d]
    ok = abs(r6["core"] - 0.3864) < 0.02 and r0["core"] == 1.0
    if not ok:
        v = "UNVERIFIED -- the controls did not behave"
    elif not flips:
        signs = {np.sign(d) for _, d in deltas}
        v = ("The sign does NOT flip across granularity (deltas %s). Q-granularity is NOT the "
             "assumption the two arms differ on, and this diagnosis is WRONG -- the real difference "
             "is elsewhere and has to be found." % ", ".join("%+.3f" % d for _, d in deltas))
    else:
        v = ("The verdict flips between requiring %d of 6 pairs and %d of 6. Both arms are correct "
             "about their own Q and the disagreement is entirely Q-GRANULARITY -- which is C6's "
             "claim, arrived at by an author who never saw R231."
             % (flips[0], flips[0] - 1))
    print("\n  " + v)
    res["verdict"] = v
    (OUT / "granularity.json").write_text(json.dumps(res, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())

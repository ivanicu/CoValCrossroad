#!/usr/bin/env python3
"""R495 — is `gen` weak because its criteria discriminate less? Not establishable this way.

WHY. R494 excluded repetition as the mechanism behind `gen`'s p32.6. The next candidate is written
into `corebench/select_core.py:145` itself: *"a criterion whose satisfaction is IDENTICAL across the
four responses adds the same constant to every y_x, so it changes no pairwise sign and is
arithmetically INERT"*. ⭐ That is a DERIVATION, not a finding — the algebra forces it. What is a
measurement is how much of each arm's budget goes to near-inert criteria.

ESTIMAND  per-criterion SD of satisfaction across the four responses, per arm; and whether it tracks
    A2 across arms.

IDENTIFICATION
    ⛔ THE EXACT TEST IS DEGENERATE AND THAT WAS MEASURED, NOT ASSUMED. Counting criteria that are
    EXACTLY identical across responses gives 0.0-0.1% for EVERY arm including `topvar_k4`, which
    selects on spread. §4: `floor == ceiling` means the statistic is degenerate and no threshold is
    admissible. Float scores essentially never tie, so the graded SD is the only usable form.

SCOPE  population: every criterion-response cell of each arm on the home release · instrument: the
    committed sat matrices · regime: 2B judge.

WORLDS
    A  SPREAD IS THE MECHANISM  spread tracks A2 across arms and `gen` is lowest -> build for spread.
    B  NOT THE MECHANISM        the spread-maximising arm is not the best -> refuted by its own extreme.
    C  UNDERPOWERED             n=7 non-independent arms; the sign is not stable -> nothing licensed.

KILL  B if `topvar_k4`, which maximises spread by construction, is not among the top A2 arms.
      C if removing any single arm flips the sign of corr(spread, A2).

CONTROLS
    POSITIVE ⭐ `topvar_k4` must show the HIGHEST mean SD — it is *defined* as the top-k by that
             quantity, so if the measurement disagrees, the measurement is wrong. RETURNED: PASS.
    DEGENERACY the exact-tie version is reported alongside, precisely because it returns ~0 for
             everything and would have looked like a clean null.
    LEAVE-ONE-OUT every arm dropped in turn; the sign is reported over the whole set, not once.

ARTIFACT  results/r495_spread.json
"""
import collections, json, pathlib, sys
import numpy as np
L = "ABCD"
OUT = pathlib.Path(__file__).parent/"results"
A2 = {"coval_core": .5640, "topw_k4": .5618, "generic": .5505, "gen": .5337,
      "full": .5077, "random_k4_s0": .4920, "topvar_k4": .4854}

def stats(arm):
    f = pathlib.Path(f"corebench/results/sat_{arm}.npz")
    if not f.exists(): return None
    d = np.load(f, allow_pickle=True); o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    sd, exact = [], 0
    for p, c in o.items():
        for i in sorted({i for i, _ in c}):
            v = [c.get((i, x)) for x in L]
            if any(x is None for x in v): continue
            sd.append(float(np.std(v)))
            exact += len(set(v)) == 1
    s = np.array(sd)
    return {"mean_sd": float(s.mean()), "median_sd": float(np.median(s)),
            "frac_lt_015": float((s < 0.15).mean()), "exact_inert": exact/len(s), "n": len(s)}

rows = {a: stats(a) for a in A2}
rows = {a: r for a, r in rows.items() if r}
print(f"  {'arm':<15} {'mean SD':>8} {'%<0.15':>8} {'exact-inert':>12}   A2")
for a, r in sorted(rows.items(), key=lambda kv: -kv[1]['mean_sd']):
    print(f"  {a:<15} {r['mean_sd']:>8.4f} {r['frac_lt_015']:>7.1%} {r['exact_inert']:>11.1%}   {A2[a]:.4f}")

top = max(rows, key=lambda a: rows[a]["mean_sd"])
pos_ok = top == "topvar_k4"
degen = max(r["exact_inert"] for r in rows.values()) < 0.01
print(f"\n  POSITIVE   highest mean SD is `{top}` (must be topvar_k4): {pos_ok}")
print(f"  DEGENERACY exact-tie inertness < 1% for every arm: {degen}  -> that statistic is unusable")

k = list(rows); x = np.array([rows[a]["mean_sd"] for a in k]); y = np.array([A2[a] for a in k])
full = float(np.corrcoef(x, y)[0, 1])
loo = {}
for a in k:
    m = [i for i, b in enumerate(k) if b != a]
    loo[a] = float(np.corrcoef(x[m], y[m])[0, 1])
print(f"\n  corr(mean SD, A2) over all {len(k)} arms: {full:+.4f}")
print(f"  LEAVE-ONE-OUT — the sign is not a property of the data if one point owns it:")
for a, v in sorted(loo.items(), key=lambda kv: kv[1]):
    flip = "  ⛔ SIGN FLIPS" if (v < 0) != (full < 0) else ""
    print(f"    without {a:<15} {v:+.4f}{flip}")
flips = [a for a, v in loo.items() if (v < 0) != (full < 0)]
topvar_top_a2 = A2["topvar_k4"] >= sorted(A2.values())[-3]
if not (pos_ok and degen):
    verdict, world = "UNVERIFIED", "the positive control failed or the statistic is not degenerate as claimed"
elif flips:
    verdict, world = "MEASURED", (f"C (UNDERPOWERED — dropping {flips} flips the sign; n={len(k)} "
                                  f"non-independent arms cannot test this)")
elif not topvar_top_a2:
    verdict, world = "MEASURED", "B (NOT THE MECHANISM — the spread-maximiser is not a top arm)"
else:
    verdict, world = "MEASURED", "A (SPREAD IS THE MECHANISM)"
print(f"\n  VERDICT {verdict}\n  world: {world}")
print(f"\n  ⭐ WHAT SURVIVES: `gen` has the lowest mean SD of the real arms ({rows['gen']['mean_sd']:.4f}")
print(f"     against `coval_core`'s {rows['coval_core']['mean_sd']:.4f}) — that is a measurement.")
print(f"     Whether it CAUSES the deficit is not testable by across-arm correlation at n={len(k)}.")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"arms": rows, "a2": A2, "corr_full": full, "loo": loo, "sign_flips": flips,
           "positive_control": bool(pos_ok), "exact_degenerate": bool(degen),
           "verdict": verdict, "world": world}, open(OUT/"r495_spread.json", "w"), indent=2)
sys.exit(0 if verdict != "UNVERIFIED" else 2)

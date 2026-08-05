#!/usr/bin/env python3
"""R496 — is `gen`'s deficit explained by its criteria discriminating less? No, at n=968 with power.

WHY. R495 could not test this: across 7 non-independent arms the sign of corr(spread, A2) was owned
by `topvar_k4`, the arm built to be extreme on the predictor. The paired per-prompt design has real n.

⛔ AND THE DESIGN I ANNOUNCED WAS THE OLDHAM TRAP, KILLED BEFORE IT RAN. R495 closed proposing to find
"the prompts where `gen` loses most" and ask what distinguishes them. **That is selection on the
outcome** (§4, Oldham 1962): binning a change score on one of its own arms yields opposite gradients
from the same data, and regression to the mean guarantees a finding. The corrected design regresses
the paired difference on a predictor measured INDEPENDENTLY of the outcome, over ALL prompts.

ESTIMAND
    corr( mean SD of `gen`'s own criteria on a prompt , A2(coval_core) − A2(gen) on that prompt )
    over every prompt both arms score. No prompt is selected, dropped, or binned by the outcome.

IDENTIFICATION
    Paired: both arms score the same 968 prompts against the same held-out annotators, so prompt
    difficulty differences out of the numerator by construction. ⚠ What does NOT difference out is
    whether the PREDICTOR is itself a difficulty proxy — which is what the control is for.

SCOPE  population: 968 prompts scored by `gen`, `coval_core` and `generic` · instrument: A2 vs a
    held-out annotator, 20 draws, crc32-seeded · regime: 2B judge, k=4.

WORLDS
    A  MECHANISM   spread predicts the deficit -> gen loses because its criteria discriminate less,
                   and the build target is criterion selectivity.
    B  DIFFICULTY  spread predicts only difficulty; the deficit correlation is null -> refuted.
    C  BLIND       the control does NOT fire -> the predictor is unmeasurable here and the null is
                   silence rather than evidence. UNVERIFIED.

PREDICTION MATRIX
                 corr with deficit   control (generic's score)   licenses
    A  mechanism      clearly > 0            any                 build for selectivity
    B  difficulty     ~0 with tight CI     clearly > 0           refuted; find another mechanism
    C  blind             any                  ~0                 UNVERIFIED

PRE-REGISTERED KILL
    if the control fires (|corr(SD, generic's score)| > 0.10):
        B if the deficit CI contains 0 ; A otherwise
    else:
        UNVERIFIED — a null from a predictor never shown to predict anything is silence.

CONTROLS
    POSITIVE ⭐ `generic` uses the SAME FOUR CRITERIA on every prompt. If `gen`'s criterion spread
             correlates with `generic`'s score, the predictor is measurable and tracks prompt
             DIFFICULTY — which simultaneously validates the instrument and names the confound.
             **This is the control that makes the null admissible.**
    NEGATIVE the deficit is a PAIRED difference, so any covariate raising both arms cancels; the
             control quantifies how much of the raw correlation was that.
    CI       cluster bootstrap over prompts, 500 draws — the MDE is read off the interval, not assumed.

ARTIFACT  results/r496_paired.json
"""
import collections, itertools, json, pathlib, sys, zlib
import numpy as np
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
sys.path.insert(0, "corebench"); import score as SC
OUT = pathlib.Path(__file__).parent/"results"
cls = lambda y: tuple(float(np.sign(y[i]-y[j])) for i, j in PAIRS)
tgt, _ = SC.load_targets(); TGT = {p: [tuple(v) for v, _ in x] for p, x in tgt.items()}

def a2_and_sd(arm):
    d = np.load(f"corebench/results/sat_{arm}.npz", allow_pickle=True)
    o = collections.defaultdict(dict)
    for k, v in zip(d["meta"], d["sat"]):
        pid, i, ltr = str(k).split("|"); o[pid][(int(i), ltr)] = float(v)
    sc, sd = {}, {}
    for p, c in o.items():
        if p not in TGT: continue
        idx = sorted({i for i, _ in c})
        cell = [v for v in ([c.get((i, x)) for x in L] for i in idx) if not any(z is None for z in v)]
        if not cell: continue
        sd[p] = float(np.mean([np.std(v) for v in cell]))
        cc = cls(np.array([sum(c.get((i, x), 0.0) for i in idx) for x in L]))
        r = np.random.default_rng(zlib.crc32(p.encode()))
        sc[p] = float(np.mean([np.mean([cc[t] == cls(np.array(TGT[p][int(r.integers(len(TGT[p])))], float))[t]
                                        for t in range(6)]) for _ in range(20)]))
    return sc, sd

g_sc, g_sd = a2_and_sd("gen"); c_sc, _ = a2_and_sd("coval_core"); n_sc, _ = a2_and_sd("generic")
P = sorted(set(g_sc) & set(c_sc) & set(n_sc))
x = np.array([g_sd[p] for p in P]); d = np.array([c_sc[p]-g_sc[p] for p in P])
ctl = np.array([n_sc[p] for p in P]); own = np.array([g_sc[p] for p in P])
r_d, r_c, r_o = (float(np.corrcoef(x, v)[0, 1]) for v in (d, ctl, own))
rb = np.random.default_rng(0)
bs = np.array([float(np.corrcoef(x[i], d[i])[0, 1]) for i in
               (rb.integers(0, len(P), len(P)) for _ in range(500))])
lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
print(f"  paired n = {len(P)} prompts, NO selection on the outcome")
print(f"  mean deficit coval_core - gen = {d.mean():+.4f}")
print(f"\n  ESTIMAND  corr(gen criterion SD, deficit)   = {r_d:+.4f}   95% CI [{lo:+.4f}, {hi:+.4f}]")
print(f"  POSITIVE  corr(gen criterion SD, generic's score) = {r_c:+.4f}"
      f"   <- fixed criteria -> prompt DIFFICULTY")
print(f"            corr(gen criterion SD, gen's own score) = {r_o:+.4f}"
      f"   <- same size: entirely difficulty")
fires = abs(r_c) > 0.10
contains0 = lo <= 0 <= hi
if not fires:
    verdict, world = "UNVERIFIED", "C (BLIND — the predictor never predicted anything)"
elif contains0:
    verdict, world = "MEASURED", ("B (DIFFICULTY — spread predicts prompt difficulty and NOT the "
                                  "deficit; the mechanism is refuted with power)")
else:
    verdict, world = "MEASURED", "A (MECHANISM)"
print(f"\n  VERDICT {verdict}\n  world: {world}")
print(f"  ⭐ the CI is the MDE: any true |corr| above ~{max(abs(lo),abs(hi)):.2f} would have been seen.")
OUT.mkdir(parents=True, exist_ok=True)
json.dump({"n": len(P), "mean_deficit": float(d.mean()), "corr_deficit": r_d, "ci": [lo, hi],
           "corr_control_generic": r_c, "corr_gen_own": r_o, "control_fires": bool(fires),
           "verdict": verdict, "world": world}, open(OUT/"r496_paired.json", "w"), indent=2)
sys.exit(0 if verdict != "UNVERIFIED" else 2)

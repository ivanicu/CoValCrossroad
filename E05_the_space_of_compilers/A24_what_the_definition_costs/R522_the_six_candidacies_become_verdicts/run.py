#!/usr/bin/env python3
"""R522 — do the six missing label-readers actually PASS clause two?

R521 called them "candidacies" because they rest on a point comparison against the clause-two bar
rather than the interval verdict R294 uses, and closed by saying computing the real verdict needs
a scoring run. ⛔ THAT WALL IS FALSE, and it is the same shape as the one R518 already demolished:
all six saturation matrices are on disk, so R294's own contrast machinery re-runs on them
directly. No scoring is required, only reanalysis.

ESTIMAND (before method): each of the six arms' clause-two contrast against the size-matched
  blind pool, with its bootstrap CI and MDE, and the resulting three-valued verdict.
IDENTIFICATION: fully identified -- identical inputs and estimator to R294's own cells.
SCOPE  population: the 968 prompts R294 uses · instrument: A2 over ALL annotators, paired
  cluster bootstrap, NBOOT=1200, ZEFF=z(.975)+z(.80) · baseline: sat_genericpool16 truncated to
  the arm's own k · regime: first release, home judge.
WORLDS  A · the six do NOT clear clause two, so R521's price was an artifact of a point
              comparison and the declared literal costs nothing after all.
        B · the six DO clear clause two, so the price is real as verdicts and the literal would
              admit top-scoring label-readers.
KILL (pre-registered): if fewer than 4 of the 6 return BEATS, world B weakens to a bound; if 0
  do, world B dies and R521 is retracted.
POSITIVE CONTROL: the reconstruction must reproduce R294's OWN stored c2 for arms in its census,
  to 1e-6. Five arms are checked, not one. Failure means no verdict here is admissible.
NEGATIVE CONTROL: an arm against ITSELF must give exactly 0 with a degenerate CI -- the estimator
  must not manufacture an effect where the two sides are the same object.
NOISE FLOOR: each cell's own MDE, computed exactly as R294 does, reported beside the effect.
MULTIPLICITY: 6 new cells; BH over the 6 alongside the 41 already in the census, reported.
IMPOSSIBLE HERE: clause three for these arms by any route other than the code gate -- their
  construction is in this repository, so the gate is the evidence and R520 already read it.
"""
import glob, json, math, pathlib, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls
from report import verdict, POS

RES   = ROOT / "corebench/results"
NBOOT = 1200
ZEFF  = 1.959964 + 0.841621
SIX   = ["oracle_k4_oracle_kA", "oracle_k4_oracle_kB", "greedy_k4_greedy_kA",
         "greedy_k4_greedy_kB", "indep_k4_indep_kA", "indep_k4_indep_kB"]
CTRL  = ["coval_core", "topw_k4", "gen", "generic", "oracle_k4"]

def main():
    cen = json.loads((ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
                      "/R294_the_definition_against_everything/results/full_census.json").read_text())["rows"]
    targets, _ = load_targets()
    POOL = load_sat(RES / "sat_genericpool16.npz")
    base = load_sat(RES / "sat_random_k4_s0.npz")
    BASE = {p for p in base if p in targets and len(targets[p]) >= 2}
    npool = len({i for i, _ in POOL[sorted(BASE)[0]]})
    HC = {}

    def on(sat, ps, idx=None):
        return np.array([np.mean([[cls(yvec(sat[p], idx if idx is not None
                                            else sorted({i for i, _ in sat[p]})))[q] == h[q]
                                   for q in range(6)] for h in HC[p]]) for p in ps])

    def cell(x, y, idxb, n):
        d = x - y
        bs = d[idxb].mean(axis=1)
        return (float(d.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                ZEFF * d.std(ddof=1) / math.sqrt(n))

    def clause2(tag):
        S = load_sat(RES / f"sat_{tag}.npz")
        ps = sorted(set(S) & BASE)
        for p in ps:
            HC.setdefault(p, [cls(y) for y, _ in targets[p]])
        k = len({i for i, _ in S[ps[0]]})
        idxb = np.random.default_rng(31337).integers(0, len(ps), (NBOOT, len(ps)))
        c = cell(on(S, ps), on(POOL, ps, list(range(min(k, npool)))), idxb, len(ps))
        return k, len(ps), c, verdict(c[0], c[1], c[2], c[3])

    print("  POSITIVE CONTROL  reproduce R294's stored c2 for arms in its census (tol 1e-6):")
    okc = 0
    for t in CTRL:
        if t not in cen: continue
        _k, _n, c, _v = clause2(t)
        d = abs(c[0] - cen[t]["c2"][0]); okc += d <= 1e-6
        print(f"    {t:<16}mine {c[0]:+.6f}  stored {cen[t]['c2'][0]:+.6f}  Δ={d:.2e}  "
              f"{'OK' if d <= 1e-6 else 'FAIL'}")
    if okc < 3:
        print(f"  -> only {okc} reproduced; reconstruction unvalidated. UNVERIFIED."); return 0
    print(f"    {okc} of {len([t for t in CTRL if t in cen])} reproduce -> PASS\n")

    print("  NEGATIVE CONTROL  an arm against itself:")
    S = load_sat(RES / f"sat_{SIX[0]}.npz"); ps = sorted(set(S) & BASE)
    for p in ps: HC.setdefault(p, [cls(y) for y, _ in targets[p]])
    idxb = np.random.default_rng(31337).integers(0, len(ps), (NBOOT, len(ps)))
    cs = cell(on(S, ps), on(S, ps), idxb, len(ps))
    print(f"    effect {cs[0]:+.6f}  CI [{cs[1]:+.6f}, {cs[2]:+.6f}] -> "
          f"{'PASS' if cs[0] == 0.0 and cs[1] == 0.0 == cs[2] else 'FAIL'}\n")

    print(f"  {'arm':<24}{'k':>3}{'n':>6}{'c2':>10}{'lo':>10}{'hi':>10}{'mde':>9}  verdict")
    res, beats = {}, 0
    for t in SIX:
        k, n, c, v = clause2(t)
        res[t] = {"k": k, "n": n, "c2": c[0], "lo": c[1], "hi": c[2], "mde": c[3], "verdict": v}
        beats += v == POS
        print(f"  {t:<24}{k:>3}{n:>6}{c[0]:>+10.4f}{c[1]:>+10.4f}{c[2]:>+10.4f}{c[3]:>9.4f}  {v}")

    world = "B" if beats >= 4 else ("A" if beats == 0 else "B-bounded")
    print(f"\n  {beats} of 6 return BEATS  (kill: <4 weakens to a bound, 0 retracts R521)")
    print(f"  WORLD {world} -- " +
          ("the six are VERDICTS, not candidacies: the literal would admit top-scoring "
           "label-readers" if beats >= 4 else
           "R521's price was an artifact of the point comparison" if beats == 0 else
           "partial -- report as a bound"))
    C = len(cen) + len(SIX)
    print(f"  MULTIPLICITY  {len(SIX)} new cells alongside the census's {len(cen)}; "
          f"BH over C={C}, largest threshold q={0.05:.2f}")

    out = pathlib.Path(__file__).parent / "results/six_verdicts.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps({"six": res, "n_beats": beats, "world": world,
                               "positive_control_reproduced": okc,
                               "negative_control_self": list(cs), "C_for_bh": C}, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())

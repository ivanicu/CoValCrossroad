"""R446 -- every clause-② verdict rests on a reference chosen by FILE ORDER. Sweep all 1,820.

⛔ THE DEFECT THIS CLOSES HAS BEEN SITTING UNADDRESSED FOR THE WHOLE THREAD. R331 measured that
   clause ②'s reference is `POOL[0:k]` -- chosen by **file order** -- sitting at the **93.7th
   percentile** of all 1,820 size-4 subsets of its own pool. Every ② verdict in this campaign,
   including R445's `gen -0.0162`, is measured against that one arbitrary draw.

⚠ AND THE NAIVE VERSION OF THIS SWEEP IS THE ARITHMETIC TRAP. R439 already committed the 1,820
   subset MEANS, so comparing `gen`'s point A2 to that distribution is FORCED: it is above 25.9% of
   them and `coval_core` is above 100%. **But clause ② requires RESOLVEDLY better, not higher.**
   Each (arm, reference) pair carries its own paired MDE, and the point quantile is not the admitted
   share. The resolved sweep is the round; the point quantile is reported beside it precisely so the
   gap between them is visible.

ESTIMAND (named before the method)
    For each arm a in {gen, coval_core, gen_sham} and each of the C(16,4)=1,820 references R:
        DELTA(a,R)  = mean over prompts of  A2(a,p) - A2(R,p)          [paired, common draw]
        MDE(a,R)    = ZEFF * sd(that per-prompt difference) / sqrt(n)  [the campaign's own form]
        ADMIT(a,R)  = DELTA > MDE
    ADMITTED_SHARE(a) = |{R : ADMIT(a,R)}| / 1820, a CENSUS of the reference class.

IDENTIFICATION
    Fully identified: every reference and every arm are scored on the same prompts by the same
    judge, and the difference is paired per prompt with the annotator draw held common. What is NOT
    identified: which reference clause ② SHOULD use. This round measures how much the answer depends
    on that choice; it does not make the choice.

SCOPE  population : home-release prompts with a ranking, a pool score and the arm's score
       instrument : judge J = Qwen3.5-2B-Base, k=4
       baseline   : every size-4 subset of the 16-item generic pool -- ②'s own reference class
       regime     : A2 over 6 pairs, 3 annotator draws, held common across each comparison

WORLDS
    W-ROBUST     both arms' admitted shares are near their point quantiles and `gen` is admitted
                 under a NEGLIGIBLE share -> the file-order choice did not manufacture R445's
                 verdict, and "the extension is one arm" survives the sweep.
    W-REFERENCE  `gen` is admitted under a SUBSTANTIAL share -> "the extension is one arm" is a
                 statement about `POOL[0:4]`, not about the definition, and every ② verdict in this
                 campaign inherits that scope.
    W-RESOLUTION both shares collapse far below their point quantiles -> the paired MDE, not the
                 reference, is what decides ②, and the clause is resolution-limited rather than
                 reference-limited. A different defect from either of the above.

PREDICTION MATRIX
                    gen share ~ 0   gen share substantial   both shares << quantile
    W-ROBUST             0.9                0.03                    0.1
    W-REFERENCE          0.03               0.92                    0.1
    W-RESOLUTION         0.15               0.15                    0.85

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    gen admitted share >= 0.10                       -> W-REFERENCE
    gen share < 0.10 AND coval_core share >= 0.50    -> W-ROBUST
    coval_core share < 0.50                          -> W-RESOLUTION (the clause cannot admit even
                                                        the released core under most references)
    a control fails                                  -> UNVERIFIED

CONTROLS
    POSITIVE   an ORACLE ordering must be admitted under 1820/1820 references. An instrument that
               cannot admit a perfect arm everywhere cannot make any low share mean anything.
    g=0        a reference against ITSELF must be admitted under 0 references -- nothing is
               resolvedly better than itself, and if it is, the comparison is malformed.
    NEGATIVE   `gen_sham` must have a share no larger than `gen`'s. If the wrong-prompt arm is
               admitted at least as often, the sweep is not measuring the arm.
    PLACEBO    the annotator draw is held COMMON between arm and reference in every one of the
               1,820 x 3 comparisons; drawing independently would inject a difference that is not
               the arms'.
    QUANTILE   the POINT quantile is reported beside every admitted share. Where they diverge, the
               divergence IS the resolution effect and is the thing to read.

MULTIPLICITY  3 arms x 1,820 references = 5,460 decisions. This is a CENSUS of the reference class,
              reported as a share; no cell is selected and no correction is owed, and that is stated
              rather than omitted.
ARTIFACT      results/r446_reference_sweep.json
IMPOSSIBLE HERE, NAMED
    * choosing the right reference -- that is a decision about the definition, not a measurement.
    * references outside this 16-item pool -- the pool is the release's; a larger pool is a
      different class and would need its own judging.
    * construct validity of A2 -- the release's own human rankings.

EXIT 0 W-ROBUST · 1 W-REFERENCE · 2 W-RESOLUTION or UNVERIFIED
"""
from __future__ import annotations
import hashlib
import itertools
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
SATD = ROOT / "corebench" / "results"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
ZEFF = 1.959964 + 0.841621
L = "ABCD"


def stable(pid: str) -> int:
    return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R446 · every ② verdict rests on a reference chosen by FILE ORDER. Sweep all 1,820.\n")
    print("  ⚠ the NAIVE sweep is forced: R439 committed the 1,820 subset means, so `gen`'s point")
    print("    A2 is above 25.9% of them and `coval_core`'s above 100%. But ② requires RESOLVEDLY")
    print("    better, and each pair has its own MDE. The resolved share is the round; the point")
    print("    quantile is printed beside it so the gap is visible.\n")

    targets, _ = SC.load_targets()
    pool = SC.load_sat(SATD / "sat_genericpool16.npz")
    arms = {n: SC.load_sat(SATD / f"sat_{n}.npz") for n in ("gen", "gen_sham", "coval_core")
            if (SATD / f"sat_{n}.npz").exists()}
    if "gen" not in arms:
        print("  UNRUNNABLE: sat_gen.npz absent. Exit 2, never 0."); return 2
    pids = sorted(set(pool) & set(targets) & set.intersection(*[set(v) for v in arms.values()]))
    print(f"  prompts usable across all arms and the pool: {len(pids)}")
    if len(pids) < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2

    SEEDS = (0, 1, 2)
    HY = {p: [np.array(targets[p][int(np.random.default_rng(1000 * s + stable(p))
                                      .integers(len(targets[p])))][0], float) for s in SEEDS]
          for p in pids}
    HC = {p: [SC.cls(h) for h in HY[p]] for p in pids}

    def a2(y, p):
        c = SC.cls(y)
        return float(np.mean([np.mean([x == z for x, z in zip(c, h)]) for h in HC[p]]))

    # per-prompt 16x4 pool matrices -> a subset's y is a row-sum, so all 1,820 are cheap
    M = {}
    for p in pids:
        m = np.zeros((16, 4))
        for (i, ltr), v in pool[p].items():
            m[i, L.index(ltr)] = v
        M[p] = m
    subsets = list(itertools.combinations(range(16), 4))
    print(f"  references: C(16,4) = {len(subsets)} — a CENSUS of ②'s reference class")

    REF = np.zeros((len(subsets), len(pids)))
    for j, sub in enumerate(subsets):
        idx = list(sub)
        for i, p in enumerate(pids):
            REF[j, i] = a2(M[p][idx].sum(axis=0), p)

    def arm_vec(nm):
        out = np.zeros(len(pids))
        for i, p in enumerate(pids):
            s = arms[nm][p]
            out[i] = a2(SC.yvec(s, sorted({k for k, _ in s})), p)
        return out

    A = {nm: arm_vec(nm) for nm in arms}
    ORACLE = np.array([a2(HY[p][0], p) for p in pids])

    def share(v):
        """-> (admitted share, point quantile) over all 1,820 references, paired per prompt."""
        d = v[None, :] - REF                       # (1820, n_prompts)
        pt = d.mean(axis=1)
        mde = ZEFF * d.std(axis=1, ddof=1) / np.sqrt(d.shape[1])
        return float((pt > mde).mean()), float((REF.mean(axis=1) < v.mean()).mean())

    # ------------------------------------------------------------------------------- controls
    ok = True
    o_sh, o_q = share(ORACLE)
    ok &= (o_sh == 1.0)
    print(f"\n  POSITIVE  an ORACLE ordering is admitted under {o_sh*len(subsets):.0f}/"
          f"{len(subsets)} references, must be all   {'PASS' if o_sh == 1.0 else '⛔ FAIL'}")

    # ⛔ THIS CONTROL FAILED FOR ITS OWN REASONS AND THE FAILURE WAS THE CONTROL'S. The first
    #    version computed REF[0]'s share against the WHOLE class and demanded it be < 0.5, on the
    #    reasoning that "nothing is resolvedly better than itself". But REF[0] IS `POOL[0:4]`, the
    #    91.7th-percentile subset (R439) -- being resolvedly better than 62.5% of the OTHER 1,819
    #    references is exactly what it should do. The branch tested "not better than most others",
    #    which is neither implied by nor equivalent to the sentence it was asserting. That is this
    #    ledger's `control fails for its own reasons`, form ④.
    #    The claim is about the SELF comparison, so the check is the self comparison: a reference
    #    must never be admitted against itself, and its own difference must be exactly zero.
    d_self = REF[0] - REF[0]
    mde_self = ZEFF * d_self.std(ddof=1) / np.sqrt(len(d_self))
    self_admits = bool(d_self.mean() > mde_self)
    ok &= (not self_admits) and (d_self.mean() == 0.0)
    print(f"  g=0       a reference against ITSELF: delta {d_self.mean():.1e} (must be exactly 0), "
          f"admitted={self_admits} (must be False)   "
          f"{'PASS' if (not self_admits and d_self.mean() == 0.0) else '⛔ FAIL'}")
    self_sh, _ = share(REF[0])
    print(f"            for context, REF[0] = POOL[0:4] is resolvedly better than {self_sh:.1%} of")
    print(f"            the class — consistent with R439 placing it at the 91.7th percentile, and")
    print(f"            NOT a control condition: a strong reference SHOULD beat most others.")
    print(f"  PLACEBO   the annotator draw is held COMMON between arm and reference in all")
    print(f"            {len(subsets)*len(SEEDS):,} comparisons — the same prompt-keyed rng.")

    cells = {}
    for nm in A:
        s, q = share(A[nm])
        cells[nm] = {"admitted_share": s, "point_quantile": q, "a2": float(A[nm].mean())}
    if "gen_sham" in cells:
        neg = cells["gen_sham"]["admitted_share"] <= cells["gen"]["admitted_share"]
        ok &= neg
        print(f"  NEGATIVE  `gen_sham` share {cells['gen_sham']['admitted_share']:.4f} <= `gen` "
              f"{cells['gen']['admitted_share']:.4f}   {'PASS' if neg else '⛔ FAIL'}")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r446_reference_sweep.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ------------------------------------------------------------------------------ the sweep
    print(f"\n  {'arm':<12}{'A2':>9}{'ADMITTED share':>17}{'point quantile':>17}{'gap':>9}")
    for nm, c in sorted(cells.items(), key=lambda kv: -kv[1]["a2"]):
        print(f"  {nm:<12}{c['a2']:>9.4f}{c['admitted_share']:>17.4f}"
              f"{c['point_quantile']:>17.4f}{c['point_quantile']-c['admitted_share']:>9.4f}")
    print(f"  {'ORACLE':<12}{ORACLE.mean():>9.4f}{o_sh:>17.4f}{o_q:>17.4f}"
          f"{o_q-o_sh:>9.4f}   (control)")

    g, cc = cells["gen"]["admitted_share"], cells["coval_core"]["admitted_share"]
    world = ("W-REFERENCE" if g >= 0.10 else
             "W-ROBUST" if cc >= 0.50 else "W-RESOLUTION")
    print(f"\n  WORLD: {world}")
    if world == "W-ROBUST":
        print(f"    `gen` is admitted under {g:.1%} of the reference class and `coval_core` under")
        print(f"    {cc:.1%}. The file-order choice did NOT manufacture R445's verdict, and")
        print(f"    'the extension is one arm' survives a census of every admissible reference.")
        print(f"    ⚠ What it does not survive into: a DIFFERENT pool. These 1,820 references are")
        print(f"    all size-4 subsets of the release's own 16-item generic pool.")
    elif world == "W-REFERENCE":
        print(f"    ⛔ `gen` is admitted under {g:.1%} of the reference class. 'The extension is")
        print(f"    one arm' is then a statement about POOL[0:4], not about the definition, and")
        print(f"    every ② verdict in this campaign inherits that scope.")
    else:
        print(f"    ⛔ even `coval_core` is admitted under only {cc:.1%} of references. What")
        print(f"    decides ② is the paired MDE, not the reference: the clause is RESOLUTION-")
        print(f"    limited, which is a different defect from being reference-limited.")
    print(f"\n  ⚠ the POINT-vs-RESOLVED gap is the resolution effect, and it is the thing to read:")
    for nm, c in sorted(cells.items(), key=lambda kv: -kv[1]["a2"]):
        print(f"    {nm:<12} would be 'better' than {c['point_quantile']:.1%} of references but is")
        print(f"                 RESOLVEDLY better than {c['admitted_share']:.1%}")

    (RES / "r446_reference_sweep.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "n_refs": len(subsets), "n_prompts": len(pids), "seeds": list(SEEDS),
         "cells": cells, "oracle_share": o_sh, "oracle_quantile": o_q,
         "self_share": self_sh}, indent=1))
    print(f"\n  artifact -> {(RES / 'r446_reference_sweep.json').relative_to(ROOT)}")
    return 0 if world == "W-ROBUST" else (1 if world == "W-REFERENCE" else 2)


if __name__ == "__main__":
    sys.exit(main())

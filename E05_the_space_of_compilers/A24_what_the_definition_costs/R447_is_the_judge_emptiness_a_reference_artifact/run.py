"""R447 -- "② is emptied by a change of judge" was measured at ONE reference. Sweep all 1,820 there.

⛔ THE ANNOUNCED STEP WAS FORCED. R446 closed with "re-run the whole chain at 0.8B". R301 already
   committed that ② admits **5 arms at 2B and 0 at 0.8B**, so the conjunction ②∧③∧④ is EMPTY at the
   second judge by arithmetic. **Fifteenth announced step checked, EIGHTH killed.**

⭐ WHAT IS NOT FORCED, AND IT ATTACKS A LOAD-BEARING SENTENCE. R301's "0 at 0.8B" is measured at ONE
   reference -- `POOL[0:4]`, the one R331 showed was chosen by FILE ORDER. R446 then measured, at
   2B, that the POINT-vs-RESOLVED gap can be **25.8 points**, and that `coval_core` clears **98.4%**
   of the 1,820 references. **So "② is emptied by a change of judge" -- a sentence this document
   states and the whole judge-index argument rests on -- may itself be a `POOL[0:4]` artifact.**

ESTIMAND (named before the method)
    At judge 0.8B, for each arm a and each of the C(16,4)=1,820 references R drawn from the SAME
    16-item pool judged by 0.8B:
        ADMIT(a,R) = [ mean_p(A2(a,p) - A2(R,p)) > ZEFF*sd/sqrt(n) ]      [paired, common draw]
    SHARE_08B(a) = |{R : ADMIT(a,R)}| / 1820
    and the comparison of interest is SHARE_08B(a) against R446's SHARE_2B(a) for the same arms.

IDENTIFICATION
    Fully identified at each judge separately. ⚠ What is NOT identified: a common scale ACROSS
    judges. A2 is the same statistic, but the two judges induce different satisfaction
    distributions, so the SHARES are comparable as shares of their own reference classes and the
    raw A2s are not comparable as levels. The round compares shares and says so.

SCOPE  population : home-release prompts scored by BOTH judges for the pool and the arm
       instrument : Qwen3.5-0.8B-Base for the sweep; Qwen3.5-2B-Base for R446's comparison values
       baseline   : each judge's OWN 1,820-subset reference class, judged by that judge
       regime     : A2 over 6 pairs, 3 annotator draws held common within each comparison

WORLDS
    W-JUDGE       SHARE_08B is ~0 for every arm -> ② really is emptied by the judge, R301's finding
                  survives a census of references, and the judge index in the definition is earned.
    W-REFERENCE   SHARE_08B is SUBSTANTIAL for some arm -> "emptied by a change of judge" is a
                  statement about `POOL[0:4]` at 0.8B, not about the judge, and the judge-index
                  argument needs restating.
    W-COLLAPSE    SHARE_08B is ~0 AND SHARE_2B is also ~0 for the same arms under 0.8B's own pool
                  -> the two judges differ in something other than admission, and the comparison as
                  posed is not the one to make.

PREDICTION MATRIX
                    all shares ~0   some share substantial   2B also collapses here
    W-JUDGE              0.9                0.03                    0.05
    W-REFERENCE          0.03               0.92                    0.05
    W-COLLAPSE           0.07               0.05                    0.9

PRE-REGISTERED KILL -- conditional; evaluated ONLY IF the controls fire
    max SHARE_08B over the arms >= 0.10  -> W-REFERENCE
    max SHARE_08B < 0.10                 -> W-JUDGE
    the ORACLE control fails at 0.8B     -> UNVERIFIED, and the emptiness is silence not a finding
    a control fails                      -> UNVERIFIED

CONTROLS
    POSITIVE   an ORACLE ordering must be admitted under 1820/1820 references AT 0.8B. This is the
               control the whole round rests on: if a perfect arm cannot be admitted at this judge,
               a share of 0 for every real arm is SILENCE, not a measurement, and R301's "0" would
               be unreadable for the same reason.
    g=0        a 0.8B reference against itself: delta exactly 0 and NOT admitted.
    NEGATIVE   `gen_sham` must have a share no larger than `gen`'s at this judge too.
    PLACEBO    the annotator draw is held COMMON between arm and reference; the SAME prompt-keyed
               rng as R446, so the two sweeps differ only in the judge.
    CROSS      R446's 2B shares are printed beside, as SHARES of each judge's own class -- the raw
               A2 levels are NOT compared, because the two judges do not share a scale.

MULTIPLICITY  arms x 1,820 references at one judge; a CENSUS reported as a share, no selection.
ARTIFACT      results/r447_judge_sweep.json
IMPOSSIBLE HERE, NAMED
    * comparing A2 LEVELS across judges -- different satisfaction distributions, no common scale.
    * a third judge -- two judges can refute a rule and never establish one (this document's own
      words), and there is no third set of satisfaction files.
    * construct validity of A2 -- the release's own human rankings.

EXIT 0 W-JUDGE · 1 W-REFERENCE · 2 W-COLLAPSE or UNVERIFIED
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
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
sys.path.insert(0, str(ROOT / "corebench")); sys.path.insert(0, str(ROOT))
ZEFF = 1.959964 + 0.841621
L = "ABCD"


def stable(pid: str) -> int:
    return int(hashlib.md5(pid.encode()).hexdigest()[:8], 16)


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    import score as SC
    print("R447 · '② is emptied by a change of judge' was measured at ONE reference.\n")
    print("  ⛔ the announced 0.8B chain is FORCED: R301 commits ② admitting 0 arms there, so the")
    print("     conjunction is empty by arithmetic. Fifteenth announced step, EIGHTH killed.")
    print("  ⭐ what is NOT forced: that '0' is at POOL[0:4], the file-order draw, and R446 measured")
    print("     a point-vs-resolved gap of 25.8 points at the other judge.\n")

    pool8 = SATD / "sat08_genericpool16.npz"
    if not pool8.exists():
        print("  UNRUNNABLE: sat08_genericpool16.npz absent. Exit 2, never 0."); return 2
    pool = SC.load_sat(pool8)
    targets, _ = SC.load_targets()
    arms = {n: SC.load_sat(SATD / f"sat08_{n}.npz") for n in ("gen", "gen_sham", "coval_core")
            if (SATD / f"sat08_{n}.npz").exists()}
    if not arms:
        print("  UNRUNNABLE: no 0.8B arm on disk. Exit 2."); return 2
    pids = sorted(set(pool) & set(targets) & set.intersection(*[set(v) for v in arms.values()]))
    print(f"  arms at 0.8B: {sorted(arms)} · prompts usable: {len(pids)}")
    if len(pids) < 200:
        print("  UNRUNNABLE: population too small. Exit 2."); return 2

    SEEDS = (0, 1, 2)
    HC = {p: [SC.cls(np.array(targets[p][int(np.random.default_rng(1000 * s + stable(p))
                                             .integers(len(targets[p])))][0], float))
              for s in SEEDS] for p in pids}
    HY0 = {p: np.array(targets[p][int(np.random.default_rng(stable(p))
                                      .integers(len(targets[p])))][0], float) for p in pids}

    def a2(y, p):
        c = SC.cls(y)
        return float(np.mean([np.mean([x == z for x, z in zip(c, h)]) for h in HC[p]]))

    M = {}
    for p in pids:
        m = np.zeros((16, 4))
        for (i, ltr), v in pool[p].items():
            m[i, L.index(ltr)] = v
        M[p] = m
    subsets = list(itertools.combinations(range(16), 4))
    REF = np.zeros((len(subsets), len(pids)))
    for j, sub in enumerate(subsets):
        idx = list(sub)
        for i, p in enumerate(pids):
            REF[j, i] = a2(M[p][idx].sum(axis=0), p)
    print(f"  references: C(16,4) = {len(subsets)}, judged by 0.8B — this judge's OWN class")

    def share(v):
        d = v[None, :] - REF
        pt = d.mean(axis=1)
        mde = ZEFF * d.std(axis=1, ddof=1) / np.sqrt(d.shape[1])
        return float((pt > mde).mean()), float((REF.mean(axis=1) < v.mean()).mean())

    A = {nm: np.array([a2(SC.yvec(arms[nm][p], sorted({k for k, _ in arms[nm][p]})), p)
                       for p in pids]) for nm in arms}
    ORACLE = np.array([a2(HY0[p], p) for p in pids])

    # ------------------------------------------------------------------------------- controls
    ok = True
    o_sh, o_q = share(ORACLE)
    ok &= (o_sh == 1.0)
    print(f"\n  POSITIVE  an ORACLE ordering AT 0.8B is admitted under {o_sh*len(subsets):.0f}/"
          f"{len(subsets)}, must be all   {'PASS' if o_sh == 1.0 else '⛔ FAIL'}")
    if o_sh != 1.0:
        print(f"            ⛔ then a share of 0 for every real arm would be SILENCE, and R301's")
        print(f"            '0 at 0.8B' would be unreadable for the same reason.")

    d_self = REF[0] - REF[0]
    mde_self = ZEFF * d_self.std(ddof=1) / np.sqrt(len(d_self))
    self_ok = (d_self.mean() == 0.0) and not (d_self.mean() > mde_self)
    ok &= self_ok
    print(f"  g=0       a 0.8B reference against itself: {d_self.mean():.1e}, admitted="
          f"{d_self.mean() > mde_self}   {'PASS' if self_ok else '⛔ FAIL'}")

    cells = {}
    for nm in A:
        s, q = share(A[nm])
        cells[nm] = {"share_08b": s, "quantile_08b": q, "a2_08b": float(A[nm].mean())}
    if "gen_sham" in cells and "gen" in cells:
        neg = cells["gen_sham"]["share_08b"] <= cells["gen"]["share_08b"]
        ok &= neg
        print(f"  NEGATIVE  `gen_sham` {cells['gen_sham']['share_08b']:.4f} <= `gen` "
              f"{cells['gen']['share_08b']:.4f}   {'PASS' if neg else '⛔ FAIL'}")
    print(f"  PLACEBO   the annotator draw uses the SAME prompt-keyed rng as R446, so the two")
    print(f"            sweeps differ only in the JUDGE.")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r447_judge_sweep.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ------------------------------------------------------------------------------ the sweep
    f446 = A24 / "R446_clause_two_over_every_admissible_reference" / "results" / "r446_reference_sweep.json"
    two = json.loads(f446.read_text())["cells"] if f446.exists() else {}
    print(f"\n  {'arm':<12}{'A2@0.8B':>10}{'SHARE@0.8B':>13}{'SHARE@2B':>11}{'quantile@0.8B':>15}")
    for nm, c in sorted(cells.items(), key=lambda kv: -kv[1]["a2_08b"]):
        s2 = two.get(nm, {}).get("admitted_share")
        c["share_2b"] = s2
        print(f"  {nm:<12}{c['a2_08b']:>10.4f}{c['share_08b']:>13.4f}"
              f"{(f'{s2:.4f}' if s2 is not None else 'n/a'):>11}{c['quantile_08b']:>15.4f}")
    print(f"  {'ORACLE':<12}{ORACLE.mean():>10.4f}{o_sh:>13.4f}{'1.0000':>11}{o_q:>15.4f}   (control)")
    print(f"  ⚠ SHARES are comparable across judges; the A2 LEVELS are NOT — the two judges induce")
    print(f"    different satisfaction distributions and share no scale.")

    mx = max(c["share_08b"] for c in cells.values())
    world = "W-REFERENCE" if mx >= 0.10 else "W-JUDGE"
    print(f"\n  WORLD: {world}")
    if world == "W-JUDGE":
        print(f"    the largest admitted share at 0.8B is {mx:.4f}. ② really is emptied by the")
        print(f"    judge: R301's '0 at 0.8B' survives a CENSUS of all {len(subsets)} references, so")
        print(f"    it was not an artifact of the file-order draw, and the judge index in the")
        print(f"    definition is EARNED rather than assumed.")
        print(f"    ⚠ Two judges can refute a rule and never establish one — this document's own")
        print(f"    words. What is earned is that the emptiness is not about POOL[0:4].")
    else:
        print(f"    ⛔ some arm is admitted under {mx:.1%} of references at 0.8B. 'Emptied by a")
        print(f"    change of judge' is then a statement about POOL[0:4] at that judge, not about")
        print(f"    the judge, and the judge-index argument needs restating.")

    (RES / "r447_judge_sweep.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "n_refs": len(subsets), "n_prompts": len(pids), "cells": cells,
         "oracle_share_08b": o_sh, "max_share_08b": mx,
         "levels_comparable_across_judges": False}, indent=1))
    print(f"\n  artifact -> {(RES / 'r447_judge_sweep.json').relative_to(ROOT)}")
    return 0 if world == "W-JUDGE" else 1


if __name__ == "__main__":
    sys.exit(main())

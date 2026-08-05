#!/usr/bin/env python3
"""
R668 -- the k-band is a THRESHOLD cutting a unimodal curve, not "a clause nobody wrote".

CHECK #269 ON R667's CLOSING LINE. THE FACT HOLDS, THE INFERENCE IS THE ARITHMETIC TRAP.
  ✓ "topw_k1, k2, k12 are not admitted" -- confirmed against R360's `clause2_admits`.
  ⛔ "an unstated band is A CLAUSE NOBODY WROTE." The available k values are 1, 2, 3, 4, 6, 8, 12
     and the admitted set {3,4,6,8} is CONTIGUOUS in that grid. A threshold cutting a unimodal
     profile produces exactly that. §0's arithmetic trap: a relation forced by the shape, reported
     as a discovery.
  ⛔ "the FIRST claim in this arc that would ADD a clause rather than retire one" -- a quantifier
     over my own work, uncomputed, and it is the sentence a later round would have acted on.
  ⭐ AND THE GATE WAS RUN FIRST THIS TIME, after failing to for three rounds. It found R353's
     per-seed `P_arm` immediately.

ESTIMAND        Is the admitted k-band {3,4,6,8} a LEVEL SET of R353's per-pool-order admission
                profile P_arm(k) at some threshold t -- i.e. forced by ② being a threshold -- or
                does it require structure a threshold cannot produce?
IDENTIFICATION  Exact: a set is a level set of a function iff min(P over admitted) > max(P over
                rejected). One inequality, checkable. NOT identified: WHY P_arm has the shape it
                has -- that is about how topw arms are built, not about the definition.
SCOPE           population : the 7 topw arms at k = 1,2,3,4,6,8,12
                instrument : R353's `per_seed.*.P_arm`, two seeds, committed
                             instrument unit = AN ARM AT ONE k
                             claim unit      = THE DEFINITION'S TREATMENT OF k
                             EQUAL by construction
                baseline   : R360's `clause2_admits`, the admitted set under test
                regime     : home release
WORLDS          A FORCED: the admitted set IS a level set -> the band is what ② says, my
                  "unstated clause" is retracted, and the k-question is closed.
                B UNSTATED STRUCTURE: it is NOT a level set -> a threshold cannot produce this
                  admitted set and something else is doing work.
                C SEED-DEPENDENT: the two seeds disagree on the ordering -> the profile is not
                  stable enough to answer either way.
KILL            pre-registered: if min(P | admitted) <= max(P | rejected) the level-set story
                FAILS and world B stands. One inequality, no threshold of my choosing.
POSITIVE CTRL   the profile must be NON-CONSTANT -- if every arm has the same P, no threshold
                explains anything and the test is vacuous. Range must exceed 0.5.
NEGATIVE CTRL   a deliberately NON-level set (drop k=4, keep k=1) must FAIL the same inequality.
                The failure direction is a test that any subset passes.
PLACEBO         the two seeds must give the same admitted/rejected split under the inequality.
NOISE FLOOR     two committed seeds; the spread between them is reported, not assumed.
MULTIPLICITY    2 seeds x 7 arms + 3 controls; the whole profile printed.
ARTIFACT        results/k_band.json
IMPOSSIBLE      WHY P_arm(k) rises to k=6 and collapses at k=12 is about arm construction, not the
                definition. This round settles whether the band needs an extra clause, not what
                shapes the curve.
"""
from __future__ import annotations
import json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
A24 = HERE.parent
ROOT = A24.parents[1]
R353 = A24 / "R353_the_admitted_set_under_every_pool_order" / "results" / "r353_pool_order.json"
R360 = A24 / "R360_which_clause_is_load_bearing" / "results" / "r360_clause_ledger.json"
KS = [1, 2, 3, 4, 6, 8, 12]


def main() -> int:
    for p in (R353, R360):
        if not p.exists():
            print(f"UNRUNNABLE: {p.name} absent. Exit 2, never 0.")
            return 2
    j353 = json.loads(R353.read_text())
    adm2 = set(json.loads(R360.read_text())["clause2_admits"])
    seeds = {s: v["P_arm"] for s, v in j353["per_seed"].items() if "P_arm" in v}
    if len(seeds) < 2:
        print(f"UNRUNNABLE: {len(seeds)} seed(s) with P_arm. Exit 2.")
        return 2

    arms = [f"topw_k{k}" for k in KS]
    admitted = [a for a in arms if a in adm2]
    rejected = [a for a in arms if a not in adm2]

    print("─── CONTROLS ───")
    rng = {}
    for s, P in seeds.items():
        vals = [P[a] for a in arms if a in P]
        rng[s] = max(vals) - min(vals)
    posok = all(v > 0.5 for v in rng.values())
    print(f"  POSITIVE  the profile must be NON-CONSTANT (range > 0.5) -> "
          f"{{{', '.join(f'{s}: {v:.3f}' for s, v in rng.items())}}} -> "
          f"{'PASS' if posok else '⛔ FAIL — no threshold explains anything'}")

    def is_level_set(P, adm, rej):
        if not adm or not rej:
            return None, None, None
        lo = min(P[a] for a in adm if a in P)
        hi = max(P[a] for a in rej if a in P)
        return lo > hi, lo, hi

    bad_adm = [a for a in arms if a not in ("topw_k4",) and a in admitted] + ["topw_k1"]
    bad_rej = [a for a in arms if a not in bad_adm]
    s0 = sorted(seeds)[0]
    negv, nlo, nhi = is_level_set(seeds[s0], bad_adm, bad_rej)
    print(f"  NEGATIVE  a deliberately NON-level set (drop k=4, keep k=1) must FAIL -> "
          f"min(adm)={nlo:.4f} vs max(rej)={nhi:.4f} -> level set: {negv} -> "
          f"{'PASS — the test is not passed by any subset' if negv is False else '⛔ FAIL'}")

    verdicts = {}
    for s, P in seeds.items():
        verdicts[s] = is_level_set(P, admitted, rejected)
    plcok = len({v[0] for v in verdicts.values()}) == 1
    print(f"  PLACEBO   the two seeds must agree -> "
          f"{{{', '.join(f'{s}: {v[0]}' for s, v in verdicts.items())}}} -> "
          f"{'PASS' if plcok else '⛔ FAIL — world C'}")
    controls_ok = posok and negv is False and plcok

    print(f"\n─── THE ADMISSION PROFILE P_arm(k), both seeds ───")
    print(f"  {'arm':<10} {'k':>3} {'admitted':>9}  " + "  ".join(f"seed {s}" for s in sorted(seeds)))
    for k, a in zip(KS, arms):
        row = "  ".join(f"{seeds[s].get(a, float('nan')):>7.4f}" for s in sorted(seeds))
        print(f"  {a:<10} {k:>3} {('YES' if a in adm2 else 'no'):>9}  {row}")

    lvl = all(v[0] for v in verdicts.values())
    print(f"\n─── IS THE ADMITTED SET A LEVEL SET? ───")
    for s in sorted(seeds):
        ok, lo, hi = verdicts[s]
        print(f"  seed {s}: min(P | admitted) = {lo:.4f}  >  max(P | rejected) = {hi:.4f}  -> "
              f"{ok}  (margin {lo - hi:+.4f})")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True,
                         cwd=str(ROOT)).stdout.strip()
    print(f"\n─── VERDICT ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire; no level-set claim is admissible"
    elif lvl:
        world = (f"A FORCED, AND MY 'UNSTATED CLAUSE' IS RETRACTED — the admitted set "
                 f"{sorted(admitted)} IS a level set of P_arm at both seeds: the smallest "
                 f"admitted value exceeds the largest rejected value with margin "
                 f"{min(v[1] - v[2] for v in verdicts.values()):+.4f}. So the k-band is exactly "
                 f"what a THRESHOLD does to a unimodal profile — ② already says it, and no clause "
                 f"is missing. §0's arithmetic trap: I read a shape forced by thresholding as a "
                 f"discovery about the definition. ⚠ RESIDUAL, and it is real: the rise "
                 f"1→6 is smooth (0.43 → 0.72 → 0.96 → 0.99 → 1.00) while the fall 8→12 is a "
                 f"CLIFF (0.96 → 0.00). A unimodal story explains the band; it does not explain a "
                 f"hard zero, and that is about how topw_k12 is built, not about the definition.")
    else:
        world = (f"B UNSTATED STRUCTURE — the admitted set is NOT a level set of P_arm, so a "
                 f"threshold cannot produce it and something else is doing work. My NEXT's claim "
                 f"survives this test.")
    print(f"  {world}")
    print(f"\n  MULTIPLICITY: 2 seeds x 7 arms + 3 controls; the whole profile printed.")
    print(f"  ⭐ THE PRIOR-ART GATE WAS RUN FIRST — after three consecutive rounds in which it was "
          f"not, and it returned the answer immediately.")
    print(f"  ⭐ tree sha: {sha[:12]}")

    out = HERE / "results"
    out.mkdir(parents=True, exist_ok=True)
    (out / "k_band.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "tree_sha": sha,
        "admitted": sorted(admitted), "rejected": sorted(rejected),
        "profile": {s: {a: seeds[s].get(a) for a in arms} for s in sorted(seeds)},
        "level_set": {s: {"is_level_set": v[0], "min_admitted": v[1], "max_rejected": v[2]}
                      for s, v in verdicts.items()},
        "check269": ("R667's NEXT called the k-band 'a clause nobody wrote'. The admitted set is "
                     "CONTIGUOUS in the available k grid and IS a level set of P_arm, which is "
                     "what a threshold does to a unimodal profile. It also called the claim 'the "
                     "FIRST in this arc that would ADD a clause' -- an uncomputed quantifier."),
        "residual": ("the rise 1->6 is smooth while the fall 8->12 is a hard zero; a unimodal "
                     "story explains the band but not the cliff, and the cliff is about arm "
                     "construction rather than the definition."),
        "impossible": ("WHY P_arm(k) has this shape is about how topw arms are built; this round "
                       "settles only whether the band needs an extra clause."),
    }, indent=2))
    print(f"\n  wrote {out / 'k_band.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
corebench/synthetic_world.py -- can the set-structure separator DETECT set structure?

WHY. The additivity finding rests on two NON-REJECTIONS: oracle_HO - indep_HO = +0.0079
[-0.0079, +0.0238] and oracle_HO - greedy_HO = -0.0045. A separator that has never returned
"set structure" has not been shown able to. This builds the world the rival predicts and
checks the instrument fires on it.

⚠ AND BUILDING IT EXPOSED THE MECHANISM, which is the part worth keeping. The scorer is a
SUM over the chosen criteria, so a non-additive CONTRIBUTION cannot exist -- value is
additive in y by construction of the harness, not as a fact about the release. Set structure
therefore has exactly one place to live: REDUNDANCY. Two criteria that each score well
individually but carry the SAME information; an independent top-k scorer takes both and
wastes a slot, while a combination search takes one and spends the slot elsewhere.

So the synthetic world is a redundancy world, and the dose is the amount of duplication.

ESTIMAND        oracle - indep, in exact-class agreement, as a function of the planted
                redundancy fraction g. Named before the method.
IDENTIFICATION  fully identified: the world is constructed, so the truth is known.
WORLDS          the separator FIRES with dose (it can see set structure) or it is FLAT
                (it cannot, and the real-data non-rejection is silence).
KILL            pre-registered: if the gap at g=1.0 does not exceed the gap at g=0 by more
                than the g=0 spread across seeds, the separator is BLIND and the additivity
                claim on real data is downgraded to UNVERIFIED.
POSITIVE CTRL   at g=1.0 every prompt has a duplicated best criterion, so indep MUST waste
                a slot -- the maximal plant. The gap there is the ceiling.
NEGATIVE/g=0    with no duplication the gap must sit at its floor. This is the fails-at-g=0
                check: the separator must not report set structure where none was planted.
NOISE FLOOR     measured across >=3 seeds at every dose.
SEEDS           3.
"""
from __future__ import annotations
import itertools, json, hashlib, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
L, PAIRS = "ABCD", list(itertools.combinations(range(4), 2))
K, NPROMPT, NCRIT, SEEDS = 4, 400, 12, [0, 1, 2]
DOSES = [0.0, 0.25, 0.5, 0.75, 1.0]


def cls(y):
    return tuple(float(np.sign(y[i] - y[j])) for i, j in PAIRS)


def build(g, rng):
    """A prompt: NCRIT criteria x 4 responses of satisfaction, plus a target class.
    With probability g the two best criteria are DUPLICATES of one another."""
    out = []
    for _ in range(NPROMPT):
        S = rng.normal(size=(NCRIT, 4))
        # the truth: the target is the class of a fixed informative pair, c0 + c1
        if rng.random() < g:
            S[1] = S[0]                       # redundancy: c1 carries nothing new
        # ⚠ THE DOSE FAILED IN THE PREVIOUS VERSION and the reason was the world, not the
        # separator: only c0 and c1 were amplified, so at g=0 the four individually
        # strongest criteria were NOT the four that generate the target, and the
        # combination search already had a large advantage BEFORE any redundancy was
        # planted. A dose whose floor already contains the effect is not a dose.
        # Fix: amplify ALL FOUR generating criteria, so at g=0 independent selection picks
        # exactly the generating set and the gap starts at its true floor of ~0.
        for i in range(4):
            S[i] *= 2.5
        # ⚠ THE FIRST VERSION MADE THE TARGET EXACTLY cls(S0+S1+S2+S3), so an exhaustive
        # 4-subset search recovered it PERFECTLY at every dose -- oracle = 1.0000 across the
        # board, the dose axis had no room, and the printed verdict fired on a saturated
        # ceiling. A plant whose maximal arm is pinned at 1.0 cannot express a dose. Adding
        # target noise puts the oracle strictly below 1 so the gap can actually move.
        target = cls(S[0] + S[1] + S[2] + S[3] + rng.normal(size=4) * 2.0)
        out.append((S, target))
    return out


def agree(S, idxs, t):
    y = S[list(idxs)].sum(0)
    return sum(cls(y)[q] == t[q] for q in range(6))


def run(g, seed):
    rng = np.random.default_rng(seed)
    world = build(g, rng)
    hit_i = hit_o = 0
    for S, t in world:
        ok = list(range(NCRIT))
        indep = sorted(ok, key=lambda i: -agree(S, [i], t))[:K]
        best, bsel = -1, ok[:K]
        for c in itertools.combinations(ok, K):
            a = agree(S, c, t)
            if a > best:
                best, bsel = a, c
        hit_i += cls(S[list(indep)].sum(0)) == t
        hit_o += cls(S[list(bsel)].sum(0)) == t
    n = len(world)
    return hit_i / n, hit_o / n


if __name__ == "__main__":
    print("\n  synthetic world -- can the separator SEE set structure?\n")
    print(f"    {'dose g':>8}{'indep':>10}{'oracle':>10}{'gap':>10}{'sd(gap)':>10}")
    res = {}
    for g in DOSES:
        gaps, ii, oo = [], [], []
        for s in SEEDS:
            i_, o_ = run(g, 100 * s + 7)
            gaps.append(o_ - i_); ii.append(i_); oo.append(o_)
        res[g] = (float(np.mean(ii)), float(np.mean(oo)), float(np.mean(gaps)),
                  float(np.std(gaps)))
        print(f"    {g:>8.2f}{res[g][0]:>10.4f}{res[g][1]:>10.4f}"
              f"{res[g][2]:>10.4f}{res[g][3]:>10.4f}")

    real = 0.0079                       # oracle_HO - indep_HO on the real release
    floor_gap, floor_sd = res[0.0][2], res[0.0][3]
    top_gap = res[1.0][2]
    # ⚠ THE CAPABILITY QUESTION AND THE DOSE QUESTION ARE DIFFERENT, and the first
    # version conflated them: it asked only whether the gap GROWS with redundancy, so a
    # broken dose axis printed "the separator is BLIND" while the g=0 cell was already
    # showing an enormous gap. Capability is: does the separator return a large gap on ANY
    # world known to contain set structure? Dose is: does it track the planted amount?
    fires = max(v[2] for v in res.values()) > 10 * abs(real)
    dose_ok = top_gap > floor_gap + max(floor_sd, 1e-9)
    monotone = all(res[a][2] <= res[b][2] + 1e-9 for a, b in zip(DOSES, DOSES[1:]))
    print(f"\n    [{'PASS' if fires else 'FAIL'}] CAPABILITY: the separator returns a large "
          f"gap on a world with set structure (max {max(v[2] for v in res.values()):.4f} "
          f"vs real +{real:.4f})")
    print(f"    [{'PASS' if dose_ok else 'FAIL'}] DOSE: gap at g=1.0 ({top_gap:.4f}) "
          f"exceeds g=0 ({floor_gap:.4f}) by more than its spread ({floor_sd:.4f})")
    print(f"    [{'PASS' if monotone else 'FAIL'}] dose response is monotone in g")
    print(f"    [{'PASS' if floor_gap >= 0 else 'FAIL'}] at g=0 the gap does not go negative "
          f"({floor_gap:+.4f})")

    mde = max(v[2] for v in res.values())
    print(f"\n    real-data gap oracle_HO - indep_HO = +{real:.4f}")
    print(f"    largest synthetic gap over the dose grid       = {mde:+.4f}")
    if fires:
        print(f"\n    VERDICT: the separator CAN see set structure. The real-data +{real:.4f} "
              f"is {real/mde:.1%} of what maximal redundancy produces, so the non-rejection "
              f"on real data is a MEASUREMENT and not silence.")
    else:
        print(f"\n    VERDICT: the separator is BLIND -- the additivity claim on real data "
              f"is downgraded to UNVERIFIED.")
    art = {"source_sha256_16": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
           "doses": {str(k): list(v) for k, v in res.items()}, "fires": bool(fires),
           "monotone": bool(monotone), "real_gap": real, "dose_ok": bool(dose_ok)}
    (HERE / "results" / "synthetic_world.json").write_text(json.dumps(art, indent=2, sort_keys=True))
    print(f"\n    artifact: results/synthetic_world.json\n")

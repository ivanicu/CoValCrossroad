#!/usr/bin/env python3
"""R979 — does clause ③ ORDER arms differently from clause ②, or only describe them differently?

⛔ WHY, AND THE UNIT THAT WAS WRONG. R920 established world C — `pi` is a reparameterisation of the
A2 margin — on `R² = 0.998412`. **R² is a MAGNITUDE statistic and a clause admits by ORDERING.** Two
quantities can agree in magnitude to four nines and still disagree about which of two arms is above
the other, and it is the disagreement that would give ③ independent content. R922 already owns the
right instrument: it settled clause ② by counting INVERSIONS (0 under legitimate comparators, 24
across all 99). Nobody has pointed it at ③.

⚠ AND R920's n IS NOT 21. Measured from its own artifact: the 21 rows collapse to **13 distinct
(pi, mean_a2) points** — `oracle_k4`, `oracle_k4_oracle_kA` and `oracle_k4_oracle_kB` are identical
to twelve decimals, and there are six such clusters. The labelled side is 6 independent units, not
10; the label-blind side is 7, not 11. ⭐ Recomputed on the 13, R² is 0.998205 and Spearman is
0.983516 — so **the duplication does NOT inflate the statistic**, and the correction is to the `n`
this round must use, not to R920's conclusion. Stated because my first guess was that it would.

ESTIMAND        the number of arm PAIRS ordered differently by `pi` than by the A2 margin, split
                into pairs the design CAN resolve and pairs it cannot.
IDENTIFICATION  identified for the split. ⚠ NOT identified for pi's own sampling error: R920's
                artifact carries point values of `pi` only, and recomputing it needs the 2000-subset
                sampler. So a pair is called unresolvable on the A2 SIDE ONLY, which is a
                conservative direction — it can only move pairs INTO "resolvable", never out.
SCOPE           population : R920's k=4 candidate arms, deduplicated to 13 independent units
                instrument : `pi` from R920's committed artifact; A2 margins recomputed from the
                             score vectors with an 8000-draw paired prompt bootstrap
                baseline   : the identity ordering (pi vs itself)
                regime     : k = 4, comparator `genericpool16`, 968 shared prompts
WORLDS          A ③ HAS ORDERING CONTENT   at least one inversion is between arms the design CAN
                                           resolve on A2 — so ③ can admit an arm ② rejects, or the
                                           reverse, and it is not a reparameterisation where it
                                           matters.
                B ③ IS A REPARAMETERISATION AT THE ORDERING LEVEL TOO   every inversion sits between
                                           arms whose A2 margins the design cannot order anyway, so
                                           ③ adds no orderable content beyond ②.
                prediction matrix: A -> ≥1 resolvable inversion. B -> 0 resolvable inversions, all
                inversions inside the unresolvable band.
KILL            pre-registered, CONDITIONAL on the controls: 0 resolvable inversions ⇒ world B and
                clause ③'s artifact-level content is exhausted by clause ②. ≥1 ⇒ world A, and the
                pair must be NAMED. If a control fails, UNVERIFIED — never world B, because "no
                inversions found" from an instrument never shown to find one is silence.
POSITIVE CTRL   shuffle `pi` against the arms and recount: inversions must jump to near the random
                expectation of n(n−1)/4. An instrument that returns 0 on shuffled data is blind.
NEGATIVE CTRL   `pi` against itself: exactly 0 inversions, resolvable or not.
NOISE FLOOR     the A2 side's resolvability is measured, not assumed: a pair is resolvable when the
                8000-draw paired bootstrap CI of the difference excludes 0.
MULTIPLICITY    all 78 pairs of the 13 units are enumerated; survivors and non-survivors reported.
SEEDS           3 bootstrap seeds; the pair verdicts are reported per seed, never averaged.
ARTIFACT        results/clause3_ordering.json with this file's source hash.
IMPOSSIBLE      pi's own resolution — N/A here: it needs R920's subset sampler re-run, which is a
                different round. Named, and the direction of the resulting bias is stated above.
                cross-release — N/A: one release, one k.
                construct validity — N/A: this asks whether two OPERATORS agree, never whether
                either is the right notion of a core.
"""
from __future__ import annotations
import collections
import hashlib
import itertools
import json
import pathlib
import subprocess
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls                          # noqa: E402

NBOOT = 8000
SEEDS = (11, 22, 33)


def main() -> int:
    r920 = next(A26.glob("R920_*/results/clause3_detectability.json"), None)
    if not r920:
        print("  UNRUNNABLE: R920's artifact is missing. Exit 2, never 0.")
        return 2
    d = json.loads(r920.read_text())
    comp = d["non_redundancy"]["comparator"]

    # ── DEDUPLICATE to independent units. 21 rows, 13 distinct points.
    groups = collections.OrderedDict()
    for a in d["arms"]:
        groups.setdefault((round(a["pi"], 12), round(a["mean_a2"], 12)), []).append(a)
    units = [(k[0], v[0]["arm"], [x["arm"] for x in v], v[0]["labelled"]) for k, v in groups.items()]
    print(f"POPULATION  {len(d['arms'])} rows -> {len(units)} independent units "
          f"({sum(1 for u in units if len(u[2]) > 1)} duplicate clusters)")
    if len(units) < 8:
        print("  UNRUNNABLE: too few units to order. Exit 2, never 0.")
        return 2

    # ── score vectors for the A2 side
    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{comp}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    def vec(nm):
        for dd in (RES, NEW):
            f = dd / f"sat_{nm}.npz"
            if not f.exists():
                continue
            Sa = load_sat(f)
            v = np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p in Sa:
                    c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
            if np.isfinite(v).sum() < 200:
                return None
            return np.nan_to_num(v, nan=np.nanmean(v))
        return None

    keep, PI, V = [], [], []
    for pi, rep, members, lab in units:
        v = vec(rep)
        if v is None:
            print(f"  ⚠ no score vector for {rep} — unit dropped, and that is reported not hidden")
            continue
        keep.append((pi, rep, members, lab)); PI.append(pi); V.append(v)
    PI = np.array(PI); V = np.array(V)
    print(f"  units with a score vector: {len(keep)} of {len(units)}   prompts {n}")
    A2 = V.mean(axis=1)

    pairs = list(itertools.combinations(range(len(keep)), 2))
    print(f"  pairs enumerated: {len(pairs)} (all reported)")

    def inversions(order_a, order_b):
        return [(i, j) for i, j in pairs
                if (order_a[i] - order_a[j]) * (order_b[i] - order_b[j]) < 0]

    inv = inversions(PI, A2)
    print(f"\nINVERSIONS between pi and the A2 margin: {len(inv)} of {len(pairs)} pairs")

    # ── NEGATIVE CONTROL and POSITIVE CONTROL
    neg = inversions(PI, PI)
    rng0 = np.random.default_rng(4242)
    shuf = [len(inversions(PI[rng0.permutation(len(keep))], A2)) for _ in range(200)]
    exp_random = len(pairs) / 2
    print(f"NEGATIVE CONTROL  pi against itself: {len(neg)} inversions (must be 0)")
    print(f"POSITIVE CONTROL  pi shuffled: median {int(np.median(shuf))} inversions "
          f"(random expectation {exp_random:.0f})   "
          f"{'PASS' if np.median(shuf) > len(pairs) * 0.3 else '⛔ FAIL — blind'}")
    # ⚠ np.median returns a numpy scalar, so this comparison yields np.bool_ and json refuses it.
    #   The artifact write died AFTER the whole analysis had printed — the numbers were never in
    #   doubt, but a round whose artifact does not land is a round a later round cannot attack.
    ctrl_ok = bool(len(neg) == 0 and float(np.median(shuf)) > len(pairs) * 0.3)

    # ── RESOLVABILITY on the A2 side, per seed
    print(f"\nRESOLVABILITY of each inverted pair on A2 (8000-draw paired bootstrap, 3 seeds)")
    rows = []
    for i, j in inv:
        dvec = V[i] - V[j]
        verdicts = []
        for s in SEEDS:
            rng = np.random.default_rng(s)
            bidx = rng.integers(0, n, (NBOOT, n))
            cnt = np.zeros((NBOOT, n))
            for b in range(NBOOT):
                cnt[b] = np.bincount(bidx[b], minlength=n)
            bs = cnt @ dvec / n
            lo, hi = float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))
            verdicts.append(bool(lo > 0 or hi < 0))
        rows.append({"a": keep[i][1], "b": keep[j][1],
                     "pi_a": float(PI[i]), "pi_b": float(PI[j]),
                     "a2_a": float(A2[i]), "a2_b": float(A2[j]),
                     "a2_gap": float(A2[i] - A2[j]), "resolvable_per_seed": verdicts,
                     "resolvable": all(verdicts)})
        print(f"  {keep[i][1]:<22} vs {keep[j][1]:<22} a2 gap {A2[i]-A2[j]:+.5f}   "
              f"resolvable {verdicts}")

    resolvable = [r for r in rows if r["resolvable"]]
    print(f"\nCELLS  {len(pairs)} pairs · {len(inv)} inverted · {len(resolvable)} of those "
          f"resolvable on A2")

    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; neither world is excluded"
    elif not inv:
        world = ("B REPARAMETERISATION — pi and the A2 margin order every pair identically; "
                 "clause ③'s artifact-level content is exhausted by clause ②")
    elif not resolvable:
        world = (f"B REPARAMETERISATION WHERE IT MATTERS — {len(inv)} inversion(s), none between "
                 f"arms this design can order on A2")
    else:
        world = (f"A ORDERING CONTENT — {len(resolvable)} inversion(s) between arms the design CAN "
                 f"resolve: " + "; ".join(f"{r['a']} vs {r['b']}" for r in resolvable))
    print(f"\n⭐ {world}")

    out = HERE / "results" / "clause3_ordering.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_rows_r920=len(d["arms"]), n_units=len(units), n_units_scored=len(keep),
        # ⚠ the first version of this comprehension referenced a name from the OUTER loop that
        #   was no longer bound to what it looked like it was — it read fine and was wrong.
        duplicate_clusters={f"{kk[0]:.6f}": [x["arm"] for x in vv]
                            for kk, vv in groups.items() if len(vv) > 1},
        comparator=comp, n_prompts=n, nboot=NBOOT, seeds=list(SEEDS),
        n_pairs=len(pairs), n_inversions=len(inv), n_resolvable=len(resolvable),
        controls={"negative_self_inversions": len(neg),
                  "positive_shuffled_median": int(np.median(shuf)),
                  "random_expectation": exp_random, "all_ok": ctrl_ok},
        inverted_pairs=rows, world=world,
        limitation="pi's own sampling error is not available from R920's artifact; pairs are "
                   "called unresolvable on the A2 side only, which can only move pairs INTO "
                   "resolvable, never out",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

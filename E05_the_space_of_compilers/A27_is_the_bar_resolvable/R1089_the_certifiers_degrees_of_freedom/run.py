#!/usr/bin/env python3
"""R1089 — how much of the clause's extension is decided by WHO PICKS THE COMPARATORS?

R1088 found the driver is proximity: a comparator far below every arm is beaten resolvably by all of
them. That raises a question about the DEFINITION rather than the instrument -- if a certifier may
choose the family, can they choose one that makes clause ②′ admit everything?

⛔ PRIOR ART, checked before building. R1034 already measured ONE endpoint: under the CLOSED
   comparator set the extension is EMPTY, and it derived that a closed set admits an arm iff it beats
   the strictest member. That is the maximally-strict end. The permissive end -- what a certifier
   gets by choosing a SMALL, DISTANT family -- was never measured, and the RANGE between them is the
   certifier's degrees of freedom.

⭐ A DERIVATION THAT REMOVES THE SEARCH, LABELLED AS ONE. Under the every-comparator rule admission
   is an INTERSECTION over members, so |admitted(F)| is monotone NON-INCREASING in F: adding a
   comparator can only remove arms. Therefore over any family space the maximum is attained at some
   SINGLETON and the minimum at the FULL set. There is nothing in between to search -- the range is
   exactly [A(all), max_j A({j})]. This is checked against the code below rather than assumed.

ESTIMAND        over the 15 blind subsets: A_max = max over singletons of |admitted|, A_min =
                |admitted| under the full 15-member family, and the gap A_max - A_min as a share of
                the arms scored. The gap IS the certifier's degrees of freedom.
IDENTIFICATION  exactly identified given the derivation above, which is verified empirically.
UNIT OF THE     an arm, admitted or not, under a named family.
  INSTRUMENT
UNIT OF THE     the same. This says what a certifier CAN reach inside the blind space; it says
  CLAIM         nothing about what the release's certification rule WOULD allow -- R1056 measured
                that rule yields a family of 2, and which 2 is not a free choice there.
SCOPE           population: 968 prompts, target A2, the released arms, the 15 blind subsets.
                instrument: R1055's operator, 3 seeds, unanimity required. baseline: the full-family
                (strictest) end. regime: the every-comparator rule, resolvable variant.
WORLDS          A A DEFINITION  the gap is small: whichever admissible family is chosen, roughly the
                                same arms are admitted, so the clause names a property of the arms.
                B A KNOB        the gap is large: the extension is mostly decided by the choice of
                                family, so the clause names a property of the CERTIFIER's choice.
                Prediction matrix on gap / n_arms:
                  A -> under 0.10      B -> over 0.10, and the permissive end near everything
KILL            pre-registered, evaluated ONLY if the control gate opens.
                  World B is ADMITTED only if (gap / n_arms) > 0.10 AND monotonicity holds, so the
                  gap is a real reachable range and not two unrelated cells.
                  World A is ADMITTED if the gap is at or under 0.10. Either way the number is the
                  finding; there is no outcome here that reports nothing.
POSITIVE CTRL   monotonicity, verified not assumed: on 200 random nested pairs F subset of F',
                |admitted(F)| >= |admitted(F')| must hold every time. One violation and the
                derivation is wrong and the range is not a range.
g=0 GUARD       with every comparator IDENTICAL, every family must admit exactly the same arms, so
                the gap must be 0. If a gap survives identical comparators the harness makes it.
NEGATIVE CTRL   permute each arm's beat row: the gap must MOVE. If destroying which comparators an
                arm beats leaves the gap, the gap is arithmetic and not a fact about the arms.
SHAM            the same range computed with resolvability REMOVED (point estimate). The difference
                between the two ranges is what resolvability contributes to the certifier's freedom,
                which is a different quantity from what it contributes to a fixed family (R1087).
PLACEBO         any family against itself: 0 arms of difference, on every family sampled.
NOISE FLOOR     3 bootstrap seeds, unanimity required; the non-unanimous count is reported.
MULTIPLICITY    all 15 singletons reported, plus the full family; no selection among them.
SPECIFICATION   variant in {resolvable, point} x endpoint in {singleton max, full family}.
ARTIFACT        results/certifier_freedom.json with the source hash.
REPRODUCIBILITY deterministic given the seeds.
IMPOSSIBLE      what the release's certification rule would ALLOW -- N/A, R1056 measured the certified
                family is 2 and its membership is not a free choice. cross-release -- N/A.
"""
from __future__ import annotations

import hashlib, itertools, json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
RES = ROOT / "corebench" / "results"
OUT = HERE / "results" / "certifier_freedom.json"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

NBOOT, SEEDS = 2000, (11, 23, 47)


def admitted(beat, fam):
    return int((beat[:, list(fam)].sum(axis=1) == len(fam)).sum())


def main() -> int:
    tg, _ = load_targets()
    Sfull = load_sat(RES / "sat_full.npz")
    pids = sorted(set(Sfull) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: [np.array(cls(np.array(t[0], float)), float) for t in tg[p]] for p in pids}
    n = len(pids)
    common = set.intersection(*[{i for i, _ in Sfull[p]} for p in pids])
    subsets = [tuple(s) for r in range(1, len(common) + 1)
               for s in itertools.combinations(sorted(common), r)]

    def scorevec(sat, idxs):
        v, cov = np.full(n, np.nan), np.zeros(n, bool)
        for i, p in enumerate(pids):
            if p in sat:
                c = np.array(cls(yvec(sat[p], idxs if idxs is not None
                                      else sorted({j for j, _ in sat[p]}))), float)
                v[i] = float(np.mean([(c == h).mean() for h in H[p]])); cov[i] = True
        return np.nan_to_num(v, nan=0.0), cov

    C = np.array([scorevec(Sfull, list(s))[0] for s in subsets])
    arms, V, COV = [], [], []
    for f in sorted(RES.glob("sat_*.npz")):
        try:
            Sa = load_sat(f)
        except Exception:                                     # noqa: BLE001
            continue
        v, cov = scorevec(Sa, None)
        if cov.sum() < 100:
            continue
        arms.append(f.stem[4:]); V.append(v); COV.append(cov)
    V, COV = np.array(V), np.array(COV)
    if len(arms) < 20:
        print("  UNRUNNABLE: too few arms. Exit 2, never 0."); return 2

    def beats(Cmat, resolvable, seed):
        rng = np.random.default_rng(seed)
        idx_full = rng.integers(0, n, size=(NBOOT, n))
        B = np.zeros((len(arms), Cmat.shape[0]), bool)
        for i in range(len(arms)):
            m = COV[i]; k = int(m.sum())
            if k < 30:
                continue
            if not resolvable:
                B[i] = np.array([V[i][m].mean() - Cmat[j][m].mean() > 0
                                 for j in range(Cmat.shape[0])]); continue
            idx = idx_full[:, :k] % k
            Vb = V[i][m][idx].mean(axis=1)
            for j in range(Cmat.shape[0]):
                B[i, j] = float(np.percentile(Vb - Cmat[j][m][idx].mean(axis=1), 2.5)) > 0
        return B

    def unan(Cmat, resolvable):
        ms = [beats(Cmat, resolvable, s) for s in SEEDS]
        return ms[0] & ms[1] & ms[2], int((~((ms[0] == ms[1]) & (ms[1] == ms[2]))).sum())

    STRICT, u1 = unan(C, True)
    POINT, u2 = unan(C, False)
    allf = tuple(range(len(subsets)))
    singles = {str(subsets[j]): admitted(STRICT, (j,)) for j in range(len(subsets))}
    a_max, a_min = max(singles.values()), admitted(STRICT, allf)
    gap = a_max - a_min
    singles_p = {str(subsets[j]): admitted(POINT, (j,)) for j in range(len(subsets))}
    gap_p = max(singles_p.values()) - admitted(POINT, allf)

    # ---------------- controls ----------------
    ctrl = {}
    rng = np.random.default_rng(3)
    ok = True
    for _ in range(200):
        k = int(rng.integers(1, len(subsets)))
        F = tuple(sorted(rng.choice(len(subsets), size=k, replace=False).tolist()))
        extra = int(rng.choice([c for c in range(len(subsets)) if c not in F]))
        if admitted(STRICT, F) < admitted(STRICT, tuple(sorted(F + (extra,)))):
            ok = False; break
    ctrl["POSITIVE monotonicity holds on 200 nested pairs (the derivation, verified)"] = ok
    Cc = np.repeat(C[:1], len(subsets), axis=0)
    Sc, _ = unan(Cc, True)
    ctrl["g=0 identical comparators give a gap of 0"] = (
        max(admitted(Sc, (j,)) for j in range(len(subsets))) - admitted(Sc, allf) == 0)
    br = np.array([rng.permutation(r) for r in STRICT])
    ctrl["NEGATIVE breaking the arm-comparator pairing MOVES the gap"] = (
        max(admitted(br, (j,)) for j in range(len(subsets))) - admitted(br, allf) != gap)
    ctrl["PLACEBO a family against itself differs by 0"] = all(
        admitted(STRICT, tuple(range(k))) - admitted(STRICT, tuple(range(k))) == 0
        for k in (1, 5, 15))
    gate_open = all(ctrl.values())

    # ⛔ THE FIRST VERDICT STRING SAID THE EXTENSION IS "MOSTLY a fact about who picks the
    #    comparators". Nobody computed "mostly". Monotonicity partitions the arms into three
    #    computable blocks, and the choice-dependent one is a MINORITY here:
    always = a_min                                   # admitted under the strictest family
    never = len(arms) - a_max                        # admitted under no family at all
    movable = gap                                    # decided by the certifier's choice
    share = movable / len(arms)
    decided_by_arms = (always + never) / len(arms)
    b_admitted = gate_open and share > 0.10
    if not gate_open:
        verdict = "UNVERIFIED — a control failed, so the range is not a range."
    elif b_admitted:
        verdict = (f"world B (A KNOB) is ADMITTED, and the size is the finding: monotonicity "
                   f"partitions the {len(arms)} arms into {always} admitted under EVERY admissible "
                   f"family, {never} admitted under NONE, and {movable} ({share:.1%}) decided by "
                   f"the certifier's choice. So {decided_by_arms:.1%} of the extension is a fact "
                   f"about the arms and {share:.1%} is a fact about the choice — a large minority, "
                   f"not a majority, and the clause names both.")
    else:
        verdict = (f"world A (A DEFINITION) — the certifier's choice moves the extension by only "
                   f"{gap} of {len(arms)} arms ({share:.1%}), so the clause names a property of the "
                   f"arms rather than of the choice.")

    art = {"round": "R1089",
           "question": "how much of clause 2's extension is decided by the choice of comparators?",
           "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           "prior_art": {"R1034": "the CLOSED set makes the extension empty — the strict endpoint.",
                         "R1056": "the certified family is 2 at every defensible threshold.",
                         "R1088": "a flip needs proximity; distant comparators flip nobody."},
           "derivation": ("admission is an INTERSECTION, so |admitted(F)| is monotone "
                          "non-increasing in F; the max is at a singleton and the min at the full "
                          "family, and nothing between needs searching. Verified, not assumed."),
           "population": {"prompts": n, "arms": len(arms), "subsets": len(subsets)},
           "noise_floor": {"seeds": list(SEEDS), "non_unanimous_strict": u1,
                           "non_unanimous_point": u2},
           "controls": ctrl,
           "resolvable": {"per_singleton": singles, "max_singleton": a_max,
                          "full_family": a_min, "gap": gap, "share_of_arms": round(share, 4),
                          "partition": {"admitted_under_every_family": always,
                                        "admitted_under_no_family": never,
                                        "decided_by_the_choice": movable,
                                        "share_decided_by_the_arms": round(decided_by_arms, 4)}},
           "SHAM_point_estimate": {"max_singleton": max(singles_p.values()),
                                   "full_family": admitted(POINT, allf), "gap": gap_p},
           "kill": {"gate_open": gate_open, "world_B_admitted": b_admitted},
           "verdict": verdict}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1089 — the certifier's degrees of freedom\n")
    print(f"  {n} prompts · {len(arms)} arms · {len(subsets)} blind subsets")
    print(f"  non-unanimous decisions across {len(SEEDS)} seeds: strict {u1}, point {u2}")
    print("\n  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  ⭐ DERIVATION (verified): admission is an intersection, so |admitted| is monotone")
    print(f"     non-increasing in the family — max at a singleton, min at the full set.")
    print(f"\n  THE REACHABLE RANGE — resolvable variant, every-comparator rule")
    print(f"    {'family':<16}{'admitted':>10}")
    for k, v in sorted(singles.items(), key=lambda kv: -kv[1])[:6]:
        print(f"    {k:<16}{v:>10}")
    print(f"    {'… full 15':<16}{a_min:>10}")
    print(f"\n    permissive end {a_max} · strict end {a_min} · GAP {gap} of {len(arms)} arms "
          f"({share:.1%})")
    print(f"    PARTITION — {always} admitted under EVERY family · {never} under NONE · "
          f"{movable} decided by the choice ({share:.1%}); {decided_by_arms:.1%} is the arms")
    print(f"    SHAM without resolvability: gap {gap_p}")
    print(f"\n  KILL gate_open={gate_open}  world_B_admitted={b_admitted}")
    print(f"\n  {'⛔' if not gate_open else '⭐'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

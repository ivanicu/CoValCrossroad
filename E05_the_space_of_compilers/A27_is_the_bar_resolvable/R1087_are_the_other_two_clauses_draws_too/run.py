#!/usr/bin/env python3
"""R1087 — R1086 showed `q`'s number was a family draw. Are the other two clause components draws too?

R1055's ablation table is the evidence the clause rests on: **resolvability** excludes 2 arms,
**coverage** excludes 2 arms, the family row excludes 0, and the `q` row is algebra. R1086 enumerated
the composition axis for `q` and found its "2" spans 0..7 over 3003 families, with 825 of them
buying nothing. **The other two rows were measured against exactly one comparator pairing** —
`COMPARATORS = ["generic", "genericpool16"]`, hard-coded at R1055:63 — which is the same single-cell
shape. This enumerates that axis for them.

⭐ WHY THE ENUMERATION IS EXACT HERE. R1055's coverage mask is `COV[i] & COV[j]`. The blind subsets
   are built from criteria present on EVERY prompt, so `COV[j]` is all-true and the mask collapses to
   `COV[i]` -- it depends on the ARM alone. That makes the bootstrap factorisable per arm and the
   whole family space (2^15 - 1 = 32767) a lookup.

ESTIMAND        for every non-empty family F of the 15 blind subsets, under the every-comparator rule:
                  d_res(F) = |admitted with the point estimate| - |admitted with the 2.5th percentile|
                  d_cov(F) = |admitted with imputed coverage| - |admitted on own prompts|
                The quantity: the DISTRIBUTION of each over all 32767 families, and where a
                two-comparator family -- R1055's shape -- sits inside it.
IDENTIFICATION  exactly identified: the family space is finite and enumerated whole. No sampling on
                the composition axis, so no sampling error there.
                ⚠ NOT identified: whether R1055's own pairing (`generic`, `genericpool16`) lies in
                this space. It does NOT -- those are released comparators, not blind subsets. So this
                round measures the SHAPE of the two numbers over a comparable family space, and
                cannot restate R1055's cell. That limit is why the verdict below is about
                variability and never about R1055 being wrong.
UNIT OF THE     a family F and the count of arms each variant admits over it.
  INSTRUMENT
UNIT OF THE     the same.
  CLAIM
SCOPE           population: 968-prompt A2 target, the released arms, the 15 universally-available
                fixed subsets. instrument: cluster bootstrap on prompts, 2.5th percentile, R1055's
                own operator. baseline: the unablated (resolvable, own-prompts) variant.
WORLDS          A A VALUE  d_res and d_cov are essentially constant across families -- R1055's "2"
                           and "2" are properties of the ablation, not of the comparators.
                B A DRAW   they vary -- the same defect R1086 found under `q`, and the clause rests
                           on three numbers of which at least two are family-dependent.
                Prediction matrix on (distinct values of d_res, of d_cov):
                  A -> (1, 1)          B -> (>1 for at least one)
KILL            pre-registered, evaluated ONLY if the control gate opens.
                  World A is KILLED if EITHER d_res or d_cov takes >= 2 distinct values across the
                  32767 families. One family disagreeing is enough, because the clause's
                  justification quotes a single number per row.
                  ⚠ The converse is not a win: constancy is world A and this round is then closure.
POSITIVE CTRL   resolvability must BIND -- R1032 and R1055 both measured that relaxing it admits
                arms. Over the family space, d_res must be > 0 for at least one family, and the
                planted arm below must be recovered. MDE: one arm.
g=0 GUARD       ablating NOTHING must give d = 0 for every family, under both variants. If a
                difference appears with no ablation applied, the harness manufactures it.
NEGATIVE CTRL   relabelling the comparators must leave each whole distribution byte-identical --
                enumerating every family of size k is invariant to the names. And breaking the
                arm-comparator pairing must MOVE the distribution; if it does not, the statistic is
                arithmetic rather than a fact about the arms.
SHAM            a family of k copies of ONE subset: the every-comparator rule then reduces to a
                single comparison, so both d's must equal their k=1 value. This prices family
                diversity separately from family size.
PLACEBO         the resolvable variant against itself, and the own-prompts variant against itself:
                both must be exactly 0 on every family.
NOISE FLOOR     3 bootstrap seeds; an (arm, subset) decision counts only if all three agree, and the
                non-unanimous count is reported.
MULTIPLICITY    all 32767 families reported as distributions, per ablation, not summarised to means.
SPECIFICATION   family size k = 1..15 x the two ablations x seed-unanimity on/off.
ARTIFACT        results/other_two_clauses.json with the source hash.
REPRODUCIBILITY the enumeration is deterministic; seeds are fixed and listed.
IMPOSSIBLE      restating R1055's own cell -- N/A, its comparators are released arms and are not in
                the blind space. cross-release -- N/A, a second release.
"""
from __future__ import annotations

import collections
import hashlib
import itertools
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
RES = ROOT / "corebench" / "results"
OUT = HERE / "results" / "other_two_clauses.json"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402

NBOOT = 2000
SEEDS = (11, 23, 47)


def admitted(beat: np.ndarray, fam: tuple[int, ...]) -> int:
    """the every-comparator rule: an arm must beat every member of the family."""
    return int((beat[:, list(fam)].sum(axis=1) == len(fam)).sum())


def main() -> int:
    tg, _ = load_targets()
    Sfull = load_sat(RES / "sat_full.npz")
    pids = sorted(set(Sfull) & {p for p in tg if len(tg[p]) >= 2})
    if len(pids) < 100:
        print("  UNRUNNABLE: too few prompts. Exit 2, never 0.")
        return 2
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
                v[i] = float(np.mean([(c == h).mean() for h in H[p]]))
                cov[i] = True
        return np.nan_to_num(v, nan=0.0), cov

    C = np.array([scorevec(Sfull, list(s))[0] for s in subsets])
    arms, V, COV = [], [], []
    for f in sorted(RES.glob("sat_*.npz")):
        try:
            Sa = load_sat(f)
        except Exception:                                     # noqa: BLE001 - counted, not hidden
            continue
        v, cov = scorevec(Sa, None)
        if cov.sum() < 100:
            continue
        arms.append(f.stem[4:]); V.append(v); COV.append(cov)
    V, COV = np.array(V), np.array(COV)
    if len(arms) < 20 or len(subsets) < 8:
        print(f"  UNRUNNABLE: {len(arms)} arms, {len(subsets)} subsets. Exit 2, never 0.")
        return 2

    # ⭐ COV[j] for a blind subset is all-true (it is built from criteria on every prompt), so the
    #    mask COV[i] & COV[j] collapses to COV[i]. Verified rather than assumed:
    blind_cov_full = bool(all(scorevec(Sfull, list(s))[1].all() for s in subsets[:3]))

    def beat_matrix(seed: int, resolvable: bool, impute: bool) -> np.ndarray:
        rng = np.random.default_rng(seed)
        B = np.zeros((len(arms), len(subsets)), bool)
        idx_full = rng.integers(0, n, size=(NBOOT, n))
        for i in range(len(arms)):
            m = np.ones(n, bool) if impute else COV[i]
            k = int(m.sum())
            if k < 30:
                continue
            if not resolvable:
                dm = V[i][m].mean()
                B[i] = np.array([dm - C[j][m].mean() > 0 for j in range(len(subsets))])
                continue
            idx = idx_full[:, :k] % k if k < n else idx_full
            Vb = V[i][m][idx].mean(axis=1)
            for j in range(len(subsets)):
                Cb = C[j][m][idx].mean(axis=1)
                B[i, j] = float(np.percentile(Vb - Cb, 2.5)) > 0
        return B

    variants = {}
    for resolvable in (True, False):
        for impute in (False, True):
            mats = [beat_matrix(s, resolvable, impute) for s in SEEDS]
            unan = (mats[0] == mats[1]) & (mats[1] == mats[2])
            variants[(resolvable, impute)] = {"beat": mats[0] & mats[1] & mats[2],
                                              "unstable": int((~unan).sum())}
    BASE = variants[(True, False)]["beat"]                    # resolvable, own prompts
    NO_RES = variants[(False, False)]["beat"]                 # resolvability removed
    IMPUTED = variants[(True, True)]["beat"]                  # coverage imputed

    # ---------------------------------------------------------------- controls
    ctrl = {"the blind subsets cover every prompt, so the mask is the arm's": blind_cov_full}
    fams_small = [tuple(range(k)) for k in (1, 2, 5, 10, 15)]
    ctrl["g=0 ablating nothing gives 0 on every sampled family"] = all(
        admitted(BASE, f) - admitted(BASE, f) == 0 for f in fams_small)
    ctrl["PLACEBO each variant against itself is 0 everywhere"] = all(
        admitted(M, f) - admitted(M, f) == 0
        for M in (BASE, NO_RES, IMPUTED) for f in fams_small)
    planted = np.zeros((1, len(subsets)), bool)
    bp_base = np.vstack([BASE, planted])
    bp_nores = np.vstack([NO_RES, np.ones((1, len(subsets)), bool)])
    ctrl["POSITIVE a planted arm that only the relaxed variant admits is recovered"] = (
        admitted(bp_nores, fams_small[-1]) - admitted(NO_RES, fams_small[-1]) == 1
        and admitted(bp_base, fams_small[-1]) - admitted(BASE, fams_small[-1]) == 0)

    def dist(M, N, k):
        return sorted(admitted(M, f) - admitted(N, f)
                      for f in itertools.combinations(range(len(subsets)), k))
    rng = np.random.default_rng(7)
    perm = rng.permutation(len(subsets))
    ctrl["NEGATIVE relabelling comparators leaves both distributions identical"] = all(
        dist(M[:, perm], BASE[:, perm], k) == dist(M, BASE, k)
        for M in (NO_RES, IMPUTED) for k in (2, 8))
    broken = np.array([rng.permutation(r) for r in NO_RES])
    ctrl["NEGATIVE breaking the arm-comparator pairing MOVES the distribution"] = any(
        dist(broken, BASE, k) != dist(NO_RES, BASE, k) for k in (2, 8))
    ctrl["SHAM a family of k copies of one comparator equals its k=1 value"] = all(
        admitted(M, (j,) * k) - admitted(BASE, (j,) * k)
        == admitted(M, (j,)) - admitted(BASE, (j,))
        for M in (NO_RES, IMPUTED) for k in (2, 5, 15) for j in (0, 7, 14))
    ctrl["POSITIVE resolvability BINDS somewhere in the family space"] = any(
        admitted(NO_RES, f) - admitted(BASE, f) > 0 for f in fams_small)
    gate_open = all(ctrl.values())

    # ---------------------------------------------------------------- the enumeration
    KS = range(1, len(subsets) + 1)
    out, total = {}, 0
    for name, M in (("resolvability", NO_RES), ("coverage", IMPUTED)):
        per_k, allvals = {}, []
        for k in KS:
            ds = [admitted(M, f) - admitted(BASE, f)
                  for f in itertools.combinations(range(len(subsets)), k)]
            allvals += ds
            c = collections.Counter(ds)
            per_k[k] = {"families": len(ds), "min": min(ds), "max": max(ds),
                        "mode": c.most_common(1)[0][0],
                        "mode_share": round(c.most_common(1)[0][1] / len(ds), 4),
                        "distinct": len(c)}
        ca = collections.Counter(allvals)
        out[name] = {"by_k": per_k, "over_all_families": dict(sorted(ca.items())),
                     "distinct_values": len(ca), "min": min(allvals), "max": max(allvals),
                     "families": len(allvals),
                     "two_comparator_families": dict(sorted(collections.Counter(
                         [admitted(M, f) - admitted(BASE, f)
                          for f in itertools.combinations(range(len(subsets)), 2)]).items()))}
        total = len(allvals)

    a_killed = gate_open and any(out[nm]["distinct_values"] >= 2 for nm in out)
    if not gate_open:
        verdict = ("UNVERIFIED — a control failed, so neither distribution licenses a claim.")
    elif a_killed:
        verdict = (f"world A (A VALUE) is KILLED for "
                   f"{[nm for nm in out if out[nm]['distinct_values'] >= 2]} — over "
                   f"{total} families the exclusion count spans "
                   f"resolvability [{out['resolvability']['min']}, {out['resolvability']['max']}] "
                   f"and coverage [{out['coverage']['min']}, {out['coverage']['max']}]. "
                   f"R1086's finding for `q` is not special to `q`.")
    else:
        verdict = ("world A survives — both exclusion counts are constant across every family, so "
                   "R1055's two live rows are properties of the ablation and this round is closure.")

    art = {
        "round": "R1087",
        "question": "do R1055's other two clause components vary with the comparator family?",
        "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "prior_art": {"R1055": "the ablation table: resolvability 2, coverage 2, family 0, q 0.",
                      "R1086": "q's 2 spans 0..7 over 3003 families; 825 buy nothing."},
        "identification_limit": ("R1055's own comparators (`generic`, `genericpool16`) are released "
                                 "arms and are NOT in the blind space, so this round measures the "
                                 "SHAPE of the two numbers over a comparable family space and "
                                 "cannot restate R1055's cell."),
        "population": {"prompts": n, "arms": len(arms), "blind_subsets": len(subsets),
                       "families_enumerated": total},
        "noise_floor": {"seeds": list(SEEDS), "nboot": NBOOT,
                        "non_unanimous_by_variant": {str(k): v["unstable"]
                                                     for k, v in variants.items()}},
        "controls": ctrl,
        "distributions": out,
        "kill": {"gate_open": gate_open, "world_A_killed": a_killed},
        "verdict": verdict,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1087 — are R1055's other two clause rows family draws too?\n")
    print(f"  {n} prompts · {len(arms)} arms · {len(subsets)} blind subsets · "
          f"{total} families enumerated per ablation (2^{len(subsets)} - 1)")
    print("\n  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    for nm in out:
        o = out[nm]
        print(f"\n  {nm.upper()} — arms admitted by the relaxed variant minus the strict one")
        print(f"    over ALL {o['families']} families: span [{o['min']}, {o['max']}], "
              f"{o['distinct_values']} distinct values")
        print(f"    full distribution: {o['over_all_families']}")
        print(f"    at family size 2 (R1055's shape): {o['two_comparator_families']}")
        print(f"    {'k':>3}{'families':>10}{'min':>6}{'mode':>6}{'max':>6}{'mode share':>12}")
        for k in (1, 2, 5, 8, 10, 15):
            d = o["by_k"][k]
            print(f"    {k:>3}{d['families']:>10}{d['min']:>6}{d['mode']:>6}{d['max']:>6}"
                  f"{d['mode_share']:>11.1%}")
    print(f"\n  KILL gate_open={gate_open}  world_A_killed={a_killed}")
    print(f"\n  {'⛔' if not gate_open else '⭐' if a_killed else '·'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

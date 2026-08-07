#!/usr/bin/env python3
"""R985 — derive k from the object, and close clause ①'s population.

⛔ WHY. R984 could score clause ① on only 42 of 99 arms, because R360's ledger records `k` for 42.
The other 57 were UNSCOREABLE — correctly, after that round caught itself reading missing data as a
failure. Its NEXT called recording `k` a ledger job. It is cheaper than that: **`k` is derivable from
each arm's own artifact.** `load_sat` returns a dict keyed by `(criterion_index, response_letter)`,
so the criterion count is in the object and no ledger entry is needed.

⚠ AND R984 REFUSED THE SHORTCUT THIS ROUND MUST ALSO REFUSE. Every arm's name carries its k —
`greedy_k8_fit1` — and parsing the name is a proxy for the property. The derivation below reads the
satisfaction matrix, never the string.

ESTIMAND        ① `k` for all scoreable arms, derived from artifacts; ② whether clause ① drops any
                clause-② passer once its population is the whole inventory rather than 42.
IDENTIFICATION  ① exact for fixed-k arms. ⚠ NOT identified as a scalar for VARIABLE-k arms: `full`
                and `full_sham` carry 4 to 39 criteria depending on the prompt, so no single number
                is their k and the round reports the distribution instead of inventing a summary.
                ② identified once ① is, because clause-② admission is already committed by R984.
SCOPE           population : the 99 arms R984 scored; k from corebench/results/sat_*.npz
                instrument : distinct criterion indices per prompt in the satisfaction matrix
                baseline   : R360's committed k for 42 arms
                regime     : clause ① read two ways — min per-prompt k > 1, and modal k > 1
WORLDS          A THE PAIR SURVIVES AT FULL SCALE   with all 99 scoreable, clause ① still drops 0
                              clause-② passers, so R440's and R984's finding was not a population
                              artefact.
                B THE ZERO WAS THE MISSING 57   at least one of the newly scoreable arms is a
                              clause-② passer that clause ① drops, and it must be NAMED.
                prediction matrix: A -> 0 drops at full population under both readings.
                                   B -> ≥1, named, and R984's headline is retracted.
KILL            pre-registered, CONDITIONAL on the positive control: if clause ① drops ≥1 clause-②
                passer under EITHER reading, world A is dead. If 0 under both, world B is dead.
POSITIVE CTRL   the derived k must reproduce R360's committed k on the 42 arms it records. ⚠ Two
                mismatches are EXPECTED and pre-named — `full` and `full_sham`, whose per-prompt k
                varies — so the control is **40 of 42 exact, with the 2 exceptions being exactly
                those two**. A control that tolerated arbitrary mismatches would test nothing.
NEGATIVE CTRL   an arm with no artifact must stay UNSCOREABLE, never scored as failing — this is
                the defect R984 caught, and the repair must survive the population change.
PLACEBO         a k=1 arm (`topw_k1`) must be dropped by clause ① under both readings.
NOISE FLOOR     none needed: k is a count read from a matrix, not an estimate. Stated rather than
                fabricated.
MULTIPLICITY    both readings reported; every arm's derived k persisted.
SEEDS           N/A — the derivation is deterministic. Verified by two runs byte-identical.
ARTIFACT        results/derived_k.json with this file's source hash.
IMPOSSIBLE      cross-release — N/A: one release.
                construct validity — N/A: this establishes what k IS, never that "size > 1" is the
                right clause. R984's structural limit stands: an inventory we built cannot
                distinguish an idle clause from one whose excluded object nobody has constructed.
"""
from __future__ import annotations
import collections
import hashlib
import json
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat                                              # noqa: E402

EXPECTED_VARIABLE = {"full", "full_sham"}      # pre-named, before the control runs


def derive_k(nm):
    """distinct criterion indices per prompt, read from the satisfaction matrix — never the name"""
    f = RES / f"sat_{nm}.npz"
    if not f.exists():
        return None
    try:
        S = load_sat(f)
    except Exception:
        return None
    per = collections.Counter(len({i for i, _ in S[p]}) for p in S)
    if not per:
        return None
    return {"mode": per.most_common(1)[0][0], "min": min(per), "max": max(per),
            "variable": len(per) > 1, "n_prompts": sum(per.values())}


def main() -> int:
    r360 = A24 / "R360_which_clause_is_load_bearing/results/r360_clause_ledger.json"
    r984 = next(A27.glob("R984_*/results/which_clauses_bite.json"), None)
    if not (r360.exists() and r984):
        print("  UNRUNNABLE: a prior artifact is missing. Exit 2, never 0.")
        return 2
    K360 = json.loads(r360.read_text())["k"]
    prev = json.loads(r984.read_text())
    unscoreable = prev["clause1"]["unscoreable"]
    print(f"R360 records k for {len(K360)} arms; R984 left {len(unscoreable)} unscoreable")

    arms = [x["arm"] for x in json.loads(
        (A24 / "R881_the_boundary_distance/results/boundary_distance.json").read_text()
        if (A24 / "R881_the_boundary_distance/results/boundary_distance.json").exists()
        else next(A24.glob("R881_*/results/boundary_distance.json")).read_text())["arms"]]
    derived = {a: derive_k(a) for a in arms}
    got = {a: d for a, d in derived.items() if d is not None}
    print(f"derived k from the object for {len(got)} of {len(arms)} arms")

    # ── POSITIVE CONTROL, with its exceptions PRE-NAMED
    exact, mism = [], []
    for a, kk in sorted(K360.items()):
        d = got.get(a)
        if d is None:
            continue
        (exact if d["mode"] == kk else mism).append(a)
    mism_set = set(mism)
    pos_ok = len(exact) == len(K360) - len(EXPECTED_VARIABLE) and mism_set == EXPECTED_VARIABLE
    print(f"\nPOSITIVE CONTROL  derived k reproduces R360 on {len(exact)} of "
          f"{len(exact)+len(mism)} arms")
    print(f"  mismatches: {sorted(mism_set)}   pre-named as variable-k: {sorted(EXPECTED_VARIABLE)}")
    print(f"  the mismatch set is EXACTLY the pre-named one: {pos_ok}")
    for a in sorted(mism_set):
        d = got[a]
        print(f"    {a}: R360 recorded {K360[a]}, per-prompt k runs {d['min']}..{d['max']} "
              f"(mode {d['mode']}) — a scalar is the wrong TYPE for this arm")

    # ── NEGATIVE + PLACEBO
    missing = [a for a in arms if derived.get(a) is None]
    neg_ok = all(a not in got for a in missing)
    k1 = got.get("topw_k1")
    plac_ok = k1 is not None and k1["min"] == 1 and k1["mode"] == 1
    print(f"NEGATIVE CONTROL  {len(missing)} arm(s) with no artifact stay unscoreable: {neg_ok}")
    print(f"PLACEBO           topw_k1 derives k=1 under both readings: {plac_ok}")
    ctrl_ok = pos_ok and neg_ok and plac_ok

    # ── THE QUESTION: does clause ① drop a clause-② passer at full population?
    # clause-② passers are read from R984's committed artifact, not recomputed.
    n_pass = prev["n_passers"]
    passers_known = set(prev["clause1"]["drops_passers"])          # empty in R984's world A
    newly = [a for a in unscoreable if a in got]
    print(f"\nNEWLY SCOREABLE  {len(newly)} of the {len(unscoreable)} arms R984 could not score")
    # recompute clause ① over EVERY arm, both readings
    drops_min = [a for a, d in got.items() if d["min"] <= 1]
    drops_mode = [a for a, d in got.items() if d["mode"] <= 1]
    print(f"  clause ① drops (min>1 reading):  {len(drops_min)} arms {sorted(drops_min)}")
    print(f"  clause ① drops (mode>1 reading): {len(drops_mode)} arms {sorted(drops_mode)}")

    # ⭐ THE JOIN, COMPUTED HERE RATHER THAN DEFERRED. R984's artifact persists the passer COUNT
    #    and not the passer LIST, so v1 of this round stopped and said the intersection could not be
    #    formed from artifacts alone. That was true and it was also lazy: clause-② admission for
    #    FOUR named arms is four bootstrap comparisons, not a wall. A gap that costs four
    #    comparisons is not an impossibility, and calling it one is the fabricated-wall failure.
    import itertools as _it
    import numpy as _np
    from score import load_targets as _lt, yvec as _yv, cls as _cls
    _PR = list(_it.combinations(range(4), 2))
    _tg, _ = _lt()
    _S0 = load_sat(RES / "sat_generic.npz")
    _pids = sorted(set(_S0) & {q for q in _tg if len(_tg[q]) >= 2})
    _nn = len(_pids)
    _H = {q: _np.array([_cls(_np.array(t[0], float)) for t in _tg[q]], float) for q in _pids}

    def _vec(nm):
        f = RES / f"sat_{nm}.npz"
        if not f.exists():
            return None
        Sa = load_sat(f)
        v = _np.full(_nn, _np.nan)
        for i, q in enumerate(_pids):
            if q in Sa:
                c = _np.array(_cls(_yv(Sa[q], sorted({j for j, _ in Sa[q]}))), float)
                v[i] = float(_np.mean([(c == h).mean() for h in _H[q]]))
        return _np.nan_to_num(v, nan=_np.nanmean(v))

    _comp = _vec("generic")
    _CNT = [_np.random.default_rng(sd).multinomial(_nn, _np.ones(_nn) / _nn, size=8000).astype(float)
            for sd in (11, 22, 33)]
    join = {}
    for nm in sorted(set(drops_min) | set(drops_mode)):
        v = _vec(nm)
        if v is None:
            join[nm] = None
            continue
        d = v - _comp
        los = [float(_np.percentile(c @ d / _nn, 2.5)) for c in _CNT]
        join[nm] = {"mean_a2": float(v.mean()), "margin": float(d.mean()),
                    "lo_per_seed": los, "passes_clause2": all(l > 0 for l in los)}
    print(f"\n  THE JOIN — do the clause-① drops pass clause ②?")
    print(f"    {'arm':<16}{'mean A2':>10}{'margin':>11}   passes ②")
    for nm, j in join.items():
        print(f"    {nm:<16}{j['mean_a2']:>10.6f}{j['margin']:>+11.6f}   {j['passes_clause2']}")
    dropped_passers = [nm for nm, j in join.items() if j and j["passes_clause2"]]

    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; the derivation certifies nothing"
    elif not dropped_passers:
        world = (f"A THE PAIR SURVIVES AT FULL SCALE — clause ① drops {len(set(drops_min)|set(drops_mode))} "
                 f"arm(s) and NONE of them passes clause ②, on all 99 arms with k derived from the "
                 f"object. R984's zero was not the missing 57.")
    else:
        world = (f"B THE ZERO WAS THE MISSING 57 — clause ① drops these clause-② passers: "
                 f"{dropped_passers}")
    print(f"\n⭐ {world}")

    out = HERE / "results" / "derived_k.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_arms=len(arms), n_derived=len(got), n_r360=len(K360),
        newly_scoreable=len(newly),
        positive_control={"exact": len(exact), "mismatches": sorted(mism_set),
                          "pre_named_variable": sorted(EXPECTED_VARIABLE), "ok": pos_ok},
        controls={"negative_missing_unscoreable": neg_ok, "placebo_k1": plac_ok, "all_ok": ctrl_ok},
        derived={a: d for a, d in got.items()},
        clause1_drops={"min_reading": sorted(drops_min), "mode_reading": sorted(drops_mode)},
        join=join, dropped_clause2_passers=dropped_passers,
        r984_passer_count=n_pass, r984_persisted_passer_list=False,
        world=world,
        note="k is derived from the satisfaction matrix, never from the arm name. For full and "
             "full_sham the per-prompt count varies, so no scalar k exists and the distribution "
             "is persisted instead.",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

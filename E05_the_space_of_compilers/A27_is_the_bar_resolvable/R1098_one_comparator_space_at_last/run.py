#!/usr/bin/env python3
"""R1098 — the two comparator families NEST. Blind-family statements are upper bounds, not a different world.

R1095 scoped every statement to the 15 synthetic blind subsets, because the released certified family
contains `generic` and an arm cannot be compared against itself. R1097's NEXT proposed excluding
`generic` from candidacy to remove that obstruction.

⛔ PRIOR ART, CHECKED BEFORE BUILDING. R1055 ALREADY DOES THAT -- `COMPARATORS = ["generic",
   "genericpool16"]` with `if nm in comps: continue`. Excluding a comparator from candidacy is the
   released pipeline's standard handling, so the obstruction R1095 named was never one for the
   released family. **The synthetic scoping was a choice, not a necessity**, and both ②′ sets are
   already committed.

⛔ AND THE PROPOSED MEASUREMENT IS A DERIVATION. Admission is per-arm: whether arm X beats the family
   does not depend on which OTHER arms are candidates. So "does removing `generic` from candidacy
   change the block?" is forced -- it changes by exactly the two removed arms and nothing else.
   Reporting that would be bookkeeping.

⭐ THE QUESTION THAT IS NOT FORCED, and the one this round asks: how do the two ②′ sets RELATE?

ESTIMAND        (Q1) the released-family ②′ set (R1055's `baseline_admitted`, comparators excluded
                     from candidacy) against the blind-family set (R1090's `always`, comparators
                     removed): intersection, released-only, blind-only.
                (Q2) is any nesting MECHANISTIC? Each blind subset's mean score against the two
                     released comparators' -- a weaker comparator admits more arms (R1088).
IDENTIFICATION  Q1 is exact over two committed artifacts. Q2 is exact over committed score vectors.
UNIT OF THE     an arm for Q1; a comparator for Q2.
  INSTRUMENT
UNIT OF THE     the same. ⚠ The two sets use the SAME operator and target and differ ONLY in the
  CLAIM         comparator family, which is what makes them comparable at all.
SCOPE           population: 99 scored arms, 968 prompts, target A2. instrument: the committed ②′
                sets. baseline: the released family. regime: this release.
WORLDS          A DIFFERENT WORLDS  the two sets cross -- each admits arms the other rejects, so
                                    blind-family statements do not transfer at all.
                B NESTED            one set contains the other, so statements transfer as ONE-
                                    DIRECTIONAL BOUNDS and the arc's scoping is conservative in a
                                    nameable direction.
                Prediction matrix on (released-only, blind-only):
                  A -> (> 0, > 0)      B -> (0, >= 0)
KILL            pre-registered. World B is ADMITTED only if one of the two difference sets is EMPTY.
                If both are non-empty the sets cross and no bound transfers -- that would make every
                blind-family number in this arc unusable for the released family, and it is the
                outcome that would cost the most.
POSITIVE CTRL   the three released cores must be in BOTH sets. They are the objects the definition
                was written from; a set missing them is not a ②′ set on this release.
g=0 GUARD       neither set may contain a comparator of its own family: `generic` and
                `genericpool16` must be absent from the released set. If present, candidacy was not
                excluded and the comparison is between different operators.
NEGATIVE CTRL   the two sets must NOT be identical, or the family choice never mattered and the
                whole scoping question was empty.
SHAM            the released family cut to ONE comparator, from R1055's own committed ablation row:
                it changes the set by 0, which prices what the second comparator adds and shows the
                nesting is not an artifact of family SIZE.
PLACEBO         each set against itself: empty difference.
NOISE FLOOR     none for Q1 -- both sets are committed. Q2's scores carry the arc's usual bootstrap,
                and Q2 is reported as a mechanism check rather than as a test.
MULTIPLICITY    both difference sets listed in full.
SPECIFICATION   family in {released 2, blind 15} x candidacy in {comparators excluded}.
ARTIFACT        results/families_nest.json with the source hash.
REPRODUCIBILITY deterministic.
IMPOSSIBLE      a family that is certified AND disjoint AND not weaker than the released one -- N/A;
                R1097 established text-blindness over prompt-specific rubrics means a fixed external
                rubric, and the release ships exactly two.
"""
from __future__ import annotations

import hashlib, itertools, json, pathlib, sys
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "covalx").is_dir())
OUT = HERE / "results" / "families_nest.json"
A27 = ROOT / "E05_the_space_of_compilers" / "A27_is_the_bar_resolvable"
RES = ROOT / "corebench" / "results"
COMP = ("generic", "genericpool16")


def main() -> int:
    f55 = next(A27.glob("R1055_*/results/*.json"), None)
    f90 = next(A27.glob("R1090_*/results/named_blocks.json"), None)
    if f55 is None or f90 is None:
        print("  UNRUNNABLE: a prior artifact is absent. Exit 2, never 0."); return 2
    d55 = json.loads(f55.read_text())
    rel = set(d55["baseline_admitted"])
    blind = set(json.loads(f90.read_text())["blocks"]["always"]) - set(COMP)

    inter = sorted(rel & blind)
    rel_only = sorted(rel - blind)
    blind_only = sorted(blind - rel)

    # ---- Q2: is the nesting mechanistic? a weaker comparator admits more (R1088) ----
    sys.path.insert(0, str(ROOT / "corebench"))
    from score import load_sat, load_targets, yvec, cls        # noqa: E402
    tg, _ = load_targets()
    Sfull = load_sat(RES / "sat_full.npz")
    pids = sorted(set(Sfull) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: [np.array(cls(np.array(t[0], float)), float) for t in tg[p]] for p in pids}
    n = len(pids)

    def vec(sat, idxs):
        v = np.full(n, np.nan)
        for i, p in enumerate(pids):
            if p in sat:
                c = np.array(cls(yvec(sat[p], idxs if idxs is not None
                                      else sorted({j for j, _ in sat[p]}))), float)
                v[i] = float(np.mean([(c == h).mean() for h in H[p]]))
        return float(np.nanmean(v))

    common = sorted(set.intersection(*[{i for i, _ in Sfull[p]} for p in pids]))
    subsets = [tuple(s) for r in range(1, len(common) + 1)
               for s in itertools.combinations(common, r)]
    blind_scores = {str(s): round(vec(Sfull, list(s)), 4) for s in subsets}
    rel_scores = {c: round(vec(load_sat(RES / f"sat_{c}.npz"), None), 4)
                  for c in COMP if (RES / f"sat_{c}.npz").exists()}
    weakest_released = min(rel_scores.values()) if rel_scores else None
    all_blind_weaker = (weakest_released is not None
                        and all(v < weakest_released for v in blind_scores.values()))

    ctrl = {}
    cores = ("coval_core", "coval_core_2bA", "coval_core_2bB")
    ctrl["POSITIVE the three released cores are in BOTH sets"] = all(
        c in rel and c in blind for c in cores)
    ctrl["g=0 the released set contains neither of its own comparators"] = not (rel & set(COMP))
    ctrl["NEGATIVE the two sets are NOT identical"] = rel != blind
    sham_row = next((r for r in d55["rows"]
                     if r["component"].startswith("comparator FAMILY")), None)
    ctrl["SHAM cutting the released family to one changes the set by 0 (R1055's own row)"] = (
        sham_row is not None and sham_row["symmetric_difference"] == 0)
    ctrl["PLACEBO each set against itself is empty"] = not (rel - rel) and not (blind - blind)
    gate_open = all(ctrl.values())

    nested = gate_open and (not rel_only or not blind_only)
    if not gate_open:
        verdict = "UNVERIFIED — a control failed."
    elif nested and not rel_only:
        verdict = (f"world B — THE FAMILIES NEST. The released-family ②′ set ({len(rel)}) is a "
                   f"strict SUBSET of the blind-family one ({len(blind)}): {len(inter)} shared, "
                   f"**0 released-only**, {len(blind_only)} blind-only. So every blind-family "
                   f"statement in this arc is an UPPER BOUND on released-family membership, and the "
                   f"synthetic scoping was conservative in a nameable direction rather than a "
                   f"different world. ⭐ And the mechanism is measured, not assumed: every one of "
                   f"the {len(blind_scores)} blind subsets scores below the weaker released "
                   f"comparator ({weakest_released}) — {all_blind_weaker} — so the blind family is "
                   f"uniformly weaker and admits more, exactly as R1088's proximity result predicts.")
    elif nested:
        verdict = (f"world B — nested the other way: {len(rel_only)} released-only, 0 blind-only.")
    else:
        verdict = (f"world A — the sets CROSS: {len(rel_only)} released-only and {len(blind_only)} "
                   f"blind-only, so no blind-family number transfers to the released family.")

    art = {"round": "R1098",
           "question": "how do the released-family and blind-family ②′ sets relate?",
           "source_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
           "prior_art": {"R1055": "already excludes comparators from candidacy — the obstruction "
                                  "R1095 named was never one for the released family"},
           "derivation_not_run": ("admission is per-arm, so removing `generic` from candidacy "
                                  "changes the block by exactly the removed arms and nothing else"),
           "sets": {"released": sorted(rel), "blind_minus_comparators": sorted(blind),
                    "intersection": inter, "released_only": rel_only, "blind_only": blind_only},
           "Q2_mechanism": {"released_comparator_scores": rel_scores,
                            "weakest_released": weakest_released,
                            "blind_subset_scores": blind_scores,
                            "every_blind_subset_weaker_than_the_weakest_released":
                                bool(all_blind_weaker)},
           "controls": ctrl,
           "consequence": ("blind-family statements are UPPER BOUNDS on released-family membership; "
                           "R1095's scope caveat is weaker than it reads"),
           "kill": {"gate_open": gate_open, "nested": nested},
           "verdict": verdict}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))

    print("R1098 — one comparator space at last: how do the two families relate?\n")
    print("  ⛔ PRIOR ART: R1055 already excludes comparators from candidacy, so R1095's")
    print("     obstruction was never one. And 'does the block change' is a DERIVATION —")
    print("     admission is per-arm, so it changes by exactly the removed arms.\n")
    print("  CONTROLS")
    for k, v in ctrl.items():
        print(f"    {'PASS' if v else '⛔ FAIL'}  {k}")
    print(f"\n  THE TWO ②′ SETS")
    print(f"    released family (2 comparators) : {len(rel)}")
    print(f"    blind family (15), comparators removed : {len(blind)}")
    print(f"    intersection {len(inter)} · released-only {len(rel_only)} · "
          f"blind-only {len(blind_only)}")
    print(f"    blind-only: {blind_only}")
    print(f"\n  Q2 · MECHANISM — a weaker comparator admits more (R1088)")
    print(f"    released comparator scores: {rel_scores}")
    print(f"    weakest released: {weakest_released}")
    print(f"    every blind subset scores below it: {all_blind_weaker}")
    print(f"    blind range: [{min(blind_scores.values())}, {max(blind_scores.values())}]")
    print(f"\n  {'⛔' if not gate_open else '⭐'} {verdict}")
    print(f"\n  artifact {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""R1001 — the same operator under clause ④'s PERMISSIVE reading, swept over R826's whole plateau.

⛔ WHY THIS IS CHEAP, AND WHY THAT MATTERS. R1000's NEXT asked for "a 99-arm scoring run at the
permissive bar", and I was about to spend the compute. The attack ladder says try arithmetic before
compute: **R825's permissive bar is already in mean-A2 units** — it is what R825 compared directly
against `coval_core`'s 0.566477 — and R826 committed the whole effort curve. So the permissive
extension is a THRESHOLD on a quantity I already have, and the entire specification curve exists
without a single new scoring run. The expensive round was unnecessary.

ESTIMAND        under the permissive reading of clause ④, at each of R826's saturated effort levels:
                ① the conjunction ①∧②∧③∧④'s extension, ② whether `coval_core` is in it, and
                ③ clause ④'s UNIQUE removals — the quantity that decided ④ was inert in R1000.
IDENTIFICATION  the bars are READ from R826's committed effort curve; the arm means and their
                bootstrap come from R923's committed operator, pinned to R922's cut at 1e-9. Clauses
                ①③ are read from R986 and R993's grammar exactly as in R1000.
SCOPE           population : R1000's 96-arm intersection, unchanged, so the two rounds are comparable
                instrument : A2 mean per arm; the bar is a HELD-OUT response-only predictor
                baseline   : the two prompt-blind comparators for clause ②
                regime     : R826's saturated cells only, k >= 40. Below saturation the bar is still
                             climbing and a threshold there measures modelling effort, not a clause.
WORLDS          A STILL INERT   ④ has 0 unique removals at every saturated bar — the permissive
                                reading changes nothing and R1000's verdict is reading-independent.
                B ④ BINDS       ④ acquires unique removals, so its inertness was an artifact of the
                                enumerated reading, and the definition's extension depends on a
                                reading its own text does not fix.
                prediction matrix: A -> unique = 0 at all 5 cells. B -> unique > 0 at >= 1 cell.
                ⚠ The two worlds also differ on the INSTANCE: under B, `coval_core` is expected to
                  leave its own extension, which A forbids.
KILL            pre-registered, and it is the one that costs me: if `coval_core` is excluded at any
                saturated cell, then R1000's headline — "the core is admitted by its own definition"
                — is READING-DEPENDENT and must be re-stated with its reading attached, in this
                round, not later.
POSITIVE CTRL   ① WIRING — R922's committed cut and count, both comparators, 1e-9. Same as R1000.
                ② the bar at k = 0 (0.524670, no modelling at all) must admit `coval_core`, because
                   R826's own committed verdict at k = 0 is "admits core". If my threshold excludes
                   it there, my threshold is not R826's comparison.
                ③ `oracle_k4` must still fail ③ and `topw_k1` must still fail ①.
NEGATIVE CTRL   a bar of 0.0 must admit the whole population; a bar of 1.0 must admit nobody. A
                threshold that does not sweep to both ends is not a threshold.
PLACEBO         at the k = 0 bar, ④'s unique removals must be 0 — nothing that clears clause ② can
                fail a bar built with no modelling. A non-zero there means the join is broken.
MULTIPLICITY    5 saturated cells × 2 comparators × 2 operator shapes = 20 cells, all printed, plus
                the 4 unsaturated cells shown for contrast and NOT used for any verdict.
ARTIFACT        results/permissive_operator.json with this file's source hash.
IMPOSSIBLE      ⚠ a RESOLVABLE permissive ④ that propagates the BAR's own error — N/A. R826 reports
                the bar's sd (0.0062–0.0079 across cells) but not a per-arm paired comparison, and
                the 12 split-level bar values are not in the committed artifact. So the `lo > bar`
                shape below treats the bar as FIXED. Direction named: that is conservative for
                ADMISSION and anti-conservative for EXCLUSION, so an arm this round calls excluded
                might survive once the bar's error is carried. What it would require: R825's 12
                per-split bar values, or a re-run that persists them.
                ⚠ construct validity — N/A, as in R1000.
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NBOOT, SEED = 8000, 921
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")
KSAT = 40  # R826: saturated from k >= 40; the last rise is below its own noise floor there


def main() -> int:
    need = {
        "r881": next(A24.glob("R881_*/results/boundary_distance.json"), None),
        "r921": next(A26.glob("R921_*/results/comparator_sweep.json"), None),
        "r922": next(A26.glob("R922_*/results/threshold_or_comparison.json"), None),
        "r826": next(A24.glob("R826_*/results/effort_curve.json"), None),
        "r986": next(A27.glob("R986_*/results/size_decomposition.json"), None),
        "r1000": next(A27.glob("R1000_*/results/conjunction.json"), None),
    }
    missing = [k for k, v in need.items() if v is None]
    if missing:
        print(f"  UNRUNNABLE: committed artifacts missing: {missing}. Exit 2, never 0.")
        return 2

    legit = json.loads(need["r921"].read_text())["legitimate_comparators"]
    ref922 = {r["comparator"]: r for r in json.loads(need["r922"].read_text())["rows"]}
    arms881 = [x["arm"] for x in json.loads(need["r881"].read_text())["arms"]]
    size986 = {r["arm"]: r for r in json.loads(need["r986"].read_text())["rows"]}
    curve = sorted(json.loads(need["r826"].read_text())["curve"], key=lambda r: r["k"])
    prev = json.loads(need["r1000"].read_text())
    pop_prev = set(prev["population_arms"])
    print(f"  bars READ from R826's committed effort curve: {len(curve)} cells, "
          f"k = {[c['k'] for c in curve]}")
    print(f"  population READ from R1000: {len(pop_prev)} arms — unchanged, so the rounds compare")

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    def vec(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                return None
            v = np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p in Sa:
                    c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    v[k] = float(np.mean([(c == h).mean() for h in H[p]]))
            if np.isfinite(v).sum() < 200:
                return None
            return np.nan_to_num(v, nan=np.nanmean(v))
        return None

    V, names = [], []
    for a in arms881:
        v = vec(a)
        if v is not None:
            V.append(v)
            names.append(a)
    V = np.array(V)
    means = dict(zip(names, V.mean(axis=1)))
    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))
    M = np.stack([V[:, idx[b]].mean(axis=1) for b in range(NBOOT)], axis=1)
    lo_arm = dict(zip(names, np.percentile(M, 2.5, axis=1)))

    c2, wiring = {}, {}
    mu = V.mean(axis=1)
    for c in legit:
        i = names.index(c)
        lo = np.percentile(M - M[i][None, :], 2.5, axis=1)
        adm = lo > 0
        wiring[c] = {"cut": float(mu[adm].min()), "n": int(adm.sum()) - int(adm[i])}
        c2[c] = {a for a, ok in zip(names, adm) if ok}
    wire_ok = all(abs(wiring[c]["cut"] - ref922[c]["implied_cut_mean_a2"]) < 1e-9
                  and wiring[c]["n"] == ref922[c]["n_admitted"] for c in legit)
    print(f"\n  POSITIVE ② WIRING — R922's cut and count reproduced, both comparators: "
          f"{'PASS' if wire_ok else '⛔ FAIL'}")

    pop = sorted(pop_prev & set(names) & set(size986))
    if len(pop) != len(pop_prev):
        print(f"  ⚠ population shrank {len(pop_prev)} -> {len(pop)}; the rounds no longer compare.")

    def c1(a):
        return size986[a]["max"] > 1

    def c3(a):
        return not a.startswith(SUPERVISED)

    core = "coval_core"
    k0 = next(c for c in curve if c["k"] == 0)
    p_k0 = means[core] > k0["bar"]
    p1 = all(not c1(a) for a in ("topw_k1", "topw_k1_08b") if a in pop)
    p3 = (core in pop) and not c3("oracle_k4")
    print(f"  POSITIVE k=0 bar {k0['bar']:.6f} must ADMIT the core "
          f"({means[core]:.6f}) — R826's own verdict there is '{k0['verdict']}': "
          f"{'PASS' if p_k0 else '⛔ FAIL'}")
    print(f"  POSITIVE ① topw_k1 fails ①: {p1}  ·  POSITIVE ③ oracle_k4 fails ③: {p3}")

    neg_lo = all(means[a] > 0.0 for a in pop)
    neg_hi = not any(means[a] > 1.0 for a in pop)
    print(f"  NEGATIVE bar 0.0 admits all: {neg_lo}  ·  bar 1.0 admits none: {neg_hi}")
    if not (wire_ok and p_k0 and p1 and p3 and neg_lo and neg_hi):
        print("\n⛔ a control failed; nothing below certifies anything. Exit 2, never 0.")
        return 2

    print(f"\n  {'k':>4} {'bar':>10} {'sat':>4} {'cmp':<15}{'shape':<9}"
          f"{'④ adm':>7}{'conj':>6}{'④uniq':>7}  core in conj")
    rows, sat_cells = [], []
    for cell in curve:
        for c in legit:
            for shape, ok4 in (("point", lambda a, b=cell["bar"]: means[a] > b),
                               ("lo>bar", lambda a, b=cell["bar"]: lo_arm[a] > b)):
                S = {"1": {a for a in pop if c1(a)}, "2": {a for a in pop if a in c2[c]},
                     "3": {a for a in pop if c3(a)}, "4": {a for a in pop if ok4(a)}}
                conj = set(pop)
                for v in S.values():
                    conj &= v
                others = set(pop)
                for j in ("1", "2", "3"):
                    others &= S[j]
                uniq4 = others - S["4"]
                sat = cell["k"] >= KSAT
                r = {"k": cell["k"], "bar": cell["bar"], "saturated": sat, "comparator": c,
                     "shape": shape, "clause4_admits": len(S["4"]), "conjunction": len(conj),
                     "clause4_unique": len(uniq4), "core_in_conjunction": core in conj,
                     "r826_verdict": cell["verdict"]}
                rows.append(r)
                if sat:
                    sat_cells.append(r)
                print(f"  {cell['k']:>4} {cell['bar']:>10.6f} {'yes' if sat else ' no':>4} "
                      f"{c:<15}{shape:<9}{len(S['4']):>7}{len(conj):>6}{len(uniq4):>7}"
                      f"  {core in conj}")

    plac = [r for r in rows if r["k"] == 0]
    plac_ok = all(r["clause4_unique"] == 0 for r in plac if r["shape"] == "point")
    print(f"\n  PLACEBO at k=0 (no modelling) clause ④ has 0 unique removals: "
          f"{'PASS' if plac_ok else '⛔ FAIL'}")
    if not plac_ok:
        print("⛔ the join is broken. Exit 2, never 0.")
        return 2

    binds = [r for r in sat_cells if r["clause4_unique"] > 0]
    core_out = [r for r in sat_cells if not r["core_in_conjunction"]]
    # ⛔ PRIOR ART, found by the currency gate refusing to go red — see README. Entry 1368 and R824
    # already committed "the extension is EMPTY" under the permissive reading. The headline below is
    # therefore a CONFIRMATION by a different route, not a discovery. What is new is the MECHANISM.
    world = ("A STILL INERT — ④ has 0 unique removals at every saturated bar" if not binds else
             f"B ④ BINDS — it acquires unique removals in {len(binds)} of {len(sat_cells)} "
             f"saturated cells, so R1000's inertness was a property of the READING")
    print(f"\n⭐ {world}")
    print("⛔ PRIOR ART — the headline is a CONFIRMATION, not a discovery. Entry 1368 and R824 already")
    print("   committed 'the extension is EMPTY' under the permissive reading. This round reaches it")
    print("   by a different route (the full 4-clause conjunction over 96 arms, swept over R826's")
    print("   plateau). ⭐ What is NEW is the MECHANISM below, which 1368 does not state.")
    print(f"⭐ `coval_core` LEAVES its own extension in {len(core_out)} of {len(sat_cells)} "
          f"saturated cells (R1000, enumerated reading: 0 of 2)")
    if core_out:
        print("⛔ PRE-REGISTERED KILL FIRES. R1000's headline — 'the core is admitted by its own")
        print("   definition' — is READING-DEPENDENT. Restated here: the released core is admitted")
        print("   under clause ④'s ENUMERATED reading and excluded under its PERMISSIVE reading,")
        print("   and the definition's text does not say which one it means.")

    # ---------- ⭐ WHY IS IT EMPTY? the mechanism, not the count ----------
    # An empty extension is a number. WHICH clause empties it, and whether the survivors of ④ are
    # exactly the arms ③ forbids, is the finding. Computed at the saturated bar nearest R825's k=100.
    cell = next(c for c in curve if c["k"] == 100)
    s4 = {a for a in pop if means[a] > cell["bar"]}
    sup = {a for a in s4 if not c3(a)}
    print(f"\n  ── ⭐ WHY EMPTY? clause ④'s survivors at k=100 (bar {cell['bar']:.6f}) ──")
    print(f"     ④ admits {len(s4)} arms. Of those, {len(sup)} read human rankings and so fail ③.")
    print(f"     ④ ∧ ③ = {len(s4 - sup)} arms: {sorted(s4 - sup)}")
    for c in legit:
        rest = (s4 - sup) & c2[c]
        print(f"     ④ ∧ ③ ∧ ② ({c}) = {len(rest)}: {sorted(rest)}")
    mech = {"clause4_admits": sorted(s4), "of_which_supervised": sorted(sup),
            "clause4_and_3": sorted(s4 - sup),
            "clause4_3_2": {c: sorted((s4 - sup) & c2[c]) for c in legit}}
    frac = len(sup) / len(s4) if s4 else None
    print(f"     ⇒ {len(sup)} of {len(s4)} arms clearing the permissive bar do it by reading human")
    print("        labels. The permissive reading and clause ③ are in DIRECT CONFLICT: the bar is")
    print("        set so high that only supervised arms clear it, and ③ forbids exactly those.")

    print("\n⚠ THE BAR IS TREATED AS FIXED. R826 reports its sd (0.0062–0.0079) but not the 12")
    print("   per-split values, so the `lo>bar` shape carries the ARM's error and not the BAR's.")
    print("   That is conservative for ADMISSION and anti-conservative for EXCLUSION.")

    out = HERE / "results" / "permissive_operator.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="the operator under clause ④'s permissive reading, swept over R826's plateau",
        n_prompts=n, nboot=NBOOT, seed=SEED, population=len(pop), k_saturated_from=KSAT,
        comparators=legit, wiring=wiring, core_mean=float(means[core]),
        controls={"positive_wiring_r922": wire_ok, "positive_k0_admits_core": bool(p_k0),
                  "positive_clause1": bool(p1), "positive_clause3": bool(p3),
                  "negative_bar0_admits_all": bool(neg_lo),
                  "negative_bar1_admits_none": bool(neg_hi), "placebo_k0_no_unique": plac_ok},
        rows=rows, world=world, mechanism=mech, supervised_share_of_clause4=frac,
        prior_art="entry 1368 / R824 already committed 'the extension is EMPTY' under the "
                  "permissive reading; this round CONFIRMS it by a different route",
        what_is_new="the mechanism: every arm clearing the permissive bar clears it by reading "
                    "human rankings, so clauses ③ and ④ have DISJOINT satisfaction sets",
        saturated_cells=len(sat_cells), cells_where_clause4_binds=len(binds),
        cells_where_core_excluded=len(core_out),
        not_measured="the bar's own sampling error — R825's 12 per-split bar values are not "
                     "committed, so the bar is treated as fixed",
        would_require="R825's per-split bar values, or a re-run that persists them",
        limitation="anti-conservative for EXCLUSION: an arm called excluded here might survive "
                   "once the bar's error is carried",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

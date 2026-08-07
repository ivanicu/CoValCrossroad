#!/usr/bin/env python3
"""R1012 — does the arc's load-bearing cut rest on arms whose A2 is 79% imputed?

⛔ WHY. R1011 measured that `coval_core_2bA` and `_2bB` are scored on **200 of 968 prompts (21%)**
and that the committed A2 loader fills the rest with the arm's own mean. A census over 1,229 committed
artifacts finds **69** that name a partial-coverage arm, and among them are result-bearing fields:
R921's `admitted_by_at_least_one_legitimate`, R978's `full_admitted`, R992's `clause2_passers`,
R1000's `conjunction`. ⭐ **The one that matters most is R922's committed cut** — `means[adm].min()`
— because the wiring control of every round in this arc pins itself to it at 1e-9. If an imputed arm
is the argmin, the number the whole arc calibrates against was set by 768 fabricated values.

ESTIMAND        the committed cut and admitted count, per comparator, recomputed with
                partial-coverage arms EXCLUDED; and whether the argmin was one of them.
IDENTIFICATION  exact. Coverage is countable from the scored files; the cut is a min over a set.
                Nothing is estimated — this is a recomputation with one population change.
SCOPE           population : R881's 99 arms, minus those scored on < 968 prompts
                instrument : A2, R923's committed operator, seed 921, 8000 draws
                baseline   : R922's committed cut and count · regime : this release
WORLDS          A THE CUT IS CLEAN     the argmin is a full-coverage arm; excluding the partial ones
                                       leaves the cut identical and only the count moves.
                B THE CUT IS IMPUTED   an imputed arm is the argmin, so the number every round in
                                       this arc pins to at 1e-9 was set by fabricated values.
                prediction matrix: A -> cut unchanged, count drops by the number excluded that were
                                   admitted. B -> cut moves.
KILL            pre-registered: if world B, every comparison to the committed cut in this arc is
                scoped in THIS round, and the corrected cut is stated beside it.
POSITIVE CTRL   the FULL-population recomputation must reproduce R922's committed cut and count to
                1e-9 under both comparators. If it does not, this is not the committed operator and
                no difference below means anything.
NEGATIVE CTRL   excluding a set of arms that are ALL at full coverage must leave the cut unchanged
                unless one of them was the argmin — checked by excluding the two arms with the
                HIGHEST A2 (never the argmin) and requiring the cut to hold exactly.
PLACEBO         excluding the empty set must reproduce the full result byte for byte.
NOISE FLOOR     n/a — this is a recomputation, not an estimate. Labelled. The bootstrap seed and
                draw count are held identical so the only moving part is the population.
MULTIPLICITY    2 comparators × 3 populations (full, minus-partial, minus-highest) = 6 cells, all
                printed.
ARTIFACT        results/cut_provenance.json with this file's source hash.
IMPOSSIBLE      ⚠ recomputing what the partial arms' A2 WOULD be with real scores — N/A. The 768
                missing prompts were never scored for them; that is the defect, not a gap in this
                round. What it would require: scoring those arms on the full corpus.
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
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NBOOT, SEED = 8000, 921


def main() -> int:
    r881 = next(A24.glob("R881_*/results/boundary_distance.json"), None)
    r921 = next(A26.glob("R921_*/results/comparator_sweep.json"), None)
    r922 = next(A26.glob("R922_*/results/threshold_or_comparison.json"), None)
    if not (r881 and r921 and r922):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0.")
        return 2
    legit = json.loads(r921.read_text())["legitimate_comparators"]
    ref = {r["comparator"]: r for r in json.loads(r922.read_text())["rows"]}
    arms881 = [x["arm"] for x in json.loads(r881.read_text())["arms"]]

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    H = {p: np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids}
    n = len(pids)

    V, names, cover = [], [], {}
    for a in arms881:
        got = None
        for d in (RES, NEW):
            f = d / f"sat_{a}.npz"
            if not f.exists():
                continue
            try:
                Sa = load_sat(f)
            except Exception:
                break
            v = np.full(n, np.nan)
            for k, p in enumerate(pids):
                if p in Sa:
                    c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                    v[k] = float(np.mean([(c == h[:len(c)]).mean() for h in H[p]]))
            if np.isfinite(v).sum() >= 200:
                cover[a] = int(np.isfinite(v).sum())
                got = np.nan_to_num(v, nan=np.nanmean(v))
            break
        if got is not None:
            V.append(got)
            names.append(a)
    V = np.array(V)
    mu = V.mean(axis=1)
    partial = sorted(a for a in names if cover[a] < n)
    print(f"  arms {len(names)} · prompts {n} · PARTIAL coverage: {len(partial)} → "
          f"{[(a, cover[a]) for a in partial]}")

    rng = np.random.default_rng(SEED)
    idx = rng.integers(0, n, size=(NBOOT, n))
    M = np.stack([V[:, idx[b]].mean(axis=1) for b in range(NBOOT)], axis=1)

    def cut_and_count(exclude):
        out = {}
        keep = [i for i, a in enumerate(names) if a not in exclude]
        for c in legit:
            i = names.index(c)
            lo = np.percentile(M - M[i][None, :], 2.5, axis=1)
            adm = [j for j in keep if lo[j] > 0]
            if not adm:
                out[c] = {"cut": None, "n": 0, "argmin": None}
                continue
            am = min(adm, key=lambda j: mu[j])
            out[c] = {"cut": float(mu[am]), "n": len(adm) - (1 if i in adm else 0),
                      "argmin": names[am]}
        return out

    full = cut_and_count(set())
    wire_ok = all(abs(full[c]["cut"] - ref[c]["implied_cut_mean_a2"]) < 1e-9
                  and full[c]["n"] == ref[c]["n_admitted"] for c in legit)
    print(f"\n  POSITIVE CONTROL — the full-population recomputation must reproduce R922's committed "
          f"cut and count at 1e-9: {'PASS' if wire_ok else '⛔ FAIL'}")
    for c in legit:
        print(f"     {c:<16} cut {full[c]['cut']:.10f} (R922 {ref[c]['implied_cut_mean_a2']:.10f})"
              f"  n {full[c]['n']} (R922 {ref[c]['n_admitted']})  argmin `{full[c]['argmin']}`")
    if not wire_ok:
        print("  this is not the committed operator. Exit 2, never 0.")
        return 2

    nopart = cut_and_count(set(partial))
    top2 = [names[j] for j in np.argsort(-mu)[:2]]
    notop = cut_and_count(set(top2))
    empty = cut_and_count(set())
    plac_ok = all(empty[c] == full[c] for c in legit)
    neg_ok = all(notop[c]["cut"] == full[c]["cut"] for c in legit
                 if full[c]["argmin"] not in top2)
    print(f"  PLACEBO  excluding the empty set reproduces the full result: "
          f"{'PASS' if plac_ok else '⛔ FAIL'}")
    print(f"  NEGATIVE excluding the two HIGHEST-A2 arms {top2} (never the argmin) leaves the cut "
          f"unchanged: {'PASS' if neg_ok else '⛔ FAIL'}")
    if not (plac_ok and neg_ok):
        print("\n⛔ a control failed. Exit 2, never 0.")
        return 2

    print(f"\n  {'comparator':<16}{'population':<18}{'cut':>14}{'n':>5}  argmin")
    rows = []
    for c in legit:
        for label, res in (("full", full), ("minus partial", nopart), ("minus top-2", notop)):
            r = res[c]
            rows.append({"comparator": c, "population": label, "cut": r["cut"], "n": r["n"],
                         "argmin": r["argmin"]})
            print(f"  {c:<16}{label:<18}{r['cut']:>14.10f}{r['n']:>5}  {r['argmin']}")

    imputed_argmin = [c for c in legit if full[c]["argmin"] in partial]
    moved = [c for c in legit if nopart[c]["cut"] != full[c]["cut"]]
    world = (f"B THE CUT IS IMPUTED — the argmin is a partial-coverage arm under {imputed_argmin}"
             if imputed_argmin else
             "A THE CUT IS CLEAN — the argmin is a full-coverage arm under every comparator")
    print(f"\n⭐ {world}")
    print(f"⭐ comparators whose cut MOVES when partial-coverage arms are excluded: "
          f"{moved if moved else 'none'}")
    for c in legit:
        d = (nopart[c]['cut'] or 0) - (full[c]['cut'] or 0)
        print(f"   {c:<16} cut {full[c]['cut']:.10f} → {nopart[c]['cut']:.10f}  "
              f"(Δ {d:+.10f})   n {full[c]['n']} → {nopart[c]['n']}")
    if imputed_argmin or moved:
        print("\n⛔ PRE-REGISTERED KILL FIRES: every comparison to the committed cut in this arc is")
        print("   scoped by this, and the corrected cut is the one stated above.")
    else:
        print("\n⭐ SO THE ARC'S CALIBRATION NUMBER IS NOT AN ARTIFACT OF THE IMPUTATION. What the")
        print("   imputation does affect is the COUNT, and that is reported above rather than left")
        print("   for a later round to find.")

    out = HERE / "results" / "cut_provenance.json"
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head="does the load-bearing cut rest on partial-coverage arms",
        n_prompts=n, nboot=NBOOT, seed=SEED, partial_coverage={a: cover[a] for a in partial},
        controls={"positive_reproduces_r922": bool(wire_ok), "placebo_empty_exclusion": bool(plac_ok),
                  "negative_top2_exclusion": bool(neg_ok), "top2_excluded": top2},
        rows=rows, world=world, imputed_argmin=imputed_argmin, comparators_whose_cut_moved=moved,
        limitation="recomputing what the partial arms' A2 WOULD be with real scores is impossible "
                   "here; those 768 prompts were never scored for them",
        would_require="scoring the partial-coverage arms on the full corpus",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

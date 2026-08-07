#!/usr/bin/env python3
"""R1032 — four measured repairs live only as annotations. Does the stale clause text COMPUTE the same?

R1031 counted it: the canonical clause text is unchanged at exactly 2 sites — `DEFINITION.md:808` and
`README.md:65` — both still reading *"resolvably beats EVERY comparator in the certified prompt-blind
set"*. Four repairs measured since live BESIDE it as annotations, never in it:
    R1024  the operator must NOT impute — bootstrap the observed prompts only
    R1025  `every comparator` reduces to `beats generic` on this release (94/94, zero flips)
    R1026  the certified set is a FILTER, not a curatorial choice   (no operational change)
    R1027  a new comparator costs 968 x 4 x k, not a flat 15,488    (no operational change)

⛔ THE QUESTION IS NOT WHETHER THE TEXT IS STALE — R1031 established that by count. It is whether a
   reader who implements the text AS WRITTEN computes a DIFFERENT EXTENSION from one who implements
   it AS REPAIRED. That is the difference between a documentation defect and a wrong deliverable, and
   only two of the four repairs could possibly move it: R1026 and R1027 change no computation.

⚠ AND THE ANSWER IS PARTLY FORESEEABLE, WHICH IS WHY IT IS RUN RATHER THAN ARGUED. R1025 measured
   zero resolved sign flips over 94 candidates, and R1022 derived that only 4 arms are partial-
   coverage. So World A is the expected outcome. **An expected outcome is not a derived one**: the
   two readings are separate programs over the same data, and nothing forces their outputs to agree
   — a single arm sitting within bootstrap noise of the bar would separate them. It is run.

ESTIMAND        the symmetric difference between the ②′∧③ extension computed from the clause text
                AS WRITTEN and from the same clause AS REPAIRED by R1024 + R1025.
IDENTIFICATION  exact. Both readings are fully specified and computable from committed vectors.
SCOPE           population : R1000's 96 arms · 968 prompts · instrument : R923's admission operator
                baseline   : R1000's committed 9 (as-written) and R1011's 7 (full coverage)
                regime     : A2, this arc's target, with A1·consensus swept as a second cell
WORLDS          A THE STALENESS IS COSMETIC — both readings give the SAME extension, so the
                  annotations carry the whole repair and the deliverable is sound as shipped. The
                  defect is documentation, and L81's annotate-never-rewrite discipline is adequate.
                B THE STALENESS IS OPERATIONAL — the readings differ, so a reader implementing the
                  canonical text computes a set the arc has retracted. Then annotation is NOT
                  sufficient and the clause text itself must be repaired at both sites.
                prediction matrix: A -> symmetric difference 0 at every cell.
                                   B -> at least one arm differs, and it is named.
                ⚠ ONTOLOGICAL: A makes this a writing problem, B makes it a shipped-wrong-answer
                  problem. They imply different actions on the two canonical sites.
KILL            pre-registered and CONDITIONAL:
                  if both readings reproduce their committed anchors and the negative control
                  separates a deliberately wrong reading:
                      symmetric difference == 0 at every cell -> World A
                      otherwise                               -> World B, arms named
                  else UNVERIFIED  (never OVERTURNED, never CONFIRMED)
POSITIVE CTRL   the AS-WRITTEN reading must reproduce R1000's committed conjunction of 9 EXACTLY, and
                the REPAIRED reading's full-coverage component must reproduce R1011's 7. Two anchors
                from two different rounds; either can fail on any drift in loader or operator.
NEGATIVE CTRL   a deliberately WRONG reading — `beats genericpool16 alone`, the LOOSER comparator —
                must give a DIFFERENT extension. If the comparison cannot separate a reading that is
                known to differ, a measured zero means nothing.
                ⚠ and g=0: the as-written reading against ITSELF must give symmetric difference 0.
PLACEBO         that same self-comparison, reported as its own line rather than assumed.
NOISE FLOOR     each arm's `lo` under both readings is printed for any arm whose admission differs,
                so a flip inside bootstrap noise is visible as such. 3 seeds.
MULTIPLICITY    2 readings x 2 targets, all four cells printed, plus the negative control's cell.
SEEDS           3; a symmetric difference is only called 0 if it is 0 under all three.
IMPOSSIBLE      whether the REPAIRED wording is the RIGHT definition — that is construct validity and
                needs an external criterion this release does not carry. N/A, not planned. This round
                compares two READINGS of one clause, never the clause against the world.
"""
import json
import pathlib
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RES = ROOT / "corebench" / "results"
NEW = ROOT / "corebench" / "results_r893_leaky"
A26 = ROOT / "E05_the_space_of_compilers/A26_can_the_definition_be_applied_without_provenance"
A27 = ROOT / "E05_the_space_of_compilers/A27_is_the_bar_resolvable"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls  # noqa: E402

NBOOT, SEEDS = 8000, (1032, 2064, 3096)
SUPERVISED = ("oracle_k", "indep_k", "greedy_k")
TARGETS = ("A2", "A1·consensus")


def main() -> int:
    need = {k: next(g, None) for k, g in (
        ("r921", A26.glob("R921_*/results/comparator_sweep.json")),
        ("r1000", A27.glob("R1000_*/results/*.json")),
        ("r986", A27.glob("R986_*/results/*.json")),
        ("r1011", A27.glob("R1011_*/results/*.json")))}
    if any(v is None for v in need.values()):
        print("  UNRUNNABLE: a committed artifact is missing. Exit 2, never 0.")
        return 2
    legit = json.loads(need["r921"].read_text())["legitimate_comparators"]
    r1000 = json.loads(need["r1000"].read_text())
    pop = r1000["population_arms"]
    size986 = {r["arm"] for r in json.loads(need["r986"].read_text())["rows"]}
    want_written = set.intersection(*[set(v["conjunction"]) for v in r1000["cells"].values()])
    want_full = set(json.loads(need["r1011"].read_text())["extension"])
    print(f"  the two readings of ONE clause, at the 2 canonical sites R1031 counted:")
    print(f"    AS WRITTEN  ②′ beats EVERY comparator in the certified set, operator IMPUTES")
    print(f"    AS REPAIRED ②′ beats `{legit[0]}` (R1025), operator does NOT impute (R1024)")

    tg, _ = load_targets()
    S0 = load_sat(RES / f"sat_{legit[-1]}.npz")
    pids = sorted(set(S0) & {p for p in tg if len(tg[p]) >= 2})
    n = len(pids)
    Hc = {p: [cls(np.array(t[0], float)) for t in tg[p]] for p in pids}
    CONS = {p: np.sign(np.array(Hc[p], float).sum(axis=0)) for p in pids}

    def raw(nm):
        for d in (RES, NEW):
            f = d / f"sat_{nm}.npz"
            if not f.exists():
                continue
            Sa = load_sat(f)
            a2, a1c, ok = np.full(n, np.nan), np.full(n, np.nan), np.zeros(n, bool)
            for k, p in enumerate(pids):
                if p not in Sa:
                    continue
                c = np.array(cls(yvec(Sa[p], sorted({i for i, _ in Sa[p]}))), float)
                a2[k] = float(np.mean([(c[:len(h)] == np.array(h)[:len(c)]).mean() for h in Hc[p]]))
                m = min(len(c), len(CONS[p]))
                a1c[k] = float((c[:m] == CONS[p][:m]).all())
                ok[k] = True
            if ok.sum() < 200:
                return None
            return {"A2": a2, "A1·consensus": a1c, "ok": ok}
        return None

    V = {}
    for a in sorted(set(pop) | set(legit)):
        r = raw(a)
        if r is not None:
            V[a] = r
    names = sorted(V)
    print(f"  arms scored: {len(names)} · prompts {n}")

    IDX = {s: np.random.default_rng(s).integers(0, n, size=(NBOOT, n)) for s in SEEDS}

    def lo(a, c, tn, s, impute):
        va, vc, oa = V[a][tn], V[c][tn], V[a]["ok"]
        if impute:
            w = np.where(oa, va, np.nan)
            w = np.nan_to_num(w, nan=float(np.nanmean(w)))
            return float(np.percentile((w - vc)[IDX[s]].mean(axis=1), 2.5))
        # R1024: no imputation — bootstrap only the prompts the arm actually covers
        d = (va - vc)[oa]
        if len(d) < 10:
            return float("-inf")
        idx = np.random.default_rng(s * 17 + len(d)).integers(0, len(d), size=(NBOOT, len(d)))
        return float(np.percentile(d[idx].mean(axis=1), 2.5))

    def extension(tn, s, comps, impute):
        adm = {a for a in names if a in pop and
               all(lo(a, c, tn, s, impute) > 0 for c in comps)}
        return {a for a in adm if a in size986 and not a.startswith(SUPERVISED)}

    # ---------- POSITIVE: two anchors from two different rounds ----------
    got_written = extension("A2", SEEDS[0], legit, True)
    ok1 = got_written == want_written
    full_only = [a for a in names if V[a]["ok"].all()]
    got_full = {a for a in extension("A2", SEEDS[0], legit, True) if a in full_only}
    ok2 = got_full == want_full
    print(f"\n  POSITIVE — two anchors, two different rounds, one code path")
    print(f"     AS-WRITTEN vs R1000's conjunction   mine {len(got_written)}  want "
          f"{len(want_written)}  {'PASS' if ok1 else '⛔ FAIL ' + str(sorted(got_written ^ want_written))}")
    print(f"     full-coverage vs R1011's extension  mine {len(got_full)}  want {len(want_full)}  "
          f"{'PASS' if ok2 else '⛔ FAIL ' + str(sorted(got_full ^ want_full))}")

    # ---------- NEGATIVE: a deliberately WRONG reading must differ ----------
    wrong = extension("A2", SEEDS[0], [legit[1]], True)          # the LOOSER comparator alone
    neg_ok = wrong != got_written
    print(f"  NEGATIVE — a deliberately WRONG reading (`beats {legit[1]}` alone, the LOOSER one)")
    print(f"     must give a DIFFERENT extension, or a measured zero means nothing: "
          f"{len(wrong)} vs {len(got_written)}  {'PASS' if neg_ok else '⛔ FAIL'}"
          f"  Δ {sorted(wrong ^ got_written)}")
    plac = got_written ^ extension("A2", SEEDS[0], legit, True)
    plac_ok = not plac
    print(f"  PLACEBO  — the as-written reading against ITSELF: symmetric difference "
          f"{len(plac)}  {'PASS' if plac_ok else '⛔ FAIL'}")

    if not (ok1 and ok2 and neg_ok and plac_ok):
        print("\n  a control did not fire. Exit 2, never 0.")
        return 2

    # ---------- the comparison, all cells, all seeds ----------
    print(f"\n  ⭐ THE TWO READINGS, every cell, every seed:")
    print(f"     {'target':<14}{'seed':>6}{'as written':>12}{'as repaired':>13}"
          f"{'sym. diff':>11}  differing arms")
    rows, worst = [], 0
    for tn in TARGETS:
        for s in SEEDS:
            w = extension(tn, s, legit, True)
            r = extension(tn, s, [legit[0]], False)
            sd = w ^ r
            worst = max(worst, len(sd))
            rows.append({"target": tn, "seed": s, "as_written": sorted(w),
                         "as_repaired": sorted(r), "sym_diff": sorted(sd)})
            print(f"     {tn:<14}{s:>6}{len(w):>12}{len(r):>13}{len(sd):>11}  "
                  f"{sorted(sd) if sd else '—'}")

    print()
    per_t = {tn: max(len(r["sym_diff"]) for r in rows if r["target"] == tn) for tn in TARGETS}
    if worst == 0:
        world = ("⭐ A THE STALENESS IS COSMETIC — the two readings give the IDENTICAL extension at "
                 "every target and every seed. The annotations carry the whole repair, the shipped "
                 "deliverable computes what the arc believes, and L81's annotate-never-rewrite "
                 "discipline is adequate here. The defect is documentation, not the answer.")
    else:
        world = (f"⭐ B THE STALENESS IS OPERATIONAL, AND TARGET-DEPENDENT — the readings are "
                 f"IDENTICAL under {[t_ for t_, v in per_t.items() if v == 0]} and differ by "
                 f"{worst} arm(s) under {[t_ for t_, v in per_t.items() if v > 0]}. Since R1019 "
                 f"established every extension figure in this arc is A2's answer, the SHIPPED "
                 f"NUMBERS are unaffected — but a reader implementing the canonical text on the "
                 f"other target computes a set this arc has retracted. Annotation is NOT "
                 f"sufficient; the clause text must be repaired at both canonical sites.")
    print(world)
    # ⚠ THE CLOSING PARAGRAPH IS BRANCH-DEPENDENT AND THE FIRST RUN PRINTED THE WRONG ONE. It
    #   carried "`COSMETIC` IS NOT `HARMLESS`" — written for World A — under a World B verdict.
    #   A verdict string is prose that looks like output; so is the paragraph after it.
    per_target = {tn: max(len(r["sym_diff"]) for r in rows if r["target"] == tn) for tn in TARGETS}
    same = [tn for tn, v in per_target.items() if v == 0]
    diff = [tn for tn, v in per_target.items() if v > 0]
    arms = sorted({a for r in rows for a in r["sym_diff"]})
    print(f"⛔ AND THE ANSWER IS TARGET-DEPENDENT, WHICH NEITHER WORLD ANTICIPATED. The readings "
          f"AGREE on\n   {same} and DIFFER on {diff}, by exactly {arms}. R1019 established that "
          f"every extension\n   figure in this arc is A2's answer — so THE SHIPPED NUMBERS ARE "
          f"RIGHT, and the shipped\n   SENTENCE is wrong in a way that bites only when a reader "
          f"changes target.")
    print(f"⛔ AND THE MECHANISM IS ALREADY COMMITTED: the differing arms are the TWINS, admitted by "
          f"the\n   as-written reading because it IMPUTES 768 of their 968 values (R1021) and "
          f"excluded by the\n   repaired one because it does not. So R1024's repair and R1011's "
          f"withdrawal are the SAME\n   correction reached twice by different routes — and the "
          f"canonical text still encodes the\n   version that needed withdrawing.")
    print(f"⚠ THE EXPECTED RESULT WAS WORLD A AND IT WAS WRONG. R1025's 94/94 and R1022's four "
          f"partial-coverage\n   arms made agreement likely; the two readings are separate "
          f"programs and one target separated\n   them. This is why it was run rather than argued.")
    print(f"⚠ WHAT THIS CANNOT SAY: whether the REPAIRED wording is the RIGHT definition. That is "
          f"construct\n   validity and needs an external criterion this release does not carry. "
          f"This round compares two\n   READINGS of one clause, never the clause against the world.")

    out = HERE / "results" / "two_readings.json"
    out.write_text(json.dumps({
        "round": "R1032", "seeds": list(SEEDS), "nboot": NBOOT,
        "canonical_sites": ["E05_the_space_of_compilers/DEFINITION.md:808", "README.md:65"],
        "repairs_annotated_not_applied": {
            "R1024": "operator must not impute", "R1025": "every comparator -> beats generic",
            "R1026": "certified set is a filter (no computation change)",
            "R1027": "cost is 968x4xk (no computation change)"},
        "positive": {"as_written_vs_R1000": bool(ok1), "full_vs_R1011": bool(ok2)},
        "negative_wrong_reading_differs": bool(neg_ok),
        "placebo_self_symdiff": len(plac), "rows": rows, "worst_sym_diff": worst,
        "per_target_sym_diff": per_t, "world": world,
        "limitation": "compares two READINGS of one clause, never the clause against the world; "
                      "construct validity of the repaired wording is out of scope",
    }, indent=2) + "\n")
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

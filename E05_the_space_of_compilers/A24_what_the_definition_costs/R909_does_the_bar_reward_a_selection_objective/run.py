#!/usr/bin/env python3
"""
R909 · among label-free rubric selectors, does the bar reward a specific SELECTION OBJECTIVE?

⛔ WHY. R908 showed the bar separates informed from random selection: `random_k` 0/38, Wilson
[0.000, 0.092], against four informed rules all clearing it. **But three INFORMED rules sit at
exactly zero too** — `topvar` 0/3, `topwvar` 0/3, `topabs` 0/2 — each unreadable alone at widths
0.562–0.658. Reading the generator's own descriptions, those three share a property:
  · `topw_k`    — the k criteria with the **highest MEAN importance score**   (signed weight)
  · `topabs_k`  — the k with the largest **|mean|**, most polarising either way
  · `topvar_k`  — selects on the **SPREAD** of satisfaction, not its level
  · `topwvar_k` — the weighted variance variant
**So the split is SIGNED MEAN WEIGHT versus VARIANCE-or-MAGNITUDE**, and it is a property of the
objective, not of the family name.

⚠⚠ **AND R908 FORBADE POOLING RULES, SO THE POOLING HERE MUST BE JUSTIFIED RATHER THAN ASSUMED.**
R908's ban existed to stop a **k-composition** artifact — `random` contributed 38 zeros at every k
while `oracle/greedy/indep` sat at k=4, so a pooled k-curve would have shown an effect through
composition alone. **That hazard is absent here and the reason is checkable: all three candidate
rules exist at k = 4 ONLY.** Pooling on a NAMED SHARED PROPERTY with the confounding axis held
CONSTANT is a different operation from pooling heterogeneous rules across a varying one — and the
round asserts the constancy in code rather than in this sentence.

ESTIMAND        the admitted share among label-free RUBRIC_SELECTOR arms, grouped by selection
                objective, at matched k = 4 and pooled over k; with Wilson intervals.
IDENTIFICATION  exact for the shares. ⚠ NOT causal, NOT an admission probability (arms were built,
                not sampled), and the objective grouping is READ from the generator's docstrings.
SCOPE           population: label-free rubric selectors — `topw`, `topabs`, `topvar`, `topwvar`.
                            The label-consuming rules are EXCLUDED by name, because R900/R907
                            already established label access as a separate axis and mixing them
                            would reproduce that confound
                instrument: R881's clause-② flag; Wilson 95%
                baseline:   equal share across objectives
                regime:     home release, judge 2B
WORLDS          A · the two objectives' intervals are DISJOINT -> the bar rewards a specific
                    selection objective, not merely being informed
                B · they overlap -> being informed is what matters; the objective is not
                    separable on this inventory
                C · the k-constancy assumption fails -> the pooling is not licensed and the round
                    reports per-rule only
KILL            CONDITIONAL:
                  ⭐ ① POOLING LICENCE, asserted in code: every arm in the VARIANCE_OR_MAGNITUDE
                     group must be at k = 4. If any is not, the k axis varies within the pool and
                     WORLD C — the pooling is withdrawn, not adjusted.
                  ⭐ ② POSITIVE: `topw` must be admitted somewhere, else both groups are zero and
                     the contrast is between two silences.
                  ⭐ ③ RESOLUTION, inherited: DISJOINT Wilson intervals, never a count threshold.
                  ④ the objective grouping READ from select_core.py's docstrings, not assigned.
MULTIPLICITY    2 objectives × {matched k=4, pooled}; every rule's own numbers also printed.
ARTIFACT        results/selection_objective.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability. ⚠ AND: if the intervals overlap, that is a
                statement about THIS inventory's size, not evidence that the objective is
                irrelevant.
"""
import json, pathlib, re, subprocess
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
GEN = ROOT / "corebench" / "select_core.py"
SIGNED = ["topw"]
OTHER = ["topabs", "topvar", "topwvar"]


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> int:
    src = GEN.read_text()
    ok_w = "highest MEAN importance" in src
    ok_a = "most polarising either way" in src
    print(f"  ④ the objective split READ from {GEN.name}'s docstrings:")
    print(f"     topw_k   'highest MEAN importance score'            present: {ok_w}")
    print(f"     topabs_k 'largest |mean|, most polarising either way' present: {ok_a}")

    r908 = next(A24.glob("R908_*/results/bar_by_rule.json"), None)
    if r908 is None:
        print("  UNRUNNABLE: R908 artifact missing. Exit 2, never 0.")
        return 2
    rules = {r["rule"]: r for r in json.loads(r908.read_text())["rules"]}
    missing = [r for r in SIGNED + OTHER if r not in rules]
    if missing:
        print(f"  UNRUNNABLE: rules absent from R908's table: {missing}. Exit 2, never 0.")
        return 2

    # ---- ① POOLING LICENCE ---------------------------------------------------------------------
    ks = sorted({k for r in OTHER for k in rules[r]["k_values"]})
    c1 = ks == [4]
    print(f"\n  ① POOLING LICENCE the VARIANCE_OR_MAGNITUDE group's k values: {ks}")
    print(f"     all at k=4, so the confounding axis is CONSTANT within the pool: {c1}  "
          f"{'PASS' if c1 else 'FAIL'}")
    print(f"     R908 banned pooling to stop a k-COMPOSITION artifact; that hazard needs k to")
    print(f"     VARY across the pooled units. Here it does not, and the check is in code.")
    if not c1:
        print("\n  ⭐ WORLD C: the pooling is not licensed. Reporting per-rule only. Exit 2.")
        json.dump({"verdict": "WORLD_C", "k_values_in_pool": ks,
                   "per_rule": {r: rules[r] for r in SIGNED + OTHER}},
                  open(OUT / "selection_objective.json", "w"), indent=2)
        return 2

    def group(names, only_k4=False):
        a = n = 0
        for r in names:
            if only_k4:
                cell = rules[r]["per_k"].get("4")
                if cell:
                    a += cell[0]; n += cell[1]
            else:
                a += rules[r]["n_admitted"]; n += rules[r]["n_built"]
        return a, n

    print(f"\n  ⭐ EVERY RULE'S OWN NUMBERS FIRST, so the pool never hides a member:")
    for r in SIGNED + OTHER:
        v = rules[r]
        lo, hi = wilson(v["n_admitted"], v["n_built"])
        print(f"     {r:<10}{v['n_admitted']}/{v['n_built']:<4} {v['share']:.3f}  "
              f"[{lo:.3f}, {hi:.3f}]   k={v['k_values']}")

    rows = []
    for label, names in (("SIGNED_MEAN_WEIGHT", SIGNED), ("VARIANCE_OR_MAGNITUDE", OTHER)):
        for spec, only in (("pooled over k", False), ("matched k=4", True)):
            a, n = group(names, only)
            lo, hi = wilson(a, n)
            rows.append({"objective": label, "spec": spec, "n_admitted": a, "n_built": n,
                         "share": (a / n) if n else float("nan"),
                         "ci95": [lo, hi], "ci_width": hi - lo})

    c2 = rules["topw"]["n_admitted"] > 0
    print(f"\n  ② POSITIVE topw is admitted somewhere ({rules['topw']['n_admitted']}/"
          f"{rules['topw']['n_built']}): {c2}  {'PASS' if c2 else 'FAIL'}")
    print(f"     else both groups are zero and the contrast is between two silences")
    if not c2:
        print("\n  UNVERIFIED: the positive control failed. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "rows": rows},
                  open(OUT / "selection_objective.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐⭐ BY SELECTION OBJECTIVE — both specifications, neither preferred:")
    print(f"     {'objective':<24}{'spec':<16}{'adm/built':>11}{'share':>8}{'Wilson 95%':>22}")
    for r in rows:
        frac = f"{r['n_admitted']}/{r['n_built']}"
        ci = f"[{r['ci95'][0]:.3f}, {r['ci95'][1]:.3f}]"
        print(f"     {r['objective']:<24}{r['spec']:<16}{frac:>11}{r['share']:>8.3f}{ci:>22}")

    verdicts = {}
    for spec in ("pooled over k", "matched k=4"):
        a = next(r for r in rows if r["objective"] == "SIGNED_MEAN_WEIGHT" and r["spec"] == spec)
        b = next(r for r in rows if r["objective"] == "VARIANCE_OR_MAGNITUDE" and r["spec"] == spec)
        dis = a["ci95"][1] < b["ci95"][0] or b["ci95"][1] < a["ci95"][0]
        gap = a["ci95"][0] - b["ci95"][1]
        verdicts[spec] = {"disjoint": bool(dis), "signed_lo_minus_other_hi": float(gap)}
        print(f"     {spec:<16} disjoint: {dis}   (signed's lower {a['ci95'][0]:.3f} − other's "
              f"upper {b['ci95'][1]:.3f} = {gap:+.3f})")

    any_dis = any(v["disjoint"] for v in verdicts.values())
    world = "A" if any_dis else "B"
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": "the two objectives' intervals are DISJOINT in at least one specification — the bar "
             "rewards a specific selection objective, not merely being informed",
        "B": "the intervals OVERLAP in both specifications — **being informed is what the bar "
             "separates; the objective is not separable at this inventory size.** ⚠ That is a "
             "statement about the inventory, NOT evidence that the objective is irrelevant"}[world])
    if world == "B":
        b4 = next(r for r in rows if r["objective"] == "VARIANCE_OR_MAGNITUDE"
                  and r["spec"] == "pooled over k")
        print(f"\n  ⚠ AND THE DIRECTION IS CONSISTENT WITHOUT BEING RESOLVED: the "
              f"variance/magnitude group is {b4['n_admitted']}/{b4['n_built']} — a clean zero —")
        print(f"     while `topw` is {rules['topw']['n_admitted']}/{rules['topw']['n_built']}. The")
        print(f"     intervals touch rather than separate. **Reporting the direction without the")
        print(f"     separation is the honest form**; quoting the zero as a finding would be the")
        print(f"     n=2 error this arc has now closed three questions with.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "groups": rows, "verdicts": verdicts,
               "per_rule": {r: {"n_admitted": rules[r]["n_admitted"],
                                "n_built": rules[r]["n_built"],
                                "k_values": rules[r]["k_values"]} for r in SIGNED + OTHER},
               "pooling_licence": {"k_values_in_pool": ks, "constant": bool(c1),
                                   "why": "R908 banned pooling to stop a k-COMPOSITION artifact, "
                                          "which needs k to VARY across pooled units; here every "
                                          "pooled rule is at k=4 and the check is in code"},
               "label_consuming_rules_excluded": ["oracle", "greedy", "indep"],
               "why_excluded": "R900/R907 established label access as a separate axis; mixing "
                               "them in would reproduce that confound",
               "objective_split_read_from_source": {"topw": "highest MEAN importance score",
                                                    "topabs": "largest |mean|, most polarising "
                                                              "either way"},
               "overlap_is_about_the_inventory": "if the intervals overlap that is a statement "
                                                 "about inventory size, not evidence the "
                                                 "objective is irrelevant",
               "unit_note": "counts are ARMS; share = admitted/built",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "selection_objective.json", "w"), indent=2)
    print(f"\n  artifact: results/selection_objective.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

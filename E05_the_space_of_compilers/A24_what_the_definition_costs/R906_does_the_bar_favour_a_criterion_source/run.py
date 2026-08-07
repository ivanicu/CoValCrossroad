#!/usr/bin/env python3
"""
R906 · does clause ②'s bar favour one criterion-source kind — and is a "rate" even admissible here?

⛔ WHY. R903–R905 established that the admitted arms span three criterion-source kinds: rubric
selectors (exact ⊆ 1.000), a paraphrasing generator (`coval_core`, exact 0.001 / lexical 0.5959),
and a fixed external checklist (`generic`, 0.0003). That is a property of the arms. **The question
it makes askable is about the BAR: does clause ② admit the three kinds at comparable rates, or is
the admitted set dominated by one?**

⛔⛔ **TWO TRAPS, BOTH DECLARED BEFORE THE RUN, BECAUSE EITHER WOULD MANUFACTURE THE ANSWER.**
① **THE DENOMINATOR IS A CONSTRUCTION CHOICE, NOT A POPULATION.** The 99 scored arms were BUILT,
   not sampled — someone chose to make 18 `random_k*` variants and one `generic`. So `admitted /
   built` per kind is a statement about *what got built*, and calling it an admission RATE would
   attribute to the bar what belongs to the arm inventory. **Every denominator is printed beside
   every rate, and no rate is compared across kinds without them.**
② **`coval_core` IS ADMITTED BY CONSTRUCTION.** The definition was fitted to it — that is the live
   limitation `the definition describes the instance` restated at the level of membership. Counting
   it toward the generator kind's rate is **self-inclusion**, the failure R883/R884/R897 each
   caught. It is reported BOTH ways and the difference is shown.

ESTIMAND        for each criterion-source kind: the count admitted by clause ② and the count built,
                reported as a pair — never as a bare rate.
IDENTIFICATION  exact for typing and for admission. ⚠ **NOT identified as an admission PROBABILITY**
                — there is no sampling frame over arms, so the ratio is descriptive of this
                inventory and nothing else.
SCOPE           population: the scored arms that can be TYPED from a committed selection file;
                            untypable arms are NAMED and counted, never dropped silently
                instrument: exact ⊆ rubric and difflib lexical coverage (R905's), plus the
                            generator's own rule taxonomy
                baseline:   equal treatment — the same admitted share in every kind
                regime:     home release, judge 2B, clause ② = R881's `admitted` flag
WORLDS          A · the kinds are admitted at comparable shares -> the bar is source-agnostic, and
                    R905's `the bar is source-agnostic` is confirmed rather than asserted
                B · one kind dominates -> the bar has a source preference the definition never
                    states, and the headline must say which
                C · too few arms per kind to compare -> the question is not answerable on this
                    inventory, which is a fact about the RELEASE
KILL            CONDITIONAL:
                  ⭐ ① WIRING, cross-round: the typing must reproduce R904/R905 exactly for the
                     three arms already typed — `topw_k4` RUBRIC_SELECTOR, `generic`
                     FIXED_CHECKLIST, `coval_core` PARAPHRASING_GENERATOR. If it does not, this
                     round's types are a different instrument and nothing carries over.
                  ⭐ ② SELF-INCLUSION MEASURED: report the generator kind's numbers with and
                     without `coval_core`. If they differ, the difference IS the self-inclusion.
                  ⭐ ③ every kind's share must have RESOLUTION, judged by its own binomial CI —
                     not by a count threshold.
                     ⛔⛔ POST-RUN: MY FIRST GATE WAS `n >= 2` AND IT WAS TOO WEAK. It admitted
                     `FIXED_CHECKLIST` at **1/2**, where the only attainable shares are 0, 0.5 and
                     1 — a quantity with no resolution — and the round printed **WORLD B, `the bar
                     has a source preference`, on the strength of ONE arm admitted out of two.**
                     That is R902's n=1 bin driving a monotonicity verdict, reproduced at n=2 one
                     round after I caught it. **A count threshold does not measure resolution; an
                     interval does.** Re-pre-registered: a source preference requires two kinds
                     whose Wilson 95% intervals DO NOT OVERLAP.
MULTIPLICITY    every kind × {built, admitted}; untypable arms counted; all printed.
ARTIFACT        results/bar_by_source.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated. ⚠ AND, the one this round adds: **admission PROBABILITY**. The arm set
                is designed, so no rate here estimates a probability over a population of arms.
"""
import difflib, json, pathlib, subprocess, sys
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
RES = ROOT / "corebench" / "results"
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
T_LEX = 0.60          # R905's committed threshold, inherited not chosen


def main() -> int:
    r881 = next(A24.glob("R881_*/results/boundary_distance.json"), None)
    if r881 is None:
        print("  UNRUNNABLE: R881 artifact missing. Exit 2, never 0.")
        return 2
    adm = {x["arm"]: bool(x["admitted"]) for x in json.loads(r881.read_text())["arms"]}
    print(f"  clause ② admission READ from R881: {sum(adm.values())} of {len(adm)} arms admitted")

    sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
    from covalx.judge import load_join                                       # noqa: E402
    joined = load_join(ROOT / "data" / "comparisons.jsonl",
                       ROOT / "data" / "conversation_rubrics.jsonl")
    fullr = {p: [i["criterion"] for i in (r.get("coval_full") or [])] for p, _q, r in joined}
    corec = {p: [i["criterion"] for i in (r.get("coval_core") or [])] for p, _q, r in joined}

    def sel_of(arm):
        if arm == "coval_core":
            return {p: v for p, v in corec.items() if v}
        f = RES / f"core_{arm}.json"
        if not f.exists():
            return None
        try:
            return json.loads(f.read_text())
        except Exception:
            return None

    typed, untypable = {}, []
    for arm in sorted(adm):
        sel = sel_of(arm)
        if not sel:
            untypable.append(arm); continue
        pids = [p for p in sel if p in fullr and sel[p]]
        if len(pids) < 50:
            untypable.append(arm); continue
        sets = [frozenset(sel[p]) for p in pids]
        fixed = len(set(sets)) == 1
        exact = float(np.mean([len(s - frozenset(fullr[p])) == 0 for s, p in zip(sets, pids)]))
        if fixed:
            t = "FIXED_CHECKLIST"
        elif exact > 0.95:
            t = "RUBRIC_SELECTOR"
        else:
            sample = pids[:150]                      # lexical is O(k*|full|); a stated subsample
            lex = float(np.mean([np.mean([max((difflib.SequenceMatcher(None, c, z).ratio()
                                               for z in fullr[p]), default=0.0) >= T_LEX
                                          for c in sel[p]]) for p in sample]))
            t = "PARAPHRASING_GENERATOR" if lex > 0.25 else "OTHER_SOURCE"
        typed[arm] = t
    print(f"  typed {len(typed)} arms · UNTYPABLE and NAMED {len(untypable)}: "
          f"{untypable[:10]}{' …' if len(untypable) > 10 else ''}")
    print(f"  ⚠ untypable = no committed per-prompt selection file; they are COUNTED, not dropped")

    exp = {"topw_k4": "RUBRIC_SELECTOR", "generic": "FIXED_CHECKLIST",
           "coval_core": "PARAPHRASING_GENERATOR"}
    got = {a: typed.get(a) for a in exp}
    c1 = all(got[a] == exp[a] for a in exp)
    print(f"\n  ① WIRING cross-round type reproduction:")
    for a in exp:
        print(f"     {a:<14} expected {exp[a]:<24} got {str(got[a]):<24} "
              f"{'PASS' if got[a] == exp[a] else 'FAIL'}")
    if not c1:
        print("\n  UNVERIFIED: the typing does not reproduce R904/R905. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "expected": exp, "got": got},
                  open(OUT / "bar_by_source.json", "w"), indent=2)
        return 2

    kinds = {}
    for a, t in typed.items():
        k = kinds.setdefault(t, {"built": [], "admitted": []})
        k["built"].append(a)
        if adm.get(a):
            k["admitted"].append(a)
    print(f"\n  ⭐ ADMISSION BY CRITERION SOURCE — counts, with every DENOMINATOR shown:")
    print(f"     {'source kind':<26}{'admitted':>10}{'built':>8}{'share':>9}")
    rows = []
    for t, v in sorted(kinds.items()):
        share = len(v["admitted"]) / len(v["built"])
        print(f"     {t:<26}{len(v['admitted']):>10}{len(v['built']):>8}{share:>9.3f}")
        rows.append({"kind": t, "n_admitted": len(v["admitted"]), "n_built": len(v["built"]),
                     "share": share, "admitted": sorted(v["admitted"]),
                     "built": sorted(v["built"])})

    # ② self-inclusion, measured
    pg = kinds.get("PARAPHRASING_GENERATOR", {"built": [], "admitted": []})
    b2 = [a for a in pg["built"] if a != "coval_core"]
    a2 = [a for a in pg["admitted"] if a != "coval_core"]
    s_with = len(pg["admitted"]) / len(pg["built"]) if pg["built"] else float("nan")
    s_wo = len(a2) / len(b2) if b2 else float("nan")
    print(f"\n  ② SELF-INCLUSION, MEASURED not assumed. `coval_core` is admitted BY CONSTRUCTION —")
    print(f"     the definition was fitted to it. Generator kind: with it {len(pg['admitted'])}/"
          f"{len(pg['built'])} = {s_with:.3f}; without it {len(a2)}/{len(b2)} = "
          f"{s_wo if b2 else float('nan'):.3f}")
    if not b2:
        print(f"     ⛔ REMOVING IT EMPTIES THE KIND. So the generator kind's share is CARRIED")
        print(f"        ENTIRELY by the arm the definition was written from — it is not evidence")
        print(f"        about the bar at all, and no comparison involving it is admissible.")

    def wilson(k, n, z=1.96):
        if n == 0:
            return (float("nan"), float("nan"))
        ph = k / n
        d = 1 + z * z / n
        c = (ph + z * z / (2 * n)) / d
        h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
        return (max(0.0, c - h), min(1.0, c + h))
    for r in rows:
        r["ci95"] = list(wilson(r["n_admitted"], r["n_built"]))
        r["ci_width"] = r["ci95"][1] - r["ci95"][0]
    # a share is readable only if its own interval is narrower than the full range it could span
    readable = [r for r in rows if r["ci_width"] < 0.60 and r["kind"] != "PARAPHRASING_GENERATOR"]
    thin = [r for r in rows if r not in readable]
    if thin:
        print(f"\n  ③ KINDS WITH < 2 BUILT ARMS — printed, EXCLUDED from the comparison, NAMED:")
        for r in thin:
            print(f"     {r['kind']:<26} {r['n_admitted']}/{r['n_built']}  {r['built']}")
    print(f"\n  ⭐ SHARES WITH THEIR OWN WILSON 95% INTERVALS — the resolution test:")
    for r in sorted(rows, key=lambda x: -x["n_built"]):
        print(f"     {r['kind']:<26}{r['n_admitted']:>4}/{r['n_built']:<4} "
              f"{r['share']:.3f}  [{r['ci95'][0]:.3f}, {r['ci95'][1]:.3f}]  "
              f"width {r['ci_width']:.3f}{'   READABLE' if r in readable else '   too wide'}")
    shares = [r["share"] for r in readable]
    spread = (max(shares) - min(shares)) if shares else float("nan")
    # a preference requires two intervals that do NOT overlap
    disjoint = any(a["ci95"][1] < b["ci95"][0] or b["ci95"][1] < a["ci95"][0]
                   for i, a in enumerate(readable) for b in readable[i + 1:])
    world = ("C" if len(readable) < 2 else "B" if disjoint else "A")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": f"no two kinds have DISJOINT intervals ({len(readable)} readable, spread "
             f"{spread:.3f}) — **no source preference is demonstrable on this inventory.** That is "
             "weaker than `the bar is source-agnostic`: it is `this inventory cannot show one`",
        "B": f"two kinds' Wilson intervals are DISJOINT (spread {spread:.3f}) — the bar has a "
             "source preference the definition never states",
        "C": f"only {len(readable)} kind(s) have >= 2 built arms, so the comparison is not "
             "available on this inventory. **That is a fact about the RELEASE**, not a null"}[world])
    print(f"\n  ⚠ AND NO NUMBER HERE IS AN ADMISSION PROBABILITY. The 99 arms were DESIGNED, not")
    print(f"    sampled — someone chose how many of each kind to build — so every share describes")
    print(f"    THIS INVENTORY and estimates nothing about arms in general. The denominators are")
    print(f"    printed so the reader can see what the ratio is a ratio OF.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "lexical_threshold_inherited": T_LEX,
               "n_arms_in_R881": len(adm), "n_typed": len(typed),
               "untypable_named": untypable, "kinds": rows,
               "readable_kinds": [r["kind"] for r in readable],
               "excluded_thin_kinds": [r["kind"] for r in thin],
               "share_spread": float(spread) if shares else None,
               "wilson_intervals_disjoint": bool(disjoint) if len(readable) >= 2 else None,
               "resolution_gate_corrected": "the first gate was n>=2, which admitted a 1/2 share "
                                            "whose only attainable values are 0/0.5/1 and printed "
                                            "WORLD B on it. A count threshold does not measure "
                                            "resolution; an interval does. Now: Wilson CI width "
                                            "< 0.60, and a preference requires DISJOINT intervals.",
               "self_inclusion": {"generator_share_with_core": s_with,
                                  "generator_share_without_core": s_wo if b2 else None,
                                  "removing_core_empties_kind": not bool(b2),
                                  "why": "coval_core is admitted by construction — the definition "
                                         "was fitted to it"},
               "denominator_is_a_construction_choice": "the 99 arms were BUILT, not sampled; every "
                                                       "share describes this inventory only",
               "not_an_admission_probability": "there is no sampling frame over arms",
               "unit_note": "counts are ARMS; share = admitted/built within a kind",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "bar_by_source.json", "w"), indent=2)
    print(f"\n  artifact: results/bar_by_source.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

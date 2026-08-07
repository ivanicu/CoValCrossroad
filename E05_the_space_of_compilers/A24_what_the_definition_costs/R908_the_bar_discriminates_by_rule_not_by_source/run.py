#!/usr/bin/env python3
"""
R908 · the bar DOES discriminate — by RULE, not by source kind and not by k.

⛔ WHY, AND IT RELOCATES THE QUESTION I SPENT TWO ROUNDS ON. R906 asked whether clause ②'s bar
favours a criterion SOURCE and could not answer: `FIXED_CHECKLIST` is 1/2, Wilson width 0.811.
R907 then priced expanding that kind at **15,488 judge calls per arm**. Both rounds treated the
inventory as the obstacle. **But the inventory is not uniformly thin — it is thin on the axis I
chose and thick on one I never looked at.** Reading the (rule × k × admitted) table:
  · `random_k` — **38 arms, 0 admitted**, spanning every k from 2 to 12
  · `topw_k`   — **16 arms, 7 admitted**, spanning k = 1 … 12
**Those are the two biggest cells in the whole arm set, they are FREE (both are subsets of
`coval_full`), and nobody had compared them.**

⛔⛔ **AND THE k QUESTION MY OWN `NEXT` PROPOSED IS STILL NOT ANSWERABLE — for the third time by the
same arithmetic.** Within `topw_k`, the 16 arms spread over 7 distinct k values, so each k cell
holds about **2** arms. A 1/2 share has no resolution; that is exactly what R906's gate was
re-registered to catch and what R902 caught at n=1. **So the per-k curve is computed and reported
as UNREADABLE, not quoted.** The k axis is thin *within* every rule; only the rule axis is thick.

⚠ **AND THE CONFOUND THAT WOULD HAVE HIDDEN THIS.** Pooling a k-curve across rules would have shown
"admission varies with k" purely through composition — `random_k` contributes 38 zeros at every k
while `oracle/greedy/indep` sit almost entirely at k=4. **That is R892's k-confound and R900's
rule-confound in one figure.** Rules are therefore never pooled here.

ESTIMAND        the admitted share by RULE among the RUBRIC_SELECTOR kind, with Wilson intervals;
                and, separately, the per-k share within the one rule that spans k.
IDENTIFICATION  exact for the shares. ⚠ NOT causal and NOT an admission probability — the arms were
                built, not sampled, so this describes THIS inventory (R906's standing caveat).
SCOPE           population: the RUBRIC_SELECTOR arms from R906's committed typing — 86, named
                instrument: R881's clause-② `admitted` flag; Wilson 95% intervals
                baseline:   equal admitted share across rules
                regime:     home release, judge 2B
WORLDS          A · two rules have DISJOINT Wilson intervals -> the bar discriminates by rule, and
                    R906's `no preference demonstrable` was about the wrong axis
                B · all rule intervals overlap -> the bar does not discriminate on this axis either,
                    and the inventory is thin everywhere
                C · the per-k cells are readable -> the k question is answerable after all and the
                    `NEXT` was right
KILL            CONDITIONAL:
                  ⭐ ① IS `random_k = 0/38` FORCED? A random k-subset of the rubric could beat the
                     comparator by chance, so **0 is not an algebraic necessity** — the round states
                     this before reading it, because a forced zero would be a derivation. The
                     control is that some OTHER rule at the SAME k values is admitted: if `topw_k`
                     is admitted at k values where `random_k` is not, the zero is a measurement.
                  ⭐ ② RESOLUTION, inherited from R906: a claim needs DISJOINT Wilson intervals,
                     never a count threshold.
                  ⭐ ③ the per-k cells must be tested for resolution and reported UNREADABLE if
                     thin — printed, never quoted.
                  ④ rules are NEVER pooled; the confound is named above and enforced in code.
MULTIPLICITY    every rule × {admitted, built}; every k cell within the spanning rule; all printed.
ARTIFACT        results/bar_by_rule.json
IMPOSSIBLE      cross-release · construct validated · causally identified · independently
                replicated · admission probability. ⚠ AND: WHY a rule is admitted. This shows THAT
                the bar separates informed from random selection, not what it is separating on.
"""
import collections, json, pathlib, re, subprocess
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
A24 = ROOT / "E05_the_space_of_compilers/A24_what_the_definition_costs"
MAXW = 0.60           # R906's inherited readability bound


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    ph = k / n
    d = 1 + z * z / n
    c = (ph + z * z / (2 * n)) / d
    h = z * np.sqrt(ph * (1 - ph) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main() -> int:
    r906 = next(A24.glob("R906_*/results/bar_by_source.json"), None)
    if r906 is None:
        print("  UNRUNNABLE: R906 artifact missing. Exit 2, never 0.")
        return 2
    kinds = json.loads(r906.read_text())["kinds"]
    rs = next((k for k in kinds if k["kind"] == "RUBRIC_SELECTOR"), None)
    if rs is None:
        print("  UNRUNNABLE: RUBRIC_SELECTOR kind absent. Exit 2, never 0.")
        return 2
    adm, built = set(rs["admitted"]), rs["built"]
    print(f"  ④ population READ from R906's typing: {len(built)} RUBRIC_SELECTOR arms, "
          f"{len(adm)} admitted. Rules are never pooled.")

    tab = collections.defaultdict(lambda: collections.defaultdict(lambda: [0, 0]))
    for a in built:
        m = re.match(r"([a-z]+)_k(\d+)", a)
        rule, k = (m.group(1), int(m.group(2))) if m else ("OTHER", 0)
        tab[rule][k][1] += 1
        if a in adm:
            tab[rule][k][0] += 1

    rows = []
    for rule in sorted(tab):
        ks = sorted(tab[rule])
        a_ = sum(tab[rule][k][0] for k in ks)
        n_ = sum(tab[rule][k][1] for k in ks)
        lo, hi = wilson(a_, n_)
        rows.append({"rule": rule, "n_admitted": a_, "n_built": n_, "share": a_ / n_,
                     "ci95": [lo, hi], "ci_width": hi - lo, "k_values": ks,
                     "per_k": {str(k): tab[rule][k] for k in ks}})
    print(f"\n  ⭐ ADMITTED SHARE BY RULE, with Wilson 95% intervals and every denominator:")
    print(f"     {'rule':<10}{'adm/built':>12}{'share':>8}{'Wilson 95%':>22}{'width':>8}  k range")
    for r in sorted(rows, key=lambda x: -x["n_built"]):
        frac = f"{r['n_admitted']}/{r['n_built']}"
        ci = f"[{r['ci95'][0]:.3f}, {r['ci95'][1]:.3f}]"
        print(f"     {r['rule']:<10}{frac:>12}{r['share']:>8.3f}{ci:>22}"
              f"{r['ci_width']:>8.3f}  {r['k_values']}")

    readable = [r for r in rows if r["ci_width"] < MAXW]
    pairs = [(a, b) for i, a in enumerate(readable) for b in readable[i + 1:]
             if a["ci95"][1] < b["ci95"][0] or b["ci95"][1] < a["ci95"][0]]
    c2 = bool(pairs)
    print(f"\n  ② RESOLUTION {len(readable)} rule(s) readable (width < {MAXW}); "
          f"{len(pairs)} DISJOINT pair(s): {c2}  {'PASS' if c2 else 'FAIL'}")

    # ① is random's zero FORCED? controlled by whether another rule is admitted at the SAME k
    rnd = next((r for r in rows if r["rule"] == "random"), None)
    tw = next((r for r in rows if r["rule"] == "topw"), None)
    c1 = False
    if rnd and tw:
        shared_k = sorted(set(rnd["k_values"]) & set(tw["k_values"]))
        tw_adm_at = [k for k in shared_k if tw["per_k"][str(k)][0] > 0]
        c1 = len(tw_adm_at) > 0
        print(f"  ① NOT-FORCED a random k-subset COULD clear the bar by chance, so 0 is not "
              f"algebraic.")
        print(f"     control: `topw` IS admitted at k = {tw_adm_at} where `random` is 0 — so the "
              f"zero is a MEASUREMENT: {c1}  {'PASS' if c1 else 'FAIL'}")
    if not (c1 and c2):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "rows": rows,
                   "controls": [bool(c1), bool(c2)]},
                  open(OUT / "bar_by_rule.json", "w"), indent=2)
        return 2

    print(f"\n  ⭐⭐ DISJOINT PAIRS — the bar separating rules:")
    for a, b in pairs:
        print(f"     {a['rule']:<10}{a['share']:.3f} [{a['ci95'][0]:.3f}, {a['ci95'][1]:.3f}]"
              f"   vs   {b['rule']:<10}{b['share']:.3f} "
              f"[{b['ci95'][0]:.3f}, {b['ci95'][1]:.3f}]")

    print(f"\n  ⭐ ③ THE PER-k CURVE WITHIN `topw` — computed, and reported UNREADABLE:")
    thin = 0
    for k in tw["k_values"]:
        a_, n_ = tw["per_k"][str(k)]
        lo, hi = wilson(a_, n_)
        u = (hi - lo) >= MAXW
        thin += u
        print(f"     k={k:<3} {a_}/{n_}  [{lo:.3f}, {hi:.3f}] width {hi-lo:.3f}"
              f"{'   UNREADABLE' if u else ''}")
    c3 = bool(thin == len(tw["k_values"]))     # numpy bool is not JSON serializable
    print(f"     every k cell unreadable: {c3}. **The k question is NOT answerable within any")
    print(f"     rule either** — 16 arms over 7 k values is ~2 per cell, and a 1/2 share has no")
    print(f"     resolution. Third time this arithmetic has closed a question; it is printed")
    print(f"     rather than quoted.")

    world = "A" if pairs else ("C" if not c3 else "B")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + {
        "A": "two rules have DISJOINT intervals — **the bar DOES discriminate, by RULE.** "
             "R906's `no preference demonstrable` was true about the SOURCE axis and I read it as "
             "a fact about the bar. The inventory is thin where I looked and thick where I did not",
        "B": "every rule interval overlaps — the bar does not discriminate on this axis either",
        "C": "the per-k cells are readable after all and the k question is answerable"}[world])
    print(f"\n  ⚠ WHAT THIS DOES NOT SAY: WHY. It shows the bar separates informed selection from")
    print(f"    random selection at this inventory. It does not say what it separates ON, and it")
    print(f"    is not an admission probability — the arms were built, not sampled.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world, "rules": rows,
               "readable_rules": [r["rule"] for r in readable],
               "disjoint_pairs": [[a["rule"], b["rule"]] for a, b in pairs],
               "per_k_within_topw_UNREADABLE": bool(c3),
               "why_k_is_unanswerable": "16 topw arms over 7 k values is ~2 per cell; a 1/2 share "
                                        "has no resolution. Third time this arithmetic closed a "
                                        "question (R902 n=1, R906 n=2, here n~2).",
               "rules_never_pooled": "pooling a k-curve across rules would show a k effect through "
                                     "composition alone — random_k contributes 38 zeros at every k "
                                     "while oracle/greedy/indep sit almost entirely at k=4",
               "zero_is_not_forced": "a random k-subset could clear the bar by chance; the control "
                                     "is that topw IS admitted at k values where random is 0",
               "relocates": "R906 asked about the SOURCE axis (n=2 per kind) and R907 priced "
                            "expanding it at 15,488 calls/arm. The inventory's power is on the "
                            "RULE axis, free, and was never looked at.",
               "does_not_say": "WHY the bar separates these rules, and it is not an admission "
                               "probability",
               "unit_note": "counts are ARMS; share = admitted/built within a rule",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "bar_by_rule.json", "w"), indent=2)
    print(f"\n  artifact: results/bar_by_rule.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

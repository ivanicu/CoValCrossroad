#!/usr/bin/env python3
"""
R947 · the currency gate checks 7 facts I chose. Turn it around: of the NUMBERS in the definition's
        own statement, how many are traceable to a committed artifact?

⛔ WHY THIS AND NOT THE ROUND I WAS ABOUT TO BUILD. The next step from R946 was another reader
iteration. Before that, the prior-art gate (L20/P4) was run on the question that looked most
load-bearing — *does the definition's extension depend on which judge J instantiates it* — and **it is
not a gap.** `DEFINITION.md:2959` already states *"the admitted set is empty at the second judge; only
`a core under J` is licensed"*, `:4157` is `R536 · The selector ordering survives a second judge`, and
R414, R359, R290, R492 exist. Its own line reads *"The wall fell first, for the sixth time."*
**A round that would have re-derived a settled result was stopped by asking the repo instead of my
memory**, which is the entire point of the gate.

⭐ **WHAT IS ACTUALLY OPEN, AND IT IS ABOUT THE DELIVERABLE.** `assurance/a_statement_is_current_with_
the_arc.py` passes 7/7. **Those 7 facts are a list I hand-wrote, covering R920–R926 only** — it cannot
see a fact from R927 onward, nor from the 900 rounds before. That is the defect R943–R946 spent four
rounds establishing in another gate: *a hand-written vocabulary cannot detect what it does not name.*
So the gate certifies that the statement SAYS seven things, and says nothing about the rest of it.

⭐⭐⭐ **THE REVERSE QUESTION HAS NEVER BEEN ASKED AND IS STRICTLY MORE LOAD-BEARING.** Not *does the
statement contain the artifacts' facts* but **do the statement's own numbers come from artifacts at
all?** A number in the definition that no committed round produced is precisely the failure this
programme exists to prevent, and it is mechanically checkable.

⚠ **AND A STRING SEARCH FOR A NUMERAL IS A COINCIDENCE ENGINE, SO THE FLOOR IS MEASURED, NOT
ASSUMED.** `2` and `0` match everywhere and mean nothing. The instrument therefore ① restricts to
numerals precise enough to be non-coincidental, ② compares NUMERICALLY at the printed precision rather
than as text, and ③ measures its own false-match rate by PERTURBING each numeral's last digit and
re-running the identical search. **If perturbed numerals match at the same rate, the instrument is
measuring the density of floats in the corpus and nothing else.**

ESTIMAND        of the high-precision numerals appearing in the definition's statement region, the
                share for which some committed results artifact holds a value equal at the numeral's
                own printed precision — and the same share for last-digit-perturbed numerals, which
                is the coincidence floor.
IDENTIFICATION  identified as a rate against a measured floor. NOT identified as `this number is
                correct`: a match shows some artifact holds that value, never that it holds it for
                the quantity the statement attributes it to. Bounds, and the direction is named.
SCOPE           population: every numeral with >=3 decimal places in the statement region, where the
                            region is computed by IMPORTING the gate's own `statement_region`, not
                            re-derived — a round that re-derives its population can move it
                instrument: numeric comparison at the numeral's printed precision against every float
                            in every non-provisional results JSON in the repo
                baseline:   the perturbed-numeral match rate, 3 seeds
                regime:     HEAD, one release, one repo
WORLDS          A · every numeral traces, and the floor is well below -> the statement is sourced,
                    and the R917–R926 additions rest on committed artifacts
                B · some do not trace above the floor -> those numerals are UNVERIFIED and are named;
                    the gate that certifies consistency never looked at them, because they are not
                    among the seven facts it was told to check
                C · the floor is comparable to the real rate -> the instrument is a coincidence
                    engine and neither answer is admissible
KILL            CONDITIONAL:
                  ⭐ ① POSITIVE: numerals this arc measured and committed — `0.009103` (R923's
                     margin) and `0.9984` (R920's R²) — must trace. If a number I watched being
                     written to an artifact does not trace, the search is broken and nothing below
                     is readable.
                  ⭐ ② FLOOR / NEGATIVE, MEASURED: every numeral's last digit is perturbed and the
                     identical search re-run, 3 seeds. **If the perturbed rate is within the real
                     rate's spread the round is World C and no share is admissible** — that is the
                     g=0 branch, and it is the one that matters because a numeral search is exactly
                     the instrument this project has been burned by.
                  ⭐ ③ POPULATION FROM THE OBJECT: the region is the gate's own function, imported.
                     Its line count must match what the gate reports (648).
                  ⭐ ④ EVERY NON-TRACING NUMERAL NAMED with its line and its surrounding phrase, so
                     the call is checkable rather than countable.
                  ⭐ ⑤ THREE-VALUED: a non-match is UNVERIFIED, never `fabricated`. A number can be
                     derived in prose from two committed numbers and appear in no artifact.
MULTIPLICITY    N numerals × {real, 3 perturbation seeds}; every cell printed, non-tracers named.
ARTIFACT        results/numbers_trace.json
IMPOSSIBLE      independently replicated · cross-release · construct validated · criterion validated —
                one repo, one release. ⚠ AND: **attribution is not measured.** A match proves some
                artifact holds the value; it cannot prove the artifact holds it for the quantity the
                statement says. Closing that needs a per-numeral read, and it is named, not assumed
                away.
"""
import json, pathlib, random, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(ROOT / "assurance"))
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip", re.I)
NUMERAL = re.compile(r"(?<![\w.])(\d+\.\d{3,})(?![\w])")
SEEDS = (11, 23, 37)
INSTRUMENT_UNIT = "some artifact holds a value equal to this numeral at its printed precision"
CLAIM_UNIT = "this numeral was produced by a committed round for the quantity claimed"


def floats(doc, out):
    if isinstance(doc, dict):
        for v in doc.values():
            floats(v, out)
    elif isinstance(doc, list):
        for v in doc:
            floats(v, out)
    elif isinstance(doc, bool):
        return
    elif isinstance(doc, (int, float)):
        out.append(float(doc))
    elif isinstance(doc, str):
        for m in NUMERAL.finditer(doc):
            out.append(float(m.group(1)))


def main() -> int:
    try:
        from a_statement_is_current_with_the_arc import statement_region
    except Exception as e:
        print(f"  UNRUNNABLE: cannot import the gate's own region function: {e}. Exit 2.")
        return 2
    text = (ROOT / "E05_the_space_of_compilers/DEFINITION.md").read_text()
    region = statement_region(text)
    if region is None:
        print("  UNRUNNABLE: the gate's region function found no statement. Exit 2, never 0.")
        return 2
    nlines = len(region.splitlines())
    c3 = nlines == 648
    print(f"  ③ POPULATION FROM THE OBJECT — region imported from the gate, {nlines} lines, gate "
          f"reports 648: {c3}  {'PASS' if c3 else 'FAIL — the population moved'}")
    print(f"  ⑤ UNITS — instrument: `{INSTRUMENT_UNIT}`")
    print(f"          claim:      `{CLAIM_UNIT}`   equal: {INSTRUMENT_UNIT == CLAIM_UNIT}")
    print(f"          -> a match bounds sourcing from ABOVE; attribution is NOT measured.")

    lines = region.splitlines()
    seen, numerals = set(), []
    for i, l in enumerate(lines, 1):
        for m in NUMERAL.finditer(l):
            s = m.group(1)
            if s in seen:
                continue
            seen.add(s)
            numerals.append({"numeral": s, "line": i, "context": l.strip()[:110]})
    print(f"\n  {len(numerals)} distinct numerals with >=3 decimal places in the statement region")

    # ⛔ EXCLUDE THIS ROUND'S OWN RESULTS. Measured, not anticipated: the first run wrote
    # numbers_trace.json -- which lists every numeral it had just failed to find -- into the very
    # tree it searches, and the identical second run returned 145/145 with the pool grown by 158
    # floats. A measurement that writes into its own population improves on re-run, silently and
    # in the flattering direction, and nothing in the output says so.
    pool = []
    nfiles = 0
    for f in sorted(ROOT.glob("E0*/A*/R*/results/**/*.json")):
        if PROVISIONAL.search(f.name) or "_smoke_archive" in f.parts:
            continue
        if OUT in f.parents:
            continue
        try:
            floats(json.loads(f.read_text()), pool)
        except Exception:
            continue
        nfiles += 1
    print(f"  {len(pool):,} float values harvested from {nfiles:,} committed results files "
          f"(this round's OWN results excluded -- see the note at the loop)")

    # index once per decimal precision -- a linear scan per numeral would be tens of millions of
    # comparisons across the perturbation seeds, and the cost meter runs before the loop, not after
    precisions = sorted({len(r["numeral"].split(".")[1]) for r in numerals})
    index = {d: {round(v, d) for v in pool} for d in precisions}
    print(f"  indexed at precisions {precisions}: "
          f"{ {d: len(index[d]) for d in precisions} } distinct rounded values")

    def traces(s):
        d = len(s.split(".")[1])
        return round(float(s), d) in index[d]

    for r in numerals:
        r["traces"] = traces(r["numeral"])
    hit = [r for r in numerals if r["traces"]]
    miss = [r for r in numerals if not r["traces"]]
    real_rate = len(hit) / len(numerals) if numerals else float("nan")

    known = {"0.009103", "0.9984"}
    present = known & seen
    c1 = bool(present) and all(traces(k) for k in present)
    print(f"\n  ① POSITIVE — arc-committed numerals present in the region {sorted(present)} all "
          f"trace: {c1}  {'PASS' if c1 else 'FAIL — the search is broken'}")

    floor = []
    for seed in SEEDS:
        rng = random.Random(seed)
        ok = 0
        for r in numerals:
            s = r["numeral"]
            last = s[-1]
            alt = rng.choice([c for c in "0123456789" if c != last])
            if traces(s[:-1] + alt):
                ok += 1
        floor.append(ok / len(numerals))
        print(f"  ② FLOOR seed {seed} — last digit perturbed: {ok}/{len(numerals)} = "
              f"{ok/len(numerals):.3f}")
    fl_lo, fl_hi = min(floor), max(floor)
    c2 = real_rate > fl_hi
    print(f"     real {real_rate:.3f} vs floor [{fl_lo:.3f}, {fl_hi:.3f}]: {c2}  "
          f"{'PASS — the search is not a coincidence engine' if c2 else 'FAIL — perturbed numerals trace as often; the instrument measures float density'}")

    fl_mean = sum(floor) / len(floor)
    power = 1.0 - fl_mean
    c6 = power >= 0.5
    print(f"\n  ⑥ THE INSTRUMENT'S OWN DETECTION POWER — a deliberately WRONG numeral traces "
          f"{fl_mean:.3f} of the time, so this test would catch a fabricated number with "
          f"probability {power:.3f}: {c6}")
    print(f"     {'PASS — a non-trace is informative' if c6 else 'FAIL — the corpus holds ' + f'{len(pool):,}' + ' floats and matches almost any numeral of the right shape. `144 of 145 trace` is very nearly VACUOUS: the count is what a fabricated statement would also produce. Only the NON-tracers carry information, and even they are weak.'}")

    if not (c1 and c3):
        print("\n  UNVERIFIED: a control failed for its own reasons. Exit 2, never 0.")
        json.dump({"verdict": "UNVERIFIED", "c1": c1, "c3": c3},
                  open(OUT / "numbers_trace.json", "w"), indent=2)
        return 2

    print(f"\n  ④ EVERY NON-TRACING NUMERAL, NAMED — {len(miss)} of {len(numerals)}:")
    for r in miss:
        print(f"     L{r['line']:<5} {r['numeral']:<12} {r['context']}")

    world = "C" if not c2 else ("A" if not miss else "B")
    print(f"\n  ⭐⭐⭐ WORLD {world}: " + (
        f"all {len(numerals)} numerals trace to a committed artifact, against a coincidence floor of "
        f"[{fl_lo:.3f}, {fl_hi:.3f}]. The statement is sourced."
        if world == "A" else
        f"{len(hit)} of {len(numerals)} numerals trace ({real_rate:.3f}) against a coincidence floor "
        f"of [{fl_lo:.3f}, {fl_hi:.3f}]. **{len(miss)} do not**, and they are named above. "
        + (f"⛔ BUT READ ⑥ BEFORE READING THAT COUNT: a wrong numeral traces {fl_mean:.3f} of the "
           f"time, so the test's power against a fabricated number is only {power:.3f}. "
           f"**`{len(hit)} of {len(numerals)} trace` is very nearly vacuous** — a fabricated "
           f"statement would score about the same. The informative content of this round is the "
           f"{len(miss)} non-tracer, not the {len(hit)} tracers, and the sourcing question is "
           f"therefore NOT answered by a rate at this precision."
           if not c6 else
           f"The currency gate passes 7/7 while never looking at them, because they are not among "
           f"the seven facts it was told to check.")
        if world == "B" else
        f"perturbed numerals trace at [{fl_lo:.3f}, {fl_hi:.3f}] against a real rate of "
        f"{real_rate:.3f}. The search is a coincidence engine at this precision and NEITHER the "
        f"tracing nor the non-tracing count is admissible."))
    print(f"     ⚠ THREE-VALUED: a non-tracing numeral is UNVERIFIED, never `fabricated`. A number "
          f"derived in prose from two committed numbers appears in no artifact and is perfectly "
          f"sound.")
    print(f"     ⚠ AND ATTRIBUTION IS NOT MEASURED: a match proves some artifact holds the value, "
          f"never that it holds it for the quantity the statement attributes it to.")

    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    json.dump({"commit": head, "world": world,
               "units": {"instrument": INSTRUMENT_UNIT, "claim": CLAIM_UNIT, "equal": False,
                         "direction": "bounds sourcing from ABOVE; attribution not measured"},
               "region_lines": nlines, "n_numerals": len(numerals),
               "n_float_values": len(pool), "n_results_files": nfiles,
               "trace_rate": real_rate, "coincidence_floor": [fl_lo, fl_hi],
               "detection_power": {"wrong_numeral_traces": fl_mean, "power": power,
                                   "reading": ("a non-trace is informative" if c6 else
                                               "the corpus matches almost any numeral of the right "
                                               "shape; the TRACE COUNT is nearly vacuous and only "
                                               "the non-tracers carry information")},
               "floor_per_seed": floor,
               "non_tracing": miss, "tracing": [r["numeral"] for r in hit],
               "self_contamination": {
                   "observed": "the first run wrote its artifact into the tree it searches; the "
                               "identical second run returned 145/145 instead of 144/145 with 158 "
                               "more floats in the pool",
                   "fix": "this round's own results directory is excluded from the pool",
                   "general": "a measurement that writes into its own population improves on "
                              "re-run, in the flattering direction, and says nothing"},
               "prior_art_gate": "the cross-judge question was checked FIRST and is not a gap: "
                                 "DEFINITION.md:2959 and :4157 (R536) already settle it",
               "three_valued": "a non-tracing numeral is UNVERIFIED, never fabricated",
               "unit_note": "counts are DISTINCT NUMERALS",
               "live_limitation": "the definition describes the instance; one release, one core"},
              open(OUT / "numbers_trace.json", "w"), indent=2)
    print(f"\n  artifact: results/numbers_trace.json @ {head[:8]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

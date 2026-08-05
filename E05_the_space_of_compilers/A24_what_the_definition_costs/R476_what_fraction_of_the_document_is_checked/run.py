#!/usr/bin/env python3
"""R476 — what fraction of DEFINITION.md does the value gate actually check?

ESTIMAND
    COVERAGE = (numeric claims in DEFINITION.md whose text span is captured by at least one
    ASSERTIONS pattern) / (numeric claims in DEFINITION.md).  R475 established the numerator is
    reported alone -- "302 of 302 assertions" -- which is a statement about the LIST, not the
    DOCUMENT, and which let a corrupted `+0.1298` pass unnoticed.

IDENTIFICATION
    ⚠ THE DENOMINATOR IS NOT GIVEN BY THE OBJECT.  "A numeric claim" is a choice, so the estimand is
    only identified relative to an extraction rule.  It is therefore swept (G4) rather than fixed,
    and the SPREAD across rules is reported as part of the answer instead of being resolved by
    picking one.  A coverage figure quoted without its extractor is not a measurement.

    ⭐ AND COVERAGE IS DECIDED BY SPAN, NEVER BY VALUE.  Asking "does some anchor capture the string
    0.5?" would mark every `0.5` in the document as checked because one anchor captures a `0.5`
    somewhere else.  A number is COVERED iff its character span lies inside the span some anchor
    pattern captures AT THAT SITE.  This is the round's single load-bearing design decision.

SCOPE
    population  DEFINITION.md as committed at HEAD (1205 lines).
    instrument  the 302 regexes in assurance/definition_matches_the_record.py, unmodified.
    baseline    none needed -- this is a census, not a contrast.  Reported as a proportion with a
                Wilson interval, because a proportion over a finite document still has one.
    regime      one document, one gate.  Says nothing about the other three gates.

WORLDS
    A  SPOT-CHECK   coverage < 0.30 -- the gate audits a minority and 46 rounds of PASS read as more
                    than they were.  Predicts: most numbers uncovered under EVERY extractor.
    B  BROAD        coverage > 0.70 -- the gap R475 found is a rare miss, not the norm.
    C  UNIT-BOUND   the extractors disagree by more than 2x on the DENOMINATOR, so "coverage" is not
                    a well-posed quantity here and the honest output is a range, not a number.

PREDICTION MATRIX
                   coverage    extractor spread    what it licenses
    A  spot-check    <0.30          small          "the gate checks a sample" -- rewrite every PASS
    B  broad         >0.70          small          "the gate checks the document" -- R475 was a miss
    C  unit-bound     any           >2x            report the range; no single coverage number

PRE-REGISTERED KILL  (conditional, never a bare threshold)
    if positive_control_fires and negative_control_is_null:
        A if max-over-extractors coverage < 0.30 ; B if min-over-extractors > 0.70 ; else MIXED
        and independently: C if max(denominator)/min(denominator) > 2
    else:
        UNVERIFIED

CONTROLS
    POSITIVE   a number KNOWN to be anchored (the live anchor count, which the gate rewrote this
               round) must be classified COVERED.  If it is not, the span logic is broken.
    g=0        a number known NOT to be anchored -- `+0.1298`, the value R475 corrupted while the
               gate passed -- must be classified UNCOVERED.  This is what makes the positive control
               able to fail: a span rule that marks everything covered passes the positive control
               and fails here.
    NEGATIVE   a number that does not occur in the document must be found 0 times by every
               extractor.  Guards against an extractor that manufactures matches.
    PLACEBO    coverage computed against the anchors with every pattern REPLACED by a never-matching
               one must be exactly 0.000.

MULTIPLICITY  4 extractors reported whole, including the ones least favourable to the gate.

ARTIFACT  results/r476_coverage.json                  SEED n/a (deterministic census)

IMPOSSIBLE HERE, NAMED
    cross-dataset      -- would require a second document with its own anchor table.
    construct validated-- "is this string a CLAIM?" has no external gold standard; the four
                          extractors are the construct, which is why the spread is reported.
"""
import json, re, sys, pathlib
sys.path.insert(0, "assurance")
import definition_matches_the_record as G

DOC = pathlib.Path("E05_the_space_of_compilers/DEFINITION.md").read_text()

EXTRACTORS = {
    "bold_any":   r"\*\*([+−-]?\d[\d,]*\.?\d*)%?\*\*",       # a number the author emphasised
    "decimal":    r"(?<![\w.])([+−-]?\d+\.\d+)(?![\w.])",     # any decimal anywhere
    "sig2plus":   r"(?<![\w.])([+−-]?\d+\.\d{2,})(?![\w.])",  # >=2 decimal places: a measurement
    "all_number": r"(?<![\w.])([+−-]?\d[\d,]*\.?\d*)(?![\w.])",
}

def covered_spans(patterns):
    """-> list of (start,end) spans that the anchor patterns CAPTURE in the document.
    Span-based, never value-based: an anchor covers the site it matched, nothing else."""
    spans = []
    for pat in patterns:
        for m in re.finditer(pat, DOC):
            if m.lastindex:
                spans.append((m.start(m.lastindex), m.end(m.lastindex)))
    return spans

def coverage(extractor, patterns):
    spans = covered_spans(patterns)
    nums = [(m.start(1), m.end(1), m.group(1)) for m in re.finditer(extractor, DOC)]
    cov = [n for n in nums if any(s <= n[0] and n[1] <= e for s, e in spans)]
    return len(nums), len(cov), nums, cov

PATS = list(G.ASSERTIONS.values())
print(f"  anchors in the gate: {len(PATS)}     document: {len(DOC.splitlines())} lines\n")
print(f"  {'extractor':<12} {'numeric claims':>14} {'covered':>8} {'coverage':>9}   95% Wilson")
res = {}
for name, ex in EXTRACTORS.items():
    n, c, nums, cov = coverage(ex, PATS)
    p = c / n if n else float("nan")
    z = 1.959964
    d = 1 + z*z/n; ctr = (p + z*z/(2*n))/d
    hw = z*((p*(1-p)/n + z*z/(4*n*n))**0.5)/d
    res[name] = {"n": n, "covered": c, "coverage": p, "lo": ctr-hw, "hi": ctr+hw}
    print(f"  {name:<12} {n:>14} {c:>8} {p:>9.4f}   [{ctr-hw:.4f}, {ctr+hw:.4f}]")

# ---- controls ---------------------------------------------------------------
# POSITIVE, DERIVED FROM THE OBJECT.  The first version asserted the document contains `**302**`
# as a standalone bolded number.  It does not -- it writes `**Declaration coverage is 27 of 302
# anchors...**`, with the number INSIDE a longer bolded span.  That control was validated against
# my idea of the document's syntax, not the document (CLAUDE.md P4, "control validated on imagined
# cases").  Correct form: take an anchor that actually fires, read the value IT captured, and
# require the extractor to mark that exact site covered.
_probe = None
for _name, _pat in G.ASSERTIONS.items():
    _m = re.search(_pat, DOC)
    if _m and _m.lastindex and re.fullmatch(r"\d+\.\d+", _m.group(_m.lastindex)):
        _probe = (_name, _m.group(_m.lastindex), _m.start(_m.lastindex)); break
n_, c_, nums_, cov_ = coverage(EXTRACTORS["decimal"], PATS)
pos = _probe is not None and any(s == _probe[2] for s, _e, _v in cov_)
print(f"\n  probe anchor: {_probe[0]} captured {_probe[1]!r} at char {_probe[2]}" if _probe
      else "\n  ⛔ no anchor captures a decimal -- probe unavailable")
g0  = not any(v in ("0.1298", "+0.1298") for *_, v in cov_)
# NEGATIVE, rebuilt: the first version mangled each extractor's lookbehind into an invalid
# pattern and CRASHED -- a control that cannot run is not a control.  Correct form: a literal
# absent from the document must be extracted 0 times by every rule, and present when injected.
ABSENT = "0.99999999"
neg = (DOC.count(ABSENT) == 0 and
       all(not any(v.strip("+−-") == ABSENT for *_, v in
                   [(m.start(1), m.end(1), m.group(1)) for m in re.finditer(ex, DOC)])
           for ex in EXTRACTORS.values()) and
       # and the extractor DOES see it once injected -- otherwise the zero is blindness, not absence
       any(m.group(1) == ABSENT for m in re.finditer(EXTRACTORS["decimal"], DOC + f" **{ABSENT}** ")))
pla = coverage(EXTRACTORS["bold_any"], [r"(?!x)x(ZZZ)"])[1] == 0
print(f"\n  POSITIVE  the site an anchor actually captured is classified COVERED       : {pos}")
print(f"  g=0       `+0.1298` (R475's corrupted value) is classified UNCOVERED     : {g0}")
print(f"  NEGATIVE  a number absent from the document is found 0 times            : {neg}")
print(f"  PLACEBO   coverage under never-matching anchors is exactly 0            : {pla}")

dens = [r["n"] for r in res.values()]; covs = [r["coverage"] for r in res.values()]
if not (pos and g0 and neg and pla):
    verdict, world = "UNVERIFIED", "controls failed"
else:
    ratio = max(dens)/min(dens)
    world = "A (spot-check)" if max(covs) < 0.30 else "B (broad)" if min(covs) > 0.70 else "MIXED"
    if ratio > 2: world += f" + C (unit-bound, denominator spread {ratio:.1f}x)"
    verdict = "MEASURED"
    print(f"\n  denominator spread across extractors: {min(dens)}..{max(dens)} = {ratio:.2f}x")
    print(f"  coverage range across extractors    : {min(covs):.4f}..{max(covs):.4f}")
print(f"\n  VERDICT {verdict}   world: {world}")
print(f"\n  ⭐ the sentence the gate may print: 'N of {len(PATS)} assertions' is a fact about the LIST.")
print(f"     the fact about the DOCUMENT is {min(covs):.1%}-{max(covs):.1%} of its numeric claims, "
      f"depending\n     on what counts as one -- and that spread is not a defect of the measurement, "
      f"it IS the answer.")

out = pathlib.Path("E05_the_space_of_compilers/A24_what_the_definition_costs/"
                   "R476_what_fraction_of_the_document_is_checked/results")
out.mkdir(parents=True, exist_ok=True)
json.dump({"anchors": len(PATS), "extractors": res, "verdict": verdict, "world": world,
           "controls": {"positive": pos, "g0": g0, "negative": neg, "placebo": pla}},
          open(out/"r476_coverage.json", "w"), indent=2)
sys.exit(0 if verdict != "UNVERIFIED" else 2)

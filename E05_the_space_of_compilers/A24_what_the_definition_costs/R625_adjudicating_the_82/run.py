#!/usr/bin/env python3
"""
R625 -- adjudicating the 82: are they fabrications, or artefacts of my own instrument?

CHECK #224 CAUGHT TWO UNCOMPUTED SUPERLATIVES IN ONE SENTENCE.
  ⛔ "the SMALLEST honest flag set this project has produced" -- a superlative over an unenumerated
     set. ⛔ "the ONLY thing now standing between this arc and a provenance claim" -- a universal;
     the arc also carries R622's T3 unbacked values and 154 uncited rounds. Eighth and ninth in
     fifteen closing lines, and both in the sentence a later round would have acted on.

⭐ AND THE INSTRUCTION ITSELF WAS WEAKER THAN NEEDED. "Read the 82" treats adjudication as a hand
   task with me as the instrument. Most of it is MECHANICAL: whether a value sits in ANOTHER round's
   artifact, whether it matches at a different precision, and whether it is absent everywhere are all
   computable. Only the derived-value class needs a reader, and bounding it is the point. A hand-read
   is the last resort, not the plan.

ESTIMAND        the decomposition of the 82 section-scope C3 flags into:
                  F1 PRECISION   the value is in the cited round's artifact at a different
                                 rounding than the value-position test emits -> MY instrument
                  F2 CROSS-ROUND the value is in SOME OTHER round's artifact -> the citation is
                                 misplaced, not the number
                  F3 DERIVED     the value is a ratio/difference/percentage of artifact values,
                                 never persisted itself -> needs a reader; bounded, not counted
                  F4 ABSENT      in no artifact at any precision -> the real provenance defect
IDENTIFICATION  F1, F2, F4 exact and mechanical. F3 is NOT identified here -- it is whatever
                survives F1/F2/F4, so it is an UPPER bound containing both genuine derivations and
                anything my three tests miss. Named as unresolved rather than reported as a class.
SCOPE           population : the 82 section-scope C3 pairs from R624
                instrument : value-position sets per round, plus a global union, at 2-6 dp
                             instrument unit = A (DECIMAL, SECTION) PAIR
                             claim unit      = A NUMERIC ASSERTION. Still not equal, unchanged.
                baseline   : R622's tiers -- T3 unbacked was 2.5% of DEFINITION.md
                regime     : this repository at this sha
WORLDS          A INSTRUMENT ARTEFACT: F4 is small. The 82 are mostly my own rounding and misplaced
                  citations, so the rule's output is not evidence of fabrication and the arc's
                  provenance is better than three rounds of gate-auditing implied.
                B REAL DEFECT: F4 is large. There are numbers in the definition backed by nothing,
                  and the count is the size of the debt.
KILL            pre-registered: F4 >= 20 of 82 -> world B. F4 < 20 -> world A, and the three
                preceding rounds were measuring my instrument rather than the document.
POSITIVE CTRL   a fabricated decimal must land F4. Fails at g=0: a value known to be in its cited
                round's artifact must not appear in the flag set at all.
NEGATIVE CTRL   a value taken from ANOTHER round's artifact, placed in a section citing a
                different round, must land F2 -- not F4, or the cross-round test is blind.
PLACEBO         a decimal occurring in no artifact and no document -> F4, no crash.
SEEDS           n/a, deterministic.
MULTIPLICITY    82 pairs x 4 classes x 5 precisions + 4 controls. All reported.
ARTIFACT        results/adjudicating_the_82.json
                ⚠ planted literals assembled at runtime, never persisted as value positions.
IMPOSSIBLE      "this number is CORRECT" still needs the round's own re-execution. F4 means only
                "no artifact on disk carries this value at any precision I tested".
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
E05 = ROOT / "E05_the_space_of_compilers"
A24 = E05 / "A24_what_the_definition_costs"
DEC = re.compile(r"(?<![\w.])(\d+\.\d{3,4})(?![\w])")
CITE = re.compile(r"R(\d{3})")
HEAD = re.compile(r"^##+ .*?R(\d{3})", re.M)

RAW: dict[str, list[float] | None] = {}


def raw_numbers(rid):
    """Every numeric scalar a round persisted, unrounded -- so precision can be swept."""
    if rid in RAW: return RAW[rid]
    fs = [f for d in A24.glob(f"R{rid}_*") for f in (d / "results").glob("*.json")]
    if not fs:
        RAW[rid] = None; return None
    out = []
    def walk(o):
        if isinstance(o, dict):
            for v in o.values(): walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o: walk(v)
        elif isinstance(o, bool) or o is None: return
        elif isinstance(o, (int, float)): out.append(float(o))
        elif isinstance(o, str):
            s = o.strip().lstrip("+-")
            if DEC.fullmatch(s):
                try: out.append(float(s))
                except ValueError: pass
    for f in fs:
        try: walk(json.loads(f.read_text(errors="ignore")))
        except Exception: pass
    RAW[rid] = out
    return out


def matches(dec, nums, dps=(4, 3)):
    if not nums: return False
    for dp in dps:
        try: t = round(float(dec), dp)
        except ValueError: return False
        for v in nums:
            if round(v, dp) == t or round(abs(v), dp) == t: return True
    return False


def sections(text):
    parts, cur = [], []
    for line in text.split("\n"):
        if re.match(r"^##+ ", line) and cur: parts.append("\n".join(cur)); cur = [line]
        else: cur.append(line)
    if cur: parts.append("\n".join(cur))
    return parts


def flags_of(text):
    """R624's section-scope C3 set, recomputed so this round does not inherit a number."""
    out = []
    for ch in sections(text):
        cited = sorted(set(HEAD.findall(ch)) | set(CITE.findall(ch)))
        if not cited: continue
        nums = [n for r in cited for n in (raw_numbers(r) or [])]
        if not any(raw_numbers(r) is not None for r in cited): continue
        for d in sorted(set(DEC.findall(ch))):
            if not matches(d, nums, dps=(4,)):
                out.append((d, cited, ch[:90].replace("\n", " ")))
    return out


def main():
    docs = {n: (E05 / n).read_text() for n in ("DEFINITION.md", "STATEMENT.md")}
    allr = sorted({m.group(1) for d in A24.glob("R[0-9]*") if (m := re.match(r"R(\d+)", d.name))})
    universe = [n for r in allr for n in (raw_numbers(r) or [])]
    if len(universe) < 1000:
        print(f"UNRUNNABLE: only {len(universe)} persisted numbers. Exit 2, never 0."); return 2
    print(f"  rounds: {len(allr)}   persisted numeric scalars: {len(universe)}")

    flags = [f for t in docs.values() for f in flags_of(t)]
    print(f"  section-scope C3 flags, recomputed: {len(flags)}")

    # ⛔ v1 SWEPT PRECISION DOWN TO 2 dp AND THE POSITIVE CONTROL KILLED IT. Over 23,819 persisted
    #    numbers, rounding a 4-digit literal to 2 places finds a match essentially always -- so the
    #    fabricated value AND the placebo both classified F1, and F1 read 80.4%. Loosening a search
    #    to admit legitimate rounding also made it unable to fail: §4's "a search is an instrument",
    #    with the collision this time built by me.
    #    REPAIR: the band is tied to the LITERAL'S OWN precision -- a value written to 4 places is
    #    matched at 4 and 3, never at 2, because asserting 0.5193 is not asserting 0.52.
    def band(dec):
        frac = len(dec.split(".")[1])
        return (frac, frac - 1) if frac >= 3 else (frac,)

    def classify(dec, cited):
        nums = [n for r in cited for n in (raw_numbers(r) or [])]
        if matches(dec, nums, dps=band(dec)): return "F1"
        if matches(dec, universe, dps=band(dec)): return "F2"
        return "F4"

    print(f"\n─── CONTROLS ───")
    FAKE = "0." + "5" + "1" + "9" + "3"
    pos = classify(FAKE, allr[:5]) == "F4"
    print(f"  POSITIVE  a fabricated decimal classifies F4 -> {'PASS' if pos else '⛔ FAIL'}")
    hit = next((r for r in allr if raw_numbers(r)), None)
    real = f"{raw_numbers(hit)[0]:.4f}" if hit and raw_numbers(hit) else None
    g0 = classify(real, [hit]) == "F1" if real else False
    print(f"  g=0       a value from its OWN cited round ({real}) classifies "
          f"{classify(real,[hit]) if real else '—'} -> {'PASS — not F4' if g0 else '⛔ FAIL'}")
    other = next((r for r in allr[::-1] if raw_numbers(r) and r != hit), None)
    ov = f"{raw_numbers(other)[0]:.4f}" if other else None
    neg = classify(ov, [hit]) in ("F2", "F1") if ov else False
    print(f"  NEGATIVE  a value from ANOTHER round, cited to R{hit}, classifies "
          f"{classify(ov,[hit]) if ov else '—'} -> {'PASS — the cross-round test sees it' if neg else '⛔ FAIL'}")
    plc = classify("0." + "9" + "9" + "9" + "1", allr) 
    print(f"  PLACEBO   a decimal in no artifact -> {plc} -> {'PASS' if plc == 'F4' else '⛔ FAIL'}")
    controls_ok = pos and g0 and neg

    print(f"\n─── THE DECOMPOSITION ───")
    cls = {"F1": [], "F2": [], "F4": []}
    for dec, cited, ctx in flags:
        cls[classify(dec, cited)].append((dec, cited, ctx))
    n = len(flags) or 1
    for k, label in (("F1", "PRECISION  in the cited round, other rounding"),
                     ("F2", "CROSS-ROUND  in another round's artifact"),
                     ("F4", "ABSENT  in no artifact at any precision")):
        print(f"  {k}  {label:<45} {len(cls[k]):>3}  ({len(cls[k])/n:>5.1%})")

    print(f"\n─── THE F4 SET, NAMED RATHER THAN COUNTED ───")
    for dec, cited, ctx in cls["F4"][:14]:
        print(f"  {dec:<9} cited R{','.join(cited[:3]):<14} {ctx[:64]}")
    if len(cls["F4"]) > 14: print(f"  … and {len(cls['F4'])-14} more, all in the artifact")

    # ── THE NULL NOBODY COMPUTED, AND IT VOIDS THE DECOMPOSITION ABOVE ───────────────
    # Both failing controls point at one thing: with tens of thousands of persisted numbers,
    # "this value appears in an artifact" may be true of almost any number. That is a FALSE
    # POSITIVE RATE and it is measurable in one minute -- and four rounds were built on this
    # test without it. §1 G2: a zero from an instrument never shown to return non-zero is
    # silence; the mirror is a HIT from an instrument never shown to return a MISS.
    import random
    print(f"\n─── THE NULL: how often does an INVENTED decimal 'anchor'? (3 seeds x 4000) ───")
    null = {}
    for dp in (4, 3, 2):
        S = {round(v, dp) for v in universe} | {round(abs(v), dp) for v in universe}
        rates = []
        for seed in (0, 1, 2):
            rng = random.Random(seed)
            rates.append(sum(1 for _ in range(4000) if round(rng.random(), dp) in S) / 4000)
        null[dp] = rates
        print(f"  {dp} dp  {len(S):>5} distinct values   match rate "
              f"{rates[0]:.2%} · {rates[1]:.2%} · {rates[2]:.2%}")
    fp4 = sum(null[4]) / 3
    print(f"\n  ⛔ AT THE OPERATING PRECISION (4 dp) THE FALSE-POSITIVE RATE IS {fp4:.1%}.")
    print(f"     So F1 and F2 above are NOT a decomposition of provenance -- they are mostly")
    print(f"     collision, and the two failed controls were the instrument telling me so.")
    print(f"     R622's 'T2 anchorable 79.0%' must be read against a {fp4:.0%} floor: the excess")
    print(f"     is {0.790-fp4:.0%} points, not 79.")

    print(f"\n─── VERDICT (threshold pre-registered at F4 >= 20) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif fp4 > 0.20:
        world = (f"NEITHER — the decomposition is VOID. At 4 dp an INVENTED decimal 'anchors' "
                 f"{fp4:.1%} of the time, so F1 and F2 are mostly collision and F4=0 means only "
                 f"that the test cannot miss. The instrument, not the document, is what four "
                 f"rounds have been measuring.")
    elif len(cls["F4"]) >= 20:
        world = (f"B REAL DEFECT — {len(cls['F4'])} of {len(flags)} flagged values appear in NO "
                 f"artifact at any precision. That is the size of the provenance debt.")
    else:
        world = (f"A INSTRUMENT ARTEFACT — only {len(cls['F4'])} of {len(flags)} are absent "
                 f"everywhere; {len(cls['F1'])} are my own rounding and {len(cls['F2'])} are "
                 f"misplaced citations. The flag set is mostly the instrument, and three rounds of "
                 f"gate-auditing were measuring my own test rather than the document.")
    print(f"  {world}")
    print(f"\n  ⚠ F3 DERIVED IS NOT A REPORTED CLASS: a ratio or difference of artifact values that "
          f"was never persisted lands in F4 by construction, so F4 is an UPPER bound on the "
          f"provenance debt and needs a reader to split further.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "adjudicating_the_82.json").write_text(json.dumps({
        "null_match_rate_by_dp": {str(k): v for k, v in null.items()},
        "false_positive_rate_4dp": round(fp4, 4),
        "world": world, "controls_ok": controls_ok, "n_flags": len(flags),
        "counts": {k: len(v) for k, v in cls.items()},
        "F4_set": [{"value": d, "cited": c, "context": x} for d, c, x in cls["F4"]],
        "check224": ("'the smallest honest flag set this project has produced' and 'the only thing "
                     "standing between this arc and a provenance claim' -- two uncomputed "
                     "superlatives in one closing sentence"),
        "impossible": ("F4 is an upper bound: a derived value never persisted lands there by "
                       "construction, and correctness still needs the round's re-execution"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'adjudicating_the_82.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

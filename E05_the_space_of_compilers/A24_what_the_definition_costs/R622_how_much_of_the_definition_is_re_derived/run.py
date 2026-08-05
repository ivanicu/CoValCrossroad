#!/usr/bin/env python3
"""
R622 -- how much of DEFINITION.md is re-derived, and how much is merely written there?

CHECK #221, TWO FINDINGS, ONE OF WHICH SAVED THE ROUND'S PREMISE.
  ⛔ "the CHEAPEST repair is not a new gate but making the anchoring directional" -- an uncomputed
     comparative. §4's remedy says a comparative word must be computed, not typed. Nothing here
     compared the cost of two repairs; the word was decoration.
  ✓ "which definition_matches_the_record already does for the values it knows" -- CHECKED against
     the object before building on it, because R619 is what happens when I do not. It is TRUE:
     `derive()` returns label -> (value from artifact, round), and the gate's own proxy line says
     "the numbers this file knows how to extract match the artifacts". The list is HAND-ENUMERATED,
     which is precisely the exposure this round measures.

⭐ WHY THIS IS THE RIGHT NEXT MOVE AND NOT MORE GATE-AUDITING. R621 proved a fabricated value can be
   laundered through DEFINITION.md. That establishes the path EXISTS. It says nothing about whether
   the path is exotic or ordinary. If most of DEFINITION.md's numbers are already unbacked prose,
   then laundering is not an attack -- it is the file's normal mode of operation, and the retraction
   owed is much larger than one gate.

ESTIMAND        the partition of DEFINITION.md's decimal values into three tiers:
                  T1 GATE-VERIFIED   the value is returned by definition_matches_the_record's
                                     derive(), so an artifact drift breaks the build
                  T2 ANCHORABLE      the value appears verbatim in some round's persisted
                                     results/*.json, but no gate checks it
                  T3 UNBACKED        the value appears in NO artifact -- prose only
IDENTIFICATION  T1 exact (read from the gate's own return value). T2/T3 by string search over 321
                results directories, which is an INSTRUMENT and gets controls. ⚠ Its known failure
                is COLLISION: a short decimal can occur in an unrelated artifact by chance, which
                inflates T2 and deflates T3 -- so T3 is a LOWER BOUND on unbacked values, and the
                bound direction is the conservative one for the claim being made.
SCOPE           population : every decimal with >=3 fractional digits in DEFINITION.md
                instrument : derive() membership; verbatim substring over results/*.json
                             instrument unit = A DECIMAL LITERAL
                             claim unit      = A NUMERIC ASSERTION. NOT equal -- one assertion can
                             carry several literals, and a literal can appear in several
                             assertions. Reported at literal level and named as the gap.
                baseline   : STATEMENT.md's decimals through the same three-tier instrument, since
                             the transitive rule makes those a subset that SHOULD be better anchored
                regime     : this repository at this sha
WORLDS          A LAUNDERING IS EXOTIC: T1 dominates. The gate covers most of the file, R621's path
                  is a real but narrow hole, and one directional check closes it.
                B LAUNDERING IS THE NORMAL CASE: T3 is large. Most numbers in the definition were
                  never re-derived from anything, so R621 did not find a hole -- it found the
                  building material. The owed retraction is about the FILE, not the gate.
                C ANCHORED BUT UNCHECKED: T2 dominates. The values are real and traceable, nothing
                  enforces it, and the repair is mechanical rather than epistemic.
KILL            pre-registered: T1 >= 50% -> world A. T3 >= 33% -> world B. T2 largest with
                T3 < 33% -> world C. Written before the run; ties resolved toward the WORSE world.
POSITIVE CTRL   a value known to be in derive() must land in T1. Fails at g=0: an invented decimal
                must land in T3, or the search cannot distinguish backed from unbacked.
NEGATIVE CTRL   a decimal drawn FROM an artifact but absent from derive() must land in T2 -- if it
                lands in T1 the tiers are not disjoint; if T3, the search is blind.
PLACEBO         a decimal of the same shape occurring nowhere -> T3, and it must not crash.
SEEDS           n/a, deterministic.
MULTIPLICITY    every decimal x 3 tiers, both documents, all reported -- no sampling.
ARTIFACT        results/definition_anchoring_tiers.json
IMPOSSIBLE      "this number is CORRECT" needs the round's own re-execution, which this site cannot
                do for 613 rounds. T1 means only "an artifact drift would break the build".
"""
from __future__ import annotations
import json, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
OUT = pathlib.Path(__file__).resolve().parent / "results"
E05 = ROOT / "E05_the_space_of_compilers"
A24 = E05 / "A24_what_the_definition_costs"
sys.path.insert(0, str(ROOT / "assurance"))
import definition_matches_the_record as DM

DEC = re.compile(r"(?<![\w.])(\d+\.\d{3,4})(?![\w])")


def artifact_blob():
    """⛔ v1 CONCATENATED THE RAW TEXT, AND THE g=0 CONTROL CAUGHT IT BY ABSORBING MY OWN FAKE.
    R621's fabricated `0.9187` -- a number with no measurement behind it, invented in that round's
    source -- landed in T2 ANCHORABLE, because R621's artifact RECORDS the mutation string that
    contains it. The laundering path completed itself through the audit record.
    So raw-text presence is not anchoring; it is "these digits occur somewhere in a JSON file",
    which includes prose fields, check-notes and quoted retractions. v2 walks the parsed JSON and
    collects only VALUE POSITIONS -- numbers, and strings that are EXACTLY the decimal -- so a
    number mentioned inside a sentence no longer counts as measured.
    ⚠ Still a proxy, stated: a value position in an artifact means the round PERSISTED that
    number, never that the number is right."""
    vals, n = set(), 0
    def walk(o):
        if isinstance(o, dict):
            for v in o.values(): walk(v)
        elif isinstance(o, (list, tuple)):
            for v in o: walk(v)
        elif isinstance(o, bool) or o is None:
            return
        elif isinstance(o, (int, float)):
            for f in (repr(o), f"{o:.4f}", f"{o:.3f}", f"{abs(o):.4f}", f"{abs(o):.3f}"):
                vals.add(f.lstrip("+"))
        elif isinstance(o, str) and DEC.fullmatch(o.strip().lstrip("+-")):
            vals.add(o.strip().lstrip("+-"))
    for f in sorted(A24.glob("R*/results/*.json")):
        try:
            walk(json.loads(f.read_text(errors="ignore"))); n += 1
        except Exception:
            pass
    return vals, n


def gate_values():
    vals = set()
    for _lbl, pair in DM.derive().items():
        v = pair[0] if isinstance(pair, tuple) else pair
        if v is None:
            continue
        for form in (f"{v}", f"{float(v):.4f}" if isinstance(v, (int, float)) else f"{v}",
                     f"{float(v):.3f}" if isinstance(v, (int, float)) else f"{v}"):
            vals.add(form.rstrip())
    return vals


def tier(dec, gv, blob):
    if dec in gv:
        return "T1"
    return "T2" if dec in blob else "T3"  # blob is now a SET of value positions


def main():
    blob, nfiles = artifact_blob()
    if nfiles < 50:
        print(f"UNRUNNABLE: only {nfiles} artifacts readable. Exit 2, never 0."); return 2
    gv = gate_values()
    print(f"  artifacts read: {nfiles}   values derive() returns: {len(gv)}")

    print(f"\n─── CONTROLS ───")
    known = sorted(gv)[:1]
    pos = known and tier(known[0], gv, blob) == "T1"
    print(f"  POSITIVE  a value derive() returns ({known[0] if known else '—'}) lands in "
          f"{tier(known[0], gv, blob) if known else '—'} -> {'PASS' if pos else '⛔ FAIL'}")
    g0 = tier("0.9187", gv, blob)
    print(f"  g=0       an invented decimal (R621's fabricated 0.9187) lands in {g0} -> "
          f"{'PASS — backed and unbacked are distinguishable' if g0 == 'T3' else '⛔ FAIL'}")
    from_art = None
    for v in sorted(blob):
        if v not in gv:
            from_art = v; break
    neg = from_art and tier(from_art, gv, blob) == "T2"
    print(f"  NEGATIVE  a decimal drawn FROM an artifact but not in derive() ({from_art}) lands in "
          f"{tier(from_art, gv, blob) if from_art else '—'} -> {'PASS' if neg else '⛔ FAIL'}")
    plc = tier("0.1357", gv, blob) if "0.1357" not in blob else None
    print(f"  PLACEBO   a same-shape decimal occurring nowhere -> {plc or 'occurs, skipped'} -> "
          f"{'PASS' if plc == 'T3' or plc is None else '⛔ FAIL'}")
    controls_ok = bool(pos) and g0 == "T3" and bool(neg)

    print(f"\n─── THE PARTITION ───")
    rows = {}
    for name, path in (("DEFINITION.md", E05 / "DEFINITION.md"),
                       ("STATEMENT.md", E05 / "STATEMENT.md")):
        decs = sorted(set(DEC.findall(path.read_text())))
        t = {"T1": [], "T2": [], "T3": []}
        for d in decs:
            t[tier(d, gv, blob)].append(d)
        n = len(decs) or 1
        rows[name] = {k: len(v) for k, v in t.items()} | {"n": len(decs), "T3_examples": t["T3"][:10]}
        print(f"  {name:<16} n={len(decs):>4}   "
              f"T1 gate-verified {len(t['T1']):>3} ({len(t['T1'])/n:>5.1%})   "
              f"T2 anchorable {len(t['T2']):>3} ({len(t['T2'])/n:>5.1%})   "
              f"T3 UNBACKED {len(t['T3']):>3} ({len(t['T3'])/n:>5.1%})")

    d = rows["DEFINITION.md"]; n = d["n"] or 1
    t1, t2, t3 = d["T1"]/n, d["T2"]/n, d["T3"]/n
    print(f"\n─── VERDICT (thresholds pre-registered; ties resolve toward the WORSE world) ───")
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif t3 >= 0.33:
        world = (f"B LAUNDERING IS THE NORMAL CASE — {t3:.1%} of DEFINITION.md's decimals appear "
                 f"in NO artifact. R621 did not find a hole in the wall; it found the building "
                 f"material. The owed retraction is about the FILE, not the gate.")
    elif t1 >= 0.50:
        world = (f"A LAUNDERING IS EXOTIC — {t1:.1%} gate-verified; one directional check closes "
                 f"a narrow hole")
    else:
        world = (f"C ANCHORED BUT UNCHECKED — T2 {t2:.1%} dominates with T3 at {t3:.1%}. The "
                 f"values are traceable to artifacts and nothing enforces it; the repair is "
                 f"mechanical rather than epistemic.")
    print(f"  {world}")
    print(f"\n  ⚠ T3 IS A LOWER BOUND. A short decimal can collide with an unrelated artifact by "
          f"chance, which inflates T2 and deflates T3 — the conservative direction for this claim.")
    print(f"  ⚠ T1 means 'an artifact drift would break the build', NEVER 'this number is correct'. "
          f"Re-executing 613 rounds is what correctness would require, and this site cannot.")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "definition_anchoring_tiers.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok, "artifacts_read": nfiles,
        "derive_values": len(gv), "per_document": rows,
        "check221": ("'the cheapest repair' was an uncomputed comparative; the claim about "
                     "definition_matches_the_record was checked against the object and held"),
        "impossible": "T1 means an artifact drift breaks the build, not that the number is correct",
    }, indent=2))
    print(f"\n  wrote {OUT / 'definition_anchoring_tiers.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

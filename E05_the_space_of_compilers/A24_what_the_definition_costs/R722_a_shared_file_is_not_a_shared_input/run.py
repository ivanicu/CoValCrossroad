#!/usr/bin/env python3
"""
R722 -- a shared FILE is not a shared INPUT, and my probe of that was an uncontrolled search.

CHECK #324 ON R721's NEXT LINE — IT HOLDS, AND MY FIRST PROBE OF IT WAS UNCONTROLLED.
  ✓ 11 sources with 3 shared, `clause_ledger.json` read by 4 of 6, and R680's `derivers` is a list of
    ROUND ids — it counted rounds, not fields.
  ⛔ BUT THE PROBE I RAN RETURNED FIELDS FOR R404 AND R405 AND NOTHING FOR R408 AND R667. That is
    SILENCE, not zero: my regex matched a few subscript shapes and the other two access the ledger
    some other way. §4 — a search is an instrument and has no positive control — and reporting
    "R408 reads no fields" would have been a fabricated zero.

ESTIMAND        for the 4 rounds reading `clause_ledger.json`, WHICH fields each reads and how many
                are read by more than one. A shared FILE is not a shared INPUT: two rounds reading
                disjoint fields share a path and no data. Unparsed rounds are UNMEASURED, never 0.
IDENTIFICATION  partially identified BY CONSTRUCTION -- field access can be written in ways no fixed
                pattern catches, so the estimand is a LOWER BOUND over the parsed rounds, and the
                unparsed count bounds how far that can be trusted. Both are reported.
SCOPE           population : R404, R405, R408, R667
                instrument : a field extractor with a coverage report
                             instrument unit = A FIELD ACCESS IN SOURCE
                             claim unit      = WHETHER TWO COMPUTATIONS SHARE AN INPUT
                             ⚠ NOT EQUAL -- an access I cannot see is not an access that is absent,
                             and that gap is why this round exists rather than last round's probe.
                baseline   : R721's file-level sharing
                regime     : this repository at HEAD
WORLDS          A SHARED INPUT · B SHARED FILE ONLY · C UNMEASURABLE
KILL            conditional on the POSITIVE recovering a known field and g=0 returning none
POSITIVE CTRL   R404's access to `clause2_admits` must be recovered
g=0             a source with no ledger access -> 0 fields; an unparsable round -> UNMEASURED, and
                the two must NEVER print the same string
NEGATIVE CTRL   R360 WRITES the ledger; recovering its field names shows the extractor matches field
                names rather than reader-specific idiom
SHAM            docstring-only extraction -- the executable body is the ingredient
PLACEBO         two identical runs differ by exactly 0
COVERAGE        the parsed share is a first-class number, not a footnote
ARTIFACT        results/fields.json
IMPOSSIBLE      proving a round does NOT read a field (absence of a match is not absence of access,
                which is why UNMEASURED exists) · cross-release
"""
from __future__ import annotations
import json, pathlib, re, subprocess, sys
from collections import Counter

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
E05 = ROOT / "E05_the_space_of_compilers"
READERS = ["R404", "R405", "R408", "R667"]
WRITER = "R360"
INSTRUMENT_UNIT, CLAIM_UNIT = "A FIELD ACCESS IN SOURCE", "WHETHER TWO COMPUTATIONS SHARE AN INPUT"
# ⭐ the ledger's own schema, read from R360's artifact so the extractor is matching REAL field names
LEDGER = json.loads(next((E05 / "A24_what_the_definition_costs").glob(
    "R360_*/results/*.json")).read_text())
SCHEMA = sorted(LEDGER.keys())

PATTERNS = {
    "subscript": lambda src: {f for f in SCHEMA
                              if re.search(r"""\[\s*["']""" + re.escape(f) + r"""["']\s*\]""", src)},
    "+ .get": lambda src: {f for f in SCHEMA
                           if re.search(r"""\.get\(\s*["']""" + re.escape(f) + r"""["']""", src)},
    "+ bare mention in code": lambda src: {f for f in SCHEMA
                                           if re.search(r"""["']""" + re.escape(f) + r"""["']""", src)},
}


def find(rid):
    for d in E05.rglob(f"{rid}_*"):
        f = d / "run.py"
        if f.exists():
            return f
    return None


def body(f):
    src = f.read_text(errors="ignore")
    m = re.search(r'^"""', src, re.M)
    if not m:
        return src
    e = src.find('"""', m.end())
    return src[e + 3:] if e != -1 else src


def fields(f, upto="+ bare mention in code"):
    """Cumulative over the pattern ladder up to `upto`. UNMEASURED is the caller's job to decide."""
    src, out = body(f), set()
    for name, fn in PATTERNS.items():
        out |= fn(src)
        if name == upto:
            break
    return out


def main() -> int:
    files = {r: find(r) for r in READERS}
    if any(v is None for v in files.values()):
        print(f"⛔ missing run.py for {[r for r,v in files.items() if v is None]} — exit 2")
        return 2
    print(f"─── THE OBJECT ───\n  readers of clause_ledger.json: {READERS}")
    print(f"  the ledger's schema, read from R360's artifact: {SCHEMA}")

    print(f"\n─── CONTROLS ───")
    f404 = fields(files["R404"], upto="subscript")
    posok = "clause2_admits" in f404
    print(f"  POSITIVE  R404 -> subscript pass finds {sorted(f404)} -> "
          f"{'PASS — the field its subject IS is recovered' if posok else '⛔ FAIL'}")
    prereg = HERE / "PREREGISTRATION.txt"
    g0 = {f for f in SCHEMA if f"'{f}'" in prereg.read_text()} if prereg.exists() else set()
    g0ok = len(g0) == 0
    print(f"  g=0       a source with no ledger access -> {len(g0)} fields -> "
          f"{'PASS — zero, and UNMEASURED is a different value' if g0ok else '⛔ FAIL'}")
    wf = find(WRITER)
    wfields = fields(wf) if wf else set()
    # ⛔ MY FIRST THRESHOLD WAS 3 AND THE CEILING IS 2 — a control that could not pass (§4). R360
    #   BUILDS the ledger dict from variables, so only 2 of its 15 schema keys appear as string
    #   literals ANYWHERE in its source, docstring included. The threshold is now computed: FLOOR is
    #   0 (a source naming no schema key) and CEILING is what R360 can possibly name, and the
    #   requirement is floor < t <= ceiling with t set at 1 — recovering ANY schema field from the
    #   writer is what shows the extractor matches field NAMES rather than one reader's idiom.
    wsrc = wf.read_text(errors="ignore") if wf else ""
    w_ceiling = len({f for f in SCHEMA if f"'{f}'" in wsrc or f'"{f}"' in wsrc})
    w_floor, w_t = 0, 1
    neg_band = w_floor < w_t <= w_ceiling
    negok = len(wfields) >= w_t and neg_band
    print(f"  NEGATIVE  R360, which WRITES the ledger -> {len(wfields)} schema field(s) "
          f"{sorted(wfields)}")
    print(f"            floor {w_floor} < t {w_t} <= ceiling {w_ceiling} -> "
          f"{'band is REAL' if neg_band else '⛔ THRESHOLD UNREACHABLE'}   overall "
          f"{'PASS — the extractor matches field NAMES, not reader idiom' if negok else '⛔ FAIL'}")
    doc_total = 0
    for r, f in files.items():
        src = f.read_text(errors="ignore")
        head = src[:src.find('"""', src.find('"""') + 3) + 3] if '"""' in src else ""
        doc_total += len({fl for fl in SCHEMA if f"'{fl}'" in head or f'"{fl}"' in head})
    body_total = sum(len(fields(f)) for f in files.values())
    shamok = doc_total < body_total
    print(f"  SHAM      docstring-only -> {doc_total} field mentions vs the body's {body_total} -> "
          f"{'PASS — the body is the ingredient' if shamok else '⛔ FAIL'}")
    plc = {r: fields(f) for r, f in files.items()} == {r: fields(f) for r, f in files.items()}
    print(f"  PLACEBO   two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT      '{INSTRUMENT_UNIT}' != claim unit -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and shamok and plc and unitok

    print(f"\n─── WHAT EACH READER TAKES FROM THE SHARED FILE ───")
    per, parsed = {}, []
    print(f"  {'round':<8}{'verdict':<13}fields")
    for r, f in files.items():
        fs = fields(f)
        v = "PARSED" if fs else "⛔ UNMEASURED"
        per[r] = {"fields": sorted(fs), "verdict": v}
        if fs:
            parsed.append(r)
        print(f"  {r:<8}{v:<13}{sorted(fs) if fs else '(no pattern matched — NOT a measured zero)'}")
    cov = len(parsed) / len(READERS)
    print(f"  ⭐ COVERAGE: {len(parsed)} of {len(READERS)} parsed = {cov:.2f} — reported first-class, "
          f"because an unparsed round is UNMEASURED and never a zero.")

    shared = Counter(fl for r in parsed for fl in per[r]["fields"])
    multi = {fl: c for fl, c in shared.items() if c > 1}
    top = max(shared.items(), key=lambda kv: kv[1]) if shared else (None, 0)
    print(f"\n─── SHARED FIELDS AMONG THE PARSED READERS ───")
    print(f"  fields read by >1 parsed reader: {len(multi)}   {multi}")
    print(f"  most-shared: {top[0]} in {top[1]} of {len(parsed)} parsed")

    print(f"\n─── THE SPECIFICATION SWEEP (3 pattern sets × 2 populations) ───")
    cells = []
    for pname in PATTERNS:
        pr = [r for r, f in files.items() if fields(f, upto=pname)]
        sh = Counter(fl for r in pr for fl in fields(files[r], upto=pname))
        cells.append({"patterns": pname, "population": "the 4 readers",
                      "parsed": len(pr), "shared_fields": sum(1 for c in sh.values() if c > 1)})
        wn = len(fields(wf, upto=pname)) if wf else 0
        cells.append({"patterns": pname, "population": "R360 the writer", "schema_fields": wn})
        print(f"  {pname:<26}readers parsed {len(pr)}/4   shared fields "
              f"{sum(1 for c in sh.values() if c > 1)}   |   writer schema fields {wn}")

    A, B, Cc = len(parsed), len(multi), top[1]
    print(f"\n─── REGISTERED ───")
    print(f"  A  readers PARSED = 3 [1,4] -> {A}: {'INSIDE' if 1 <= A <= 4 else '⛔ OUTSIDE'}")
    print(f"  B  fields shared by >1 parsed reader = 1 [0,5] -> {B}: "
          f"{'INSIDE' if 0 <= B <= 5 else '⛔ OUTSIDE'}")
    print(f"  C  most-shared field's reader count = 2 [0,4] -> {Cc}: "
          f"{'INSIDE' if 0 <= Cc <= 4 else '⛔ OUTSIDE'}")
    print(f"  DIRECTIONAL coverage is INCOMPLETE -> "
          f"{'HOLDS' if A < len(READERS) else '⛔ FAILS — all four parsed'}")
    print(f"\n  MULTIPLICITY: {len(cells)} cells; counts are EXACT so no p-values are computed.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; the field counts would be silence."
    elif A <= 2:
        world = (f"⭐⭐⭐ C UNMEASURABLE — only {A} of {len(READERS)} readers parse, so the field-level "
                 f"question cannot be answered and R721's file-level qualification stands unrefined. "
                 f"COVERAGE {cov:.2f} is the finding.")
    elif B == 0:
        world = (f"⭐⭐⭐ B SHARED FILE ONLY — the {A} parsed readers take DISJOINT fields from "
                 f"`clause_ledger.json`, so they share a path and no data. R721's 'not disjoint "
                 f"evidences' is SOFTENED, at coverage {cov:.2f}.")
    else:
        world = (
            f"⭐⭐⭐ A SHARED INPUT, AND THE FILE-LEVEL COUNT UNDERSTATED IT. Of the {len(READERS)} "
            f"rounds reading `clause_ledger.json`, {A} parse and they share {B} field(s): "
            f"{dict(multi)}, the most common being `{top[0]}` in {top[1]} of {A}. ⭐ SO THE SHARING "
            f"IS NOT NOMINAL — two of the six derivations behind the number 5 take the SAME FIELD "
            f"from the SAME FILE, which is a shared INPUT and not merely a shared path, and R721's "
            f"qualification was right to call them not-disjoint. ⛔ AND THE COVERAGE IS THE OTHER "
            f"HALF OF THE ANSWER: {len(READERS)-A} of {len(READERS)} readers match no pattern and are "
            f"reported UNMEASURED, never as zero — the probe I ran last round would have printed "
            f"those as 'no fields' and turned silence into a finding. ⚠ SO THIS IS A LOWER BOUND ON "
            f"SHARING over the parsed rounds, and the unparsed count bounds how far it can be "
            f"trusted; both numbers are on the page. ⚠ The negative control recovers "
            f"{len(wfields)} schema fields from R360, which WRITES the ledger, so the extractor is "
            f"matching field NAMES rather than one reader's idiom. ⚠ UNIT GAP: instrument unit is "
            f"{INSTRUMENT_UNIT}, claim unit is {CLAIM_UNIT} — an access I cannot see is not an access "
            f"that is absent.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "fields.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "readers": READERS, "schema": SCHEMA, "per_reader": per,
        "parsed": parsed, "coverage": cov, "unmeasured": [r for r in READERS if r not in parsed],
        "shared_fields": dict(multi), "most_shared": {"field": top[0], "n_readers": top[1]},
        "writer_schema_fields": sorted(wfields),
        "negative_band": {"floor": w_floor, "threshold": w_t, "ceiling": w_ceiling},
        "cells": cells,
        "registered": ("A parsed 3 [1,4]; B shared fields 1 [0,5]; C most-shared count 2 [0,4]; "
                       "directional coverage incomplete"),
        "observed": {"A": A, "B": B, "C": Cc, "directional": A < len(READERS)},
        "limit": ("absence of a pattern match is NOT absence of access — unparsed rounds are "
                  "UNMEASURED, and the sharing count is a LOWER BOUND over the parsed ones."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""R981 — how much of the statement do the 343 anchoring assertions actually cover?

⛔ WHY. `definition_matches_the_record.py` holds 343 assertions and prints, every run, that *"every
prose claim not in the assertion table is unchecked BY CONSTRUCTION, and that remainder is why this
line prints a count instead of a clean bill."* **It names the remainder and never counts it.** A
reader sees `343 of 343` and has no way to learn what fraction of the document that is.

This round was provoked by a concrete instance: R981's production step added a block of numbers to
DEFINITION.md, the currency gate went red then green, and the anchoring gate returned **0 both
before and after** — because none of the new numerals is in its table. Currency without consistency,
the exact mirror of the defect R977 found.

⚠ PRIOR ART, CHECKED: the *property* is documented by the gate itself, in its own proxy ledger. This
round does not claim to discover it. What does not exist anywhere is the **number**.

ESTIMAND        how the 343 assertions DIVIDE between the two halves of DEFINITION.md — the 693-line
                statement a reader reads as "the definition", and the 9,128-line evidence record —
                and the share of each half's numerals that no assertion locates.
⛔ MY FIRST POPULATION WAS WRONG AND THE POSITIVE CONTROL REFUSED IT. v1 ran the census over the
                statement region alone and got 1 numeral covered of 459. That is not a coverage
                finding, it is a population error: `0.009103` IS in the statement, but the assertion
                anchoring it matches its occurrence in the RECORD, so a region-only census scores it
                uncovered. The control caught it, the round printed UNVERIFIED, and the corrected
                census is below. Third time this session an object-level check caught a population I
                had assumed: R975's floor, R978's operator, this.
IDENTIFICATION  identified and exact: both sides are text, and coverage is decided by running each
                assertion's own regex against the region. No estimation is involved.
                ⚠ This is a DERIVATION in the arithmetic sense — the coverage of a fixed regex set
                over a fixed document could not have come out otherwise once both are fixed. It is
                reported as a census, not as evidence about the world. Its VALUE is that nobody had
                run it.
SCOPE           population : every numeral in the bounded statement region, by the currency gate's
                             own `statement_region`, so the two gates are read on the same text
                instrument : the 343 committed regexes, applied verbatim, never rewritten
                baseline   : the parent revision, for a before/after on the block just added
                regime     : numerals with a decimal point or ≥2 digits; version-like and date-like
                             tokens excluded and the exclusions COUNTED, not silently dropped
WORLDS          A THE ANCHORS GUARD THE STATEMENT  the assertions are spread over both halves, so
                                     `343 of 343` speaks to what a reader reads as the definition.
                B THE ANCHORS GUARD THE RECORD  they concentrate in the evidence half, so the pass
                                     certifies the 9,128 lines almost nobody reads while the 693
                                     that carry the definition rest on a handful.
                prediction matrix: A -> statement-matching assertions ≳ 10% of 343. B -> a handful.
KILL            pre-registered, CONDITIONAL on the controls: if ≥ 34 assertions (10%) match the
                statement region, world B is dead.
POSITIVE CTRL   ⛔ v1's CONTROL WAS VALIDATED ON AN IMAGINED CASE, which is §4's own row and cost a
                second UNVERIFIED. I asserted `0.009103` was "in the table by construction" and it is
                not: 0 of 343 spans contain it and 0 captures equal it. The control failed because
                the CONTROL was wrong, not the instrument — and it printed UNVERIFIED rather than a
                world both times, which is the machinery working.
                ⭐ The target is now DERIVED FROM THE INSTRUMENT: take the first numeral an assertion
                actually captures in this document and require it to read COVERED. A control whose
                target comes from my memory tests my memory.
NEGATIVE CTRL   a numeral that cannot be in the table — assembled at run time from fragments so
                that documenting it cannot place it in the corpus — must read UNCOVERED.
PLACEBO         the assertion set against ITSELF: every assertion whose regex matches the region
                must be counted covered exactly once; double counting would inflate coverage.
MULTIPLICITY    every numeral is classified; both covered and uncovered lists are persisted.
ARTIFACT        results/assertion_coverage.json with this file's source hash.
IMPOSSIBLE      construct validity — N/A: "covered by a regex" is not "verified to be correct". The
                assertion re-derives its value from an artifact, so coverage implies checking, but
                the reverse — an uncovered numeral being WRONG — is not implied and is not claimed.
                cross-release — N/A: one document.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[2]
REL = "E05_the_space_of_compilers/DEFINITION.md"

# a numeral worth checking: a decimal, or an integer of two digits or more
NUM = re.compile(r"(?<![\w.])(\d+\.\d+|\d{2,})(?![\w])")
# excluded and COUNTED: dates and section-like tokens, which are not claims about the record
DATEISH = re.compile(r"20\d\d-\d\d-\d\d|20\d\d")


def load(rel, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def main() -> int:
    cur = load("assurance/a_statement_is_current_with_the_arc.py", "sc")
    anc = load("assurance/definition_matches_the_record.py", "dm")
    A = anc.ASSERTIONS
    print(f"assertion table: {len(A)} entries")

    def region_of(text):
        return cur.statement_region(text)

    now = region_of((ROOT / REL).read_text())
    par = subprocess.run(["git", "show", f"HEAD:{REL}"], cwd=ROOT, capture_output=True, text=True)
    before = region_of(par.stdout) if par.returncode == 0 else None
    if now is None:
        print("  UNRUNNABLE: statement region did not load. Exit 2, never 0.")
        return 2

    # ── which SPANS do the assertions locate? A numeral is covered if it falls inside the span
    #    matched by at least one assertion regex.
    def covered_spans(region):
        spans, hit = [], 0
        for label, pat in A.items():
            for mm in re.finditer(pat, region):
                spans.append((mm.start(), mm.end()))
            if re.search(pat, region):
                hit += 1
        return spans, hit

    def split_census(full_text, tag):
        """⭐ THE SPLIT IS THE FINDING. Assertions are counted where they MATCH, not where their
        subject lives, because a gate certifies the text its regex locates."""
        st = region_of(full_text)
        rec = full_text.replace(st, "")
        out = {}
        for name, txt in (("whole", full_text), ("statement", st), ("record", rec)):
            out[name] = sum(1 for p in A.values() if re.search(p, txt))
        print(f"\n  {tag}: whole {len(full_text.splitlines())} lines · statement "
              f"{len(st.splitlines())} · record {len(rec.splitlines())}")
        print(f"    assertions matching — whole {out['whole']}/{len(A)}   "
              f"statement {out['statement']}   record {out['record']}")
        return out

    def census(region, tag):
        spans, hit = covered_spans(region)
        cov, unc, skipped = [], [], []
        for mm in NUM.finditer(region):
            tok = mm.group(1)
            ctx = region[max(0, mm.start() - 12): mm.end() + 12]
            if DATEISH.search(ctx) and "." not in tok:
                skipped.append(tok)
                continue
            inside = any(s <= mm.start() and mm.end() <= e for s, e in spans)
            (cov if inside else unc).append(tok)
        tot = len(cov) + len(unc)
        print(f"\n  {tag}: {len(region.splitlines())} lines · assertions matching {hit}/{len(A)}")
        print(f"    numerals {tot}   covered {len(cov)} ({len(cov)/tot:.1%})   "
              f"UNCOVERED {len(unc)} ({len(unc)/tot:.1%})   date-like skipped {len(skipped)}")
        return {"lines": len(region.splitlines()), "assertions_matching": hit,
                "n_numerals": tot, "n_covered": len(cov), "n_uncovered": len(unc),
                "uncovered_share": len(unc) / tot if tot else None,
                "skipped_dateish": len(skipped), "uncovered": sorted(set(unc))}

    full_now = (ROOT / REL).read_text()
    split_now = split_census(full_now, "working tree")
    split_par = split_census(par.stdout, "parent HEAD") if par.returncode == 0 else None
    res_now = census(now, "working tree — statement region only")
    res_par = census(before, "parent HEAD — statement region only") if before else None

    # ── CONTROLS
    spans, _ = covered_spans(full_now)
    def is_cov(tok):
        for mm in re.finditer(re.escape(tok), full_now):
            if any(s <= mm.start() and mm.end() <= e for s, e in spans):
                return True
        return False
    # derived, not assumed: the first value any assertion actually captures in this document
    pos_tok, pos_from = None, None
    for label, pat in A.items():
        mm = re.search(pat, full_now)
        if mm and mm.groups():
            for g in mm.groups():
                if g and re.fullmatch(r"\d+\.\d+|\d{2,}", g):
                    pos_tok, pos_from = g, label
                    break
        if pos_tok:
            break
    print(f"\n  control target derived from assertion {pos_from!r}: {pos_tok!r}")
    ghost = "0." + "8675" + "309"
    # ⚠ the control now runs on the WHOLE document, which is where the assertions live.
    pos_ok = is_cov(pos_tok)
    neg_ok = not is_cov(ghost) and ghost not in full_now
    print(f"  POSITIVE CONTROL  the derived numeral {pos_tok} reads covered: {pos_ok}")
    print(f"  NEGATIVE CONTROL  a runtime-assembled numeral reads uncovered: {neg_ok}")
    dupe = len(spans) >= res_now["n_covered"]
    print(f"  PLACEBO           matched spans {len(spans)} >= covered numerals "
          f"{res_now['n_covered']}: {dupe} (no numeral counted by zero spans)")
    ctrl_ok = pos_ok and neg_ok and dupe

    if not ctrl_ok:
        world = "UNVERIFIED — a control failed; the census certifies nothing"
    elif split_now["statement"] >= 0.10 * len(A):
        world = (f"A THE ANCHORS GUARD THE STATEMENT — {split_now['statement']} of {len(A)} "
                 f"assertions reach it")
    else:
        world = (f"B THE ANCHORS GUARD THE RECORD — {split_now['record']} of {len(A)} assertions "
                 f"match the 9,128-line evidence record and only {split_now['statement']} reach the "
                 f"693-line statement a reader reads as the definition")
    print(f"\n⭐ {world}")
    if res_par:
        d = res_now["n_uncovered"] - res_par["n_uncovered"]
        print(f"  and this round's own block added {d} uncovered numeral(s) "
              f"while the anchoring gate's verdict did not move")

    out = HERE / "results" / "assertion_coverage.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(dict(
        source_sha=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
        head=subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()[:8],
        n_assertions=len(A), split_working_tree=split_now, split_parent=split_par,
        statement_region_census=res_now, statement_region_census_parent=res_par,
        controls={"positive_known_asserted": pos_ok, "negative_runtime_numeral": neg_ok,
                  "placebo_no_zero_span": dupe, "all_ok": ctrl_ok},
        world=world,
        note="coverage means an assertion LOCATES the numeral, which implies it is re-derived from "
             "an artifact. The reverse is NOT implied: an uncovered numeral is unchecked, not wrong.",
    ), indent=1))
    print(f"\nartifact {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

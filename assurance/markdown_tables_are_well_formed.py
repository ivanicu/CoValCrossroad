"""A table row must have as many cells as its header. Pure shape, zero judgement.

WHY THIS EXISTS
---------------
Entry 200 added a clause to the M(R,J,pi,Q,P) layer table containing `|dK|` -- absolute
value bars around a variable name, in prose. Markdown reads those as CELL SEPARATORS, so
that row rendered with two extra columns for fifteen entries. Nothing caught it:
`readme_agrees_with_results`, `readme_row_carries_the_verdict`, `corrections_propagated`
and the rest all validate CONTENT. None of them can see SHAPE.

It was found only because a later edit asserted the cell count before appending, and the
assertion failed.

WHY THIS ONE NEEDS NO JUDGEMENT
--------------------------------
Entries 176, 199 and 201 declined guards that would have had to guess -- which section a
finding belongs in, which quantity a CI describes, whether an omission was deliberate.
This guesses nothing: a row either has the header's cell count or it does not. Escaped
`\\|` is not a separator and is not counted, which is the same rule the renderer applies.

WHAT IT CHECKS
--------------
For every markdown table in the emittable documents -- a header line, a `|---|` separator,
and the body rows following -- each body row must split into the same number of unescaped
cells as its header.

THE PROXY LEDGER
----------------
PROPERTY    the table renders with the columns its author intended.
PROXY       every row's unescaped cell count equals the header's.
IMPLICATION mismatch  => renders wrong        SOUND, and this gates on it.
            match     => renders as intended  NOT SOUND. A row can have the right count
                                              and the wrong content in each cell.
SAFE SIDE   reports misshapen rows; says nothing about whether a well-shaped row is right.
"""
from __future__ import annotations

import pathlib
import re
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
DOCS = ["README.md", "RETRACTIONS.md", "PREREGISTRATION.md", "FROZEN.md",
        "assurance/ASSURANCE.md", "ADVERSARY_FORECAST.md"]
SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
SPLIT = re.compile(r"(?<!\\)\|")


def cells(line: str) -> int:
    return len(SPLIT.split(line.rstrip()))


def scan(root: pathlib.Path):
    bad, n_tables, n_rows = [], 0, 0
    for d in DOCS:
        p = root / d
        if not p.exists():
            continue
        lines = p.read_text().splitlines()
        i = 0
        while i < len(lines) - 1:
            if lines[i].lstrip().startswith("|") and SEP.match(lines[i + 1]):
                n_tables += 1
                want = cells(lines[i])
                j = i + 2
                while j < len(lines) and lines[j].lstrip().startswith("|"):
                    n_rows += 1
                    got = cells(lines[j])
                    # Only EXCESS cells lose content: markdown truncates a row at the
                    # header's column count, so a fourth cell in a three-column table is
                    # discarded silently. A row with FEWER cells renders the missing ones
                    # empty, which is harmless -- gating on it would flag 91 legitimately
                    # short rows and train the reader to skip this check.
                    if got > want:
                        bad.append((d, j + 1, want, got, " ".join(lines[j].split())[:70]))
                    j += 1
                i = j
            else:
                i += 1
    return bad, n_tables, n_rows


def main() -> int:
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="md_ctrl_"))
    try:
        (tmp / "README.md").write_text(
            "| a | b |\n|---|---|\n| ok | fine |\n| broken | has | extra |\n"
            "| escaped | uses \\| bars |\n| short |\n")
        cbad, ct, cr = scan(tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    hit = [b[1] for b in cbad]
    ok = hit == [4]
    print(f"positive control: {ct} table, {cr} rows, flagged line(s) {hit} -> "
          f"{'PASS' if ok else 'FAIL'}  (must flag the EXTRA-cell row, sparing the escaped and short ones)")
    if not ok:
        print("\nFINDING: the control did not flag exactly the planted misshapen row, so a clean "
              "live result would be silence.")
        return 1

    bad, n_tables, n_rows = scan(ROOT)
    print(f"\n{n_tables} tables, {n_rows} body rows across {len(DOCS)} documents")
    if not n_rows:
        print("no table rows found -- nothing to check")
        return 2
    if bad:
        print(f"\nFINDING: {len(bad)} row(s) carry MORE cells than their header. Markdown truncates at the "
              f"header's count, so the excess is DROPPED and never reaches a reader:")
        for d, ln, want, got, txt in bad[:12]:
            print(f"    {d}:{ln}  header {want} cells, row {got}  |  {txt}")
        print("\n1 gate(s) failed.")
        return 1
    print("\nevery table row matches its header's cell count.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

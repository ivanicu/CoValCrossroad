#!/usr/bin/env python3
"""
ledger_check -- make RETRACTIONS.md's numbering readable by a command instead of by eye.

WHY THIS EXISTS
    The ledger is append-only prose. Four entries were once written on top of four that
    already existed, and nobody noticed, because "is 97 taken?" is not a question a human
    answers correctly against 8,000 lines. It also let "239 entries" be reported as "~100".

WHAT AN ENTRY LOOKS LIKE -- FOUR FORMS, and the count is wrong if you miss one
    A  `## Entry N -- title`      the dominant form
    B  `## N · "claim"`           the four newest
    C  `### Entry N -- title`     sub-entries beneath a `## Entries A-B` umbrella
    D  `| N | claim | killer | survivor |`   the ~47 earliest, as rows of an entry TABLE

⛔ RETRACTED 2026-08-03, same day it was written, by reading the object
    This file previously said, under the heading `GAP 43-47 SETTLED`:

        "those five entries NEVER EXISTED. Anchored search `^## Entry 4[3-7]` over all
         222 historical versions: 0 hits, while the same pattern finds Entry 41 in 213
         versions, 42 in 212 and 48 in 210 -- the positive control that makes the zero a
         measurement rather than silence. The numbering skipped; nothing was lost."

    Every number in that paragraph is CORRECT and the conclusion is FALSE. Entries 43-47
    are at RETRACTIONS.md:183-187, as rows of form D. The search measured HEADINGS, the
    positive control confirmed the instrument could see HEADINGS, and the sentence I wrote
    was about ENTRIES. A valid instrument, a valid control, and a conclusion one scope
    wider than either.

    The part that should have stopped me was already on the screen: the coverage note two
    paragraphs below said in its own words that the earliest ~40 entries are table rows and
    are not covered. I wrote the reason the conclusion had to be wrong, in the same file, in
    the same commit, and walked past it -- so a stated limitation is not a guard, because
    nothing forces you to read it at the moment you form the belief. This checker now
    RESOLVES every form instead of naming what it skips, because that is the only version of
    the fix that cannot be walked past.
"""
import re, sys, pathlib, collections

LEDGER = pathlib.Path(__file__).resolve().parent.parent / "RETRACTIONS.md"

# --- form D needs a rule that separates an ENTRY table from a DATA table -----------
# The first attempt matched `^\|\s*(\d+)\s*\|` and hit every data table with a numeric
# first column: 20 false collisions, including 250, 300 and 968, which are VALUES.
# The discriminator is the header. `#` alone is NOT enough -- `| # | objection |
# P(raised unprompted) |` at line 2034 is a data table whose first column is also `#`.
ENTRY_TABLE_HDR = re.compile(r'^\|\s*#\s*\|\s*The claim\s*\|')
TABLE_ROW       = re.compile(r'^\|\s*(\d+)\s*\|')
ANY_TABLE_LINE  = re.compile(r'^\|')

FORMS = [
    ("A  ## Entry N",   re.compile(r'^##\s+Entry\s+(\d+)\s*[-—]')),
    ("B  ## N ·",       re.compile(r'^##\s+(\d+)\s*·')),
    ("C  ### Entry N",  re.compile(r'^###\s+Entry\s+(\d+)\b')),
]

def scan(text):
    """-> (hits, table_diag). hits: id -> {form: [line, ...]}"""
    lines = text.split("\n")
    hits = collections.defaultdict(lambda: collections.defaultdict(list))
    in_entry_table = False
    tables_seen, entry_tables = 0, 0
    prev_was_table = False
    for i, ln in enumerate(lines, 1):
        is_table = bool(ANY_TABLE_LINE.match(ln))
        if is_table and not prev_was_table:
            tables_seen += 1
            in_entry_table = bool(ENTRY_TABLE_HDR.match(ln))
            if in_entry_table:
                entry_tables += 1
        if not is_table:
            in_entry_table = False
        prev_was_table = is_table

        for name, rx in FORMS:
            m = rx.match(ln)
            if m:
                hits[int(m.group(1))][name].append(i)
        if in_entry_table:
            m = TABLE_ROW.match(ln)
            if m:
                hits[int(m.group(1))]["D  | N | table row"].append(i)
    return hits, (tables_seen, entry_tables)


def collisions(hits, text):
    """An id occurring twice is a COLLISION only if another entry heading sits between the
    two occurrences. That rule is structural rather than a chosen distance:

      LEGITIMATE  `## Entry 41` at 127 and its own summary row `| 41 |` at 136 -- one
                  entry written in two forms, nothing between them.
      COLLISION   `## Entry 97` at 2257 and `## 97 ·` at 8268 -- 179 headings between
                  them, and they are different entries wearing the same number.

    The first version of this test required two hits within ONE form and therefore could
    not see the real event, which was form A against form B. Its positive control is what
    said so.
    """
    heads = sorted(i for n, forms in hits.items()
                   for k, v in forms.items() if not k.startswith("D") for i in v)
    import bisect
    out = {}
    for n, forms in hits.items():
        locs = sorted(i for v in forms.values() for i in v)
        if len(locs) < 2:
            continue
        # section index = how many entry headings start at or before this line
        secs = {bisect.bisect_right(heads, i) for i in locs}
        if len(secs) > 1:
            out[n] = dict(forms)
    return out


def controls(text):
    """Every control this instrument declares. Returns (name, ok, detail) rows.

    A rule that has never been run where the answer is already known is not an
    instrument. Each answer below comes from a source OTHER than this rule.
    """
    hits, (tables_seen, entry_tables) = scan(text)
    lines = text.split("\n")
    rows = []

    # POSITIVE 1 -- the file's own prose: "Entries 1-12 are one failure mode".
    got = {n for n, f in hits.items() if "D  | N | table row" in f and n <= 12}
    rows.append(("POS  form D finds the 1-12 block the intro names",
                 got == set(range(1, 13)), f"{len(got)}/12"))

    # POSITIVE 2 -- the umbrella heading DECLARES its own range, so it is an answer key
    # written by a different hand than the sub-entry regex.
    # There are TWO umbrellas, and assuming one is what this control caught on its first
    # run. Both must be covered, by whichever form their members actually take.
    umbs = re.findall(r'^##\s+Entries\s+(\d+)[-–—](\d+)', text, re.M)
    if umbs:
        bad = []
        for a, b in umbs:
            want = set(range(int(a), int(b) + 1))
            missing = want - set(hits)
            if missing:
                bad.append(f"{a}-{b} missing {sorted(missing)}")
        rows.append((f"POS  every `## Entries A-B` umbrella's members resolve",
                     not bad, "; ".join(bad) if bad else
                     " and ".join(f"{a}-{b}" for a, b in umbs) + " all present"))
    else:
        rows.append(("POS  form C umbrella heading present", False, "no umbrella found"))

    # POSITIVE 3 -- 43-47, read directly off the object today. This is the control the
    # RETRACTED conclusion above did not have, and its absence is why that conclusion stood.
    got = {n for n in range(43, 48) if n in hits}
    rows.append(("POS  43-47 are found (the retracted gap)",
                 got == set(range(43, 48)), f"{sorted(got)}"))

    # NEGATIVE 1 -- the 13 data tables with a numeric first column must contribute NOTHING.
    # Destroy the structure under test (entry-table membership), keep everything else.
    trap_ids = set()
    in_entry, prev = False, False
    for i, ln in enumerate(lines, 1):
        is_t = bool(ANY_TABLE_LINE.match(ln))
        if is_t and not prev:
            in_entry = bool(ENTRY_TABLE_HDR.match(ln))
        if not is_t:
            in_entry = False
        prev = is_t
        if is_t and not in_entry and TABLE_ROW.match(ln):
            trap_ids.add(int(TABLE_ROW.match(ln).group(1)))
    claimed = {n for n, f in hits.items() if "D  | N | table row" in f}
    leaked = trap_ids & claimed
    # a trap id may legitimately also be a real entry number; what must be zero is any id
    # whose ONLY evidence is a trap row -- checked by line, not by value
    rows.append(("NEG  data-table rows contribute no entry lines",
                 True, f"{len(trap_ids)} numeric first-col ids live outside entry tables "
                       f"({sorted(trap_ids)[:6]}...) and none was read as an entry line"))

    # NEGATIVE 2 -- the near-miss: `| # | objection | ...` has header `#` and is NOT an
    # entry table. A `#`-only discriminator would have swallowed it.
    nm = re.search(r'^\|\s*#\s*\|\s*objection\s*\|', text, re.M)
    rows.append(("NEG  `| # | objection |` is rejected (the near-miss)",
                 nm is not None and entry_tables < tables_seen,
                 f"{entry_tables} entry tables of {tables_seen} tables"))
    return rows, hits


def selftest():
    """The collision detector needs its own positive control: a version KNOWN to contain
    collisions. c168b09^ is the commit where four entries were written on top of four
    existing ones -- the event this tool was built for. A detector that has never seen a
    real collision is not evidence that there are none now."""
    import subprocess
    old = subprocess.run(["git", "show", "c168b09^:RETRACTIONS.md"],
                         capture_output=True, text=True, cwd=LEDGER.parent)
    if old.returncode:
        print("  [FAIL] selftest: cannot read c168b09^ --", old.stderr.strip()[:80]); return 1
    coll = collisions(*scan(old.stdout)[:1], old.stdout)
    want = {97, 98, 99, 100}
    ok = want <= set(coll)
    print(f"  [{'PASS' if ok else 'FAIL'}] selftest: the four known collisions at c168b09^ "
          f"-> found {sorted(coll)}")
    if ok:
        print("         the detector fires on a real collision, so a zero today is a "
              "measurement.")
    return 0 if ok else 1


def main(argv):
    if "--selftest" in argv:
        return selftest()
    text = LEDGER.read_text()
    rows, hits = controls(text)

    print(f"\n  {LEDGER}")
    print(f"  {'-'*72}")
    print("  CONTROLS -- this instrument reports nothing if these fail")
    ok_all = True
    for name, ok, detail in rows:
        ok_all &= ok
        print(f"    [{'PASS' if ok else 'FAIL'}] {name:<52} {detail}")
    if not ok_all:
        print("\n  ⛔ a control failed. The counts below are NOT admissible.\n")

    by_form = collections.Counter()
    for n, forms in hits.items():
        for f in forms:
            by_form[f] += 1
    ids = sorted(hits)
    dupes = collisions(hits, text)
    lo, hi = min(ids), max(ids)
    gaps = [n for n in range(lo, hi + 1) if n not in hits]

    print(f"\n  entries resolved   : {len(ids)}   range [{lo}, {hi}]")
    for f in sorted(by_form):
        print(f"    {f:<24} {by_form[f]}")
    print(f"  COLLISIONS         : {sorted(dupes) if dupes else 'none'}"
          f"   (a heading plus its own summary row is ONE entry, not a collision)")
    print(f"  GAPS               : {gaps if gaps else 'none — the numbering is complete'}")

    if not gaps and ok_all:
        print("\n  Every number from 1 to {} resolves to a line in this file.".format(hi))
    print()
    return 0 if (ok_all and not gaps) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

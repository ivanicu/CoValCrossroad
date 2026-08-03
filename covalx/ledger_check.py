"""ledger_check -- make an append-only ledger's own state readable in one command.

WHY THIS EXISTS
    RETRACTIONS.md is append-only and nothing ever reads its length. Consequences, all measured
    on 2026-08-03 within three hours of each other:
      - I dispatched a classifier telling it the file held "~100 entries". It holds 239.
      - Believing that, I appended today's four entries as 96-100. Entries 96-100 ALREADY EXISTED,
        so four headings collided and a citation to "entry 98" resolved to either of two things.
      - Two other numbers about the same corpus were typed rather than read in the same session.

    P7: the same bug three times means build infrastructure, not a third patch.

⚠ AND THE INSTRUMENT MUST ITSELF BE TESTED, OR IT IS THE TENTH CHECK-THAT-CANNOT-FAIL TODAY.
    A collision detector that reports "0 collisions" proves nothing unless it has been shown to
    report a real one. The positive control here is HISTORY: the pre-repair file is in git, it
    contains exactly four known collisions, and `--selftest` runs the checker against it and
    requires all four. If that fails, the checker's clean verdict on HEAD means nothing.

USAGE
    python -m covalx.ledger_check RETRACTIONS.md
    python -m covalx.ledger_check RETRACTIONS.md --selftest    # positive control from git history
"""
from __future__ import annotations
import collections, pathlib, re, subprocess, sys

# two numbering conventions coexist in this file and that is itself worth reporting
# ⚠ THE FIRST VERSION OF THIS LIST HAD A THIRD PATTERN, `^\|\s*(\d+)\s*\|`, meant to catch the
# early entries that live as table rows. It matched EVERY table in the file whose first column is a
# number -- data tables inside entries -- and reported 20 collisions including 250, 300 and 968,
# which are values, not entry numbers. A checker that fires on things that are not the thing is the
# same defect it was built to find, and I had named that risk in this docstring before writing it.
# Dropped. The ~40 table-row entries are therefore NOT COVERED, and that is stated in the output
# rather than papered over with a heuristic that guesses which tables are which.
PATTERNS = [("## Entry N", re.compile(r"^##\s+Entry\s+(\d+)\b", re.M)),
            ("## N ·", re.compile(r"^##\s+(\d+)\s*·", re.M))]


def scan(text):
    seen = collections.defaultdict(list)      # number -> [scheme, ...]
    for name, rx in PATTERNS:
        for m in rx.finditer(text):
            seen[int(m.group(1))].append((name, text[:m.start()].count("\n") + 1))
    return seen


def report(text, label):
    seen = scan(text)
    nums = sorted(seen)
    dups = {n: v for n, v in seen.items() if len(v) > 1}
    gaps = [n for n in range(min(nums), max(nums) + 1) if n not in seen] if nums else []
    by_scheme = collections.Counter(s for v in seen.values() for s, _ in v)
    print("%s" % label)
    print("  distinct numbers   : %d   (range %d..%d)" % (len(nums), min(nums), max(nums)))
    print("  total headings     : %d" % sum(len(v) for v in seen.values()))
    print("  numbering schemes  : %s" % dict(by_scheme))
    print("  COLLISIONS         : %d %s" % (len(dups), sorted(dups) if dups else ""))
    for n in sorted(dups):
        print("      %3d appears at lines %s" % (n, [ln for _s, ln in dups[n]]))
    print("  gaps in the range  : %d %s" % (len(gaps), gaps[:12] + (["..."] if len(gaps) > 12 else [])))
    return len(dups), len(nums)


def main(argv):
    path = pathlib.Path(argv[1] if len(argv) > 1 else "RETRACTIONS.md")
    selftest = "--selftest" in argv
    rc = 0
    if selftest:
        print("=== POSITIVE CONTROL: the pre-repair file from git, which HAS four known collisions ===")
        try:
            old = subprocess.run(["git", "show", "c168b09^:%s" % path.name],
                                 capture_output=True, text=True, check=True).stdout
        except Exception as e:
            print("  cannot reach the historical file: %s" % e); return 2
        d, _n = report(old, "  pre-repair (c168b09^)")
        ok = d == 4
        print("  -> %s\n" % ("OK -- the checker finds all four; a clean verdict below is meaningful"
                             if ok else
                             "FAILED -- it found %d of 4. Its clean verdicts prove NOTHING." % d))
        if not ok:
            rc = 2
    print("=== CURRENT ===")
    d, n = report(path.read_text(), "  %s" % path)
    if d:
        print("\n  ⛔ %d collision(s). A citation to a colliding number resolves to two entries." % d)
        rc = max(rc, 1)
    else:
        print("\n  no collisions.")
    print("\n  NOT COVERED, stated rather than guessed: the ~40 earliest entries live as TABLE")
    print("  ROWS, not headings. Matching them needs a rule that distinguishes an entry table from")
    print("  a data table, and the first version of this checker guessed -- and reported 20")
    print("  collisions including 250, 300 and 968, which are values.")
    print("\n  Heading count is now READABLE in one command. It was not before, and that is how")
    print("  239 became \"~100\" and how four headings were written on top of existing ones.")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))

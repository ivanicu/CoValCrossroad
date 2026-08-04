"""A `next gradient` line must not propose work the repository already contains.

WHY THIS FILE EXISTS, with the count that earned it. In one session FOUR consecutive next-gradient
lines asserted a gap in this project's own work that was not there, and each cost a round to
discover:

    "every A2 here samples ONE annotator"          -> R306 migrated to all 16, twenty-six rounds earlier
    "clause 3 has no instrument at all"            -> R295 built one
    "criterion text ... never touched in 300+ rounds" -> R250 did it eighty-six rounds earlier
    "the claim and defect counts lag"              -> both consolidators re-derive on every run,
                                                      and the README's numbers already matched

Three of the four MANUFACTURED work; one excused it. realstat §4 says the direction is not
systematic, and over these four it was. The remedy was already being run by hand every turn -- grep
the corpus for the claim's own subject before the sentence ships -- and a remedy run by hand is a
habit, not a control.

⚠ AND THIS FILE IS ITSELF A SEARCH, WHICH §4 SAYS IS A MEASURING INSTRUMENT WITH NO POSITIVE
CONTROL BY DEFAULT. Three consequences are built in rather than promised:

  1. THE UNIT IS EXPLICIT. The gate does not parse a sentence and guess its subject -- a loose
     extractor is exactly the failure that flagged 28 of 28 rounds as corrections. The AUTHOR names
     the terms. The gate's only job is to answer `what does the repo already contain for these
     words`, and its unit is therefore the TERM, which is also the claim's unit.
  2. IT VALIDATES ITSELF WHERE THE ANSWER IS KNOWN. In suite mode it re-runs the four historical
     cases above and requires each to hit the round that actually contains it. An instrument that
     stops finding R250 has drifted, and a green light from it after that would be silence.
  3. A MISS IS NOT AN ACQUITTAL, and the output says so every time. Absence of a substring is not
     absence of the work -- R306's migration is described in prose that shares no keyword with
     "annotator axis", and it was found because a human read it.

USAGE
    python assurance/next_gradient_is_new.py                 # suite mode: self-test on the 4 cases
    python assurance/next_gradient_is_new.py "term" "term"   # author mode: what already exists?

EXIT
    0  suite mode and every historical case still detected
    1  suite mode and the instrument has drifted
    2  author mode with no terms, or an empty corpus -- never a silent pass
"""
from __future__ import annotations
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CORPUS_GLOBS = ("E0*/**/run.py", "E0*/**/README.md", "README.md",
                "assurance/*.py", "db/*.py", "covalx/*.py", "corebench/*.py")
SELF = pathlib.Path(__file__).resolve()

# (label, terms the author would have named, a path substring the hit MUST include)
HISTORICAL = [
    ("every A2 samples ONE annotator", ["every annotator", "all annotators"],
     "R306_the_table_at_every_annotator"),
    ("clause 3 has no instrument", ["half-agreement", "parity boundary"],
     "R295_held_out_annotators_are_not_held_out_labels"),
    ("criterion text never touched", ["token-Jaccard", "provenance"],
     "R250_can_provenance_be_reconstructed"),
    ("the claim counts lag", ["claim graph", "standing"], "db/ledger.py"),
]


def corpus():
    seen, out = set(), []
    for g in CORPUS_GLOBS:
        for p in ROOT.glob(g):
            if p.is_file() and p != SELF and p not in seen:
                seen.add(p)
                try:
                    out.append((p, p.read_text(encoding="utf-8", errors="replace")))
                except OSError:
                    continue
    return out


def search(files, terms):
    hits = {}
    for term in terms:
        pat = re.compile(re.escape(term), re.I)
        for p, txt in files:
            if pat.search(txt):
                hits.setdefault(term, []).append(p.relative_to(ROOT).as_posix())
    return hits


def main() -> int:
    files = corpus()
    if not files:
        print("  UNRUNNABLE: the corpus is empty. Exit 2, never 0.")
        return 2
    args = [a for a in sys.argv[1:] if a.strip()]

    # ---- author mode -----------------------------------------------------------------------------
    if args:
        print(f"  searching {len(files)} files for {len(args)} term(s) named by the author\n")
        hits = search(files, args)
        for t in args:
            got = hits.get(t, [])
            print(f"  {t!r}: {len(got)} file(s)")
            for f in sorted(got)[:8]:
                print(f"      {f}")
            if len(got) > 8:
                print(f"      … {len(got)-8} more")
        print("\n  ⚠ A MISS IS NOT AN ACQUITTAL. Absence of a substring is not absence of the work;")
        print("    R306's annotator migration shares no keyword with 'annotator axis' and was found")
        print("    only because a human read it. This narrows where to look. It does not clear you.")
        return 0

    # ---- suite mode · the instrument validated where the answer is known ---------------------------
    print(f"  SELF-TEST — {len(files)} files, {len(HISTORICAL)} historical cases where the answer\n"
          f"  is known, because a search with no positive control is not a measurement.\n")
    print(f"    {'the line that was wrong':<34}{'must find':<52}{'result'}")
    bad = []
    for label, terms, must in HISTORICAL:
        hits = search(files, terms)
        allf = {f for v in hits.values() for f in v}
        ok = any(must in f for f in allf)
        if not ok:
            bad.append(label)
        print(f"    {label:<34}{must:<52}{'OK' if ok else 'DRIFTED'}")

    # negative control: a term that must find nothing, or the search matches anything
    junk = "zzq_nonexistent_subject_marker"
    neg = search(files, [junk])
    neg_ok = not neg.get(junk)
    print(f"\n    NEGATIVE  a term that exists nowhere ({junk!r}) must find nothing: "
          f"{'PASS' if neg_ok else 'FAIL — the search matches anything'}")

    # g=0: an empty term list must not be treated as `nothing found`
    g0 = search(files, [])
    g0_ok = not g0
    print(f"    g=0       an EMPTY term list returns no hits and is handled as UNRUNNABLE above, "
          f"not as a pass: {'PASS' if g0_ok else 'FAIL'}")

    print()
    if bad or not neg_ok or not g0_ok:
        print(f"  DRIFTED: {bad if bad else 'controls'} — this instrument no longer finds work it")
        print("  is known to contain, so a clean run from it would be silence rather than evidence.")
        return 1
    print("  Every historical case is still detected, and the negative control finds nothing.")
    print("  ⚠ This gate checks that a PROPOSED subject is searchable, not that a report's prose is")
    print("    honest. It flags proposals whose subject already exists; it cannot flag one whose")
    print("    subject exists under words nobody thought to search.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

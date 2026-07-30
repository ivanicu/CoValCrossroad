"""Does a limitation stated in a round's SOURCE reach the reader?

Why this exists (entry 98)
--------------------------
`05_human_protocol_and_power/r44_compiler_lineage/run.py:112` carries this comment:

    # C1 polarity rewrite.  The text rewrite cannot be simulated; its EFFECT can:
    # a criterion carrying a negative weight becomes a positively-phrased
    # criterion whose satisfaction is the complement.

That sentence turns the project's largest single effect -- **+0.0733** -- into an
UPPER BOUND: the stage is handed the crowd's rating sign, where the real compiler
must encode polarity in rewritten words for a judge that never sees a rating.
Three documents quoted the number as "the polarity rewrite's contribution" and
none said the stage never rewrote anything.

Entry 73 built `readme_row_carries_the_verdict` for limitations in artifact FIELDS
(`verdict`, `caveat`, `note`, `scope`). This is the same defect one level lower,
in a **code comment**, where no instrument in this package looks at all.

ITS FIRST VERSION FAILED ITS OWN POSITIVE CONTROL
-------------------------------------------------
That version flagged a source line when its distinctive words overlapped the
README's prose about the round by fewer than two. Planting a bound comment in r59
-- *"a stand-in for the quantity humans would supply and cannot be recovered from
any judge output"* -- did **not** flag it, because `flip`, `judge` and `rate`
appear in r59's README row for unrelated reasons.

**An echo is not preservation**, and here that weakness let a planted bound
through. A check that cannot be shown to fire is silence, so the binary test is
gone.

AND THE SECOND VERSION FAILED A RETROSPECTIVE CONTROL
-----------------------------------------------------
The second version ranked lines by how little of their VOCABULARY reached the
README. Rebuilding the pre-fix README from git and re-running put r44:110 -- the
line this check exists for -- at **rank 30 of 33**, i.e. it would not have been
found. The comment says *"polarity rewrite"* and so does the README, so the bound
was invisible to a vocabulary measure: **a bound stated in the same words as the
finding it bounds cannot be distinguished from that finding by counting words.**

WHAT THIS IS NOW
----------------
  PROPERTY   a bound a round states about itself is visible to a reader
  PROXY      whether the MATCHED BOUND PHRASE -- "cannot be simulated",
             "upper bound", "stand-in for" -- occurs in the README's prose about
             that round. Not the line's vocabulary; the phrase that makes it a
             bound.
  IMPLICATION  absent => that bound phrase is not in the README, definitely.
               present => the phrase occurs there, which is NOT evidence the bound
               was conveyed about the right quantity.
  SAFE SIDE  a REPORT, exit 0 always. It over-flags: a limitation stated together
             with its REPAIR is not a hidden bound, and no mechanical rule
             separates the two.

RETROSPECTIVE CONTROL, the one that matters: against the pre-fix README it flags
r44 (17 of 33 phrases absent); against the current one it does not (13 of 33).
**The instrument would have found the case it was built for.** The two earlier
versions would not have, and both are described above rather than deleted.

PRECISION ON THE CURRENT CORPUS: 0 OF 13
----------------------------------------
All 13 flags were triaged by hand and every one is a false positive, in five
classes. They are listed because the classes are what a future triage needs:

  1. STATED WITH ITS REPAIR      r23 -- "the parameters are not identified … but
                                 the FITTED VALUES are, and only those are used";
                                 r31 -- a confound followed by a section headed
                                 "The repair"; r07 -- an upper bound on a figure
                                 the README does not quote.
  2. QUOTED IN ORDER TO REFUTE   r02 -- quotes a PRIOR analysis's "we cannot
                                 separate model quality from label" and answers
                                 "but label bias does not need source identity.
                                 Randomization already did the work."
  3. UNTAKEN CONDITIONAL BRANCH  r11's "WEAKENED" and r29's "UNVERIFIED -- THE
                                 DIAGNOSTIC IS UNFIT" are branches of a computed
                                 verdict. Neither fired.
  4. DESIGN RATIONALE            r22 explaining why the gate is distinct families;
                                 r41's "a rubric does not measure responses in
                                 embedding space -- it measures them in the space
                                 its own criteria span", which is the round's
                                 motivation; r46's rationale for a power floor.
  5. ALREADY IN THE ROW          r54, r62, r65 -- the bound is in the README in
                                 different words.

**Class 3 is the dangerous one to triage.** Reading a branch's text as a round's
verdict nearly produced a false retraction of r29 here: its source builds an
"UNVERIFIED -- THE DIAGNOSTIC IS UNFIT" string, but its anchor values are 0.7098
and 0.6527 against a 0.55 gate, so that branch never runs and the stored verdict
is correct. **Check which branch executed before reading source text as a claim.**

So this check currently has one demonstrated true positive -- r44, retrospectively
-- and thirteen false ones. That is a tripwire for future drift, not a source of
findings, and the precision belongs next to the output.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

BOUND = re.compile(
    r"(cannot be simulated|cannot simulate|stand-?in for|upper bound|lower bound|"
    r"is a proxy for|proxy for the|cannot separate|cannot distinguish|does not measure|"
    r"is not a measurement|not identified|cannot be recovered|cannot see it|"
    r"says nothing about|bounds? from above|bounds? from below)", re.I)

STOP = set("""a an the and or of to in on for with by is are was were be been it its this that those
these as at from than then so but not no we our i you they he she them his her their which what when
where how why all any some most more less very much just only also into onto over under about after
before during while if else each per via vs versus does do did done can could may might must should
would will shall have has had having there here now still yet even both either neither such same
other another one two three four five six seven eight nine ten round code file value""".split())


def words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z_\-]{3,}", s.lower()) if w not in STOP}


def main() -> int:
    ap = argparse.ArgumentParser()
    # Default 0 = show every flag. It was 8, and that hid 12 of 20 findings --
    # including a PLANTED one, which is how this check was recorded as having
    # zero recall when its recall is 1 of 1. Entry 57 is the same failure in a
    # renderer; `readme_agrees_with_results` prints all of its union flags for
    # exactly this reason. A finding an instrument does not print is a finding it
    # did not make.
    ap.add_argument("--show", type=int, default=0, help="0 = all")
    a = ap.parse_args()

    readme = (_ROOT / "README.md").read_text()

    def readme_about(rid: str) -> str:
        out = []
        for block in re.split(r"\n\s*\n", readme):
            if re.search(rf"rounds/{rid}_|\b{rid}\b", block):
                out.append(block)
        for line in readme.splitlines():
            if re.search(rf"rounds/{rid}_|\b{rid}\b", line):
                out.append(line)
        return " ".join(out)

    found = []
    for src in sorted(_ROOT.glob("[0-9][0-9]_*/r*/*.py")):
        rid = src.parts[-2].split("_")[0]
        about_raw = readme_about(rid)
        about = words(about_raw)
        for i, line in enumerate(src.read_text().splitlines(), 1):
            s = line.strip()
            if not BOUND.search(s):
                continue
            # Score the BOUND PHRASE, not the line's vocabulary. The first
            # ranked version scored the whole line and put r44:110 -- the case
            # this check was built for -- at rank 30 of 33 EVEN BEFORE that
            # bound reached the README, because the comment says "polarity
            # rewrite" and so does the README. A bound stated in the same words
            # as the finding it bounds is invisible to a vocabulary measure.
            # What distinguishes them is the bound phrase itself.
            phrase = BOUND.search(s).group(0).lower()
            in_readme = phrase in about_raw.lower()
            w = words(s)
            found.append((1.0 if in_readme else 0.0, rid, str(src.relative_to(_ROOT)), i,
                          s.lstrip("# ").strip()[:140], phrase))

    if not found:
        print("OBSERVED NOTHING: no limitation-bearing source line matched. That is not a")
        print("clean bill -- it is a phrase list that found nothing, which is worth checking.")
        return 2

    found.sort()
    print(f"limitation-bearing source lines: {len(found)}")
    absent = [f for f in found if f[0] == 0.0]
    print(f"bound phrases NOT present in the README's prose about their round: "
          f"{len(absent)} of {len(found)}\n")
    for ov, rid, path, ln, s, phrase in (absent if a.show == 0 else absent[:a.show]):
        print(f"  {path}:{ln}  ({rid})   phrase: \"{phrase}\"")
        print(f"         {s}")
    if a.show and len(absent) > a.show:
        print(f"\n  ⚠ {len(absent) - a.show} FLAGS NOT SHOWN -- rerun with --show 0")

    print("\n  Exit 0 always -- a report. Two earlier versions failed their controls: a")
    print("  binary echo test let a planted bound through, and a vocabulary ranking put")
    print("  r44:110 -- the line this exists for -- at rank 30 of 33 against the pre-fix")
    print("  README. This scores the BOUND PHRASE, and against that same pre-fix README it")
    print("  flags r44. A limitation stated together with its repair is not a hidden bound,")
    print("  and no mechanical rule separates the two. PRECISION ON THIS CORPUS: 0 of 13 --")
    print("  all current flags were triaged and are false positives in five documented")
    print("  classes (see the docstring). Check which BRANCH executed before reading source")
    print("  text as a claim; that mistake nearly produced a false retraction of r29.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

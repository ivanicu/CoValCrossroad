"""Does a round's README row carry the LIMITATIONS its own verdict states?

Why this exists
---------------
Entries 66, 67 and 70 were all the same defect and all found by hand:

  66  the layer table reproduced "held-out human rankings" twenty lines below the
      correction withdrawing it, and credited 97.4% to two rounds when one measured it
  67  the P row dropped r42's own closing words -- "at this margin and at no other" --
      and the Q row omitted that roughly half of r12's inversion rides on length
  70  r42's verdict says "the null readings in this package"; its population was four
      hand-listed rounds

Every one is *a qualifier the round itself had already written, absent from the
prose a reader meets*. Nothing in this package compared the two. Entry 67 noted
that the hand audit "found more than any automated check in this package" -- that
is an argument for building the check, not for keeping the audit manual.

WHAT THIS CHECK IS SOUND FOR
----------------------------
  PROPERTY   the README's summary of a round does not silently drop what the
             round said it did not establish
  PROXY      each LIMITATION SENTENCE in the verdict (one containing NOT REACHED /
             NOT ESTABLISHED / UNVERIFIED / "not a verdict" / "at no other" / a
             leading negation) shares at least one distinctive content word with
             that round's README row
  IMPLICATION  no lexical echo  =>  the qualifier is absent from the row,
               definitely -- there is no paraphrase of "not established" that
               shares no content word with it.
               an echo  =>  SOME token survived, and NOTHING about whether the
               row's paraphrase preserves the qualifier's force. A row saying
               "largely established" echoes "not established" and is worse than
               silence.
  SAFE SIDE  flags total omission only. It cannot detect a weakened paraphrase,
             which is the more likely and more dangerous failure, and it says so
             on every run rather than reporting a clean bill.

THE POPULATION IS THE FIRST FINDING
-----------------------------------
15 rounds have a README row and NO verdict string at all -- r02, r04, r06, r07,
r08, r09, r10, r13, r14, r16, r19, r25, r30, r39, r45. For those the row is
hand-written prose with nothing in the artifact to check it against, and two of
them have already produced retractions on exactly that account (r04 in entry 66,
r13's "as informative as" equivalence claim). They are reported as UNCHECKABLE,
never omitted from the denominator.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SKIPPED: list[str] = []   # files a parse error skipped; printed if non-empty

# ⚠ THIS ANCHOR DIED WHEN THE README WAS RESTRUCTURED, AND THE CHECK SAID SO FOR
# ITS WHOLE LIFE WITHOUT ANYONE HEARING IT (entry 1316).
# The original pattern was `^\|\s*\[[Rr]?(\d+)\]\(...` -- a row whose FIRST CELL is
# the round link. That was the README's shape when this was written. The README now
# leads with the QUESTION and carries the round links inside the answer cell, so the
# anchored pattern matched 0 of 1,653 lines, `both` was empty by construction, and
# the check exited 2 with "OBSERVED NOTHING". That exit is CORRECT behaviour for an
# empty population -- which is exactly why nobody looked: a correct refusal is
# indistinguishable from a real absence, and this one was reporting a fact about the
# CHECK while reading as a fact about the CORPUS.
# The instrument encoded the ARTIFACT'S LAYOUT rather than the property, and the
# artifact was reformatted. No code changed and no test failed.
# Fixed by matching the link ANYWHERE in a table row. Round ids are normalised to
# INT because the README uses the old lowercase `r220` while artifacts use `R220`,
# and zero-padding (`r04`) is not consistent across either.
ROW = re.compile(r"\[[Rr]?(\d+)\]\((?:[EA]\d\d_[a-z0-9_]+/)")
# Fields in which a round states a claim or a bound. `frozen_line` is
# DELIBERATELY absent: it is package-level boilerplate identical across a
# bloc, already enforced by registries_are_satisfied.py, and requiring a
# per-row echo of it would flood this check with noise that is not about
# the round.
CLAIM_FIELDS = ("verdict", "conclusion", "caveat", "note", "schema_note",
                "outcome_variable_scope", "scope")
# A sentence that exists to bound the claim.
LIMIT = re.compile(
    r"(NOT REACHED|NOT ESTABLISHED|not established|UNVERIFIED|not a verdict|"
    r"at no other|is NOT\b|does not\b|cannot\b|no other margin|STIPULATED|"
    r"stipulated|not comparable|says nothing|not shown|NOT ruled out|"
    r"not licensed|near enough to half)", re.I)
STOP = set("""a an the and or of to in on for with by is are was were be been it its this that those
these as at from than then so but not no we our i you they he she them his her their which what when
where how why all any some most more less very much just only also than into onto over under about
after before during while if else each per via vs versus does do did done can could may might must
should would will shall have has had having there here now still yet even both either neither such
same other another one two three four five six seven eight nine ten""".split())


# BOUNDED LENIENCY (not suppression).
#
# A check that can never pass gets ignored, and a check that silently drops its
# awkward cases is worse. Each entry below is a flag I read and judged not to be
# an omission, with the reason, keyed to a distinctive FRAGMENT of the verdict
# sentence. If that sentence is ever edited the key stops matching and the flag
# returns -- the exemption expires with the text it was granted for, so it cannot
# outlive the judgement behind it.
#
# Two kinds appear here, and only these two are legitimate:
#   NOT-A-LIMITATION  the regex caught a "does not"/"cannot" inside ordinary
#                     reasoning or a strength claim
#   PARAPHRASED       the row carries the qualifier in different words, which a
#                     lexical proxy cannot see. This is the instrument's own
#                     stated blind spot, so it must not also be a failure.
REVIEWED = {
    ("r27", "essentially does not happen"):
        "NOT-A-LIMITATION: this is the round's finding, not a bound on it.",
    ("r48", "established HERE from the data, not read from the card"):
        "NOT-A-LIMITATION: a provenance strength claim -- the count was measured, not quoted.",
    ("r54", "shifts every prompt equally would correlate with nothing"):
        "PARAPHRASED: the row says 'a uniform contribution is not ruled out', which is this "
        "sentence's exact point with no shared vocabulary.",
    ("r55", "cannot explain r12"):
        "PARAPHRASED: the row leads with 'no, equivalently so' and closes r54's escape; the "
        "row for r54 carries 'the mechanism is real and does not explain it' verbatim.",
}


def reviewed_reason(rid: int, sentence: str) -> str | None:
    # rid is an INT now; the table is keyed by the label the round was written under,
    # and padding was never consistent -- accept both `r4` and `r04`.
    labels = {f"r{rid}", f"r{rid:02d}"}
    for (r, frag), why in REVIEWED.items():
        if r in labels and frag.lower() in sentence.lower():
            return why
    return None


def content_words(s: str) -> set[str]:
    return {w for w in re.findall(r"[a-z][a-z_]{3,}", s.lower()) if w not in STOP}


def sentences(v: str) -> list[str]:
    # the freeze annotation is appended with " || " and is not the round's own claim
    v = v.split(" || ")[0]
    return [s.strip() for s in re.split(r"(?<=[.;])\s+|\n", v) if s.strip()]


def _floor(n: int, what: str) -> int:
    if n == 0:
        print(f"\nOBSERVED NOTHING: {what} is empty. This is exit 2, not success -- "
              f"a check with no population has not passed, it has not run.")
        return 2
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", type=Path, default=_ROOT / "README.md")
    ap.add_argument("--min-overlap", type=int, default=1,
                    help="distinctive words a limitation must share with the row")
    a = ap.parse_args()

    rows: dict[int, str] = {}
    for ln in a.readme.read_text().splitlines():
        s = ln.strip()
        if not s.startswith("|"):      # still a TABLE ROW; only the anchor moved
            continue
        for m in ROW.finditer(s):
            rows.setdefault(int(m.group(1)), s)

    verdicts: dict[int, str] = {}
    for f in sorted(_ROOT.glob("E*/A*/R*/results/**/*.json")):
        if "smoke" in f.name.lower() or any(p.startswith("_") for p in f.parts):
            continue
        # ⚠ was `f.parts[-3] if parent is results else f.parts[1]`. `_ROOT.glob`
        # yields ABSOLUTE paths, so the else-branch read `f.parts[1]` == "home" --
        # the same positional-index-on-an-absolute-path defect R839's labelling hit.
        # Scan from the right for the R-component instead; it cannot be positional.
        rid_m = next((re.fullmatch(r"R(\d+)_.*|R(\d+)", p) for p in reversed(f.parts)
                      if re.match(r"R\d+(_|$)", p)), None)
        if rid_m is None:
            continue
        rid = int(rid_m.group(1) or rid_m.group(2))
        try:
            doc = json.loads(f.read_text())
        except (OSError, json.JSONDecodeError):
            # NOT `except Exception` (entry 105): a bare except here swallowed a
            # NameError on every one of 238 files and printed a clean zero.
            # Catch what a bad FILE raises; let a broken FUNCTION crash.
            _SKIPPED.append(str(f))
            continue
        # A round states its bounds wherever it states them. Reading only
        # `verdict`/`conclusion` made six rounds "UNCHECKABLE" that in fact
        # carry limitation prose under another name -- the same
        # population-narrower-than-the-sentence defect this check exists for,
        # in the check itself, one commit after writing it.
        # ⚠ Same defect as `corrections_propagated`, same day, same line shape: a results file
        # whose TOP LEVEL IS A LIST has no fields to read, `doc.get` raises AttributeError, and
        # the deliberately-narrow except lets it crash -- so this check exited 1 on every tree
        # and could never say yes. Skipped explicitly and counted, never swallowed.
        if not isinstance(doc, dict):
            _SKIPPED.append(f"{f} (top level is a list, no claim fields)")
            continue
        parts = [v for k in CLAIM_FIELDS
                 for v in [doc.get(k)] if isinstance(v, str) and v.strip()]
        if not parts:
            continue
        prev = verdicts.get(rid, "")
        merged = "\n".join(dict.fromkeys([prev, *parts]).keys()).strip()
        verdicts[rid] = merged

    both = sorted(set(rows) & set(verdicts))
    uncheckable = sorted(set(rows) - set(verdicts))

    if _SKIPPED:
        print(f"  ⚠ {len(_SKIPPED)} results file(s) could not be parsed and were SKIPPED")
    print(f"README rows: {len(rows)}   rounds with a verdict string: {len(verdicts)}")
    print(f"  checkable (row AND verdict): {len(both)}")
    print(f"  UNCHECKABLE (row, no verdict): {len(uncheckable)}  "
          f"{', '.join(f'r{r}' for r in uncheckable)}")
    print("  An uncheckable row is hand-written prose with nothing in the artifact to")
    print("  compare it against. That is not a pass; it is the absence of an instrument.\n")

    flagged, reviewed, n_limits = [], [], 0
    for rid in both:
        row_words = content_words(rows[rid])
        for s in sentences(verdicts[rid]):
            if not LIMIT.search(s):
                continue
            n_limits += 1
            sw = content_words(s)
            if not sw:
                continue
            if len(sw & row_words) >= a.min_overlap:
                continue
            why = reviewed_reason(rid, s)
            (reviewed if why else flagged).append((rid, s, sorted(sw)[:8], why))

    print(f"limitation sentences found in verdicts: {n_limits}")

    if reviewed:
        print(f"\n{len(reviewed)} flagged and REVIEWED -- exemption keyed to the sentence text, so "
              f"an edit re-flags it:")
        for rid, s, _sw, why in reviewed:
            print(f"  {rid}: {s[:104]}")
            print(f"       {why}")
    stale = [k for k in REVIEWED
             if not any(k[0] in {f"r{rid}", f"r{rid:02d}"} and k[1].lower() in s.lower()
                        for rid, s, _sw, _w in reviewed)]
    if stale:
        print(f"\n  {len(stale)} exemption(s) match nothing any more -- the verdict changed and the")
        print("  judgement behind them no longer applies. Remove or re-justify:")
        for r, frag in stale:
            print(f"    {r}: \"{frag}\"")

    if flagged:
        print(f"\n{len(flagged)} carry NO lexical echo in their README row and are NOT reviewed:\n")
        for rid, s, sw, _ in flagged:
            print(f"  {rid}: {s[:150]}")
            print(f"       distinctive words: {', '.join(sw)}\n")
    else:
        print("\nEvery unreviewed limitation sentence has some echo in its round's README row.")

    print("  An echo is not preservation. A row that says \"largely established\" echoes")
    print("  \"not established\" and passes this check while inverting the claim -- the")
    print("  weakened paraphrase is the likelier failure and this instrument cannot see it.")

    floor = _floor(len(both), "the set of rounds with both a README row and a verdict")
    if floor:
        return floor
    return 1 if (flagged or stale) else 0


if __name__ == "__main__":
    sys.exit(main())

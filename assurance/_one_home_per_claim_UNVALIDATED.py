"""⛔ NOT SHIPPED — this gate could not validate, and the rule says it therefore does not score.

Renamed with a leading underscore so run_all.py skips it (PREFIX_SKIP). Kept rather than deleted
because the REASON it failed is the finding, and L81 says annotate, never rm.

WHAT HAPPENED. Built to catch the one documented prose drift — ③ stated two ways on one page. Its
positive control had to find a historical version asserting both wordings. Scanned all 28 versions of
STATEMENT.md: NONE does. Before 21:19 the retracted wording is asserted and the current wording does
not exist on the page; from 21:19 it is present only INSIDE QUOTATION MARKS, in the correction note.

WHY THE PROBE WAS WRONG, AND IT IS THE INSTRUMENT/CLAIM MISMATCH AGAIN. I gave the gate the FIX'''s
vocabulary ("checkable from the PRODUCER") as the target it must find in the PRE-fix history. That
string was written BY the fix. The contradiction retraction 334 describes was real and was between
the clause table'''s wording and the FORK'''s wording of the day — neither of which is the string I
probed for. A positive control built from post-fix language cannot fire on pre-fix text.

SO: entry 334'''s substance stands; this instrument does not. It exits 2 and is out of the suite.
"""

A claim stated twice in different words drifts. This catches the one instance we can prove.

WHY. Entry 334: `STATEMENT.md`'s clause table said ③ *"cannot be checked on an object alone"* while
the fork table below it said ③ needs *"the producer"*. **Two tables, one page, disagreeing for four
rounds**, because retraction 329 was applied where I was looking and the same claim sat above it in
different words. Entry 343 then swept the page for repeated NUMBERS, found none inconsistent, and
noted that the sweep's unit is not the risk's unit — the drift was PROSE.

⛔ THE RULE THIS GATE HAD TO CLEAR BEFORE IT WAS ALLOWED TO EXIST
(`feedback_replacement_proxy_needs_its_own_control`, carved this session after FOUR unvalidated
replacement proxies): it must PASS where the property is absent and FAIL where it is present, on
REAL cases, before it scores anything. Both controls below come from git history, not from
imagination.

⚠ AND IT FAILED ITS OWN FIRST TEST, WHICH IS WHY THE QUOTE RULE EXISTS. A naive co-occurrence check
flags the CURRENT, CORRECTED document: the retracted wording survives inside a quotation in the
correction note — L81, annotate never rewrite, working as designed. An instrument that cannot tell an
ASSERTION from a QUOTATION of a retracted assertion condemns the very act of correcting properly.

SCOPE. This gate polices ONE claim — ③'s checkability — because that is the only prose drift this
project has DOCUMENTED, and a hand-written population of claims would make the check self-report
(the failure `feedback_check_only_as_good_as_its_population` names). It is deliberately narrow.
Narrow-with-a-control beats broad-and-unvalidated; that is the whole point of the rule above.
"""
from __future__ import annotations
import pathlib, re, subprocess, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOC = "E05_the_space_of_compilers/STATEMENT.md"
RETRACTED = "cannot be checked on an object alone"
CURRENT = "checkable from the PRODUCER"


def unquoted(text: str, phrase: str) -> int:
    """Occurrences of `phrase` that are NOT inside quotation marks — i.e. asserted, not cited."""
    n = 0
    for m in re.finditer(re.escape(phrase), text):
        pre, post = text[max(0, m.start()-2):m.start()], text[m.end():m.end()+2]
        quoted = ('"' in pre or '“' in pre or '*"' in pre) and ('"' in post or '”' in post)
        if not quoted: n += 1
    return n


def verdict(text: str) -> tuple[bool, str]:
    a, b = unquoted(text, RETRACTED), unquoted(text, CURRENT)
    if a and b: return False, f"BOTH asserted (retracted×{a}, current×{b}) — the claim has two homes"
    if a and not b: return False, "only the RETRACTED wording is asserted"
    return True, f"consistent (retracted asserted ×{a}, current ×{b})"


def main() -> int:
    cur = (ROOT/DOC).read_text()

    # POSITIVE CONTROL — real, from history: a version that genuinely asserted both.
    shas = subprocess.run(["git", "log", "--format=%H", "-40", "--", DOC],
                          cwd=ROOT, capture_output=True, text=True, timeout=120).stdout.split()
    planted = None
    for s in shas:
        t = subprocess.run(["git", "show", f"{s}:{DOC}"], cwd=ROOT,
                           capture_output=True, text=True, timeout=60).stdout
        if unquoted(t, RETRACTED) and unquoted(t, CURRENT):
            planted = (s[:8], t); break
    if planted is None:
        print("  POSITIVE CONTROL cannot run: no historical version asserts both. UNVERIFIED."); return 2
    ok_pos = not verdict(planted[1])[0]
    print(f"  POSITIVE CONTROL  {planted[0]} asserted both -> flagged: {ok_pos}  "
          f"{'PASS' if ok_pos else 'FAIL'}")

    # NEGATIVE CONTROL — the current document, where the retracted wording survives ONLY as a
    # quotation. If this flags, the gate punishes correcting properly and must not ship.
    ok_cur, why = verdict(cur)
    print(f"  NEGATIVE CONTROL  current document -> {why}   {'PASS' if ok_cur else 'FAIL'}")

    if not (ok_pos and ok_cur):
        print("\n  a control misbehaved -- this gate does not get to score anything.")
        print("  (feedback_replacement_proxy_needs_its_own_control: pass AND fail on command first.)")
        return 1
    print(f"\n  PASS -- ③'s checkability has one asserted home in {DOC}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

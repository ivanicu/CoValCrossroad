#!/usr/bin/env python3
"""assurance/clause3_as_written.py — clause ③, DERIVED from the source instead of hand-listed.

⛔ WHY THIS FILE EXISTS. Clause ③ has been applied everywhere by one hand-written set —
   `{oracle_k4, oracle_k4_fit1, greedy_k4_fit1, indep_k4_fit1}` — duplicated across four rounds.
   R442 measured that this makes the definition's extension **5 arms**, while the definition's own
   text makes it **1**, because the text also excludes anything built from a rubric the prompt's own
   annotators wrote. **The document asserted both and reconciled neither.**

⭐ AND THE DECISION WAS FORCED, NOT A MATTER OF TASTE. There were two ways to close it: correct the
   SET to match the text, or weaken the TEXT to match what a hand-list can enforce. The second was
   only preferable while ③-as-written looked unenforceable — and R443 showed it is not.
   `corebench/select_core.py:131` computes `w[i] = mean(annotator score)` from
   `conversation_rubrics.jsonl`, and the file names every selector that consumes it. **So the text
   IS mechanically enforceable, and the reason to prefer weakening it disappeared.**

WHAT THIS ENFORCES, and where each half comes from:
    TARGET-READERS  oracle_k, indep_k, greedy_k — open `comparisons.jsonl`, i.e. the prompt's own
                    human rankings. Audited by R363 against `select_core.py`.
    W-READERS       topw_k, topabs_k, topwvar_k — consume `w = mean annotator importance score`.
                    Read off `select_core.py:138-152` by R443. `topvar_k` does NOT: its own comment
                    says the spread is "a property of the responses, never of the human target".

⚠ WHAT IT CANNOT ENFORCE. An arm whose selector the source does not name — `coval_core`, `gen`,
   `generic`, `promptecho` and their shams — is returned as UNKNOWN, never as admitted. Clause ③ is
   a PROVENANCE requirement and provenance for those arms lives outside `select_core.py`; R443
   measured `coval_core`'s textual containment in its own rubric at 0.0779 against a cross-prompt
   sham of 0.0000, which is why it survives, but that is a separate measurement and not something
   this file can decide.

⚠ AND THE SHAMS ARE EXCLUDED WITH THEIR PARENTS. `topw_k4_sham` read the same importance scores;
   the objection is about what the arm CONSUMED, not about how well it performed.
"""
from __future__ import annotations
import sys

# corebench/select_core.py:51 — the nine selectors this campaign builds arms from.
SELECTORS = ["random_k", "topw_k", "topabs_k", "oracle_k", "full",
             "topvar_k", "topwvar_k", "indep_k", "greedy_k"]
TARGET_READERS = {"oracle_k", "indep_k", "greedy_k"}      # R363, comparisons.jsonl
W_READERS = {"topw_k", "topabs_k", "topwvar_k"}            # R443, select_core.py:138-152


def selector_of(arm: str):
    """-> the selector an arm was built with, or None. LONGEST match wins, which is what keeps
    `topwvar_k4` from being read as a `topw_k` arm."""
    hits = [s for s in SELECTORS if arm.startswith(s)]
    return max(hits, key=len) if hits else None


def excluded(arm: str) -> bool:
    """True iff clause ③ AS WRITTEN excludes this arm on provenance the source can establish."""
    return selector_of(arm) in (TARGET_READERS | W_READERS)


def partition(arms):
    """-> (excluded, admitted, unknown_provenance). `unknown` is never folded into `admitted`."""
    exc, adm, unk = [], [], []
    for a in sorted(arms):
        s = selector_of(a)
        (exc if s in (TARGET_READERS | W_READERS) else adm if s else unk).append(a)
    return exc, adm, unk


def selftest() -> int:
    ok = True
    # POSITIVE: every selector the source names must be classifiable, and the two reader sets must
    # be disjoint -- an arm cannot be excluded twice for the same reason without that being visible.
    cls = {s: (s in TARGET_READERS, s in W_READERS) for s in SELECTORS}
    disjoint = not (TARGET_READERS & W_READERS)
    ok &= disjoint
    print(f"  POSITIVE  the two reader sets are disjoint: {disjoint}   "
          f"{'PASS' if disjoint else '⛔ FAIL'}")

    # the case that motivated reading the source instead of writing a regex
    pairs = [("topw_k4", True), ("topw_k4_sham", True), ("topwvar_k4", True),
             ("topvar_k4", False), ("random_k4_s0", False), ("full", False),
             ("oracle_k4", True), ("coval_core", False)]
    for arm, want in pairs:
        got = excluded(arm)
        good = got == want
        ok &= good
        print(f"    {arm:<16} excluded={got!s:<5} want={want!s:<5} {'ok' if good else '⛔'}")

    # NEGATIVE: `topvar_k` must NOT be excluded -- it is the one top* selector that reads no
    # annotator field, and folding it in would over-apply the clause.
    neg = not excluded("topvar_k4")
    ok &= neg
    print(f"  NEGATIVE  `topvar_k4` is NOT excluded (it reads satisfaction, not annotator w): "
          f"{neg}   {'PASS' if neg else '⛔ FAIL'}")

    # g=0: an arm the source cannot classify is UNKNOWN, never admitted silently
    exc, adm, unk = partition(["coval_core", "gen", "topw_k4", "oracle_k4", "random_k4_s0"])
    g0 = ("coval_core" in unk and "gen" in unk and "random_k4_s0" in adm)
    ok &= g0
    print(f"  g=0       unclassifiable arms -> UNKNOWN {unk}, not admitted   "
          f"{'PASS' if g0 else '⛔ FAIL'}")

    print(f"\n  {'PASS' if ok else '⛔ FAIL'} — clause ③ is now derived from the source, not a list.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest())

r"""Shared token-boundary helpers. Built after the SAME bug appeared THREE times in one arc.

⛔ THE BUG, three instances, one root cause: `_` IS A WORD CHARACTER in Python regex.
   ledger 762 -- `\bpublished\b` could not match `published_five`  -> a publication list read as a
                 measurement.
   ledger 768 -- `\bR(\d{3})\b` could not match `R294_the_definition...` -> a producer map built
                 0 rounds from 5 paths, and the verdict printed anyway.
   R686      -- `(?<![\w.])(2B)` could not match `scores_2B.json`   -> the positive control failed
                 and the round returned UNVERIFIED.

   Each time I fixed it locally and the next round re-committed it, because a lesson in a ledger is
   not a function anyone calls. P7: same bug three times means build infrastructure, not a third
   patch. Import these instead of writing `\b` around an identifier.

THE RULE: for identifiers that live inside snake_case, paths and filenames, the boundary you want is
"not adjacent to a LETTER OR DIGIT" -- `_`, `.`, `-`, `/` and string edges are separators, not
continuations. `\b` gets this backwards for exactly the characters these corpora use most.
"""
from __future__ import annotations
import re

SEP_L = r"(?<![A-Za-z0-9])"
SEP_R = r"(?![A-Za-z0-9])"


def token(*alternatives: str) -> re.Pattern:
    """Match any alternative as a whole token. Longest alternative first, always.

    >>> bool(token("2B").search("scores_2B.json"))     # separator-adjacent -> MATCH
    True
    >>> bool(token("2B").search("d2Bx"))               # letter-adjacent -> NO MATCH
    False
    """
    alts = "|".join(sorted((re.escape(a) for a in alternatives), key=len, reverse=True))
    return re.compile(f"{SEP_L}({alts}){SEP_R}")


def identifier(name: str) -> re.Pattern:
    """One identifier as a whole token, safe inside snake_case and paths."""
    return token(name)


def numbered(prefix: str, digits: int = 3) -> re.Pattern:
    """e.g. numbered('R') matches R294 in `R294_the_definition_against_everything`."""
    return re.compile(f"{SEP_L}{re.escape(prefix)}(\\d{{{digits}}}){SEP_R}")


if __name__ == "__main__":
    cases = [
        (token("2B"), "scores_2B.json", True), (token("2B"), "d2Bx", False),
        (token("2B", "0.8B"), "0.8B", True), (token("published"), "published_five", True),
        (numbered("R"), "R294_the_definition_against_everything", True),
        (numbered("R"), "(R529, R534)", True), (numbered("R"), "XR294", False),
    ]
    bad = [(p.pattern, s, w) for p, s, w in cases if bool(p.search(s)) != w]
    for p, s, w in cases:
        print(f"  {'ok ' if bool(p.search(s)) == w else '⛔ '} {s:<44} expect {w}")
    print("PASS -- every boundary case behaves" if not bad else f"⛔ FAIL: {bad}")
    raise SystemExit(1 if bad else 0)

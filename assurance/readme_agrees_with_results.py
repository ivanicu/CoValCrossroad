"""Does every number in the README still appear in the results file it came from?

Why this exists
---------------
r36 and r37 were published from 2-seed smoke runs while their full runs were
still executing. The full runs finished, overwrote the results files, and nobody
compared them to what had already gone into the README. Two significance calls
were wrong for hours (entry 42). Before that, r19's span was quoted as 2.2x in
one paragraph and 2.47x in a table nine lines below, and r12's 0.102 was
transplanted into a sentence about r19's farthest donor.

Every one of those is the same defect: **a number in the prose that no longer
matches the artifact it was read from**, with nothing in the repository able to
notice.

What it checks
--------------
For each round with a results file, collect every float the round stored. Then
scan the README paragraph-by-paragraph; for each paragraph that cites a round by
its `rounds/rNN_...` link, extract the decimal numbers it contains and ask
whether each one is present among that round's stored values.

A number is matched if it agrees with a stored value at the precision it was
printed to. `0.6419` matches 0.641903...; `2.47` matches 2.4659; `45.7%` matches
0.4573. Percentages, signs and thousands separators are normalised.

What it deliberately does NOT do
---------------------------------
It cannot know which numbers are *supposed* to come from a round -- a paragraph
may legitimately contain a threshold, a count of prompts, a year, or a number
derived from two rounds. So an unmatched number is a QUESTION, not a verdict,
and the output says so. The value is that the question gets asked at all: before
this, nothing in the repository compared prose against artifacts, and the two
places it went wrong were both found by hand, late.

Exit code is 0 always. This is a report, not a gate: making it a gate would
create pressure to delete inconvenient prose rather than check it.

THE COVERAGE BUG (entry 69)
---------------------------
For its whole life this check split the README on blank lines and skipped any
block citing != 1 round. A markdown TABLE contains no blank lines, so an entire
table is one block citing every round in it -- and every table was skipped whole.
Measured before the fix: **58 of 760 eligible numbers tested, 8%**. The three
largest skipped blocks were the round-summary table (53 numbers, 21 rounds), the
r39 table (88, 19) and the layer table (22, 18) -- i.e. the densest, most
checkable, most load-bearing prose in the document, invisible because it was
well-organised.

Two changes:
  * markdown table ROWS are split into their own blocks, so a row citing one
    round gets the strong per-round test
  * a block still citing several rounds is no longer skipped. Its numbers are
    tested against the UNION of those rounds' pools and reported separately.

  PROPERTY     no README number contradicts the artifact it came from
  PROXY        per-round pool match (strong) or union-of-cited-rounds (weak)
  IMPLICATION  unmatched under the UNION => unbacked by any cited round,
               definitely.  matched under the UNION => SOME cited round holds
               that value, and NOT that the right one does.
  SAFE SIDE    the union arm is reported apart from the per-round arm and never
               folded into it, because a union match is a weaker fact.

HOW MUCH A "MATCH" IS WORTH (measured, not assumed)
---------------------------------------------------
For its whole life this check reported matches without ever calibrating them. A
match is only evidence if a value that CANNOT have come from the round would
usually MISS. Drawing random values and testing them against real round pools:

    decimals   chance-match rate (mean over 70 pools)   worst pool
        1                56.5%                            100.0%
        2                22.8%                             98.5%
        3                 8.4%                             56.5%
        4                 2.3%                             24.5%

So the verdict depends almost entirely on printed precision, and the README's
tokens are 25.6% at <=1 decimal and 63.8% at >=3. A match on a 4-decimal figure
is strong; a match on a 1-decimal figure is nearly free, and on the largest pool
it is free outright. The table is recomputed at run time and printed with the
results, so the PASS side can never again be read as if it were uniform.

WHY THE CONVERSE CHECK WAS NOT BUILT
------------------------------------
The mirror direction -- do the ROUNDS' stored findings reach the documents? --
was measured and declined. Testing artifact values for presence anywhere in
README+RETRACTIONS (354,586 chars) has a chance-match rate of 94.1% for
correlation-like values and 100.0% for small effects: a number that never
existed "appears" as often as one that did. Such a check reports almost
everything as surfaced, and it fails toward PASS. The real case that motivated
it -- r47's `proxy_validation_on_original`, measured and never read out for many
rounds -- was found by reading the artifact, not by any matcher.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SKIPPED: list[str] = []   # files a parse error skipped; printed if non-empty

# A provisional run is not a result. This check had NO name filter at all and
# relied on its non-recursive glob, which a06_dryrun.json -- written straight
# into results/ -- defeated for the life of the round (entry 75).
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip", re.I)
NUM = re.compile(r"[-+]?\d+(?:,\d{3})*(?:\.\d+)?%?")
ROUND_LINK = re.compile(r"rounds/(r\d+)_[a-z0-9_]+")
# A round named in plain text -- "r06's 0.6575 arm", "found in r02". Prose names
# rounds without linking them, and four numbers were flagged against the linked
# round's pool while the sentence itself said which OTHER round they came from.
# Such a block goes to the UNION arm, never the strong arm: naming widens the
# pool, and a wider pool is a weaker test (P6).
ROUND_MENTION = re.compile(r"\br(\d{2})\b(?!\d)")
# numbers that are never claims about a result
IGNORE_EXACT = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "100",
                "2026", "0.05", "95", "1.0", "0.5"}


def split_blocks(text: str) -> list[str]:
    """Paragraph blocks, but a markdown table row is its own block (entry 69).

    `re.split(r"\\n\\s*\\n", text)` alone makes every table a single block, because
    a table has no blank line in it. The block then cites every round in the
    table and was skipped for being ambiguous -- so the most claim-dense prose in
    the document was the least checked. Splitting rows restores the one-row,
    one-round case to the strong per-round test.

    ROWS FROM A TABLE INHERIT THE TABLE'S ATTRIBUTION (entry 82). Splitting rows
    solved one problem and made another: a table whose HEADER or caption cites a
    round lost that citation for every row, so 426 claim-like numbers across 145
    blocks became unattributable -- and entry 81's two invisible stale figures
    were exactly there. Each row now carries its table's round ids appended as
    bare MENTIONS, which routes it to the weaker union arm unless the row cites a
    round itself. Inherited attribution should be weaker than direct: the header
    says which round the table is about, not which round each cell came from.
    """
    out = []
    for para in re.split(r"\n\s*\n", text):
        lines = para.splitlines()
        if sum(1 for ln in lines if ln.lstrip().startswith("|")) >= 2:
            inherited = sorted(set(ROUND_LINK.findall(para)))
            suffix = ("  " + " ".join(inherited)) if inherited else ""
            for ln in lines:
                if not ln.lstrip().startswith("|"):
                    out.append(ln)
                elif ROUND_LINK.search(ln):
                    # The row cites a round itself. Inheriting the table's other
                    # links as well would widen it into the union arm and DEMOTE
                    # a test that was strong -- measured: the strong arm fell
                    # 166 -> 39 checked numbers before this guard. A row that
                    # names its own source keeps the stronger test.
                    out.append(ln)
                else:
                    out.append(ln + suffix)
        else:
            out.append(para)
    return out


def collect_floats(obj, out):
    if isinstance(obj, dict):
        for v in obj.values():
            collect_floats(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_floats(v, out)
    elif isinstance(obj, bool):
        pass
    elif isinstance(obj, (int, float)):
        out.add(float(obj))


def matches(tok: str, pool: set[float]) -> bool:
    raw = tok.replace(",", "")
    pct = raw.endswith("%")
    if pct:
        raw = raw[:-1]
    try:
        v = float(raw)
    except ValueError:
        return False
    cands = [v, -v]
    if pct:
        cands += [v / 100.0, -v / 100.0]
    dec = len(raw.split(".")[1]) if "." in raw else 0
    tol = 0.5 * (10 ** -dec) if dec else 0.5
    for c in cands:
        for p in pool:
            if abs(p - c) <= tol:
                return True
            if abs(abs(p) - abs(c)) <= tol:      # sign-insensitive fallback
                return True
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--readme", type=Path, default=_ROOT / "README.md")
    ap.add_argument("--show", type=int, default=6, help="max unmatched shown per round")
    a = ap.parse_args()

    pools: dict[str, set[float]] = {}
    for f in sorted(_ROOT.glob("rounds/*/results/*.json")):
        if PROVISIONAL.search(f.name):
            continue
        rid = f.parts[-3].split("_")[0]
        pools.setdefault(rid, set())
        try:
            collect_floats(json.loads(f.read_text()), pools[rid])
        except (OSError, json.JSONDecodeError):
            # NOT `except Exception` (entry 105). A bare except here swallowed a
            # NameError on all 238 files in a sibling check and printed a clean
            # zero. `pass` is worse than `continue`: it hides the file AND keeps
            # an empty pool entry, so the round looks present with no values.
            _SKIPPED.append(str(f))
    if _SKIPPED:
        print(f"  ⚠ {len(_SKIPPED)} results file(s) could not be parsed and were SKIPPED: "
              f"{', '.join(_SKIPPED[:3])}{' …' if len(_SKIPPED) > 3 else ''}")
    print(f"rounds with results: {len(pools)}   "
          f"stored values: {sum(len(v) for v in pools.values()):,}\n")

    text = a.readme.read_text()
    blocks = split_blocks(text)
    flagged, checked = {}, 0
    union_flagged, union_checked = [], 0
    eligible = 0
    for b in blocks:
        linked = set(ROUND_LINK.findall(b))
        # A round NAMED in prose is not an attribution. A paragraph about r12's
        # anomaly carries r41's measurements of it, so letting a bare mention
        # drive the strong arm produced 33 false flags. Mentions may only WIDEN
        # a block into the weak union arm; the strong arm requires a link and
        # nothing else named alongside it.
        named = {f"r{m}" for m in ROUND_MENTION.findall(b)} & set(pools)
        rids = linked | named
        toks = [t for t in NUM.findall(b)
                if t.strip("+-") not in IGNORE_EXACT
                and not re.fullmatch(r"[-+]?\d{1,2}", t)]
        eligible += len(toks)
        if not rids or not toks:
            continue
        if len(linked) == 1 and len(rids) == 1:
            rid = next(iter(rids))
            pool = pools.get(rid)
            if not pool:
                continue
            for tok in toks:
                checked += 1
                if not matches(tok, pool):
                    flagged.setdefault(rid, []).append(tok)
        else:
            # entry 69: no longer skipped. Weaker test, reported apart.
            pool = set()
            for r in rids:
                pool |= pools.get(r, set())
            if not pool:
                continue
            for tok in toks:
                union_checked += 1
                if not matches(tok, pool):
                    union_flagged.append((tok, sorted(rids)[:4]))

    print(f"{'round':7s} {'unmatched':>10}   sample")
    for rid in sorted(flagged, key=lambda r: int(r[1:])):
        vals = flagged[rid]
        print(f"{rid:7s} {len(vals):>10}   {', '.join(vals[:a.show])}"
              f"{' ...' if len(vals) > a.show else ''}")
    if not flagged:
        print("  (none)")

    print(f"\n  numbers checked against ONE round's pool: {checked:,}   "
          f"unmatched: {sum(len(v) for v in flagged.values())}")

    print(f"\nUNION ARM -- blocks citing several rounds (weaker: a match names no round)")
    print(f"  numbers checked against the union: {union_checked:,}   "
          f"unmatched: {len(union_flagged)}")
    # Entry 57 was a renderer that truncated claims and so deleted exactly the
    # clauses that qualify them. Truncating THIS list hid a planted value from
    # its own positive control, which is the same failure wearing a new hat: a
    # finding the check made and did not show. Print all of them.
    for tok, rids in union_flagged:
        print(f"    {tok:>10}   cited: {', '.join(rids)}")
    if not union_flagged:
        print("    (none unmatched)")

    # Calibration, computed here so it always travels with the verdict.
    import numpy as _np
    _rng = _np.random.default_rng(20260805)
    print(f"\nWHAT A MATCH IS WORTH -- chance-match rate of values that came from NO round:")
    _decs = [len(t.split(".")[1].rstrip("%")) if "." in t else 0
             for t in NUM.findall(text)
             if t.strip("+-") not in IGNORE_EXACT and not re.fullmatch(r"[-+]?\d{1,2}", t)]
    for _d in (1, 2, 3, 4):
        _r = [float(_np.mean([matches(f"{x:.{_d}f}", pool)
                              for x in _rng.uniform(-1, 1, 120)]))
              for pool in pools.values() if pool]
        _share = float(_np.mean([q == _d for q in _decs])) if _decs else 0.0
        print(f"    {_d} decimal(s): {_np.mean(_r):6.1%} mean, {_np.max(_r):6.1%} worst pool"
              f"   ({_share:.0%} of README tokens are at this precision)")
    print("    A match is evidence in proportion to precision. At 1 decimal it is nearly free.")

    cov = (checked + union_checked) / eligible if eligible else 0.0
    print(f"\n  COVERAGE: {checked + union_checked:,} of {eligible:,} eligible numbers "
          f"reached a pool ({cov:.0%}).")
    print(f"  The remainder sit in blocks citing NO round and cannot be attributed. That is a")
    print(f"  limit of the instrument, not a clean bill -- before entry 69 this figure was 8%,")
    print(f"  because every markdown table was one unsplittable block.")
    print("  An unmatched number is a QUESTION, not a verdict: a paragraph may legitimately")
    print("  carry a threshold, a count, or a figure derived from two rounds. What this")
    print("  catches is the case nothing else in the repository can -- prose that no longer")
    print("  matches the artifact it was read from, which has happened twice (entries 18, 42).")


if __name__ == "__main__":
    main()

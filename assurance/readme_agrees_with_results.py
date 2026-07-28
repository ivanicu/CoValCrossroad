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
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

NUM = re.compile(r"[-+]?\d+(?:,\d{3})*(?:\.\d+)?%?")
ROUND_LINK = re.compile(r"rounds/(r\d+)_[a-z0-9_]+")
# numbers that are never claims about a result
IGNORE_EXACT = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "100",
                "2026", "0.05", "95", "1.0", "0.5"}


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
        rid = f.parts[-3].split("_")[0]
        pools.setdefault(rid, set())
        try:
            collect_floats(json.loads(f.read_text()), pools[rid])
        except Exception:
            pass
    print(f"rounds with results: {len(pools)}   "
          f"stored values: {sum(len(v) for v in pools.values()):,}\n")

    text = a.readme.read_text()
    blocks = re.split(r"\n\s*\n", text)
    flagged, checked = {}, 0
    for b in blocks:
        rids = set(ROUND_LINK.findall(b))
        if len(rids) != 1:
            continue                       # ambiguous or unattributed: skip
        rid = rids.pop()
        pool = pools.get(rid)
        if not pool:
            continue
        for tok in NUM.findall(b):
            if tok.strip("+-") in IGNORE_EXACT:
                continue
            if re.fullmatch(r"[-+]?\d{1,2}", tok):     # bare small ints
                continue
            checked += 1
            if not matches(tok, pool):
                flagged.setdefault(rid, []).append(tok)

    print(f"{'round':7s} {'unmatched':>10}   sample")
    for rid in sorted(flagged, key=lambda r: int(r[1:])):
        vals = flagged[rid]
        print(f"{rid:7s} {len(vals):>10}   {', '.join(vals[:a.show])}"
              f"{' ...' if len(vals) > a.show else ''}")
    if not flagged:
        print("  (none)")

    print(f"\n  numbers checked: {checked:,}   unmatched: {sum(len(v) for v in flagged.values())}")
    print("  An unmatched number is a QUESTION, not a verdict: a paragraph may legitimately")
    print("  carry a threshold, a count, or a figure derived from two rounds. What this")
    print("  catches is the case nothing else in the repository can -- prose that no longer")
    print("  matches the artifact it was read from, which has happened twice (entries 18, 42).")


if __name__ == "__main__":
    main()

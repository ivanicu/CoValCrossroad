"""Does a round's verdict cite its own significant results, or a favourable subset?

Why this exists (entry 79)
--------------------------
r44 stores two significant contrasts about the same compiler stage:

    compatibility selection            -0.0181  [-0.0241, -0.0125]   the stage COSTS accuracy
    selection vs size-matched random   +0.0149  [+0.0082, +0.0221]   its choice is better than random

Its verdict cites +0.0149, +0.0733, +0.0662. It does not cite -0.0181 -- the
round's only negative contrast. The README repeated the verdict, and **every
check in this package passed**, including `readme_row_carries_the_verdict`,
because the row and the verdict agreed with each other. A check that compares
prose to a verdict cannot catch a verdict that already dropped the qualifier.

So this compares the verdict to the round's own NUMBERS, which is the layer
underneath everything else the suite validates.

WHAT THIS CHECK IS SOUND FOR
----------------------------
  PROPERTY   a verdict states its round's significant findings rather than the
             flattering ones
  PROXY      each significant contrast's point estimate appears somewhere in the
             verdict string, at any of the precisions it would be printed to
  IMPLICATION  absent  =>  the value is not stated NUMERICALLY. It may still be
               described in words, so this is a QUESTION, not a verdict.
               present =>  it was cited, and NOTHING about whether the
               surrounding sentence characterises it honestly.
  SAFE SIDE  flags numerical omission only, and reports the SIGN pattern of what
             was omitted -- because the interesting failure is not that something
             was left out but that what gets left out has a direction.

THE SIGN TEST IS THE POINT
--------------------------
Omitting a contrast is unremarkable; verdicts summarise. Omitting the ones whose
sign runs against the headline is not. Per round, the headline sign is taken from
the largest-magnitude CITED contrast, and the check reports how many omitted
contrasts oppose it. A binomial null asks whether opposite-sign omission is more
common than citation-independent-of-sign would give.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from math import comb
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_SKIPPED: list[str] = []   # files a parse error skipped; printed if non-empty
CENSUS = _ROOT / "rounds/r58_equivalence_census/results/r58_equivalence_census.json"
PROVISIONAL = re.compile(r"smoke|dry[_-]?run|draft|scratch|trial|pilot|prelim|wip", re.I)


def printed_forms(v: float) -> list[str]:
    """Every way this value plausibly appears in prose."""
    out = set()
    for dec in (2, 3, 4):
        out.add(f"{abs(v):.{dec}f}")
        out.add(f"{abs(v):.{dec}f}".lstrip("0"))
    for dec in (1, 2):
        out.add(f"{abs(v) * 100:.{dec}f}%")
        out.add(f"{abs(v) * 100:.0f}%")
    return [s for s in out if s not in ("0.00", ".00", "0%", "0.0%")]


def cited(v: float, text: str) -> bool:
    return any(f in text for f in printed_forms(v))


def binom_tail(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binom(n, p)."""
    if n == 0:
        return 1.0
    return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))


def _floor(n: int, what: str) -> int:
    if n == 0:
        print(f"\nOBSERVED NOTHING: {what} is empty. This is exit 2, not success -- "
              f"a check with no population has not passed, it has not run.")
        return 2
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--census", type=Path, default=CENSUS)
    a = ap.parse_args()

    if not a.census.exists():
        print(f"  ! census missing: {a.census.relative_to(_ROOT)} -- run r59's predecessor r58 first")
        return 1
    census = json.loads(a.census.read_text())["contrasts"]

    verdicts: dict[str, str] = {}
    for f in sorted(_ROOT.glob("rounds/*/results/*.json")):
        if PROVISIONAL.search(f.name):
            continue
        rid = f.parts[-3].split("_")[0]
        if rid in verdicts:
            continue
        try:
            doc = json.loads(f.read_text())
        except (OSError, json.JSONDecodeError):
            # NOT `except Exception` (entry 105): a bare except here swallowed a
            # NameError on every one of 238 files and printed a clean zero.
            # Catch what a bad FILE raises; let a broken FUNCTION crash.
            _SKIPPED.append(str(f))
            continue
        v = doc.get("verdict") or doc.get("conclusion")
        if isinstance(v, str) and v.strip():
            verdicts[rid] = v.split(" || ")[0]

    by_round: dict[str, list] = {}
    for c in census:
        if c["round"] in verdicts and c.get("significant") and c.get("delta_hat") is not None:
            by_round.setdefault(c["round"], []).append(c)

    rows, tot_opp, tot_om = [], 0, 0
    for rid in sorted(by_round, key=lambda r: int(r[1:])):
        cs = by_round[rid]
        text = verdicts[rid]
        yes = [c for c in cs if cited(c["delta_hat"], text)]
        no = [c for c in cs if not cited(c["delta_hat"], text)]
        if not yes:
            head = 0
        else:
            head = 1 if max(yes, key=lambda c: abs(c["delta_hat"]))["delta_hat"] >= 0 else -1
        opp = [c for c in no if head and (1 if c["delta_hat"] >= 0 else -1) != head]
        rows.append((rid, len(cs), len(yes), len(no), head, opp))
        tot_opp += len(opp)
        tot_om += len(no)

    if _SKIPPED:
        print(f"  ⚠ {len(_SKIPPED)} results file(s) could not be parsed and were SKIPPED")
    print(f"rounds with a verdict AND significant contrasts: {len(rows)}")
    print(f"{'round':7s} {'sig':>4} {'cited':>6} {'omitted':>8}   omitted-and-opposite-signed")
    for rid, n, y, o, head, opp in rows:
        mark = "  <-" if opp else ""
        print(f"{rid:7s} {n:>4} {y:>6} {o:>8}   {len(opp)}{mark}")
        for c in opp:
            print(f"          {c['delta_hat']:+.4f}  {c['path'][:62]}")

    floor = _floor(len(rows), "rounds carrying both a verdict and a significant contrast")
    if floor:
        return floor

    # ---- the population defect this check had on its first run ----------
    #
    # A round that cites NONE of its contrasts has no headline sign, so `opp` is
    # empty for it BY CONSTRUCTION -- not because its omissions are balanced.
    # Counting those omissions in the denominator of the sign test made the null
    # look far stronger than the data supports. They are separated out and
    # reported first, because "the verdict cites no number at all" is a worse
    # state than "the verdict omits an unfavourable one".
    silent = [(rid, n, o) for rid, n, _y, o, head, _opp in rows if head == 0]
    classifiable = tot_om - sum(o for _r, _n, o in silent)

    if silent:
        print(f"\n{len(silent)} round(s) cite NONE of their own significant contrasts:")
        for rid, n, o in silent:
            print(f"  {rid}: {n} significant contrast(s), 0 cited")
        print("  A verdict that states no number cannot be compared to its round, and every")
        print("  prose check in this package will happily agree with it. Their "
              f"{sum(o for _r, _n, o in silent)} omissions are")
        print("  EXCLUDED from the sign test below -- they are unclassifiable, not balanced.")

    cited_opp = cited_tot = 0
    for rid, _n, _y, _o, head, _opp in rows:
        for c in by_round[rid]:
            if head and cited(c["delta_hat"], verdicts[rid]):
                cited_tot += 1
                if (1 if c["delta_hat"] >= 0 else -1) != head:
                    cited_opp += 1
    p0 = cited_opp / cited_tot if cited_tot else 0.5
    p = binom_tail(tot_opp, classifiable, p0) if classifiable else 1.0

    print(f"\nomissions in rounds that DO cite something: {classifiable}"
          f"   of which opposite-signed: {tot_opp}")
    print(f"  among CITED contrasts, opposite-signed: {cited_opp}/{cited_tot} = {p0:.3f}"
          f"  -> expected {classifiable * p0:.1f} of {classifiable}")
    print(f"  P(>= {tot_opp} opposite | citation independent of sign) = {p:.4f}")
    print(f"  {'SIGN BIAS NOT ESTABLISHED' if p > 0.05 else 'SIGN BIAS: omission runs against the headline'}")
    print("\n  An omitted number may still be described in words -- these are QUESTIONS.")
    print("  What the check asks is whether omission has a DIRECTION, and separately")
    print("  whether a verdict is connected to its round's numbers at all.")
    return 1 if (tot_opp or silent) else 0


if __name__ == "__main__":
    sys.exit(main())

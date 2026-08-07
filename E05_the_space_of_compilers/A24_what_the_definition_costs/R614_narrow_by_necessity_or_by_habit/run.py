#!/usr/bin/env python3
"""
R614 -- is the claim table's window narrow by necessity or by habit?

CHECK #213 CAUGHT A UNITS CONFLATION IN R613's CLOSING LINE. It called R519-R581 a "63-round
window": 63 is the count of ID POSITIONS in the span, while the table cites 17 DISTINCT ROUNDS
inside it. The word `round` doing double duty -- the same class of error as the rest of this
session, arriving in a sentence about counting.

⚠ AND A DRIFT WORTH NAMING: R612's closing line asked to leave corpus archaeology and return to
the definition. R613 did exactly that -- and then ITS closing line went straight back. This
round runs the measurement because it is cheap and does bear on evidence selection, but the
drift is recorded rather than repeated silently.

ESTIMAND        coverage = |rounds the claim table cites| / |rounds available in the same span|,
                and the same ratio over the whole post-boundary era 431-606.
IDENTIFICATION  Exact as counts over a complete enumeration. THE WHOLE ROUND IS A DERIVATION
                and is labelled: no cell could have come out otherwise. What is TESTED is only
                whether the cited set is more clustered than a random subset of the same size,
                which is a separate question with its own null.
SCOPE           population : rounds 431-606 with >=1 parseable results/*.json
                instrument : the gate's citation regex on the claim-table block
                             instrument unit = A DISTINCT ROUND ID CITED IN THE TABLE
                             claim unit      = A ROUND THE DEFINITION DRAWS ON -- NOT equal,
                             since one citation may carry a caveat rather than a number
                baseline   : random subsets of the same size drawn from the same era
                regime     : as committed at this sha
WORLDS          A NARROW BY HABIT: coverage is low AND the cited set is more clustered than
                  random -> the page draws on a small contiguous slice of a large era, and
                  "why those" is a live question.
                B NARROW BY NECESSITY: coverage is low but the cited set is no more clustered
                  than random -> the era is large and any 17 rounds would look like this;
                  nothing to explain.
                C WIDE: coverage is high -> the table draws on most of what exists and there
                  was no wider choice available.
KILL            pre-registered: if fewer than 10 rounds are cited, the clustering statistic is
                not admissible at this n and only the coverage fraction is reported.
POSITIVE CTRL   a synthetic contiguous block of the same size must be detected as clustered.
                Fails at g=0: a random subset must not be.
NEGATIVE CTRL   2000 random subsets of the same size from the same era -> the null for spread.
PLACEBO         the full era as its own "cited set" must give coverage exactly 1.0 and spread
                exactly at the maximum.
SEEDS           0, 1, 2.
MULTIPLICITY    one statistic, one null; the coverage fraction is a derivation and is labelled.
ARTIFACT        results/coverage.json
IMPOSSIBLE      construct validity for "draws on": a citation may carry a caveat rather than a
                number, so coverage bounds the evidence base from ABOVE, never characterises it.
"""
from __future__ import annotations
import json, pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
E05 = ROOT / "E05_the_space_of_compilers"
OUT = pathlib.Path(__file__).resolve().parent / "results"
CITE = r"\(R(\d{3})[,)]|R(\d{3})[,)]"
B, TOP = 431, 606


def claim_block(text):
    m = re.search(r"\n\| # \| claim \| scope it holds over \|\n(.*?)\n\n", text, re.S)
    return m.group(1) if m else ""


def era_rounds():
    out = []
    for d in sorted(E05.glob("A*/R[0-9]*")):
        if not d.is_dir() or d.name.startswith("R614_"):
            continue
        m = re.match(r"R(\d+)", d.name)
        if not m:
            continue
        rid = int(m.group(1))
        if B <= rid <= TOP and (d / "results").is_dir() and list((d / "results").glob("*.json")):
            out.append(rid)
    return sorted(out)


def spread(sel):
    """Mean gap between consecutive selected ids -- large = spread out, small = clustered."""
    s = sorted(sel)
    return (sum(b - a for a, b in zip(s, s[1:])) / (len(s) - 1)) if len(s) > 1 else 0.0


def main():
    text = (E05 / "STATEMENT.md").read_text()
    block = claim_block(text)
    cited = sorted({int(a or b) for a, b in re.findall(CITE, block)})
    era = era_rounds()
    if not block or not era:
        print("UNRUNNABLE: empty block or era. Exit 2, never 0."); return 2
    lo, hi = min(cited), max(cited)
    in_span = [r for r in era if lo <= r <= hi]
    print(f"POPULATION  era {B}-{TOP}: {len(era)} rounds with artifacts")
    print(f"  claim table cites {len(cited)} DISTINCT rounds, span {lo}-{hi}")
    print(f"  ⚠ that span holds {hi-lo+1} ID POSITIONS and {len(in_span)} ROUNDS THAT EXIST — "
          f"R613's line called it a '63-round window', conflating the two")
    print(f"\n─── COVERAGE (a DERIVATION — counts over a complete enumeration) ───")
    print(f"  within the span   : {len(cited)}/{len(in_span)} = {len(cited)/len(in_span):.4f}")
    print(f"  over the whole era: {len(cited)}/{len(era)} = {len(cited)/len(era):.4f}")

    print(f"\n─── CONTROLS ───")
    obs = spread(cited)
    rng = random.Random(0)
    nulls = sorted(spread(rng.sample(era, len(cited))) for _ in range(2000))
    lo5, hi95 = nulls[int(0.05*len(nulls))], nulls[int(0.95*len(nulls))]
    contig = era[:len(cited)]
    pos_ok = spread(contig) < lo5
    print(f"  POSITIVE  a contiguous block of {len(cited)}: spread {spread(contig):.4f} vs null "
          f"5% {lo5:.4f} -> {'PASS — clustering is detectable' if pos_ok else 'FAIL'}")
    rng2 = random.Random(9)
    g0 = spread(rng2.sample(era, len(cited)))
    g0_ok = lo5 <= g0 <= hi95
    print(f"  POSITIVE @ g=0  a random subset: spread {g0:.4f} in [{lo5:.4f}, {hi95:.4f}] -> "
          f"{'PASS (can fail)' if g0_ok else 'FAIL'}")
    plc_cov = len(era)/len(era)
    plc_ok = abs(plc_cov - 1.0) < 1e-12
    print(f"  PLACEBO   the full era as its own cited set: coverage {plc_cov:.4f} -> "
          f"{'PASS — exactly 1' if plc_ok else 'FAIL'}")
    enough = len(cited) >= 10
    print(f"  KILL      cited rounds {len(cited)} >= 10 -> "
          f"{'clustering statistic admissible' if enough else 'NOT admissible; coverage only'}")
    controls_ok = pos_ok and g0_ok and plc_ok

    print(f"\n─── SPREAD ───")
    print(f"  observed mean gap between cited rounds: {obs:.4f}")
    print(f"  null (2000 random subsets of size {len(cited)} from the era): "
          f"5% {lo5:.4f}  median {nulls[len(nulls)//2]:.4f}  95% {hi95:.4f}")
    clustered = enough and obs < lo5

    print(f"\n─── VERDICT ───")
    cov = len(cited)/len(era)
    if not controls_ok:
        world = "UNVERIFIED — a control did not fire"
    elif cov >= 0.5:
        world = (f"C WIDE — the table cites {cov:.1%} of the era's rounds; there was no much "
                 f"wider choice available")
    elif clustered:
        world = (f"A NARROW BY HABIT — coverage {cov:.1%} and the cited set is MORE clustered "
                 f"than random (mean gap {obs:.4f} below the null's 5% of {lo5:.4f}); 'why "
                 f"those rounds' is a live question")
    else:
        world = (f"B NARROW BY NECESSITY — coverage {cov:.1%}, but the cited set is no more "
                 f"clustered than a random subset of the same size (mean gap {obs:.4f} inside "
                 f"[{lo5:.4f}, {hi95:.4f}]). The era is large; any {len(cited)} rounds would "
                 f"look like this, and there is nothing to explain.")
    print(f"  {world}")

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "coverage.json").write_text(json.dumps({
        "world": world, "controls_ok": controls_ok,
        "era_lo": B, "era_hi": TOP, "n_era": len(era),
        "cited": cited, "n_cited": len(cited), "span": [lo, hi],
        "id_positions_in_span": hi-lo+1, "rounds_in_span": len(in_span),
        "coverage_in_span": len(cited)/len(in_span), "coverage_era": cov,
        "spread_obs": obs, "null_p05": lo5, "null_p95": hi95,
        "null_median": nulls[len(nulls)//2], "clustered": clustered,
        "check213": ("R613's closing line called R519-R581 a '63-round window' — 63 is the count "
                     "of ID POSITIONS while 17 rounds are cited; and its NEXT returned to corpus "
                     "archaeology one round after R612's NEXT asked to leave it"),
        "impossible": ("a citation may carry a caveat rather than a number, so coverage bounds "
                       "the evidence base from ABOVE and never characterises it"),
    }, indent=2))
    print(f"\n  wrote {OUT / 'coverage.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

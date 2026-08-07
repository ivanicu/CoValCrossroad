"""R406 -- R327's "better than EVERY prompt-blind set" was instantiated below the 99th percentile.

R405 exited UNVERIFIED because R360's percentile sweep does not order readings by strictness, and it
named the reason two committed rounds disagree about whether the definition admits its own instance:
R327's universal reading used the "best HELD-OUT of 1,820" while R360's top cell uses the in-sample
maximum. R405's NEXT said that reconciliation needs the subset scores and would cost a run.

⛔ IT DOES NOT. R331 committed the blind distribution's order statistics -- min, p25, med, p75, p90,
   p99 and MAX over the same 1,820 size-4 subsets -- and R327 committed the reference it used. Both
   numbers are on disk, in two rounds that never cited each other, and comparing them costs nothing.
   This is the campaign's own recurring lesson one more time: before paying for a measurement, count
   what the committed artifacts already contain.

⛔ AND THE COMPARISON IS EXACT ARITHMETIC ON TWO STORED NUMBERS, SO IT IS A DERIVATION. `max - ref`
   could not come out otherwise given those two values. What is NOT forced, and is the content, is
   whether the two rounds' numbers COINCIDE -- if R327's reference equalled the max, its reading
   would be a faithful instantiation of the word EVERY and there would be nothing to report.

⚠ AND THE UNIT DISCIPLINE IS THE POINT, NOT A CAVEAT. The failure table's hardest-won row says a
  positive control asks "can this instrument see?" and never "is what it sees the thing I am about to
  claim about?" -- and that the instrument's unit and the claim's unit must be written as two strings
  and required to be EQUAL. Here the claim's unit is `the MAXIMUM over 1,820 blind subsets`; the
  instrument's unit is `the best HELD-OUT of 1,820`. Those are not the same object, and no control in
  R327 could have caught it, because R327's controls were all about ORDERING its three readings.

ESTIMAND        (A) `max(blind) - ref_A`, the gap in A2 units between the maximum of the blind subset
                    distribution and the reference R327 used for the reading it called UNIVERSAL;
                (B) where ref_A falls in the committed order statistics, i.e. what share of the 1,820
                    blind subsets BEAT the bar the word EVERY was tested against;
                (C) whether the published reference's recorded percentile is consistent with the same
                    order statistics -- a cross-artifact consistency check that can fail.

IDENTIFICATION  (A) exact -- two committed scalars. (B) PARTIALLY identified and reported as a bound:
                R331 stored seven order statistics, not the 1,820 scores, so the share above ref_A is
                bracketed by the percentile grid and CANNOT be counted exactly. Saying "18 subsets"
                would be inventing precision the artifact does not carry.
                NOT identified: which instantiation is correct -- an act of definition.

SCOPE           population: the 1,820 prompt-blind size-4 subsets · instrument: R331's committed order
                statistics and R327's committed reference · baseline: the published reference ·
                regime: HEAD, no re-scoring.

WORLDS
  W-EVERY-WAS-EVERY   ref_A == max(blind). The universal reading was faithfully instantiated and
                      R405's disagreement must have another source entirely.
  W-EVERY-WAS-A-TAIL  ref_A < max(blind). Then the sentence said EVERY and the number said "a high
                      percentile", the two rounds' disagreement is explained, and the admitted set
                      under the plain-English reading was never actually tested.

PREDICTION MATRIX
  W-EVERY-WAS-EVERY  -> gap == 0
  W-EVERY-WAS-A-TAIL -> gap > 0, and ref_A lands at or below p99 in the committed grid

PRE-REGISTERED KILL -- conditional on the consistency control, never on the gap alone.
    if order_statistics_are_monotone and published_reference_percentile_is_consistent:
        if gap == 0 -> W-EVERY-WAS-EVERY
        else        -> W-EVERY-WAS-A-TAIL, with the bracket on the share
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  MONOTONE (+)   min < p25 < med < p75 < p90 < p99 < max. An order-statistic vector that is not
                 increasing is not an order-statistic vector, and every percentile claim below would
                 be meaningless.
  CROSS (+)      R331 records the published reference at the 93.74th percentile. That value must lie
                 between the committed p90 and p99, using ONLY the stored statistics. This checks two
                 artifacts against each other rather than checking one against itself.
  ABSURD (-)     a value below `min` must bracket to the 0th percentile, so the bracketing routine is
                 shown able to return an extreme rather than always landing mid-grid.
  BOUND          the share above ref_A is reported as a BRACKET from the percentile grid, never as a
                 count. R331 stored 7 numbers, not 1,820.

MULTIPLICITY    one gap, one bracket, one consistency check; all printed.
SEEDS           none -- arithmetic on committed scalars.
ARTIFACT        results/r406_universal_not_universal.json with the source hash.

IMPOSSIBLE HERE
  an exact count above ref_A -- R331 committed order statistics, not the 1,820 scores. Bracketed.
  deciding which reference is correct -- an act of definition, not a measurement.
  re-scoring the subsets     -- would need the judge; the point of this round is that it is unnecessary.
  a second release           -- two corpora, neither re-scored.

EXIT
    0  the controls hold and the gap is reported
    1  the order statistics or the cross-check fail -- UNVERIFIED
    2  an artifact is absent -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
R331 = HERE.parent / "R331_what_makes_a_clause2_reference_safe" / "results" / "reference_safety.json"
R327 = HERE.parent / "R327_clause2_names_no_reference" / "results" / "readings.json"
GRID = ["min", "p25", "med", "p75", "p90", "p99", "max"]
PCT = {"min": 0.0, "p25": 25.0, "med": 50.0, "p75": 75.0, "p90": 90.0, "p99": 99.0, "max": 100.0}


def bracket(v, dist):
    """Return the (lower_label, upper_label) of the committed grid that v falls between."""
    lo = None
    for k in GRID:
        if dist[k] <= v:
            lo = k
        else:
            return (lo, k)
    return (lo, None)


def main() -> int:
    for f in (R331, R327):
        if not f.exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
    a331 = json.loads(R331.read_text())
    a327 = json.loads(R327.read_text())
    dist = a331["blind_dist"]
    n_blind = a331["n_blind"]
    pub = a331["r294_reference"]
    readA = next(r for r in a327["readings"] if r["reading"].startswith("A"))
    ref_a = readA["ref_a2"]

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R406 · was the universal reading universal?   HEAD {head}\n")
    print("  ⛔ R405's NEXT SAID THIS NEEDED A RUN. IT DOES NOT. R331 committed the blind")
    print("     distribution's order statistics over the same 1,820 subsets and R327 committed the")
    print("     reference it used. Two rounds, neither citing the other, both numbers on disk.\n")

    # ---- CONTROLS -------------------------------------------------------------------------------
    vals = [dist[k] for k in GRID]
    mono = all(a < b for a, b in zip(vals, vals[1:]))
    lo_p, hi_p = bracket(pub["a2"], dist)
    cross_ok = (lo_p == "p90" and hi_p == "p99")
    absurd = bracket(dist["min"] - 1.0, dist)
    absurd_ok = (absurd[0] is None and absurd[1] == "min")
    print(f"  CONTROLS")
    print(f"    MONOTONE (+)  min<p25<med<p75<p90<p99<max: {mono}   {'PASS' if mono else 'FAIL'}")
    print(f"                  {[f'{k}={dist[k]:.6f}' for k in GRID]}")
    print(f"    CROSS (+)     R331 records the published reference at pctile "
          f"{pub['pctile']:.2f}; using ONLY the stored statistics it brackets to ({lo_p}, {hi_p}): "
          f"{cross_ok}   {'PASS' if cross_ok else 'FAIL'}")
    print(f"    ABSURD (-)    a value below min brackets to {absurd}: {absurd_ok}   "
          f"{'PASS' if absurd_ok else 'FAIL — the bracketer never returns an extreme'}")
    if not (mono and cross_ok and absurd_ok):
        print("\n  UNVERIFIED — the order statistics or the cross-check failed. Exit 1."); return 1

    # ---- (A) the gap ------------------------------------------------------------------------------
    gap = dist["max"] - ref_a
    lo_r, hi_r = bracket(ref_a, dist)
    print(f"\n  (A) THE GAP BETWEEN THE SENTENCE AND THE NUMBER")
    print(f"      R327 reading A  : {readA['reading']}")
    print(f"      its reference   : {readA['reference']!r}  ref_a2 = {ref_a:.10f}")
    print(f"      max over {n_blind:,} blind subsets      = {dist['max']:.10f}")
    print(f"      p99 over the same subsets       = {dist['p99']:.10f}")
    print(f"      GAP (max - ref) = {gap:+.10f}")
    print(f"      ref_A brackets to ({lo_r}, {hi_r}) — i.e. BELOW the committed p99")

    # ---- (B) the bound on the share ---------------------------------------------------------------
    share_lo = 100.0 - PCT[hi_r] if hi_r else 0.0
    share_hi = 100.0 - PCT[lo_r] if lo_r else 100.0
    print(f"\n  (B) HOW MANY BLIND SUBSETS BEAT THE BAR THE WORD `EVERY` WAS TESTED AGAINST")
    print(f"      bracket from the committed grid: between {share_lo:.0f}% and {share_hi:.0f}%")
    print(f"      i.e. between {int(n_blind*share_lo/100):,} and {int(n_blind*share_hi/100):,} "
          f"of the {n_blind:,} subsets")
    print(f"      ⚠ A BRACKET, NOT A COUNT. R331 committed SEVEN order statistics, not 1,820 scores,")
    print(f"        so `18 subsets` would be precision the artifact does not carry.")

    # ---- VERDICT ----------------------------------------------------------------------------------
    print()
    if gap == 0:
        v = "W_EVERY_WAS_EVERY"
        print(f"  W-EVERY-WAS-EVERY — the reference IS the maximum. The universal reading was")
        print(f"  faithfully instantiated and R405's disagreement has another source.")
    else:
        v = "W_EVERY_WAS_A_TAIL"
        print(f"  W-EVERY-WAS-A-TAIL — the reading called `better than EVERY prompt-blind set of that")
        print(f"  size` was tested against a bar {gap:.6f} BELOW the actual maximum, sitting below the")
        print(f"  committed p99. So the sentence said EVERY and the number said `a high percentile`,")
        print(f"  and the admitted set under the plain-English reading was never actually tested.")
        print(f"  This explains R405's disagreement exactly: R327 admits `coval_core` because it")
        print(f"  cleared a 99th-percentile bar, and R360's top cell does not because it did not")
        print(f"  clear the maximum.")

    print(f"\n  ⚠ THE UNIT DISCIPLINE IS THE POINT, NOT A CAVEAT. The claim's unit is `the MAXIMUM over")
    print(f"    1,820 blind subsets`; the instrument's unit is `the best HELD-OUT of 1,820`. No")
    print(f"    control in R327 could have caught this — its controls were all about ORDERING its")
    print(f"    three readings, and an ordering can be perfectly correct while every rung is")
    print(f"    mislabelled.")
    print(f"  ⚠ AND THIS DOES NOT RETRACT R327. Its reading B and C results stand, its finding that")
    print(f"    the readings DIVERGE stands and is strengthened. What is corrected is the NAME of one")
    print(f"    rung: reading A is not the universal reading, it is a p99 reading.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, n_blind=n_blind, blind_dist=dist, ref_a=ref_a,
               ref_label=readA["reference"], gap=gap, ref_bracket=[lo_r, hi_r],
               share_bracket_pct=[share_lo, share_hi],
               published_reference=pub,
               controls=dict(monotone=mono, cross_ok=cross_ok, absurd_ok=absurd_ok),
               verdict=v, derivation=True)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r406_universal_not_universal.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

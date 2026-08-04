"""R411 -- R410's NEXT compares two numbers in different units. Standardised, is the replication powered?

R410 closed by proposing that the second corpus R398 found should test whether `coval_core`'s +0.009
over the maximum blind set is real, citing R401's finding that clause ② is powered there at n=26,789.

⛔ THAT SENTENCE COMPARES TWO NUMBERS ON DIFFERENT SCALES, AND IT IS MY OWN. The +0.009 is in CoVal's
   A2-AGREEMENT units -- the share of criterion-level verdicts matching a human's. R401's MDE of
   0.0094 is in `pick the chosen response` ACCURACY units on the second corpus, against a chance floor
   R402 measured at 0.4328. Setting `0.009 vs 0.0094` side by side and reading "marginal" would be
   comparing a length to a mass because both print as four decimals.

⭐ AND THE FIX IS NOT TO ABANDON THE COMPARISON BUT TO STANDARDISE IT. `d = e / sd` of the per-prompt
   difference is dimensionless, so it IS comparable across metrics -- and a design's resolution in the
   same units is `ZEFF / sqrt(n)`, which depends on nothing but n. Under the stated assumption that a
   standardised effect transports, the question becomes answerable from committed numbers alone.

⛔ ARITHMETIC TRAP, TWICE, AND BOTH ARE LABELLED. `d = e/sd` is a definition. `MDE_d = ZEFF/sqrt(n)`
   is algebra. Neither is evidence. What is NOT forced is the `sd`, which R408 measured, and the
   RATIO of the two -- and the ratio is the only thing this round reports as a finding.

⚠ AND THE TRANSPORT ASSUMPTION IS REAL AND IS NAMED, NOT BURIED. A standardised effect is comparable
  across metrics only if the two metrics measure the same construct with different scaling. CoVal's A2
  and the second corpus's `if_chosen` accuracy plausibly do not. So the output is a POWER STATEMENT
  CONDITIONAL ON THAT ASSUMPTION, and the round says what would falsify it.

ESTIMAND        (A) `coval_core`'s advantage over the maximum blind set in STANDARDISED units,
                    d = e / sd, from R408's committed e, se and n;
                (B) the second-corpus design's resolution in the SAME units, ZEFF / sqrt(n), at both
                    n R398/R402 established;
                (C) their ratio -- how many times the design's resolution the effect is;
                and (D) the NAIVE raw-unit comparison, printed beside them, because showing the error
                    is the point and describing it is not the same as showing it.

IDENTIFICATION  (A)-(D) exact given committed scalars. NOT identified: whether a standardised effect
                TRANSPORTS between these two metrics. That is the assumption, it is stated, and the
                verdict is explicitly conditional on it.

SCOPE           population: CoVal's 968 prompts (source) and the second corpus's 26,789 interactions
                (target) · instrument: committed artifacts only · baseline: the per-k maximum blind
                set on the source side · regime: no re-scoring anywhere.

WORLDS
  W-POWERED       standardised, the effect is comfortably above the target design's resolution. Then
                  the replication is worth its GPU and R410's NEXT survives -- for a reason R410 did
                  not give.
  W-MARGINAL      the effect sits within ~2x the resolution. Then the replication is a coin flip and
                  should be re-scoped before it is run.
  W-UNDERPOWERED  the effect is below the resolution. Then the replication cannot resolve what it
                  targets and must not be run as stated.

PREDICTION MATRIX
  W-POWERED      -> ratio >= 3
  W-MARGINAL     -> 1 <= ratio < 3
  W-UNDERPOWERED -> ratio < 1

PRE-REGISTERED KILL -- conditional on the gauge test, never on the ratio alone.
    if standardisation_is_scale_invariant and standardisation_is_NOT_noise_invariant:
        ratio = d_effect / (ZEFF / sqrt(n_target))
        >= 3 -> W-POWERED ; >= 1 -> W-MARGINAL ; else -> W-UNDERPOWERED
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  GAUGE (+/-)   the cheapest kill available, and exactly the right one here. Multiplying every
                measurement by a constant is a change of UNITS and must leave d IDENTICAL; adding
                noise is a change of the OBJECT and must SHRINK d. A standardisation invariant under
                both would be measuring nothing, and one invariant under neither would not be a
                standardisation. Both directions are executed on synthetic data.
  NAIVE         the raw-unit comparison R410's NEXT implied is COMPUTED and printed beside the
                standardised one. A described error is not a demonstrated one.
  SOURCE        e, se and n are read from R408's committed artifact, never retyped.
  ASSUMPTION    the transport assumption is printed in the verdict, not only in this docstring.

MULTIPLICITY    one ratio at two candidate n; both printed.
SEEDS           3 for the synthetic gauge control; the arithmetic itself is deterministic.
ARTIFACT        results/r411_commensurability.json with the source hash.

IMPOSSIBLE HERE
  validating the transport assumption -- needs both metrics measured on a SHARED population, which
                                         no object on this box provides. It is the assumption, named.
  a replication result                -- this round runs no test on the second corpus.
  a common scale for the two metrics  -- would need a linking study.

EXIT
    0  the gauge test holds and the ratio is reported
    1  the gauge test fails -- UNVERIFIED
    2  an artifact is absent -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import math
import pathlib
import subprocess
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
R408 = HERE.parent / "R408_the_literal_test_at_the_universal_reference" / "results" / \
    "r408_literal_test.json"
R402 = HERE.parent / "R402_does_the_harness_fire_before_the_judge" / "results" / \
    "r402_harness_validation.json"
R401 = HERE.parent / "R401_can_n99_resolve_anything" / "results" / "r401_power_at_99.json"
ZEFF = 1.959964 + 0.841621
SEEDS = (1, 2, 3)


def main() -> int:
    for f in (R408, R402, R401):
        if not f.exists():
            print(f"  UNRUNNABLE: {f} absent. Exit 2, never 0."); return 2
    a408 = json.loads(R408.read_text())
    a402 = json.loads(R402.read_text())
    a401 = json.loads(R401.read_text())
    row = a408["rows"]["coval_core"]
    e, se = row["e"], row["se"]
    n_src = a408["n_prompts"]
    n_tgt_i = a402["n"]                      # interactions with one if_chosen, after exclusions
    n_tgt_c = 8011                           # conversations (R398)

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R411 · are the two effects even commensurable?   HEAD {head}\n")
    print("  ⛔ R410's NEXT COMPARES TWO NUMBERS ON DIFFERENT SCALES, AND IT IS MY OWN. `+0.009` is")
    print("     in CoVal's A2-AGREEMENT units; R401's `0.0094` is in `pick the chosen response`")
    print("     ACCURACY units on the second corpus, against a chance floor of "
          f"{a402['floor']:.4f}. Setting")
    print("     them side by side reads `marginal` the way a length reads heavier than a mass when")
    print("     both print as four decimals.\n")

    # ---- GAUGE CONTROL: the cheapest kill, and exactly the right one --------------------------------
    print("  CONTROLS — the GAUGE TEST, executed on synthetic data in both directions")
    inv, shr = [], []
    for s in SEEDS:
        rng = np.random.default_rng(s)
        x = rng.normal(0.01, 0.12, 968)
        d0 = x.mean() / x.std(ddof=1)
        d_scaled = (3.0 * x).mean() / (3.0 * x).std(ddof=1)          # UNITS change
        y = x + rng.normal(0.0, 0.12, 968)                            # the OBJECT changes
        d_noised = y.mean() / y.std(ddof=1)
        inv.append(abs(d_scaled - d0))
        shr.append(d0 - d_noised)
    scale_ok = max(inv) < 1e-12
    noise_ok = min(shr) > 0
    print(f"    GAUGE (+)  multiplying every measurement by 3 is a change of UNITS and leaves d")
    print(f"               IDENTICAL: max|Δd| = {max(inv):.2e}   {'PASS' if scale_ok else 'FAIL'}")
    print(f"    GAUGE (-)  adding noise is a change of the OBJECT and must SHRINK d: min Δd = "
          f"{min(shr):+.4f}   {'PASS' if noise_ok else 'FAIL'}")
    print(f"               a standardisation invariant under BOTH would measure nothing; one")
    print(f"               invariant under NEITHER would not be a standardisation")
    if not (scale_ok and noise_ok):
        print("\n  UNVERIFIED — the standardisation is not a gauge. Exit 1."); return 1

    # ---- (D) the NAIVE comparison, computed rather than described ----------------------------------
    naive_mde = a401["within_corpus"]["interactions with one `if_chosen` (R399)"]["mde_at_pd30"]
    print(f"\n  (D) THE NAIVE COMPARISON R410's NEXT IMPLIED — computed, because a described error is")
    print(f"      not a demonstrated one")
    print(f"      effect (A2 units)                    {e:+.6f}")
    print(f"      R401's target MDE (accuracy units)   {naive_mde:+.6f}")
    print(f"      raw ratio                            {e/naive_mde:.2f}x   -> reads MARGINAL")
    print(f"      ⚠ AND IT IS MEANINGLESS: the numerator and denominator are not the same quantity.")

    # ---- (A)(B)(C) standardised --------------------------------------------------------------------
    sd = se * math.sqrt(n_src)
    d = e / sd
    print(f"\n  (A) THE EFFECT IN STANDARDISED UNITS — dimensionless, so comparable across metrics")
    print(f"      e {e:+.6f} · se {se:.6f} · n {n_src}  ->  sd = se·√n = {sd:.6f}")
    print(f"      d = e / sd = {d:.5f}")
    print(f"\n  (B) THE TARGET DESIGN'S RESOLUTION IN THE SAME UNITS — ZEFF/√n, a function of n alone")
    rows = {}
    for label, n in (("interactions with one `if_chosen`", n_tgt_i), ("conversations", n_tgt_c)):
        mde_d = ZEFF / math.sqrt(n)
        rows[label] = dict(n=n, mde_d=mde_d, ratio=d / mde_d)
        print(f"      {label:<36} n={n:>7,}   MDE_d = {mde_d:.5f}   ratio = {d/mde_d:.2f}x")
    ratio = min(r["ratio"] for r in rows.values())

    print()
    if ratio >= 3:
        v = "W_POWERED"
        print(f"  W-POWERED — standardised, the effect is {ratio:.1f}x the target design's resolution")
        print(f"  at the WORSE of the two n. The replication is worth its GPU, and R410's NEXT")
        print(f"  survives — for a reason R410 did not give, since its own raw comparison read")
        print(f"  {e/naive_mde:.2f}x and would have called the same experiment marginal.")
    elif ratio >= 1:
        v = "W_MARGINAL"
        print(f"  W-MARGINAL — {ratio:.1f}x resolution. The replication is close to a coin flip and")
        print(f"  should be re-scoped before it is run.")
    else:
        v = "W_UNDERPOWERED"
        print(f"  W-UNDERPOWERED — {ratio:.1f}x. The replication cannot resolve what it targets and")
        print(f"  must not be run as stated.")

    print(f"\n  ⚠ CONDITIONAL ON AN ASSUMPTION THAT IS NOT VALIDATED HERE AND MAY BE FALSE. A")
    print(f"    standardised effect is comparable across metrics only if the two measure the SAME")
    print(f"    CONSTRUCT with different scaling. CoVal's A2 agreement and the second corpus's")
    print(f"    `if_chosen` accuracy plausibly do not. Validating it needs both metrics on a SHARED")
    print(f"    population, which no object on this box provides — so this is a power statement")
    print(f"    CONDITIONAL on transport, not a promise that the replication will resolve.")
    print(f"  ⚠ AND BOTH d AND MDE_d ARE DERIVATIONS. `d = e/sd` is a definition and `ZEFF/√n` is")
    print(f"    algebra; only the `sd` behind them was measured. The ratio is what this round adds.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, e=e, se=se, n_source=n_src, sd=sd, d=d,
               naive_target_mde=naive_mde, naive_ratio=e / naive_mde,
               targets=rows, worst_ratio=ratio,
               controls=dict(scale_invariant=scale_ok, noise_shrinks=noise_ok,
                             max_scale_delta=max(inv), min_noise_delta=min(shr)),
               assumption="a standardised effect transports between A2 agreement and if_chosen accuracy",
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r411_commensurability.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

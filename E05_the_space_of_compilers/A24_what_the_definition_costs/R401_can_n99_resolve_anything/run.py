"""R401 -- at n<=99, can a transport test resolve any effect this campaign has ever measured?

R400 established that a depth-matched transport test can draw at most 99 pairable conversations, 77 of
them at depth 2. Its NEXT required the MDE be computed BEFORE the design, because a test that cannot
resolve the effect it targets is a way to spend GPU on an inequality I already have.

⛔ THE MDE FORMULA IS A DERIVATION AND IS LABELLED ONE. `MDE = ZEFF * sd / sqrt(n)` could not have
   come out otherwise; it is algebra, not evidence. What is NOT forced, and is the only thing this
   round contributes, is the COMPARISON: the derived resolution floor set beside the effect sizes this
   campaign has actually measured for clause ②. A derivation is worth more than a measurement when it
   decides whether to spend the measurement -- but only if it is called a derivation.

⛔ AND THE NOISE TERM IS NOT FREE EITHER, SO IT IS SWEPT RATHER THAN ASSUMED. For a paired binary
   outcome -- does arm A predict `if_chosen` correctly where arm B does not -- the per-conversation
   difference lives in {-1, 0, +1} and its variance is governed by the DISCORDANCE RATE p_d, the share
   of conversations where the two arms disagree. Under the null sd = sqrt(p_d). p_d is unmeasured
   here, so the whole admissible range is swept and the answer is reported as a CURVE. Picking one
   p_d and quoting one MDE would be the one-cell failure at power-analysis scale.

⚠ AND sd = sqrt(p_d) IS ITSELF AN APPROXIMATION WITH A KNOWN DIRECTION. It holds under a symmetric
  null; when the effect is non-zero the variance is slightly smaller, so this MDE is mildly
  CONSERVATIVE -- it overstates the required effect. That direction is the safe one for a
  go/no-go decision (it makes "underpowered" harder to conclude), and it is stated rather than
  discovered later.

ESTIMAND        (A) the MDE of a paired accuracy-difference test at n = 99, as a function of the
                    discordance rate p_d over its whole admissible range;
                (B) the ratio of that MDE to the LARGEST clause-② effect this campaign has measured,
                    and the value of p_d at which the two cross.

IDENTIFICATION  (A) exact given n and p_d -- it is algebra. (B) exact given the published effects,
                which are quoted from DEFINITION.md and VERIFIED PRESENT in it by this round, so they
                inherit that document's gate (`definition_matches_the_record.py`) rather than resting
                on my memory of them.

SCOPE           population: the 99 depth-matched pairs R400 found · instrument: the standard
                two-sided 80%-power MDE · baseline: this campaign's own measured transport effects ·
                regime: paired binary outcome on `if_chosen`.

WORLDS
  W-UNDERPOWERED  the MDE at n=99 exceeds the largest effect the campaign has measured across most of
                  the admissible p_d range. Then the transport test CANNOT resolve what it targets,
                  and running it buys an inequality already in hand. The honest output is R400's scope
                  statement and NO test.
  W-POWERED       the MDE sits below those effects across most of the range. Then the test is worth
                  the GPU and the design proceeds.
  W-BOUNDARY      the crossing sits inside the plausible range, so the answer depends on a quantity
                  nobody has measured. Then MEASURING p_d is the next round, and it is far cheaper
                  than the test itself.

PREDICTION MATRIX
  W-UNDERPOWERED -> MDE > largest measured effect for >= 80% of the swept p_d grid
  W-POWERED      -> MDE < largest measured effect for >= 80% of the grid
  W-BOUNDARY     -> between; the crossing p_d is the finding

PRE-REGISTERED KILL -- conditional on the controls, never on the curve alone.
    if mde_monotone_in_n and mde_resolves_at_huge_n and mde_fails_at_tiny_n and effects_located:
        share = fraction of the p_d grid where MDE(99, p_d) > max_measured_effect
        if share >= 0.80 -> W-UNDERPOWERED
        elif share <= 0.20 -> W-POWERED
        else -> W-BOUNDARY, crossing named
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

CONTROLS
  MDE (+)      at n = 1,000,000 the MDE must fall BELOW every measured effect. Without this the
               criterion could be one no design could ever pass -- the "control that cannot PASS"
               failure, which this campaign has built four times and caught four times.
  MDE (-)      at n = 4 the MDE must EXCEED every measured effect. Together with the above this
               establishes floor < threshold < ceiling rather than assuming it.
  MONOTONE     the MDE must strictly decrease in n across a sweep. A function returning a constant
               would pass a single-point check; monotonicity is what shows it responds to n at all.
  EFFECTS      every quoted effect is asserted PRESENT in DEFINITION.md before use. A number I recall
               is a number I may have invented; a number located in a gated document is not.
  GRID         the whole p_d range is reported, including the cells that would kill the verdict.

MULTIPLICITY    one derivation swept over a grid; every cell printed.
SEEDS           none -- this is algebra, not a draw.
ARTIFACT        results/r401_power_at_99.json with the source hash.

IMPOSSIBLE HERE
  measuring p_d          -- needs both arms actually run, which is the test being priced. Swept.
  the effect's true size on the SECOND corpus -- unknown; the campaign's own effects are used as the
                            reference, and transporting an effect SIZE is itself an assumption, named.
  a one-sided design's smaller MDE -- would need a pre-registered direction, which the definition's
                            clause ② does not commit to on a new corpus.
  a second release       -- two corpora, and R398 already corrected that line.

EXIT
    0  controls hold and the curve is reported
    1  a control misbehaved -- UNVERIFIED
    2  the reference effects cannot be located -- never a silent pass
"""
from __future__ import annotations
import hashlib
import json
import math
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[3]
SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
DEFN = ROOT / "E05_the_space_of_compilers" / "DEFINITION.md"
R400 = HERE.parent / "R400_is_conversation_depth_a_confound" / "results" / "r400_depth_confound.json"
ZEFF = 1.959964 + 0.841621          # two-sided 0.05, 80% power
# clause-2 / transport effects this campaign has MEASURED. Quoted from DEFINITION.md and asserted
# present there below, so they inherit that document's gate instead of resting on my memory.
EFFECTS = {"R368 exact": 0.0992, "R368 pair": 0.0612, "R370 exact": 0.0810, "R370 pair": 0.0161}
PD_GRID = [round(0.05 + 0.05 * i, 2) for i in range(12)]     # 0.05 .. 0.60


def mde(n: int, pd: float) -> float:
    """DERIVATION, not a measurement: ZEFF * sd / sqrt(n), with sd = sqrt(pd) for a paired
    binary difference under a symmetric null."""
    return ZEFF * math.sqrt(pd) / math.sqrt(n)


def main() -> int:
    if not DEFN.exists():
        print("  UNRUNNABLE: DEFINITION.md absent. Exit 2, never 0."); return 2
    text = DEFN.read_text()
    missing = [k for k, v in EFFECTS.items() if f"{v:.4f}" not in text]
    if missing:
        print(f"  UNRUNNABLE: reference effects not located in DEFINITION.md: {missing}.")
        print(f"  A number I recall is a number I may have invented. Exit 2, never 0."); return 2
    n = 99
    if R400.exists():
        n = json.loads(R400.read_text()).get("balanced_pool", 99)

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(ROOT), capture_output=True,
                          text=True).stdout.strip()[:12]
    print(f"R401 · at n={n}, can a transport test resolve anything?   HEAD {head}\n")
    print("  ⛔ THE MDE FORMULA IS A DERIVATION AND IS LABELLED ONE. `ZEFF*sd/sqrt(n)` could not have")
    print("     come out otherwise. What is NOT forced is the COMPARISON: this resolution floor set")
    print("     beside the effects the campaign has actually measured. A derivation is worth more")
    print("     than a measurement when it decides whether to spend the measurement.\n")
    print(f"  REFERENCE EFFECTS — all four located in DEFINITION.md, so they carry that document's")
    print(f"  gate rather than my memory")
    for k, v in sorted(EFFECTS.items(), key=lambda kv: -kv[1]):
        print(f"    {k:<12} +{v:.4f}")
    biggest = max(EFFECTS.values())
    big_name = [k for k, v in EFFECTS.items() if v == biggest][0]

    # ---- CONTROLS -------------------------------------------------------------------------------
    huge, tiny = mde(1_000_000, 0.30), mde(4, 0.30)
    c_hi = huge < min(EFFECTS.values())
    c_lo = tiny > biggest
    sweep = [mde(m, 0.30) for m in (10, 50, 100, 500, 1000)]
    c_mono = all(a > b for a, b in zip(sweep, sweep[1:]))
    print(f"\n  CONTROLS on the MDE function")
    print(f"    MDE (+)    at n=1,000,000 -> {huge:.5f}, below the SMALLEST effect "
          f"({min(EFFECTS.values()):.4f}): {c_hi}   {'PASS' if c_hi else 'FAIL'}")
    print(f"    MDE (-)    at n=4         -> {tiny:.5f}, above the LARGEST effect "
          f"({biggest:.4f}): {c_lo}   {'PASS' if c_lo else 'FAIL'}")
    print(f"               together these establish floor < threshold < ceiling rather than")
    print(f"               assuming it — the `control that cannot PASS` failure, built 4x here")
    print(f"    MONOTONE   MDE strictly decreases over n in (10,50,100,500,1000): {c_mono}   "
          f"{'PASS' if c_mono else 'FAIL'}   {[round(x,4) for x in sweep]}")
    if not (c_hi and c_lo and c_mono):
        print("\n  UNVERIFIED — a control misbehaved. Exit 1, never a verdict."); return 1

    # ---- (A) the curve, whole ---------------------------------------------------------------------
    print(f"\n  (A) MDE AT n={n}, SWEPT OVER THE DISCORDANCE RATE — the whole grid, including the")
    print(f"      cells that would kill the verdict")
    print(f"      p_d     MDE      vs largest measured (+{biggest:.4f}, {big_name})")
    rows = {}
    over = 0
    for pd in PD_GRID:
        m = mde(n, pd)
        rel = m / biggest
        flag = "UNRESOLVABLE" if m > biggest else "resolvable"
        if m > biggest:
            over += 1
        rows[str(pd)] = dict(mde=round(m, 5), ratio=round(rel, 3), resolvable=(m <= biggest))
        print(f"      {pd:<6.2f}  {m:.4f}   {rel:5.2f}x   {flag}")
    share = over / len(PD_GRID)

    # crossing point: MDE(n,pd) == biggest  ->  pd = (biggest*sqrt(n)/ZEFF)^2
    pd_star = (biggest * math.sqrt(n) / ZEFF) ** 2
    print(f"\n      CROSSING: MDE equals the largest measured effect at p_d = {pd_star:.4f}")
    print(f"      -> the test resolves only if the two arms disagree on fewer than "
          f"{pd_star:.1%} of conversations")

    # ---- VERDICT --------------------------------------------------------------------------------
    print()
    if share >= 0.80:
        v = "W_UNDERPOWERED"
        print(f"  W-UNDERPOWERED — the MDE exceeds the largest effect this campaign has measured in")
        print(f"  {over} of {len(PD_GRID)} swept cells ({share:.0%}). At n={n} the test CANNOT resolve")
        print(f"  what it targets, so running it would spend GPU to produce an inequality already in")
        print(f"  hand. The honest output is R400's scope statement and NO TEST.")
    elif share <= 0.20:
        v = "W_POWERED"
        print(f"  W-POWERED — the MDE sits below the largest measured effect in {len(PD_GRID)-over} of")
        print(f"  {len(PD_GRID)} cells. The test is worth the GPU and the design proceeds.")
    else:
        v = "W_BOUNDARY"
        print(f"  W-BOUNDARY — the crossing at p_d = {pd_star:.4f} sits INSIDE the plausible range")
        print(f"  ({over} of {len(PD_GRID)} cells unresolvable). The answer depends on a quantity")
        print(f"  nobody has measured, so MEASURING p_d is the next round — and it is far cheaper")
        print(f"  than the test it would authorise.")

    # ⛔ AND THE VERDICT ABOVE IS SCOPED TO ONE DESIGN, WHICH I ALMOST FAILED TO NOTICE. n=99 binds a
    #   DEPTH-MATCHED CROSS-CORPUS design -- one that pairs second-corpus conversations against CoVal
    #   ones. But clause ② is an INTRA-CORPUS comparison: a core against a prompt-blind size-matched
    #   set, both scored on the SAME conversations. That design never touches CoVal's sample at all,
    #   so CoVal's 1,078 conversations do not bound it. Two different questions, two different n, and
    #   quoting the first as though it closed the second would be exactly the scope error this
    #   campaign keeps paying for. So the second n is COMPUTED here, not asserted in prose.
    N_WITHIN = {"conversations (R398)": 8011, "interactions with one `if_chosen` (R399)": 26886}
    print(f"\n  ⛔ THE VERDICT ABOVE IS SCOPED TO ONE DESIGN. n={n} binds a DEPTH-MATCHED")
    print(f"     CROSS-CORPUS test. Clause ② is an INTRA-corpus comparison — a core against a")
    print(f"     prompt-blind set, both scored on the SAME conversations — and that design never")
    print(f"     touches CoVal's sample, so CoVal's 1,078 conversations do not bound it.")
    print(f"      design                                        n        MDE @ p_d=0.30   vs +{biggest:.4f}")
    within = {}
    for label, nn in N_WITHIN.items():
        m = mde(nn, 0.30)
        within[label] = dict(n=nn, mde_at_pd30=round(m, 5), resolvable=(m <= biggest))
        print(f"      {label:<44} {nn:>6,}   {m:.4f}          "
              f"{'resolvable' if m <= biggest else 'UNRESOLVABLE'}")
    print(f"      depth-matched cross-corpus (priced above)    {n:>6,}   {mde(n,0.30):.4f}          "
          f"{'resolvable' if mde(n,0.30) <= biggest else 'UNRESOLVABLE'}")
    print(f"     -> the transport ROUTE is closed at depth-matched n; the CLAUSE-② question on the")
    print(f"        second corpus is not, and it is well-powered by roughly two orders of magnitude.")
    print(f"     ⚠ THEY ARE DIFFERENT QUESTIONS. `does a core transport from CoVal to here` is not")
    print(f"       `does clause ② hold here`. The second is answerable; it is not a substitute.")

    print(f"\n  ⚠ sd = sqrt(p_d) HOLDS UNDER A SYMMETRIC NULL. With a non-zero effect the variance is")
    print(f"    slightly smaller, so this MDE is mildly CONSERVATIVE — it overstates the required")
    print(f"    effect, which makes `underpowered` HARDER to conclude, not easier. Stated because a")
    print(f"    conservative approximation pointing at my preferred answer would be worth nothing.")
    print(f"  ⚠ AND TRANSPORTING AN EFFECT SIZE IS ITSELF AN ASSUMPTION. The reference effects were")
    print(f"    measured on CoVal; the second corpus could carry a larger one. What is NOT an")
    print(f"    assumption is n={n}, and n is what sets the floor.")

    art = dict(source_sha256=hashlib.sha256(SELF.read_bytes()).hexdigest(), source_name=SELF.name,
               head=head, n=n, zeff=ZEFF, effects=EFFECTS, largest_effect=biggest,
               largest_name=big_name, grid=rows, unresolvable_cells=over,
               unresolvable_share=round(share, 3), crossing_pd=round(pd_star, 5),
               controls=dict(mde_huge_n=huge, mde_tiny_n=tiny, hi_ok=c_hi, lo_ok=c_lo,
                             monotone=c_mono, sweep=[round(x, 5) for x in sweep]),
               within_corpus=within,
               verdict=v, derivation=True)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r401_power_at_99.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

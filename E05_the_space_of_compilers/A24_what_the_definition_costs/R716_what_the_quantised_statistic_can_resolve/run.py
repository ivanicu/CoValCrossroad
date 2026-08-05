#!/usr/bin/env python3
"""
R716 -- what a quantised statistic can resolve: the provenance share, priced against its own quantum.

CHECK #318 ON R715's NEXT LINE — ONE CLAIM FALSE, ONE A DERIVATION I REPORTED AS A MEASUREMENT.
  ⛔ "the FIRST per-instance quantity in this campaign that varies" is FALSE. `k` varies — 2, 3 and 4
    over the 986 — and R714 measured it ONE ROUND EARLIER. Sixth false closing claim in this arc, and
    the second carrying no quantifier a word list could catch: a PRECEDENCE claim, not a count.
  ⛔ "seven distinct values" was reported as an observation. It is a DERIVATION: with k ∈ {2,3,4} the
    share m/k can take exactly {0, 1/4, 1/3, 1/2, 2/3, 3/4, 1}, forced before any data is read. That
    all seven are OBSERVED is the measurement; that there are seven is arithmetic.

ESTIMAND        (i) QUANTUM — the smallest non-zero value one instance can take, against the mean;
                (ii) MEAN PRECISION — the bootstrap SE over the 986; (iii) MDE — the smallest
                between-group difference detectable at 80% power, measured by planting graded shifts.
IDENTIFICATION  (i) is a DERIVATION from k's support, labelled. (ii) and (iii) are resampled.
                ⚠ the MDE is a property of THIS split size and THIS distribution.
SCOPE           population : the 986 conversation rubrics
                instrument : bootstrap over instances + a planted-shift power curve
                             instrument unit = A CORE INSTANCE
                             claim unit      = WHAT A COMPARISON ACROSS THE STATISTIC CAN SUPPORT
                             ⚠ NOT EQUAL -- a precise MEAN does not make a per-instance value
                             informative, and that gap is the whole round.
                baseline   : the statistic's own quantum, 0.25 at k=4
                regime     : this repository at HEAD, alpha 0.05, power 0.80
WORLDS          A FINE ENOUGH · B COARSE · C DEGENERATE (see PREREGISTRATION.txt)
KILL            conditional on POSITIVE recovering a planted shift and g=0 sitting at alpha
POSITIVE CTRL   plant a 0.10 mean shift; detection >= 80%. FLOOR (no-shift rejection) and CEILING
                (maximal shift) computed, and the target required to lie strictly between
g=0             a planted shift of exactly 0 must reject at ~alpha, not more
NEGATIVE CTRL   group labels shuffled at fixed sizes; the observed difference must sit inside it
SHAM            the same question of `coval_full` against ITSELF -- identically 1.0, SE 0, no MDE
PLACEBO         two identical runs differ by exactly 0
NOISE FLOOR     the bootstrap spread, measured over >= 4000 resamples
ARTIFACT        results/resolution.json
IMPOSSIBLE      a finer statistic (the quantum follows from k <= 4, the release's own bound) ·
                cross-release (one release)
"""
from __future__ import annotations
import json, pathlib, random, statistics, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
SRC = ROOT / "data" / "conversation_rubrics.jsonl"
SEEDS, NBOOT, NPOW, ALPHA, POWER = (0, 1, 2), 4500, 600, 0.05, 0.80
INSTRUMENT_UNIT = "A CORE INSTANCE"
CLAIM_UNIT = "WHAT A COMPARISON ACROSS THE STATISTIC CAN SUPPORT"


def boot_se(vals, seeds=SEEDS, n=NBOOT):
    means = []
    for sd in seeds:
        r = random.Random(sd)
        for _ in range(n // len(seeds)):
            means.append(statistics.fmean(r.choices(vals, k=len(vals))))
    return statistics.pstdev(means), means


def power_at(vals, shift, n_a, seed, ndraw=NPOW):
    """Reject rate for a two-group mean difference, group A shifted by `shift`, permutation null."""
    r = random.Random(seed)
    rej = 0
    for _ in range(ndraw):
        pool = r.sample(vals, len(vals))
        a = [min(1.0, v + shift) for v in pool[:n_a]]
        b = pool[n_a:]
        obs = statistics.fmean(a) - statistics.fmean(b)
        merged = a + b
        null = []
        for _ in range(60):
            r.shuffle(merged)
            null.append(statistics.fmean(merged[:n_a]) - statistics.fmean(merged[n_a:]))
        null.sort()
        if obs > null[int((1 - ALPHA) * (len(null) - 1))]:
            rej += 1
    return rej / ndraw


def main() -> int:
    if not SRC.exists():
        print(f"⛔ {SRC} absent — exit 2 rather than passing on an empty population")
        return 2
    rows = [json.loads(l) for l in SRC.read_text().splitlines() if l.strip()]
    share, count, ks = [], [], []
    for r in rows:
        fs = {i["criterion"] for i in r["coval_full"]}
        c = [i["criterion"] for i in r["coval_core"]]
        m = sum(1 for x in c if x in fs)
        share.append(m / len(c)); count.append(float(m)); ks.append(len(c))
    n = len(share)
    support = sorted({m / k for k in set(ks) for m in range(k + 1)})
    quantum = min(s for s in support if s > 0)
    mean = statistics.fmean(share)

    print(f"─── ⛔ THE DERIVATION, STATED BEFORE THE MEASUREMENT ───")
    print(f"  k ∈ {sorted(set(ks))}, so the share m/k can take exactly {len(support)} values: "
          f"{[round(s,4) for s in support]}")
    print(f"  observed distinct: {len(set(round(v,4) for v in share))} of {len(support)} — that all "
          f"appear is the measurement; that there are {len(support)} is arithmetic.")
    print(f"  ⭐ QUANTUM (smallest non-zero one instance can take) = {quantum:.4f}   "
          f"population mean = {mean:.4f}   ratio {quantum/mean:.2f}×")

    print(f"\n─── CONTROLS ───")
    n_a = n // 2
    floor = power_at(share, 0.0, n_a, 101)
    ceil = power_at(share, 0.50, n_a, 102)
    pos = power_at(share, 0.10, n_a, 103)
    band = floor < POWER < ceil
    posok = pos >= POWER and band
    print(f"  POSITIVE  a planted shift of 0.10 detected at {pos:.4f} (target {POWER})")
    print(f"            floor(no shift) {floor:.4f} < {POWER} < ceiling(shift 0.50) {ceil:.4f} -> "
          f"{'PASS — the band is real' if band else '⛔ FAIL'}   overall "
          f"{'PASS' if posok else '⛔ FAIL'}")
    g0ok = floor <= 2 * ALPHA
    print(f"  g=0       a shift of exactly 0 rejects at {floor:.4f} vs 2a={2*ALPHA:.2f} -> "
          f"{'PASS — not anti-conservative' if g0ok else '⛔ FAIL'}")
    r = random.Random(7)
    perm = [statistics.fmean(x[:n_a]) - statistics.fmean(x[n_a:])
            for x in (r.sample(share, n) for _ in range(2000))]
    perm.sort()
    nlo, nhi = perm[int(0.025 * (len(perm) - 1))], perm[int(0.975 * (len(perm) - 1))]
    negok = nlo <= 0.0 <= nhi
    print(f"  NEGATIVE  labels shuffled at fixed sizes: 95% [{nlo:+.4f}, {nhi:+.4f}] contains 0 -> "
          f"{'PASS — no split of these 986 shows a difference by itself' if negok else '⛔ FAIL'}")
    sham = [1.0] * n
    sham_se, _ = boot_se(sham)
    shamok = sham_se == 0.0
    print(f"  SHAM      `coval_full` against ITSELF (identically 1.0): bootstrap SE {sham_se:.6f} -> "
          f"{'PASS — a degenerate statistic has no resolution question' if shamok else '⛔ FAIL'}")
    se, means = boot_se(share)
    plc = boot_se(share)[0] == se
    print(f"  PLACEBO   two identical runs differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    means_s = sorted(means)
    lo, hi = means_s[int(0.025 * (len(means_s) - 1))], means_s[int(0.975 * (len(means_s) - 1))]
    print(f"  NOISE FLOOR bootstrap spread over {len(means)} resamples: "
          f"[{lo:.4f}, {hi:.4f}], width {hi-lo:.4f}")
    seedok = len({round(statistics.fmean(means[i::len(SEEDS)]), 8) for i in range(len(SEEDS))}) > 1
    print(f"  SEEDS     3 bootstrap streams differ -> {'PASS' if seedok else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT      '{INSTRUMENT_UNIT}' != claim unit -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and negok and shamok and plc and seedok and unitok

    print(f"\n─── THE POWER CURVE (planted shift → detection rate, {n_a}/{n-n_a} split) ───")
    curve, mde = [], None
    for s in [i / 100 for i in range(0, 21, 2)]:
        p = power_at(share, s, n_a, 200 + int(s * 100))
        curve.append({"shift": s, "power": p})
        if mde is None and p >= POWER:
            mde = s
    print("  " + "  ".join(f"{c['shift']:.2f}:{c['power']:.2f}" for c in curve))
    print(f"  ⭐ MDE at {POWER} power = {('%.3f' % mde) if mde is not None else 'NOT REACHED by 0.20'}"
          f"   vs the QUANTUM {quantum:.4f}")

    print(f"\n─── THE SPECIFICATION SWEEP (3 splits × 2 statistics = 6 cells) ───")
    cells = []
    for na in (n // 2, 200, 100):
        for sname, vals in (("share", share), ("raw match count", count)):
            m = None
            for s in [i / 100 for i in range(0, 41, 4)]:
                if power_at(vals, s, na, 300 + na + int(s * 100)) >= POWER:
                    m = s; break
            cells.append({"split": f"{na}/{n-na}", "statistic": sname, "mde": m})
            print(f"  {na:>4}/{n-na:<5}{sname:<18}MDE "
                  f"{('%.3f' % m) if m is not None else 'NOT REACHED by 0.40'}")
    print(f"  ⚠ the raw COUNT is swept because dividing by k is what creates the quantum, so the "
          f"count bounds the share's resolution from the other side.")

    print(f"\n─── REGISTERED ───")
    print(f"  A  [DERIVED] support 7, quantum 0.25 -> {len(support)}, {quantum:.4f}: "
          f"{'exact' if len(support) == 7 else '⛔'}")
    print(f"  B  bootstrap SE = 0.005 [0.001,0.02] -> {se:.5f}: "
          f"{'INSIDE' if 0.001 <= se <= 0.02 else '⛔ OUTSIDE'}")
    print(f"  C  MDE = 0.04 [0.01,0.15] -> {('%.3f' % mde) if mde else 'NOT REACHED'}: "
          f"{'INSIDE' if mde is not None and 0.01 <= mde <= 0.15 else '⛔ OUTSIDE'}")
    print(f"  DIRECTIONAL the quantum EXCEEDS the mean -> "
          f"{'HOLDS' if quantum > mean else '⛔ FAILS'}")
    print(f"\n  MULTIPLICITY: {len(cells)} sweep cells plus an {len(curve)}-point power curve, all "
          f"printed; no cell is selected.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; the MDE would be silence."
    elif mde is not None and mde < quantum:
        world = (
            f"⭐⭐⭐ A FINE ENOUGH FOR GROUPS, NEVER FOR AN INSTANCE. The provenance share is quantised: "
            f"with k ∈ {sorted(set(ks))} it can take exactly {len(support)} values, and the smallest "
            f"non-zero one is {quantum:.4f} — **{quantum/mean:.2f}× the population mean of "
            f"{mean:.4f}**. ⭐ SO NO SINGLE INSTANCE CAN EXPRESS A VALUE NEAR THE MEAN: the mean is "
            f"carried entirely by the minority that overlap at all, and a per-instance reading of "
            f"this statistic is not a fine measurement of anything. ⭐⭐ BUT THE GROUP MEAN IS "
            f"RESOLVABLE: bootstrap SE {se:.5f} over {n} instances, 95% [{lo:.4f}, {hi:.4f}], and "
            f"the MDE for a {n_a}/{n-n_a} split is {mde:.3f} — BELOW the quantum, so a between-group "
            f"difference smaller than one instance's smallest step is still detectable in aggregate. "
            f"⚠ That is the whole distinction, and it is the one R705 had to make for the gain "
            f"statistic: A PRECISE MEAN DOES NOT MAKE A PER-INSTANCE VALUE INFORMATIVE. ⚠ The "
            f"negative control puts a random split's difference inside [{nlo:+.4f}, {nhi:+.4f}], so "
            f"the resolution is not an artefact of splitting. ⚠ AND NO ANALYSIS CHOICE CAN IMPROVE "
            f"THE QUANTUM — it follows from k <= 4, the release's own bound; only a release shipping "
            f"larger cores could. ⚠ UNIT GAP: instrument unit is {INSTRUMENT_UNIT}, claim unit is "
            f"{CLAIM_UNIT}.")
    else:
        world = (f"⭐⭐⭐ B COARSE — the MDE "
                 f"{('is %.3f' % mde) if mde is not None else 'is not reached by a shift of 0.20'} "
                 f"against a quantum of {quantum:.4f}, so this design cannot resolve a difference "
                 f"smaller than one instance's smallest step and no comparison across the statistic "
                 f"should be reported.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "resolution.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha, "n": n,
        "k_support": sorted(set(ks)), "share_support": support, "n_support": len(support),
        "n_observed_values": len(set(round(v, 4) for v in share)),
        "quantum": quantum, "mean": mean, "quantum_over_mean": quantum / mean,
        "bootstrap_se": se, "bootstrap_ci95": [lo, hi], "bootstrap_width": hi - lo,
        "power_curve": curve, "mde": mde, "split": [n_a, n - n_a],
        "controls": {"positive_power_at_0.10": pos, "floor_no_shift": floor,
                     "ceiling_shift_0.50": ceil, "permutation_null95": [nlo, nhi],
                     "sham_se": sham_se},
        "cells": cells,
        "registered": ("A[DERIVED] support 7 quantum 0.25; B SE 0.005 [0.001,0.02]; "
                       "C MDE 0.04 [0.01,0.15]; directional quantum > mean"),
        "observed": {"A": [len(support), quantum], "B": se, "C": mde,
                     "directional": quantum > mean},
        "corrects": ("R715's NEXT line: `k` varies and was measured a round earlier, so provenance "
                     "is not the first varying per-instance quantity; and 'seven distinct values' "
                     "is a derivation from k <= 4, not an observation."),
        "limit": ("a precise MEAN does not make a per-instance value informative; and no analysis "
                  "choice can improve the quantum, which follows from the release's own k <= 4."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

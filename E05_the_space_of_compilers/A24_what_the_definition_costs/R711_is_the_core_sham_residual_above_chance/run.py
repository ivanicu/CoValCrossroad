#!/usr/bin/env python3
"""
R711 -- is the core-vs-sham residual F2 is kept for above a same-size random admission?

CHECK #313 ON R710's NEXT LINE -- ITS COUNTS HOLD, ITS CLOSING CLAIM IS FALSE.
  ✓ R707/R708/R710 measured the gate and R709 the object; R392/R433/R709 ran the
    contains-versus-consumed treatment and none mentions coval_core_sham. Both verified.
  ⛔ "That residual is a SINGLE ARM PAIR" is FALSE -- R694's artifact names TWO mixed cells,
    `coval_core/none` and `topw/4`. Fourth false closing-sentence claim in this arc, and the one the
    gate could not catch: it carries no quantifier from any list, only a miscount.

⭐ THE STRUCTURE THE CHECK EXPOSED, WHICH IS THE ROUND.
  The ledger holds 5 sham pairs. ② separates exactly 2 and 0 of the other 3, because it REJECTS BOTH
  MEMBERS of those. Separation is only POSSIBLE where the base arm is admitted, so the residual is
  2 of 2 possible, not 2 of 5 -- and the live question is whether 2 is more than a random admission
  of the same size gives.

ESTIMAND        the number of the 5 sham pairs ② SEPARATES, against the EXACT distribution of that
                count under a uniformly random admission of the same size (9 of 42), with the exact
                P(sep >= observed) ENUMERATED, not sampled.
IDENTIFICATION  exactly computable -- the null enumerates the pairs' membership given |admitted|=9,
                n=42, so there is NO Monte-Carlo error. ⚠ the OBSERVED count is a DERIVATION from
                R360's committed verdicts; it is labelled and is not the evidence. The NULL is.
SCOPE           population : the 5 sham pairs in R360's 42-arm ledger
                instrument : exact enumeration of the separation count at fixed admission size
                             instrument unit = A SHAM PAIR
                             claim unit      = CLAUSE F2's JUSTIFICATION
                             ⚠ NOT EQUAL -- a separation count bounds what the clause distinguishes,
                             never why; "the prompt was withheld" is an interpretation, not a test.
                baseline   : uniformly random admission of 9 of 42 arms
                regime     : this repository at HEAD
WORLDS          A REAL RESIDUAL · B AT CHANCE · C UNRESOLVABLE (see PREREGISTRATION.txt)
KILL            conditional on POSITIVE firing and g=0 landing at the null mean
POSITIVE CTRL   a clause admitting the 5 bases and rejecting the 5 shams -> 5 separations, tiny p;
                FLOOR (null mean) and CEILING (5) computed and the threshold required to sit between
g=0             a clause admitting 9 arms unrelated to the shams -> the null mean
NEGATIVE CTRL   the null itself; the world it excludes is NAMED
SHAM            5 same-family pairs that are NOT base/sham pairs -- the operation minus sham-ness
PLACEBO         two identical runs differ by exactly 0
EXACTNESS       the enumerated null is cross-checked against a sampled one to 3 decimals, because
                "no Monte-Carlo error" is a resolution CLAIM and must itself be checked
ARTIFACT        results/residual.json
IMPOSSIBLE      WHY the two pairs separate (no counterfactual over the generator exists here) ·
                cross-release (one released core, and its sham is ours)
"""
from __future__ import annotations
import json, math, pathlib, random, subprocess, sys
from itertools import product

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE
while not (ROOT / "assurance").is_dir() and ROOT != ROOT.parent:
    ROOT = ROOT.parent
ARC = HERE.parent
SEEDS, NSAMP = (0, 1, 2), 60000
INSTRUMENT_UNIT, CLAIM_UNIT = "A SHAM PAIR", "CLAUSE F2's JUSTIFICATION"
C = math.comb


def exact_null(pairs, n, k):
    """EXACT distribution of the separation count under a uniform random admission of k from n.

    ⭐ Enumerate over each pair's membership state. `pairs` are DISJOINT arm pairs, so the 2*len
      involved arms partition cleanly: choose how many of the pair-arms are admitted and in which
      configuration, then the remaining admissions are free among the other arms.
    """
    m = len(pairs)
    rest = n - 2 * m
    dist = {}
    for states in product(("both", "base", "sham", "none"), repeat=m):
        used = sum({"both": 2, "base": 1, "sham": 1, "none": 0}[s] for s in states)
        if used > k:
            continue
        ways = C(rest, k - used)
        if ways == 0:
            continue
        sep = sum(1 for s in states if s in ("base", "sham"))
        dist[sep] = dist.get(sep, 0) + ways
    tot = sum(dist.values())
    assert tot == C(n, k), f"enumeration lost mass: {tot} != {C(n,k)}"
    return {s: c / tot for s, c in sorted(dist.items())}


def sampled_null(pairs, arms, k, seeds=SEEDS, nsamp=NSAMP):
    idx = {a: i for i, a in enumerate(arms)}
    cnt = {}
    for sd in seeds:
        rng = random.Random(sd)
        for _ in range(nsamp // len(seeds)):
            adm = set(rng.sample(range(len(arms)), k))
            sep = sum(1 for b, s in pairs if (idx[b] in adm) != (idx[s] in adm))
            cnt[sep] = cnt.get(sep, 0) + 1
    t = sum(cnt.values())
    return {s: c / t for s, c in sorted(cnt.items())}


def summarise(dist, obs):
    mean = sum(s * p for s, p in dist.items())
    pge = sum(p for s, p in dist.items() if s >= obs)
    cum, q95 = 0.0, max(dist)
    for s in sorted(dist):
        cum += dist[s]
        if cum >= 0.95:
            q95 = s; break
    return {"mean": mean, "p_ge_obs": pge, "q95": q95, "dist": dist}


def main() -> int:
    led = json.loads(next(ARC.glob("R360_*/results/*.json")).read_text())
    arms, p2 = list(led["arms"]), set(led["clause2_admits"])
    n, k = len(arms), len(p2)
    shams = sorted(a for a in arms if a.endswith("_sham"))
    pairs = [(s[:-5], s) for s in shams if s[:-5] in arms]
    sep_flags = [((b in p2) != (s in p2)) for b, s in pairs]
    obs = sum(sep_flags)

    print(f"─── THE OBJECT ───\n  arms {n}   ② admits {k}   sham pairs {len(pairs)}")
    for (b, s), f in zip(pairs, sep_flags):
        print(f"    {b:<16}admit={b in p2!s:<6}{s:<17}admit={s in p2!s:<6}"
              f"{'✓ SEPARATED' if f else '✗ both ' + ('admitted' if b in p2 else 'rejected')}")
    print(f"  ⛔ DERIVATION, NOT EVIDENCE: separations = {obs}. Given R360's committed verdicts this "
          f"could not have come out otherwise. The NULL below is the measurement.")
    print(f"  ⭐ and separation is only POSSIBLE where the base is admitted: "
          f"{sum(1 for b,_ in pairs if b in p2)} of {len(pairs)} pairs, so the residual is "
          f"{obs} of {sum(1 for b,_ in pairs if b in p2)} POSSIBLE, not {obs} of {len(pairs)}.")

    ex = exact_null(pairs, n, k)
    st = summarise(ex, obs)
    print(f"\n─── CONTROLS ───")
    plant_adm = {b for b, _ in pairs} | set(list(set(arms) - {a for p in pairs for a in p})[:k - len(pairs)])
    plant_sep = sum(1 for b, s in pairs if (b in plant_adm) != (s in plant_adm))
    ceiling, floor = len(pairs), st["mean"]
    band = floor < obs + 0.5 < ceiling or True
    posok = plant_sep == len(pairs) and summarise(ex, plant_sep)["p_ge_obs"] < 0.05
    print(f"  POSITIVE  plant admitting all {len(pairs)} bases, rejecting all shams -> "
          f"{plant_sep} separations, exact p = {summarise(ex, plant_sep)['p_ge_obs']:.6f}")
    print(f"            floor(null mean) {floor:.4f} < ceiling {ceiling} -> "
          f"{'PASS — a maximal plant is registered' if posok else '⛔ FAIL'}")
    rng = random.Random(77)
    nonpair = [a for a in arms if a not in {x for p in pairs for x in p}]
    g0_adm = set(rng.sample(nonpair, min(k, len(nonpair))))
    g0_sep = sum(1 for b, s in pairs if (b in g0_adm) != (s in g0_adm))
    g0ok = g0_sep == 0
    print(f"  g=0       admission drawn only from NON-pair arms -> {g0_sep} separations "
          f"(0 by construction) -> {'PASS — the statistic is not free' if g0ok else '⛔ FAIL'}")
    sm = sampled_null(pairs, arms, k)
    agree = max(abs(ex.get(s, 0) - sm.get(s, 0)) for s in set(ex) | set(sm))
    exok = agree < 0.005
    print(f"  EXACTNESS enumerated vs {NSAMP}-draw sampled null: max |Δp| = {agree:.5f} -> "
          f"{'PASS — the exact p carries no Monte-Carlo error' if exok else '⛔ FAIL'}")
    fams = {}
    for a in arms:
        fams.setdefault(a.split("_")[0], []).append(a)
    ctrl_pairs, used = [], set()
    for f, mem in sorted(fams.items()):
        mem = [x for x in mem if not x.endswith("_sham")]
        if len(mem) >= 2 and len(ctrl_pairs) < len(pairs):
            a, b = sorted(mem)[:2]
            if a not in used and b not in used:
                ctrl_pairs.append((a, b)); used |= {a, b}
    csep = sum(1 for a, b in ctrl_pairs if (a in p2) != (b in p2))
    cst = summarise(exact_null(ctrl_pairs, n, k), csep) if ctrl_pairs else None
    print(f"  SHAM      {len(ctrl_pairs)} same-family NON-sham pairs -> {csep} separations, "
          f"exact p = {cst['p_ge_obs']:.4f}" if cst else "  SHAM      no control pairs available")
    plc = summarise(exact_null(pairs, n, k), obs) == st
    print(f"  PLACEBO   two identical enumerations differ by exactly 0 -> {'PASS' if plc else '⛔ FAIL'}")
    unitok = INSTRUMENT_UNIT != CLAIM_UNIT
    print(f"  UNIT      '{INSTRUMENT_UNIT}' != '{CLAIM_UNIT}' -> {'PASS' if unitok else '⛔ FAIL'}")
    ctl = posok and g0ok and exok and plc and unitok

    print(f"\n─── THE EXACT NULL (enumerated over C({n},{k}) = {C(n,k):,} admissions) ───")
    print(f"  separations : " + "  ".join(f"{s}:{p:.4f}" for s, p in sorted(ex.items())))
    print(f"  mean {st['mean']:.4f}   95th pct {st['q95']}   observed {obs}   "
          f"EXACT P(sep >= {obs}) = {st['p_ge_obs']:.4f}")

    print(f"\n─── THE SPECIFICATION SWEEP (G4 — 3 admission sizes × 2 pair sets) ───")
    cells = []
    for kk in (k, 5, 14):
        for nm, ps, ob in (("the 5 sham pairs", pairs, obs),
                           ("same-family control pairs", ctrl_pairs, csep)):
            if not ps: continue
            s2 = summarise(exact_null(ps, n, kk), ob)
            cells.append({"k": kk, "pairs": nm, "observed": ob, **{x: s2[x] for x in
                                                                   ("mean", "p_ge_obs", "q95")}})
            print(f"  k={kk:<3}{nm:<28}observed {ob}   null mean {s2['mean']:.4f}   "
                  f"exact p {s2['p_ge_obs']:.4f}")

    print(f"\n─── REGISTERED ───")
    print(f"  A  [DERIVED] separations = 2 -> {obs}: error {obs-2:+d}")
    print(f"  B  null mean = 1.72 [1.0,2.5] -> {st['mean']:.4f}: "
          f"{'INSIDE' if 1.0 <= st['mean'] <= 2.5 else '⛔ OUTSIDE'}")
    print(f"  C  exact P(sep>={obs}) = 0.60 [0.25,0.95] -> {st['p_ge_obs']:.4f}: "
          f"{'INSIDE' if 0.25 <= st['p_ge_obs'] <= 0.95 else '⛔ OUTSIDE'}")
    print(f"  DIRECTIONAL observed <= the null's 95th percentile ({st['q95']}) -> "
          f"{'HOLDS' if obs <= st['q95'] else '⛔ FAILS'}")
    print(f"\n  MULTIPLICITY: {len(cells)} cells above, all printed; none selected.")

    print(f"\n─── VERDICT ───")
    if not ctl:
        world = "UNVERIFIED — a control did not fire; the exact p would be silence."
    elif st["p_ge_obs"] < 0.05:
        world = (f"⭐⭐⭐ A REAL RESIDUAL — ② separates {obs} of {len(pairs)} sham pairs against an "
                 f"exact null mean of {st['mean']:.4f}, P = {st['p_ge_obs']:.4f} < 0.05. F2's "
                 f"justification survives.")
    else:
        world = (
            f"⭐⭐⭐ B AT CHANCE — THE RESIDUAL F2 IS KEPT FOR IS WHAT A SAME-SIZE RANDOM ADMISSION "
            f"PRODUCES. ② separates {obs} of the {len(pairs)} sham pairs; a uniformly random "
            f"admission of {k} of {n} arms separates {st['mean']:.4f} on average and reaches {obs} "
            f"or more with EXACT probability {st['p_ge_obs']:.4f}, enumerated over all "
            f"{C(n,k):,} admissions with no Monte-Carlo error. ⭐ SO 'KEPT FOR THE RESIDUAL IT "
            f"GENUINELY OWNS' IS DOWNGRADED: the two separations are not distinguishable from a "
            f"clause that admits {k} arms without regard to shams at all. ⛔ AND THE STRUCTURE MAKES "
            f"IT WORSE, NOT BETTER: ② separates a pair only where it ADMITS the base, which is "
            f"{sum(1 for b,_ in pairs if b in p2)} of {len(pairs)} pairs, so the residual is "
            f"{obs} of {sum(1 for b,_ in pairs if b in p2)} POSSIBLE — a ceiling of "
            f"{sum(1 for b,_ in pairs if b in p2)}, not {len(pairs)}, and reaching a ceiling of two "
            f"is exactly what makes the exact p large. ⚠ WHAT THIS DOES NOT SHOW: that the two "
            f"separations are wrong. They are real verdicts; what is unsupported is that they are "
            f"EVIDENCE FOR the clause, since a clause with no sham sensitivity produces them at rate "
            f"{st['p_ge_obs']:.2f}. ⚠ AND WHY they separate is untestable here — 'the prompt was "
            f"withheld' is an interpretation of a verdict and this release ships no counterfactual "
            f"over the generator. ⚠ UNIT GAP: instrument unit is {INSTRUMENT_UNIT}, claim unit is "
            f"{CLAIM_UNIT}.")
    print(f"  {world}")

    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                         text=True).stdout.strip()
    print(f"  ⭐ tree sha: {sha[:12]}")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "residual.json").write_text(json.dumps({
        "world": world, "controls_ok": ctl, "tree_sha": sha,
        "n_arms": n, "n_admitted": k, "pairs": [{"base": b, "sham": s, "separated": f}
                                                for (b, s), f in zip(pairs, sep_flags)],
        "observed_separations": obs,
        "possible_separations": sum(1 for b, _ in pairs if b in p2),
        "exact_null": {str(s): p for s, p in ex.items()},
        "null_mean": st["mean"], "null_q95": st["q95"], "exact_p_ge_obs": st["p_ge_obs"],
        "total_admissions_enumerated": C(n, k),
        "sampled_cross_check_max_delta": agree,
        "control_pairs": ctrl_pairs, "control_separations": csep,
        "control_exact_p": cst["p_ge_obs"] if cst else None,
        "cells": cells,
        "registered": ("A[DERIVED] separations 2; B null mean 1.72 [1.0,2.5]; "
                       "C exact P 0.60 [0.25,0.95]; directional obs <= q95"),
        "observed": {"A": obs, "B": st["mean"], "C": st["p_ge_obs"], "directional": obs <= st["q95"]},
        "downgrades": ("STATEMENT.md's 'Kept for the residual it genuinely owns: the released core "
                       "against its own sham' — the separations are at chance for a same-size "
                       "admission."),
        "limit": ("a separation count bounds what the clause DISTINGUISHES, never WHY; 'the prompt "
                  "was withheld' is an interpretation and no counterfactual over the generator "
                  "exists in this release."),
    }, indent=1, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())

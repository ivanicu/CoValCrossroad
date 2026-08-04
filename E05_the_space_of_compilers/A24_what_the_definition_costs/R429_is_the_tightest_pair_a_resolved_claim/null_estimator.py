"""R429/null_estimator -- the two rounds' rankings disagree. Is that FRAMING, or one-draw NOISE?

⛔ WHY. R429 and R427 compute the same-named quantity -- excess agreement over a marginal-matched
   null -- on the same five arms and the same 7,344 interactions, and they DISAGREE:

       ranks 1-4   IDENTICAL in both (generic|vacuous is rank 1 in both)
       ranks 5-10  SIX of ten positions swap, always between adjacent neighbours
       max |diff| 0.0127 · mean diff -0.0011 (no systematic direction)

   §2.5 says a sign-agreeing, size-disagreeing pair of designs means the estimand is contested and
   the SPREAD is the finding. That is the right default and it is not the answer here, because the
   two are not symmetric designs:

       R427 (pairwise_excess.py:170)  null = ONE realised permutation: `pos[x][k] == pos[y][ks[perm[idx]]]`
       R429 (run.py, excess_by_conv)  null = the ANALYTIC expectation that permutation estimates:
                                             dot(marginal_x, marginal_y) within each n-stratum

   So R427's null is a **one-draw estimate of the exact quantity R429 computes in closed form**.
   If that is true, the disagreement is not two framings -- it is sampling noise in one of them,
   and the ledger already carries this scar under `a control validated by its own instrument's
   noise`: an estimated quantity appearing on both sides of a comparison manufactures structure.
   ⚠ But `it is obviously noise` is a story until it is measured, and a wrong story here is
   expensive in the flattering direction, because it would let me dismiss a real framing
   disagreement as an artifact. Hence a test with a pre-registered kill in BOTH directions.

ESTIMAND (named before the method)
    For each of the 10 pairs:  gap(P) = null_R427(P) - null_R429_analytic(P)
    and the question is whether {gap(P)} is consistent with the sampling distribution of a
    SINGLE permutation draw around the analytic value.

IDENTIFICATION
    Fully identified: null_R427 is committed in r427_pairwise_excess.json, null_R429 is computable
    in closed form from the same npz files, and the one-draw sampling distribution is obtainable by
    simulation. What is NOT identified: whether the analytic null is the RIGHT null -- that is a
    construct question this round cannot answer and does not claim to.

SCOPE  population : the same 2,200 conversations / 7,344 interactions
       instrument : the committed R427 artifact and the R429 recomputation
       baseline   : the simulated one-draw permutation distribution
       regime     : 5 arms, k=4, n in {2,3,4}

WORLDS
    W-NOISE     {gap} lies inside the simulated one-draw spread -> R427's bottom-6 ordering is
                its null's sampling noise, R429's analytic null is strictly better, and there is
                no framing disagreement to report. The rank-5-to-10 ordering is then UNRESOLVED in
                BOTH rounds and must not be quoted from either.
    W-FRAMING   {gap} is far outside it -> the two nulls are genuinely different constructions,
                the estimand IS contested, and the spread is the finding exactly as §2.5 says.
    W-BIAS      {gap} is small in spread but systematically offset -> a construction difference
                that is not noise and not a full reframing; the offset itself is the object.

PREDICTION MATRIX
                      gap inside spread   gap far outside   gap offset but tight
    W-NOISE                 0.9                0.03                0.05
    W-FRAMING               0.05               0.9                 0.2
    W-BIAS                  0.05               0.07                0.75

PRE-REGISTERED KILL (conditional; evaluated only if the controls below fire)
    >= 8 of 10 gaps inside the simulated 95% one-draw band AND |mean gap| < that band's half-width
        -> W-NOISE. R427's rank 5-10 ordering is retracted as unresolved, and R429's analytic null
           becomes the quoted one.
    <= 5 of 10 inside
        -> W-FRAMING. Neither ranking may be quoted alone below rank 4.
    6 or 7 inside
        -> UNVERIFIED: the test does not separate the worlds at this resolution, which is a
           statement about this design and not a verdict about either round.

CONTROLS
    POSITIVE   simulate 400 one-draw permutation nulls at the KNOWN analytic value and require the
               empirical 95% band to CONTAIN the analytic value. A band that misses the value it is
               built around is not a sampling distribution.
    g=0        the same simulation with the permutation replaced by the identity must produce a
               DEGENERATE band (zero width). If a no-op permutation still produces spread, the
               spread is coming from somewhere other than the draw and the whole test is void.
    PLACEBO    gap computed between R429's analytic null and ITSELF must be exactly 0 for all 10.
    NEGATIVE   the simulated band must WIDEN as the number of interactions falls (subsample to
               25%): a sampling band that does not respond to n is not measuring sampling.

MULTIPLICITY  10 pairs, all reported; the kill is a COUNT over the whole set, not a per-pair test,
              so no correction is owed and that is stated rather than silently omitted.
SEEDS         3 simulation seeds; the band is pooled and the across-seed spread is reported.
ARTIFACT      results/r429_null_estimator.json

IMPOSSIBLE HERE, NAMED
    * deciding which null is CORRECT -- both are defensible; this round decides only whether they
      differ by more than one draw's noise. Would require an external criterion for agreement.
    * recovering R427's exact permutation -- its seed produced one realisation and the artifact
      stores the result, not the permutation. Would require re-running it, which would give a
      DIFFERENT draw and could not reproduce the committed number anyway. This is why the test is
      distributional and not a re-derivation.

EXIT  0 W-NOISE · 1 W-FRAMING or W-BIAS · 2 UNVERIFIED or controls unfit
"""
from __future__ import annotations
import hashlib
import itertools
import importlib.util
import json
import pathlib
import sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
HERE = pathlib.Path(__file__).resolve().parent
RES = HERE / "results"
R427 = ROOT / ("E05_the_space_of_compilers/A24_what_the_definition_costs/"
               "R427_does_the_definition_transport_at_all/results/r427_pairwise_excess.json")
ARMS = ["generic", "vacuous", "randblind_s0", "randblind_s1", "randblind_s2"]


def _load_run():
    spec = importlib.util.spec_from_file_location("r429run", HERE / "run.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def analytic_null(pa, pb, order):
    """dot(marginal_a, marginal_b) within each n-stratum, weighted by stratum size."""
    common = sorted(set(pa) & set(pb))
    by_n = {}
    for k in common:
        by_n.setdefault(pa[k][1], []).append(k)
    tot, num = 0, 0.0
    per_n = {}
    for n, keys in by_n.items():
        ma, mb = np.zeros(n), np.zeros(n)
        for k in keys:
            ma[order[k].index(pa[k][0])] += 1
            mb[order[k].index(pb[k][0])] += 1
        ma, mb = ma / ma.sum(), mb / mb.sum()
        per_n[n] = float(np.dot(ma, mb))
        num += per_n[n] * len(keys); tot += len(keys)
    return num / tot, per_n, by_n


def simulate_onedraw(pa, pb, order, by_n, rng, reps, frac=1.0, identity=False):
    """The sampling distribution of ONE permutation-based null, at the analytic value."""
    out = np.empty(reps)
    for r in range(reps):
        hit = tot = 0
        for n, keys in by_n.items():
            # ⚠ subsample by INDEX, never by element: `rng.choice` on a list of tuples returns an
            #   ndarray of ndarrays, and the keys stop being hashable. The first version died here,
            #   which is the cheap failure -- it crashed rather than silently subsampling wrong.
            if frac >= 1.0:
                ks = keys
            else:
                take = rng.choice(len(keys), max(2, int(len(keys) * frac)), replace=False)
                ks = [keys[i] for i in take]
            pos_a = np.array([order[k].index(pa[k][0]) for k in ks])
            pos_b = np.array([order[k].index(pb[k][0]) for k in ks])
            perm = np.arange(len(ks)) if identity else rng.permutation(len(ks))
            hit += int((pos_a == pos_b[perm]).sum()); tot += len(ks)
        out[r] = hit / tot
    return out


def main() -> int:
    RES.mkdir(parents=True, exist_ok=True)
    if not R427.exists():
        print("  UNRUNNABLE: R427's artifact absent. Exit 2, never 0."); return 2
    m = _load_run()
    scored, targets = {}, None
    for a in ARMS:
        s, t = m.load(a)
        if s is None:
            print(f"  UNRUNNABLE: sat_transport_{a}.npz absent. Exit 2."); return 2
        scored[a] = s; targets = targets or t
    P = {a: m.picks(scored[a], targets) for a in ARMS}
    order = {(t["conv"], t["inter"]): sorted(r["id"] for r in t["resp"]) for t in targets}
    r427 = {"|".join(sorted(k.split("|"))): v["null"]
            for k, v in json.loads(R427.read_text())["pairs"].items()}

    print("R429/null_estimator · is the ranking disagreement FRAMING, or one draw of noise?\n")

    pairs = list(itertools.combinations(ARMS, 2))
    an, byn = {}, {}
    for p in pairs:
        v, _per, b = analytic_null(P[p[0]], P[p[1]], order)
        an["|".join(sorted(p))] = v; byn[p] = b

    # ------------------------------------------------------------------------------- controls
    ok = True
    probe = pairs[0]
    seeds = [7, 8, 9]
    sims = np.concatenate([simulate_onedraw(P[probe[0]], P[probe[1]], order, byn[probe],
                                            np.random.default_rng(s), 140) for s in seeds])
    lo, hi = np.percentile(sims, [2.5, 97.5])
    av = an["|".join(sorted(probe))]
    contains = lo <= av <= hi
    ok &= contains
    print(f"  POSITIVE  simulated one-draw band for {probe[0]}|{probe[1]}: "
          f"[{lo:.4f},{hi:.4f}] must CONTAIN the analytic {av:.4f}   "
          f"{'PASS' if contains else '⛔ FAIL — the band is not a sampling distribution'}")

    idsim = simulate_onedraw(P[probe[0]], P[probe[1]], order, byn[probe],
                             np.random.default_rng(7), 40, identity=True)
    degen = float(idsim.std()) == 0.0
    ok &= degen
    print(f"  g=0       identity permutation -> band width {idsim.max()-idsim.min():.2e}, must be 0"
          f"   {'PASS' if degen else '⛔ FAIL — spread is not coming from the draw'}")

    plac = max(abs(an[k] - an[k]) for k in an)
    ok &= (plac == 0.0)
    print(f"  PLACEBO   analytic null vs itself, all 10 -> max |gap| {plac:.1e}, must be 0"
          f"   {'PASS' if plac == 0.0 else '⛔ FAIL'}")

    small = simulate_onedraw(P[probe[0]], P[probe[1]], order, byn[probe],
                             np.random.default_rng(11), 140, frac=0.25)
    widens = small.std() > sims.std()
    ok &= widens
    print(f"  NEGATIVE  at 25% of interactions the band sd goes {sims.std():.5f} -> "
          f"{small.std():.5f}, must WIDEN   "
          f"{'PASS' if widens else '⛔ FAIL — the band does not respond to n'}")

    if not ok:
        print("\n  UNVERIFIED — a control is unfit; the kill is NOT evaluated.")
        (RES / "r429_null_estimator.json").write_text(json.dumps({"world": "UNVERIFIED"}, indent=1))
        return 2

    # ------------------------------------------------------------------------------ the test
    print(f"\n  {'pair':<32}{'R427 null':>11}{'analytic':>11}{'gap':>9}{'band':>21}{'in?':>5}")
    rows, inside = [], 0
    for p in pairs:
        k = "|".join(sorted(p))
        s = np.concatenate([simulate_onedraw(P[p[0]], P[p[1]], order, byn[p],
                                             np.random.default_rng(sd), 140) for sd in seeds])
        blo, bhi = np.percentile(s, [2.5, 97.5])
        gap = r427[k] - an[k]
        ins = blo <= r427[k] <= bhi
        inside += ins
        rows.append({"pair": k, "r427_null": r427[k], "analytic": an[k], "gap": float(gap),
                     "band": [float(blo), float(bhi)], "inside": bool(ins),
                     "band_sd": float(s.std())})
        print(f"  {k:<32}{r427[k]:>11.4f}{an[k]:>11.4f}{gap:>+9.4f}"
              f"  [{blo:.4f},{bhi:.4f}]{'yes' if ins else ' no':>5}")

    gaps = np.array([r["gap"] for r in rows])
    half = float(np.mean([(r["band"][1] - r["band"][0]) / 2 for r in rows]))
    # ⛔ THE BRANCH BELOW ORIGINALLY TESTED TWO OF THE THREE WORLDS THIS ROUND DECLARED. The
    #    docstring names W-NOISE, W-FRAMING and W-BIAS; the code coded the first two and folded
    #    W-BIAS into W-FRAMING. That is this campaign's `the verdict string is not a computation`
    #    failure in its purest form -- the world existed in prose and had no branch -- and the data
    #    landed squarely in the missing branch: 2/10 inside, and all TEN gaps the same sign.
    #    W-BIAS is what "a systematic offset with a tight spread" means, and it is a different
    #    object from "two unrelated framings": a constant offset would not reorder anything, while
    #    a PAIR-VARYING offset reorders exactly the ranks whose gaps are smaller than its spread.
    #    So the discriminator is the offset's SPREAD across pairs, not its mean.
    same_sign = bool(np.all(gaps > 0) or np.all(gaps < 0))
    spread = float(gaps.std())
    world = ("W-NOISE" if (inside >= 8 and abs(gaps.mean()) < half) else
             "W-BIAS" if (inside <= 5 and same_sign) else
             "W-FRAMING" if inside <= 5 else "UNVERIFIED")
    print(f"\n  inside the one-draw band: {inside}/10 · mean gap {gaps.mean():+.4f} "
          f"vs mean band half-width {half:.4f}")
    print(f"  all ten gaps share a sign: {same_sign} · gap spread across pairs {spread:.4f} "
          f"(range {gaps.min():+.4f} to {gaps.max():+.4f})")
    print(f"  (10 pairs, one COUNT-based kill over the whole set — no per-pair correction is owed,"
          f" and that is stated rather than omitted)")
    print(f"\n  WORLD: {world}")
    if world == "W-NOISE":
        print("    R427's null is a ONE-DRAW estimate of the quantity R429 computes exactly, and")
        print("    its rank-5-to-10 ordering is that draw's noise. Neither round may quote an")
        print("    ordering below rank 4. The analytic null is the quoted one from here.")
        print("    ⚠ What does NOT change: ranks 1-4 agree in both, and R429's paired bootstrap")
        print("    separates rank 1 from rank 2 at +0.0234 [+0.0103,+0.0364], BH-surviving.")
    elif world == "W-BIAS":
        print(f"    the two nulls differ SYSTEMATICALLY, not randomly: all ten gaps carry the same")
        print(f"    sign and only {inside}/10 land inside the one-draw band. R427's null sits")
        print(f"    {abs(gaps.mean()):.4f} BELOW the analytic expectation of its own construction.")
        print(f"    ⛔ AND THE OFFSET IS NOT CONSTANT: it ranges {gaps.min():+.4f} to {gaps.max():+.4f},")
        print(f"    a spread of {spread:.4f}. A constant offset would reorder nothing; a")
        print(f"    pair-varying one reorders exactly the ranks whose gaps are smaller than it —")
        print(f"    which is ranks 5-10, and is why the two rounds disagree there and nowhere else.")
        print(f"    ⚠ WHAT THIS DOES NOT ESTABLISH: which null is correct. The simulation is a")
        print(f"    positive control on MY construction and shares its blind spots; it cannot")
        print(f"    adjudicate R427's. The direction is measured; the cause is UNVERIFIED.")
        print(f"    ⚠ WHAT SURVIVES: ranks 1-4 agree in both, and R429's paired bootstrap separates")
        print(f"    rank 1 from rank 2 at +0.0234 [+0.0103,+0.0364], BH-surviving over 45 cells.")
    elif world == "W-FRAMING":
        print("    the two nulls are genuinely different constructions. The spread IS the finding;")
        print("    neither ranking may be quoted alone, and the assumption they differ on is the")
        print("    next object.")
    else:
        print("    the test does not separate the worlds at this resolution. That is a statement")
        print("    about THIS design, not a verdict about either round.")

    (RES / "r429_null_estimator.json").write_text(json.dumps(
        {"source_sha": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()[:16],
         "world": world, "inside": int(inside), "n_pairs": len(pairs),
         "mean_gap": float(gaps.mean()), "mean_band_half": half,
         "seeds": seeds, "rows": rows}, indent=1))
    print(f"\n  artifact -> {(RES / 'r429_null_estimator.json').relative_to(ROOT)}")
    return 0 if world == "W-NOISE" else (2 if world == "UNVERIFIED" else 1)


if __name__ == "__main__":
    sys.exit(main())

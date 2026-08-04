"""R355 — R332's closure level is the FIRST closed reference, not the LOWEST SAFE one.

R332 defines the closure level in its own docstring as: "the LOWEST reference that is closed:
anything stronger is gratuitous, anything weaker admits an object the clause exists to exclude."
It then computes it as `closed[0]` -- the first grid index whose blind admission rate is 0.

Those are the same object ONLY IF the rate is monotone in the reference level, i.e. only if the
closed region is an UPWARD SET. Nothing guarantees that here, and R331 -- the sibling round that
motivated R332 -- already found the reason it need not be, in its own words:

    "A paired MDE is a property of the PAIR, not of the design. A near-neighbour has a small paired
     sd, so it clears its own resolution on a tiny gap."

R331 applied that to the ARM axis. `rate()` compares a class member against a reference VECTOR and
admits on `(e > 0) & (|e| >= mde)` where `mde` is the sd of the PER-PROMPT DIFFERENCE. So a
reference with a HIGHER MEAN but a different per-prompt PROFILE can have a smaller paired sd against
some blind set and admit it. The lesson was never applied to the REFERENCE axis, which is R332's own
instrument.

⛔ ARITHMETIC TRAP, answered before the run. Could this come out otherwise? YES. If admission were a
   threshold on the reference mean -- which is what every "level" sentence in this campaign presumes
   -- the closed region would be upward-closed BY CONSTRUCTION and the violation count would be
   identically 0. That world is not merely imagined: it is BUILT here as the negative control, by
   flattening every reference to a constant vector at its own mean. The comparison of the two is the
   round.

ESTIMAND        Per k and per grid: (a) `first0`, R332's published closure index; (b) `last_nonzero`,
                the index above which EVERY candidate is closed; (c) the number of candidate
                references strictly above `first0` whose blind admission rate is > 0, with the raw
                COUNT of blind sets each admits -- never only the rate, because a rate of 1.2e-4 is
                one cell out of 8,008 and must be reported as such.

IDENTIFICATION  Exact ON THE GRID: every C(16,k) subset is enumerated, so each rate is a population
                proportion over the whole blind class, not a sample of it. NOT identified: whether
                references BETWEEN grid points are closed. This makes the finding CONSERVATIVE --
                a finer grid can only ADD violations, so the measured `last_nonzero` is a LOWER
                bound on the true minimal safe level. The specification curve tests exactly this by
                sweeping 9 / 45 / 91 points.

SCOPE           968 CoVal prompts with >=2 annotators (398 for `promptecho`) · Qwen3.5-2B-Base under
                R234's canonical builder · the 16-criterion generic pool · k in R294's resolvable
                set · baseline = each candidate reference itself · regime: R332's own `rate()` and
                `build()`, COPIED VERBATIM rather than re-implemented, because the object under test
                is R332's instrument and a rewrite would test my code instead of its claim.

WORLDS
  W-UPWARD-CLOSED  admission is effectively a threshold on the reference mean; the violations are
                   absent, or are numerical ties. R332's `closed[0]` is the right object and the
                   docstring sentence is true.
  W-NEAR-NEIGHBOUR violations are real and concentrated in reference/blind-set pairs that SHARE
                   criteria -- the R331 pair-MDE effect, now on the reference axis. Closure must be
                   redefined as upward-closed; the mechanism is already known and named.
  W-CHAOTIC        violations are real and their shared-criteria profile matches the class baseline.
                   Then admission is not orderly in the reference level at all, and every sentence
                   in this campaign of the form "a reference at level L" is suspect.

PREDICTION MATRIX
  W-UPWARD-CLOSED  -> n_violations == 0 at every k, every grid
  W-NEAR-NEIGHBOUR -> n_violations > 0; mean shared criteria of violating pairs >> class baseline
  W-CHAOTIC        -> n_violations > 0; mean shared criteria ~= class baseline
The three differ on a measured statistic computed the same way in all three, so the round cannot
come out all ways.

PRE-REGISTERED KILL -- a CONDITIONAL, never a bare threshold. A kill that can fire on a broken
instrument is an automated way to publish an artifact.
    if placebo_ok and positive_ok and g0_ok and synthetic_ok:
        if total_violations == 0                      -> W-UPWARD-CLOSED, R332's sentence stands
        elif shared_violating >= shared_baseline + 1.0 -> W-NEAR-NEIGHBOUR
        else                                           -> W-CHAOTIC
    else: UNVERIFIED -- never OVERTURNED, never CONFIRMED.

⚠ THE MECHANISM ARM OF THAT KILL WAS UNFIT, AND IS REPLACED RATHER THAN RETUNED (v2, same session,
  found by reading v1's own output). Two defects, both in the comparison and neither in the data:
    (i)  `shared_baseline` accumulated once per violating REFERENCE while `shared_violating`
         accumulated once per (reference, admitted set) PAIR. Two different weightings compared as
         one object -- and v1's own permutation null, which carries the statistic's weighting, sat
         at 7.16-7.36 against the 6.68 the kill was using. The kill was reading a weighting
         artefact of 0.6 shared criteria as though it were mechanism.
    (ii) a RAW shared count is not comparable across k. Two k-subsets of a 16-pool share at least
         2k-16, so at k=13 every pair shares >=10 by pigeonhole while at k=3 the maximum is 3.
         Pooling raw counts across k measures WHICH k VIOLATED, not how similar the pairs are.
  The replacement is not a new threshold chosen to reach a verdict; it is this campaign's standing
  admission rule applied to the mechanism statistic: each pair scored as an EXCESS over its own k's
  permutation null, pooled, and required to clear ITS OWN MDE. That is strictly harder to pass than
  "+1.0 shared criteria" and it is the same rule every other number in this campaign is held to.
  Per P6 an unfit check is UNVERIFIED, never an acquittal -- so v1's W-NEAR-NEIGHBOUR verdict is
  withdrawn as unearned, whatever v2 returns.
  AND THE THIRD BRANCH IS NARROWED. v1 would have printed W-CHAOTIC whenever the excess failed to
  clear -- reading a null as evidence FOR the rival world. An excess inside its own resolution is
  silence about the mechanism. The count of violations is a CENSUS over an enumerated class and
  stands on its own either way; only its EXPLANATION is at stake in this arm.

POSITIVE CTRL   inject the WEAKEST reference (rate ~0.98 by construction) into the candidate list at
                a position ABOVE `first0`. The violation detector MUST flag it. A detector never
                shown able to return non-zero above the closure index would make every 0 below
                silence rather than a measurement.
g=0 CTRL        inject the class-MAX reference at that same slot. It must NOT be flagged. This is
                what stops the detector from firing on position rather than on rate.
PLACEBO         every candidate reference against itself: exactly 0 admitted, at every k.
NEGATIVE /      build W-UPWARD-CLOSED synthetically: replace each reference vector by a CONSTANT
SYNTHETIC       vector at its own mean, so admission becomes a pure threshold on the mean and the
                closed region is upward-closed by algebra. Violations MUST fall to 0. If they do
                not, the detector is measuring something other than the per-prompt profile and the
                whole reading is void. This is the world the finding excludes, built rather than
                imagined.
MULTIPLICITY    every (k, grid, candidate) cell computed is printed -- the violating ones and the
                closed ones -- with the cell count stated per grid.
SPECIFICATION   grid resolution 9 / 45 / 91 points, the axis R331-vs-R332 already proved is an
                instrument. Reported whole, including any grid that kills the finding.
SEEDS           the enumeration is deterministic; 3 seeds on the shared-criteria permutation null.
ARTIFACT        results/r355_upward_closed.json with the source hash.

IMPOSSIBLE HERE, each with what it would require
  cross-dataset / cross-pool  -- a second release, or a second criterion pool. Everything below is a
                                 fact about THIS 16-criterion pool.
  construct validity           -- an external gold standard for "safe reference". There is none; the
                                 clause's own words are the only criterion available.
  continuous identification    -- the true minimal safe level over ALL references, not just grid
                                 points, needs the full |class|-point sweep: 12,870 rates at k=8.

EXIT
    0  controls hold and the classification is reported
    1  a control misbehaved -- the verdict is UNVERIFIED and the numbers are silence
    2  an input is missing -- an empty population is never a silent pass
"""
from __future__ import annotations
import hashlib, itertools, json, math, pathlib, sys

import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "corebench"))
from score import load_sat, load_targets, yvec, cls          # noqa: E402
sys.path.insert(0, str(ROOT / "covalx"))
try:
    from stamp import stamp                                  # noqa: E402
except Exception:                                            # pragma: no cover
    def stamp(f):
        return {"source_sha256": hashlib.sha256(pathlib.Path(f).read_bytes()).hexdigest(),
                "source_name": pathlib.Path(f).name}

SELF = pathlib.Path(__file__).resolve()
HERE = SELF.parent
A24 = ROOT / "E05_the_space_of_compilers" / "A24_what_the_definition_costs"
PAIRS = list(itertools.combinations(range(4), 2))
ZEFF = 1.959964 + 0.841621

# The three grids. R331 used 9 points, R332 used 45. 91 is the refinement that tests whether the
# measured last_nonzero is a lower bound, as IDENTIFICATION states it must be.
GRIDS = {
    9:  np.array([0.0, 10.0, 25.0, 50.0, 75.0, 90.0, 95.0, 99.0, 100.0]),
    45: np.concatenate([np.array([0.0, 25.0, 50.0, 75.0]), np.linspace(80.0, 100.0, 41)]),
    91: np.concatenate([np.array([0.0, 25.0, 50.0, 75.0]), np.linspace(80.0, 100.0, 87)]),
}


def load_json(pat):
    d = next(A24.glob(pat), None)
    if d is None:
        return None
    f = sorted((d / "results").glob("*.json"))
    return json.loads(f[0].read_text()) if f else None


def admitted_mask(Bk, ref_vec):
    """R332's `rate()`, verbatim in its arithmetic, returning the MASK instead of the mean.

    Copied rather than re-derived: the object under test is R332's instrument."""
    d = Bk - ref_vec
    e = d.mean(axis=1)
    mde = ZEFF * d.std(axis=1, ddof=1) / math.sqrt(d.shape[1])
    return (e > 0) & (np.abs(e) >= mde)


def candidates(per, grid):
    """R332's grid: order the class by mean, take the member at each percentile, dedup keeping order."""
    order = np.argsort(per)
    seen, cand = set(), []
    for p in grid:
        c = int(order[min(int(round(p / 100 * (len(order) - 1))), len(order) - 1)])
        if c not in seen:
            seen.add(c); cand.append(c)
    return cand


def main() -> int:
    r294 = load_json("R294_*")
    if r294 is None:
        print("  UNRUNNABLE: R294's census is absent. Exit 2, never 0.")
        return 2
    rows = r294["rows"]

    tg, _ = load_targets()
    S = load_sat(ROOT / "corebench" / "results" / "sat_genericpool16.npz")
    pids = sorted(set(S) & {p for p in tg if len(tg[p]) >= 2})
    H = [np.array([cls(np.array(t[0], float)) for t in tg[p]], float) for p in pids]
    N = len(pids)
    npool = len({i for i, _ in S[pids[0]]})
    SAT = np.stack([np.array([[S[p][(i, x)] for x in "ABCD"] for i in range(npool)], float)
                    for p in pids])
    ii = np.array([i for i, _ in PAIRS]); jj = np.array([j for _, j in PAIRS])
    KS = sorted({min(rows[a]["k"], npool) for a in rows if rows[a]["ok3"]})

    def build(k):
        sb = np.array(list(itertools.combinations(range(npool), k)))
        out = np.empty((len(sb), N))
        for n in range(N):
            Y = SAT[n][sb].sum(axis=1)
            C_ = np.sign(Y[:, ii] - Y[:, jj])
            out[:, n] = (C_[:, None, :] == H[n][None, :, :]).mean(axis=(1, 2))
        return sb, out

    print(f"R355 · is the closed region upward-closed?   {N} prompts · pool {npool} · k in {KS}\n")
    print("  R332's docstring: \"the LOWEST reference that is closed: anything stronger is")
    print("  gratuitous\". Its code takes closed[0] — the FIRST zero. Those differ iff the rate")
    print("  is non-monotone in the reference level.\n")

    SUBS, BK = {}, {}
    for k in KS:
        SUBS[k], BK[k] = build(k)

    # ---- PLACEBO, before anything is believed ------------------------------------------------------
    placebo = []
    for k in KS:
        per = BK[k].mean(axis=1)
        for c in candidates(per, GRIDS[45]):
            placebo.append(int(admitted_mask(BK[k], BK[k][c])[c]))
    placebo_ok = sum(placebo) == 0
    print(f"  PLACEBO   every reference against itself, {len(placebo)} cells: "
          f"{sum(placebo)} self-admissions  {'PASS' if placebo_ok else 'FAIL'}")

    # ---- the measurement, over the specification curve ---------------------------------------------
    RES, cells = {}, {}
    for g, grid in GRIDS.items():
        RES[g], cells[g] = {}, 0
        for k in KS:
            per = BK[k].mean(axis=1)
            cand = candidates(per, grid)
            cells[g] += len(cand)
            masks = [admitted_mask(BK[k], BK[k][c]) for c in cand]
            counts = [int(m.sum()) for m in masks]
            zeros = [i for i, n_ in enumerate(counts) if n_ == 0]
            if not zeros:
                RES[g][k] = None
                continue
            first0 = zeros[0]
            nz_above = [i for i in range(first0 + 1, len(cand)) if counts[i] > 0]
            last_nz = max(nz_above) if nz_above else first0 - 1
            safe = last_nz + 1
            RES[g][k] = dict(
                n_cand=len(cand), first0=first0, safe_idx=safe,
                first0_a2=float(per[cand[first0]]),
                safe_a2=float(per[cand[safe]]) if safe < len(cand) else None,
                first0_pct=float(100.0 * (per < per[cand[first0]]).mean()),
                safe_pct=float(100.0 * (per < per[cand[safe]]).mean()) if safe < len(cand) else None,
                n_violations=len(nz_above),
                violation_counts=[counts[i] for i in nz_above],
                violating_refs=[int(cand[i]) for i in nz_above],
                violating_admits=[[int(x) for x in np.where(masks[i])[0]] for i in nz_above],
            )

    print(f"\n  SPECIFICATION CURVE — grid resolution is an instrument (R331 9pt vs R332 45pt)\n")
    print(f"    {'grid':>5}{'cells':>7}{'k':>4}{'first0':>8}{'safe':>6}"
          f"{'first0 A2':>11}{'safe A2':>10}{'viol':>6}   blind sets admitted above first0")
    for g in sorted(GRIDS):
        for k in KS:
            r = RES[g][k]
            if r is None:
                print(f"    {g:>5}{cells[g]:>7}{k:>4}{'never closes':>28}")
                continue
            sa = f"{r['safe_a2']:.4f}" if r["safe_a2"] is not None else "none"
            print(f"    {g:>5}{cells[g]:>7}{k:>4}{r['first0']:>8}{r['safe_idx']:>6}"
                  f"{r['first0_a2']:>11.4f}{sa:>10}{r['n_violations']:>6}   {r['violation_counts']}")
        print()

    tot = {g: sum(RES[g][k]["n_violations"] for k in KS if RES[g][k]) for g in GRIDS}
    print(f"  total violations by grid: {dict(sorted(tot.items()))}")
    print(f"  IDENTIFICATION said a finer grid can only ADD violations (the coarse grid cannot see")
    print(f"  a reference it never evaluates). Observed 9->45->91: "
          f"{tot[9]} -> {tot[45]} -> {tot[91]}  "
          f"{'CONSISTENT' if tot[9] <= tot[45] <= tot[91] else 'VIOLATED — the grids are not nested'}")

    # ---- POSITIVE / g=0 controls on the violation detector -----------------------------------------
    k0 = 4 if 4 in KS else KS[0]
    per0 = BK[k0].mean(axis=1)
    cand0 = candidates(per0, GRIDS[45])
    weakest, strongest = int(np.argmin(per0)), int(np.argmax(per0))
    r0 = RES[45][k0]

    def viol_above(cand_list, first0):
        return [i for i in range(first0 + 1, len(cand_list))
                if int(admitted_mask(BK[k0], BK[k0][cand_list[i]]).sum()) > 0]

    inj_pos = cand0[:] + [weakest]
    pos_ok = (len(inj_pos) - 1) in viol_above(inj_pos, r0["first0"])
    inj_g0 = cand0[:] + [strongest]
    g0_hit = (len(inj_g0) - 1) in viol_above(inj_g0, r0["first0"])
    g0_ok = not g0_hit
    print(f"\n  POSITIVE  weakest reference (rate {admitted_mask(BK[k0],BK[k0][weakest]).mean():.3f}) "
          f"injected ABOVE first0 -> {'flagged' if pos_ok else 'MISSED'}  {'PASS' if pos_ok else 'FAIL'}")
    print(f"  g=0       class-max reference injected in the SAME slot -> "
          f"{'flagged' if g0_hit else 'not flagged'}  {'PASS' if g0_ok else 'FAIL — fires on position'}")

    # ---- NEGATIVE / SYNTHETIC: build W-UPWARD-CLOSED and require violations to vanish ---------------
    syn_tot, syn_detail = 0, {}
    for k in KS:
        per = BK[k].mean(axis=1)
        cand = candidates(per, GRIDS[45])
        counts = [int(admitted_mask(BK[k], np.full(N, per[c])).sum()) for c in cand]
        zeros = [i for i, n_ in enumerate(counts) if n_ == 0]
        v = len([i for i in range(zeros[0] + 1, len(cand)) if counts[i] > 0]) if zeros else -1
        syn_detail[k] = v
        syn_tot += max(v, 0)
    syn_ok = syn_tot == 0
    print(f"\n  SYNTHETIC (the rival world, BUILT)  each reference flattened to a constant vector at")
    print(f"    its own mean -> admission becomes a pure threshold on the mean, so the closed region")
    print(f"    is upward-closed BY ALGEBRA. violations per k {syn_detail}, total {syn_tot}  "
          f"{'PASS' if syn_ok else 'FAIL — the detector is not reading the per-prompt profile'}")

    # ---- mechanism: shared criteria, EXCESS OVER THAT k's OWN NULL --------------------------------
    # ⚠ Two defects in v1 of this block, both fixed here and both found by reading the output.
    #  (1) the baseline was accumulated once per violating REFERENCE while the statistic was once per
    #      (reference, admitted set) PAIR -- two different weightings compared as though they were one
    #      object. The permutation null carries the statistic's OWN weighting and is the only
    #      admissible comparison.
    #  (2) a raw shared count is NOT COMPARABLE ACROSS k: two k-subsets of a 16-pool share at least
    #      2k-16, so at k=13 every pair shares >=10 by pigeonhole and at k=3 at most 3. Pooling raw
    #      counts measures which k happened to violate. Every pair is therefore scored as an EXCESS
    #      over its own k's permutation null, which is dimensionless in the same way for all k.
    per_k, seeds_sp, exc_all = {}, {}, []
    for k in KS:
        r = RES[45][k]
        if not r or not r["n_violations"]:
            continue
        sb = SUBS[k]
        obs, nulls = [], {s: [] for s in (0, 1, 2)}
        for ref, adm in zip(r["violating_refs"], r["violating_admits"]):
            rs = set(sb[ref].tolist())
            obs += [len(rs & set(sb[a].tolist())) for a in adm]
            for s in (0, 1, 2):
                rng = np.random.default_rng(1000 * s + ref)
                nulls[s] += [len(rs & set(sb[rng.integers(len(sb))].tolist())) for _ in adm]
        nm = float(np.mean([np.mean(nulls[s]) for s in (0, 1, 2)]))
        floor_ = max(0, 2 * k - npool)
        per_k[k] = dict(n=len(obs), obs=float(np.mean(obs)), null=nm,
                        excess=float(np.mean(obs)) - nm, pigeonhole_floor=floor_,
                        seeds=[float(np.mean(nulls[s])) for s in (0, 1, 2)])
        exc_all += [o - nm for o in obs]
    mech_ok = bool(exc_all)
    mv = float(np.mean(exc_all)) if exc_all else float("nan")
    sd = float(np.std(exc_all, ddof=1)) if len(exc_all) > 1 else float("nan")
    mde_exc = ZEFF * sd / math.sqrt(len(exc_all)) if len(exc_all) > 1 else float("nan")
    print(f"\n  MECHANISM  criteria shared between a violating reference and the blind set it admits,")
    print(f"    scored as an EXCESS over that k's own permutation null (raw counts are not")
    print(f"    comparable across k: two k-subsets of {npool} share at least 2k-{npool} by pigeonhole)")
    print(f"      {'k':>3}{'pairs':>7}{'observed':>10}{'null':>8}{'excess':>9}{'floor':>7}   null across 3 seeds")
    for k in sorted(per_k):
        d = per_k[k]
        print(f"      {k:>3}{d['n']:>7}{d['obs']:>10.2f}{d['null']:>8.2f}{d['excess']:>+9.2f}"
              f"{d['pigeonhole_floor']:>7}   {[round(x,2) for x in d['seeds']]}")
    print(f"    pooled excess {mv:+.3f} against its own MDE {mde_exc:.3f} (n={len(exc_all)} pairs, "
          f"sd {sd:.3f}) -> {'RESOLVED' if mv > mde_exc else 'INSIDE THE MDE'}")

    # ---- verdict: a CONDITIONAL, so it cannot fire on a broken instrument ---------------------------
    ctrl_ok = placebo_ok and pos_ok and g0_ok and syn_ok
    print()
    if not ctrl_ok:
        print("  UNVERIFIED — a control misbehaved, so every number above is silence.")
        v = "UNVERIFIED"
    elif tot[45] == 0:
        print("  W-UPWARD-CLOSED — no reference above first0 admits anything. R332's sentence stands.")
        v = "W_UPWARD_CLOSED"
    elif mech_ok and mv > mde_exc:
        print(f"  W-NEAR-NEIGHBOUR — the closed region is NOT an upward set: {tot[45]} references")
        print(f"  ABOVE R332's closure index admit blind sets again. The mechanism is R331's, on the")
        print(f"  axis R331 never applied it to: a violating pair shares {mv:+.2f} criteria more than")
        print(f"  its own k's null (MDE {mde_exc:.2f}), so a near-neighbour reference has a small")
        print(f"  PAIRED sd and clears its own resolution on a tiny gap.")
        v = "W_NEAR_NEIGHBOUR"
    else:
        print(f"  NOT-UPWARD-CLOSED, MECHANISM UNRESOLVED — {tot[45]} references above R332's closure")
        print(f"  index admit blind sets, and that COUNT is a census, not an inference. But the")
        print(f"  shared-criteria excess {mv:+.3f} sits inside its own MDE {mde_exc:.3f}, so this")
        print(f"  round does NOT establish the near-neighbour mechanism. ⚠ Nor does it establish")
        print(f"  W-CHAOTIC: an excess inside the resolution is silence about the mechanism, and")
        print(f"  reading it as evidence for the rival would be a null used as a finding.")
        v = "W_NOT_UPWARD_CLOSED_MECHANISM_UNRESOLVED"

    if ctrl_ok and tot[45] > 0:
        print(f"\n  ⛔ WHAT THIS RETRACTS. R332's published closure levels are the FIRST closed")
        print(f"     reference, not the lowest SAFE one. Corrected, at the 45-point grid:")
        print(f"       {'k':>3}{'R332 closure':>14}{'pctile':>8}   {'minimal SAFE':>13}{'pctile':>8}")
        for k in KS:
            r = RES[45][k]
            if not r:
                continue
            if r["n_violations"] == 0:
                print(f"       {k:>3}{r['first0_a2']:>14.4f}{r['first0_pct']:>8.1f}   "
                      f"{'(unchanged)':>13}")
            else:
                sa = f"{r['safe_a2']:.4f}" if r["safe_a2"] is not None else "none in grid"
                sp = f"{r['safe_pct']:.1f}" if r["safe_pct"] is not None else "--"
                print(f"       {k:>3}{r['first0_a2']:>14.4f}{r['first0_pct']:>8.1f}   "
                      f"{sa:>13}{sp:>8}")

    art = dict(stamp(str(SELF)), n_prompts=N, pool=npool, ks=KS,
               grids={str(g): {str(k): RES[g][k] for k in KS} for g in GRIDS},
               cells=cells, totals={str(g): tot[g] for g in GRIDS},
               controls=dict(placebo=placebo_ok, positive=pos_ok, g0=g0_ok, synthetic=syn_ok,
                             synthetic_per_k=syn_detail),
               mechanism=dict(excess_pooled=mv,
                              per_k=per_k, pooled_mde=mde_exc, n_pairs_pooled=len(exc_all)),
               verdict=v)
    (HERE / "results").mkdir(exist_ok=True)
    outp = HERE / "results" / "r355_upward_closed.json"
    outp.write_text(json.dumps(art, indent=2, sort_keys=True, default=str))
    print(f"\n  artifact {outp.relative_to(ROOT)}  "
          f"sha256[:12] {hashlib.sha256(outp.read_bytes()).hexdigest()[:12]}")
    return 0 if ctrl_ok else 1


if __name__ == "__main__":
    sys.exit(main())
